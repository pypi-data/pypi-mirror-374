#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/dl-loader-export.h>
#include <alpaqa/dl/dl-problem.h>
#include <alpaqa/problem/box-constr-problem.hpp>
#include <alpaqa/problem/sparsity.hpp>
#include <guanaqo/demangled-typename.hpp>
#include <guanaqo/dl-flags.hpp>
#include <guanaqo/dl.hpp>

#include <filesystem>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>

namespace alpaqa::dl {

using guanaqo::dynamic_load_error;
using guanaqo::DynamicLoadFlags;

struct DL_LOADER_EXPORT invalid_abi_error : dynamic_load_error {
    using dynamic_load_error::dynamic_load_error;
};

class ExtraFuncs {
  public:
    /// Unique type for calling an extra function that is a member function.
    struct instance_t;

    ExtraFuncs() = default;
    ExtraFuncs(std::shared_ptr<function_dict_t> &&extra_funcs)
        : extra_functions(std::move(extra_funcs)) {}

    /// An associative array of additional functions exposed by the problem.
    std::shared_ptr<function_dict_t> extra_functions;

    template <class Signature>
        requires std::is_function_v<Signature>
    const std::function<Signature> &extra_func(const std::string &name) const {
        if (!extra_functions)
            throw std::out_of_range("DLProblem: no extra functions");
        auto it = extra_functions->dict.find(name);
        if (it == extra_functions->dict.end())
            throw std::out_of_range("DLProblem: no extra function named \"" +
                                    name + '"');
        try {
            using func_t = detail::function_wrapper_t<Signature>;
            return std::any_cast<const func_t &>(it->second).function;
        } catch (const std::bad_any_cast &) {
            throw std::logic_error(
                "DLProblem: incorrect type for extra function \"" + name +
                "\" (stored type: " +
                guanaqo::demangled_typename(it->second.type()) + ')');
        }
    }

    template <class Func>
    struct FuncTag {};

    template <class Ret, class... FArgs, class... Args>
    decltype(auto)
    call_extra_func_helper(const void *instance,
                           FuncTag<Ret(const instance_t *, FArgs...)>,
                           const std::string &name, Args &&...args) const {
        return extra_func<Ret(const void *, FArgs...)>(name)(
            instance, std::forward<Args>(args)...);
    }

    template <class Ret, class... FArgs, class... Args>
    decltype(auto)
    call_extra_func_helper(void *instance, FuncTag<Ret(instance_t *, FArgs...)>,
                           const std::string &name, Args &&...args) {
        return extra_func<Ret(void *, FArgs...)>(name)(
            instance, std::forward<Args>(args)...);
    }

    template <class Ret, class... FArgs, class... Args>
    decltype(auto) call_extra_func_helper(const void *, FuncTag<Ret(FArgs...)>,
                                          const std::string &name,
                                          Args &&...args) const {
        return extra_func<Ret(FArgs...)>(name)(std::forward<Args>(args)...);
    }
};

/// Class that loads a problem using `dlopen`.
///
/// The shared library should export a C function with the name @c function_name
/// that accepts a void pointer with user data, and returns a struct of type
/// @ref alpaqa_problem_register_t that contains all data to represent the
/// problem, as well as function pointers for all required operations.
/// See @ref C++/DLProblem/main.cpp and
/// @ref problems/sparse-logistic-regression.cpp for examples.
///
/// @note   Copies are shallow, they all share the same problem instance, take
///         that into account when using multiple threads.
///
/// @ingroup    grp_Problems
/// @see @ref   TypeErasedProblem
/// @see @ref   alpaqa_problem_functions_t
/// @see @ref   alpaqa_problem_register_t
class DL_LOADER_EXPORT DLProblem : public BoxConstrProblem<DefaultConfig> {
  public:
    USING_ALPAQA_CONFIG(DefaultConfig);

    /// Load a problem from a shared library.
    DLProblem(
        /// Filename of the shared library to load.
        const std::filesystem::path &so_filename,
        /// Name of the problem registration function.
        /// Should have signature
        /// `alpaqa_problem_register_t(alpaqa_register_arg_t user_param)`.
        const std::string &function_name = "register_alpaqa_problem",
        /// Pointer to custom user data to pass to the registration function.
        alpaqa_register_arg_t user_param = {},
        /// Flags passed to dlopen when loading the problem.
        DynamicLoadFlags dl_flags = {});
    /// Load a problem from a shared library.
    DLProblem(
        /// Filename of the shared library to load.
        const std::filesystem::path &so_filename,
        /// Name of the problem registration function.
        /// Should have signature
        /// `alpaqa_problem_register_t(alpaqa_register_arg_t user_param)`.
        const std::string &function_name,
        /// Custom user data to pass to the registration function.
        std::any &user_param,
        /// Flags passed to dlopen when loading the problem.
        DynamicLoadFlags dl_flags = {});
    /// Load a problem from a shared library.
    DLProblem(
        /// Filename of the shared library to load.
        const std::filesystem::path &so_filename,
        /// Name of the problem registration function.
        /// Should have signature
        /// `alpaqa_problem_register_t(alpaqa_register_arg_t user_param)`.
        const std::string &function_name,
        /// Custom string arguments to pass to the registration function.
        std::span<std::string_view> user_param,
        /// Flags passed to dlopen when loading the problem.
        DynamicLoadFlags dl_flags = {});

  private:
    /// Path to the shared module file.
    std::filesystem::path file;
    /// Handle to the shared module defining the problem.
    std::shared_ptr<void> handle;
    /// Problem instance created by the registration function, including the
    /// deleter to destroy it.
    std::shared_ptr<void> instance;
    /// Pointer to the struct of function pointers for evaluating the objective,
    /// constraints, their gradients, etc.
    problem_functions_t *functions = nullptr;
    /// Dictionary of extra functions that were registered by the problem.
    ExtraFuncs extra_funcs;

  public:
    // clang-format off
    void eval_projecting_difference_constraints(crvec z, rvec e) const;
    void eval_projection_multipliers(rvec y, real_t M) const;
    real_t eval_proximal_gradient_step(real_t γ, crvec x, crvec grad_ψ, rvec x̂, rvec p) const;
    index_t eval_inactive_indices_res_lna(real_t γ, crvec x, crvec grad_ψ, rindexvec J) const;
    real_t eval_objective(crvec x) const;
    void eval_objective_gradient(crvec x, rvec grad_fx) const;
    void eval_constraints(crvec x, rvec gx) const;
    void eval_constraints_gradient_product(crvec x, crvec y, rvec grad_gxy) const;
    void eval_constraints_jacobian(crvec x, rvec J_values) const;
    Sparsity get_constraints_jacobian_sparsity() const;
    void eval_grad_gi(crvec x, index_t i, rvec grad_gi) const;
    void eval_lagrangian_hessian_product(crvec x, crvec y, real_t scale, crvec v, rvec Hv) const;
    void eval_lagrangian_hessian(crvec x, crvec y, real_t scale, rvec H_values) const;
    Sparsity get_lagrangian_hessian_sparsity() const;
    void eval_augmented_lagrangian_hessian_product(crvec x, crvec y, crvec Σ, real_t scale, crvec v, rvec Hv) const;
    void eval_augmented_lagrangian_hessian(crvec x, crvec y, crvec Σ, real_t scale, rvec H_values) const;
    Sparsity get_augmented_lagrangian_hessian_sparsity() const;
    real_t eval_objective_and_gradient(crvec x, rvec grad_fx) const;
    real_t eval_objective_and_constraints(crvec x, rvec g) const;
    void eval_objective_gradient_and_constraints_gradient_product(crvec x, crvec y, rvec grad_f, rvec grad_gxy) const;
    void eval_lagrangian_gradient(crvec x, crvec y, rvec grad_L, rvec work_n) const;
    real_t eval_augmented_lagrangian(crvec x, crvec y, crvec Σ, rvec ŷ) const;
    void eval_augmented_lagrangian_gradient(crvec x, crvec y, crvec Σ, rvec grad_ψ, rvec work_n, rvec work_m) const;
    real_t eval_augmented_lagrangian_and_gradient(crvec x, crvec y, crvec Σ, rvec grad_ψ, rvec work_n, rvec work_m) const;
    std::string get_name() const;

    [[nodiscard]] bool provides_eval_objective() const;
    [[nodiscard]] bool provides_eval_objective_gradient() const;
    [[nodiscard]] bool provides_eval_constraints() const;
    [[nodiscard]] bool provides_eval_constraints_gradient_product() const;
    [[nodiscard]] bool provides_eval_constraints_jacobian() const;
    [[nodiscard]] bool provides_get_constraints_jacobian_sparsity() const;
    [[nodiscard]] bool provides_eval_grad_gi() const;
    [[nodiscard]] bool provides_eval_lagrangian_hessian_product() const;
    [[nodiscard]] bool provides_eval_lagrangian_hessian() const;
    [[nodiscard]] bool provides_get_lagrangian_hessian_sparsity() const;
    [[nodiscard]] bool provides_eval_augmented_lagrangian_hessian_product() const;
    [[nodiscard]] bool provides_eval_augmented_lagrangian_hessian() const;
    [[nodiscard]] bool provides_get_augmented_lagrangian_hessian_sparsity() const;
    [[nodiscard]] bool provides_eval_objective_and_gradient() const;
    [[nodiscard]] bool provides_eval_objective_and_constraints() const;
    [[nodiscard]] bool provides_eval_objective_gradient_and_constraints_gradient_product() const;
    [[nodiscard]] bool provides_eval_lagrangian_gradient() const;
    [[nodiscard]] bool provides_eval_augmented_lagrangian() const;
    [[nodiscard]] bool provides_eval_augmented_lagrangian_gradient() const;
    [[nodiscard]] bool provides_eval_augmented_lagrangian_and_gradient() const;
    [[nodiscard]] bool provides_get_variable_bounds() const;
    [[nodiscard]] bool provides_get_general_bounds() const;
    [[nodiscard]] bool provides_eval_inactive_indices_res_lna() const;
    // clang-format on

    using instance_t = ExtraFuncs::instance_t;

    template <class Signature, class... Args>
    decltype(auto) call_extra_func(const std::string &name,
                                   Args &&...args) const {
        return call_extra_func_helper(instance.get(),
                                      ExtraFuncs::FuncTag<Signature>{}, name,
                                      std::forward<Args>(args)...);
    }

    template <class Signature, class... Args>
    decltype(auto) call_extra_func(const std::string &name, Args &&...args) {
        return extra_funcs.call_extra_func_helper(
            instance.get(), ExtraFuncs::FuncTag<Signature>{}, name,
            std::forward<Args>(args)...);
    }
};

#if ALPAQA_WITH_OCP

/// Class that loads an optimal control problem using `dlopen`.
///
/// The shared library should export a C function with the name @c function_name
/// that accepts a void pointer with user data, and returns a struct of type
/// @ref alpaqa_control_problem_register_t that contains all data to represent
/// the problem, as well as function pointers for all required operations.
///
/// @note   Copies are shallow, they all share the same problem instance, take
///         that into account when using multiple threads.
///
/// @ingroup    grp_Problems
/// @see @ref   TypeErasedControlProblem
class DL_LOADER_EXPORT DLControlProblem {
  public:
    USING_ALPAQA_CONFIG(DefaultConfig);
    using Box = alpaqa::Box<config_t>;

    /// Load a problem from a shared library.
    DLControlProblem(
        /// Filename of the shared library to load.
        const std::filesystem::path &so_filename,
        /// Name of the problem registration function.
        /// Should have signature
        /// `alpaqa_control_problem_register_t(alpaqa_register_arg_t user_param)`.
        const std::string &function_name = "register_alpaqa_control_problem",
        /// Pointer to custom user data to pass to the registration function.
        alpaqa_register_arg_t user_param = {},
        /// Flags passed to dlopen when loading the problem.
        DynamicLoadFlags dl_flags = {});

  private:
    /// Handle to the shared module defining the problem.
    std::shared_ptr<void> handle;
    /// Problem instance created by the registration function, including the
    /// deleter to destroy it.
    std::shared_ptr<void> instance;
    /// Pointer to the struct of function pointers for evaluating the objective,
    /// constraints, their gradients, etc.
    control_problem_functions_t *functions = nullptr;
    /// Dictionary of extra functions that were registered by the problem.
    ExtraFuncs extra_funcs;

  public:
    length_t get_N() const { return functions->N; }
    length_t get_nx() const { return functions->nx; }
    length_t get_nu() const { return functions->nu; }
    length_t get_nh() const { return functions->nh; }
    length_t get_nh_N() const { return functions->nh_N; }
    length_t get_nc() const { return functions->nc; }
    length_t get_nc_N() const { return functions->nc_N; }

    void check() const {} // TODO

    // clang-format off
    void get_U(Box &U) const;
    void get_D(Box &D) const;
    void get_D_N(Box &D) const;
    void get_x_init(rvec x_init) const;
    void eval_f(index_t timestep, crvec x, crvec u, rvec fxu) const;
    void eval_jac_f(index_t timestep, crvec x, crvec u, rmat J_fxu) const;
    void eval_grad_f_prod(index_t timestep, crvec x, crvec u, crvec p, rvec grad_fxu_p) const;
    void eval_h(index_t timestep, crvec x, crvec u, rvec h) const;
    void eval_h_N(crvec x, rvec h) const;
    [[nodiscard]] real_t eval_l(index_t timestep, crvec h) const;
    [[nodiscard]] real_t eval_l_N(crvec h) const;
    void eval_qr(index_t timestep, crvec xu, crvec h, rvec qr) const;
    void eval_q_N(crvec x, crvec h, rvec q) const;
    void eval_add_Q(index_t timestep, crvec xu, crvec h, rmat Q) const;
    void eval_add_Q_N(crvec x, crvec h, rmat Q) const;
    void eval_add_R_masked(index_t timestep, crvec xu, crvec h, crindexvec mask, rmat R, rvec work) const;
    void eval_add_S_masked(index_t timestep, crvec xu, crvec h, crindexvec mask, rmat S, rvec work) const;
    void eval_add_R_prod_masked(index_t timestep, crvec xu, crvec h, crindexvec mask_J, crindexvec mask_K, crvec v, rvec out, rvec work) const;
    void eval_add_S_prod_masked(index_t timestep, crvec xu, crvec h, crindexvec mask_K, crvec v, rvec out, rvec work) const;
    [[nodiscard]] length_t get_R_work_size() const;
    [[nodiscard]] length_t get_S_work_size() const;
    void eval_constr(index_t timestep, crvec x, rvec c) const;
    void eval_constr_N(crvec x, rvec c) const;
    void eval_grad_constr_prod(index_t timestep, crvec x, crvec p, rvec grad_cx_p) const;
    void eval_grad_constr_prod_N(crvec x, crvec p, rvec grad_cx_p) const;
    void eval_add_gn_hess_constr(index_t timestep, crvec x, crvec M, rmat out) const;
    void eval_add_gn_hess_constr_N(crvec x, crvec M, rmat out) const;

    [[nodiscard]] bool provides_get_D() const;
    [[nodiscard]] bool provides_get_D_N() const;
    [[nodiscard]] bool provides_eval_add_Q_N() const;
    [[nodiscard]] bool provides_eval_add_R_prod_masked() const;
    [[nodiscard]] bool provides_eval_add_S_prod_masked() const;
    [[nodiscard]] bool provides_get_R_work_size() const;
    [[nodiscard]] bool provides_get_S_work_size() const;
    [[nodiscard]] bool provides_eval_constr() const;
    [[nodiscard]] bool provides_eval_constr_N() const;
    [[nodiscard]] bool provides_eval_grad_constr_prod() const;
    [[nodiscard]] bool provides_eval_grad_constr_prod_N() const;
    [[nodiscard]] bool provides_eval_add_gn_hess_constr() const;
    [[nodiscard]] bool provides_eval_add_gn_hess_constr_N() const;
    // clang-format on

    using instance_t = ExtraFuncs::instance_t;

    template <class Signature, class... Args>
    decltype(auto) call_extra_func(const std::string &name,
                                   Args &&...args) const {
        return extra_funcs.call_extra_func_helper(
            instance.get(), ExtraFuncs::FuncTag<Signature>{}, name,
            std::forward<Args>(args)...);
    }

    template <class Signature, class... Args>
    decltype(auto) call_extra_func(const std::string &name, Args &&...args) {
        return extra_funcs.call_extra_func_helper(
            instance.get(), ExtraFuncs::FuncTag<Signature>{}, name,
            std::forward<Args>(args)...);
    }
};

#endif

} // namespace alpaqa::dl