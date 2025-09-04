#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/export.hpp>
#include <alpaqa/problem/box.hpp>
#include <alpaqa/problem/sparsity.hpp>
#include <alpaqa/util/alloc-check.hpp>
#include <alpaqa/util/check-dim.hpp>
#include <guanaqo/not-implemented.hpp>
#include <guanaqo/required-method.hpp>
#include <guanaqo/type-erasure.hpp>
#include <type_traits>
#include <utility>

namespace alpaqa {

/// Raised when calling problem functions that are not implemented.
using guanaqo::not_implemented_error;

/// Struct containing function pointers to all problem functions (like the
/// objective and constraint functions, with their derivatives, and more).
/// Some default implementations are available.
/// Internal struct, it is used by @ref TypeErasedProblem.
template <Config Conf>
struct ProblemVTable : guanaqo::BasicVTable {
    USING_ALPAQA_CONFIG(Conf);
    using Box = alpaqa::Box<config_t>;

    template <class F>
    using optional_function_t = guanaqo::optional_function_t<F, ProblemVTable>;
    template <class F>
    using required_function_t = guanaqo::required_function_t<F>;

    // clang-format off

    // Required
    required_function_t<void(crvec z, rvec e) const>
        eval_projecting_difference_constraints;
    required_function_t<void(rvec y, real_t M) const>
        eval_projection_multipliers;
    required_function_t<real_t(real_t γ, crvec x, crvec grad_ψ, rvec x̂, rvec p) const>
        eval_proximal_gradient_step;
    required_function_t<real_t(crvec x) const>
        eval_objective;
    required_function_t<void(crvec x, rvec grad_fx) const>
        eval_objective_gradient;
    required_function_t<void(crvec x, rvec gx) const>
        eval_constraints;
    required_function_t<void(crvec x, crvec y, rvec grad_gxy) const>
        eval_constraints_gradient_product;
    optional_function_t<index_t(real_t γ, crvec x, crvec grad_ψ, rindexvec J) const>
        eval_inactive_indices_res_lna = default_eval_inactive_indices_res_lna;

    // Second order
    optional_function_t<void(crvec x, rvec J_values) const>
        eval_constraints_jacobian = default_eval_constraints_jacobian;
    optional_function_t<Sparsity() const>
        get_constraints_jacobian_sparsity = default_get_constraints_jacobian_sparsity;
    optional_function_t<void(crvec x, index_t i, rvec grad_gi) const>
        eval_grad_gi = default_eval_grad_gi; // TODO: remove
    optional_function_t<void(crvec x, crvec y, real_t scale, crvec v, rvec Hv) const>
        eval_lagrangian_hessian_product = default_eval_lagrangian_hessian_product;
    optional_function_t<void(crvec x, crvec y, real_t scale, rvec H_values) const>
        eval_lagrangian_hessian = default_eval_lagrangian_hessian;
    optional_function_t<Sparsity() const>
        get_lagrangian_hessian_sparsity = default_get_lagrangian_hessian_sparsity;
    optional_function_t<void(crvec x, crvec y, crvec Σ, real_t scale, crvec v, rvec Hv) const>
        eval_augmented_lagrangian_hessian_product = default_eval_augmented_lagrangian_hessian_product;
    optional_function_t<void(crvec x, crvec y, crvec Σ, real_t scale, rvec H_values) const>
        eval_augmented_lagrangian_hessian = default_eval_augmented_lagrangian_hessian;
    optional_function_t<Sparsity() const>
        get_augmented_lagrangian_hessian_sparsity = default_get_augmented_lagrangian_hessian_sparsity;

    // Combined evaluations
    optional_function_t<real_t(crvec x, rvec grad_fx) const>
        eval_objective_and_gradient = default_eval_objective_and_gradient;
    optional_function_t<real_t(crvec x, rvec g) const>
        eval_objective_and_constraints = default_eval_objective_and_constraints;
    optional_function_t<void(crvec x, crvec y, rvec grad_f, rvec grad_gxy) const>
        eval_objective_gradient_and_constraints_gradient_product = default_eval_objective_gradient_and_constraints_gradient_product;

    // Lagrangian and augmented lagrangian evaluations
    optional_function_t<void(crvec x, crvec y, rvec grad_L, rvec work_n) const>
        eval_lagrangian_gradient = default_eval_lagrangian_gradient;
    optional_function_t<real_t(crvec x, crvec y, crvec Σ, rvec ŷ) const>
        eval_augmented_lagrangian = default_eval_augmented_lagrangian;
    optional_function_t<void(crvec x, crvec y, crvec Σ, rvec grad_ψ, rvec work_n, rvec work_m) const>
        eval_augmented_lagrangian_gradient = default_eval_augmented_lagrangian_gradient;
    optional_function_t<real_t(crvec x, crvec y, crvec Σ, rvec grad_ψ, rvec work_n, rvec work_m) const>
        eval_augmented_lagrangian_and_gradient = default_eval_augmented_lagrangian_and_gradient;

    // Constraint sets
    optional_function_t<const Box &() const>
        get_variable_bounds = default_get_variable_bounds;
    optional_function_t<const Box &() const>
        get_general_bounds = default_get_general_bounds;

    // Check
    optional_function_t<void() const>
        check = default_check;
    optional_function_t<std::string() const>
        get_name = default_get_name;

    // clang-format on

    ALPAQA_EXPORT static real_t calc_ŷ_dᵀŷ(const void *self, rvec g_ŷ, crvec y, crvec Σ,
                                           const ProblemVTable &vtable);
    ALPAQA_EXPORT static index_t default_eval_inactive_indices_res_lna(const void *, real_t, crvec,
                                                                       crvec, rindexvec,
                                                                       const ProblemVTable &);
    ALPAQA_EXPORT static void default_eval_constraints_jacobian(const void *, crvec, rvec,
                                                                const ProblemVTable &);
    ALPAQA_EXPORT static Sparsity default_get_constraints_jacobian_sparsity(const void *,
                                                                            const ProblemVTable &);
    ALPAQA_EXPORT static void default_eval_grad_gi(const void *, crvec, index_t, rvec,
                                                   const ProblemVTable &);
    ALPAQA_EXPORT static void default_eval_lagrangian_hessian_product(const void *, crvec, crvec,
                                                                      real_t, crvec, rvec,
                                                                      const ProblemVTable &);
    ALPAQA_EXPORT static void default_eval_lagrangian_hessian(const void *, crvec, crvec, real_t,
                                                              rvec, const ProblemVTable &);
    ALPAQA_EXPORT static Sparsity default_get_lagrangian_hessian_sparsity(const void *,
                                                                          const ProblemVTable &);
    ALPAQA_EXPORT static void
    default_eval_augmented_lagrangian_hessian_product(const void *self, crvec x, crvec y, crvec,
                                                      real_t scale, crvec v, rvec Hv,
                                                      const ProblemVTable &vtable);
    ALPAQA_EXPORT static void
    default_eval_augmented_lagrangian_hessian(const void *self, crvec x, crvec y, crvec,
                                              real_t scale, rvec H_values,
                                              const ProblemVTable &vtable);
    ALPAQA_EXPORT static Sparsity
    default_get_augmented_lagrangian_hessian_sparsity(const void *, const ProblemVTable &);
    ALPAQA_EXPORT static real_t default_eval_objective_and_gradient(const void *self, crvec x,
                                                                    rvec grad_fx,
                                                                    const ProblemVTable &vtable);
    ALPAQA_EXPORT static real_t default_eval_objective_and_constraints(const void *self, crvec x,
                                                                       rvec g,
                                                                       const ProblemVTable &vtable);
    ALPAQA_EXPORT static void default_eval_objective_gradient_and_constraints_gradient_product(
        const void *self, crvec x, crvec y, rvec grad_f, rvec grad_gxy,
        const ProblemVTable &vtable);
    ALPAQA_EXPORT static void default_eval_lagrangian_gradient(const void *self, crvec x, crvec y,
                                                               rvec grad_L, rvec work_n,
                                                               const ProblemVTable &vtable);
    ALPAQA_EXPORT static real_t default_eval_augmented_lagrangian(const void *self, crvec x,
                                                                  crvec y, crvec Σ, rvec ŷ,
                                                                  const ProblemVTable &vtable);
    ALPAQA_EXPORT static void
    default_eval_augmented_lagrangian_gradient(const void *self, crvec x, crvec y, crvec Σ,
                                               rvec grad_ψ, rvec work_n, rvec work_m,
                                               const ProblemVTable &vtable);
    ALPAQA_EXPORT static real_t
    default_eval_augmented_lagrangian_and_gradient(const void *self, crvec x, crvec y, crvec Σ,
                                                   rvec grad_ψ, rvec work_n, rvec work_m,
                                                   const ProblemVTable &vtable);
    ALPAQA_EXPORT static const Box &default_get_variable_bounds(const void *,
                                                                const ProblemVTable &);
    ALPAQA_EXPORT static const Box &default_get_general_bounds(const void *, const ProblemVTable &);
    ALPAQA_EXPORT static void default_check(const void *, const ProblemVTable &);
    ALPAQA_EXPORT static std::string default_get_name(const void *, const ProblemVTable &);

    length_t n, m;

    template <class P>
    ProblemVTable(std::in_place_t, P &p) : guanaqo::BasicVTable{std::in_place, p} {
        auto &vtable = *this;

        // Initialize all methods

        // Required
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_projecting_difference_constraints);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_projection_multipliers);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_proximal_gradient_step);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_objective);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_objective_gradient);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_constraints);
        GUANAQO_TE_REQUIRED_METHOD(vtable, P, eval_constraints_gradient_product);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_inactive_indices_res_lna, p);
        // Second order
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_constraints_jacobian, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_constraints_jacobian_sparsity, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_grad_gi, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_lagrangian_hessian_product, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_lagrangian_hessian, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_lagrangian_hessian_sparsity, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_augmented_lagrangian_hessian_product, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_augmented_lagrangian_hessian, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_augmented_lagrangian_hessian_sparsity, p);
        // Combined evaluations
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_objective_and_gradient, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_objective_and_constraints, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P,
                                   eval_objective_gradient_and_constraints_gradient_product, p);
        // Lagrangian and augmented lagrangian evaluations
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_lagrangian_gradient, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_augmented_lagrangian, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_augmented_lagrangian_gradient, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, eval_augmented_lagrangian_and_gradient, p);
        // Constraint set
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_variable_bounds, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_general_bounds, p);
        // Check
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, check, p);
        GUANAQO_TE_OPTIONAL_METHOD(vtable, P, get_name, p);

        // Dimensions
        vtable.n = p.get_num_variables();
        vtable.m = p.get_num_constraints();
    }
    ProblemVTable() = default;
};

// clang-format off
ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, ProblemVTable, EigenConfigd);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, ProblemVTable, EigenConfigf);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, ProblemVTable, EigenConfigl);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, ProblemVTable, EigenConfigq);)
// clang-format on

/// @addtogroup grp_Problems
/// @{

/// The main polymorphic minimization problem interface.
///
/// This class wraps the actual problem implementation class, filling in the
/// missing member functions with sensible defaults, and providing a uniform
/// interface that is used by the solvers.
///
/// The problem implementations do not inherit from an abstract base class.
/// Instead, [structural typing](https://en.wikipedia.org/wiki/Structural_type_system)
/// is used. The @ref ProblemVTable constructor uses reflection to discover
/// which member functions are provided by the problem implementation. See
/// @ref page-problem-formulations for more information, and
/// @ref C++/CustomCppProblem/main.cpp for an example.
template <Config Conf = DefaultConfig, class Allocator = std::allocator<std::byte>>
class TypeErasedProblem : public guanaqo::TypeErased<ProblemVTable<Conf>, Allocator> {
  public:
    USING_ALPAQA_CONFIG(Conf);
    using Box            = alpaqa::Box<config_t>;
    using VTable         = ProblemVTable<config_t>;
    using allocator_type = Allocator;
    using TypeErased     = guanaqo::TypeErased<VTable, allocator_type>;
    using TypeErased::TypeErased;

  protected:
    using TypeErased::call;
    using TypeErased::self;
    using TypeErased::vtable;

  public:
    template <class T, class... Args>
    static TypeErasedProblem make(Args &&...args) {
        return TypeErased::template make<TypeErasedProblem, T>(std::forward<Args>(args)...);
    }

    /// @name Problem dimensions
    /// @{

    /// **[Required]**
    /// Number of decision variables.
    [[nodiscard]] length_t get_num_variables() const;
    /// **[Required]**
    /// Number of constraints.
    [[nodiscard]] length_t get_num_constraints() const;

    /// @}

    /// @name Required cost and constraint functions
    /// @{

    /// **[Required]**
    /// Function that evaluates the cost, @f$ f(x) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    [[nodiscard]] real_t eval_objective(crvec x) const;
    /// **[Required]**
    /// Function that evaluates the gradient of the cost, @f$ \nabla f(x) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [out] grad_fx
    ///         Gradient of cost function @f$ \nabla f(x) \in \R^n @f$
    void eval_objective_gradient(crvec x, rvec grad_fx) const;
    /// **[Required]**
    /// Function that evaluates the constraints, @f$ g(x) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [out] gx
    ///         Value of the constraints @f$ g(x) \in \R^m @f$
    void eval_constraints(crvec x, rvec gx) const;
    /// **[Required]**
    /// Function that evaluates the gradient of the constraints times a vector,
    /// @f$ \nabla g(x)\,y = \tp{\jac_g(x)}y @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] y
    ///         Vector @f$ y \in \R^m @f$ to multiply the gradient by
    /// @param  [out] grad_gxy
    ///         Gradient of the constraints
    ///         @f$ \nabla g(x)\,y \in \R^n @f$
    void eval_constraints_gradient_product(crvec x, crvec y, rvec grad_gxy) const;

    /// @}

    /// @name Projections onto constraint sets and proximal mappings
    /// @{

    /// **[Required]**
    /// Function that evaluates the difference between the given point @f$ z @f$
    /// and its projection onto the constraint set @f$ D @f$.
    /// @param  [in] z
    ///         Slack variable, @f$ z \in \R^m @f$
    /// @param  [out] e
    ///         The difference relative to its projection,
    ///         @f$ e = z - \Pi_D(z) \in \R^m @f$
    /// @note   @p z and @p e can refer to the same vector.
    void eval_projecting_difference_constraints(crvec z, rvec e) const;
    /// **[Required]**
    /// Function that projects the Lagrange multipliers for ALM.
    /// @param  [inout] y
    ///         Multipliers, @f$ y \leftarrow \Pi_Y(y) \in \R^m @f$
    /// @param  [in] M
    ///         The radius/size of the set @f$ Y @f$.
    ///         See @ref ALMParams::max_multiplier.
    void eval_projection_multipliers(rvec y, real_t M) const;
    /// **[Required]**
    /// Function that computes a proximal gradient step.
    /// @param  [in] γ
    ///         Step size, @f$ \gamma \in \R_{>0} @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] grad_ψ
    ///         Gradient of the subproblem cost, @f$ \nabla\psi(x) \in \R^n @f$
    /// @param  [out] x̂
    ///         Next proximal gradient iterate, @f$ \hat x = T_\gamma(x) =
    ///         \prox_{\gamma h}(x - \gamma\nabla\psi(x)) \in \R^n @f$
    /// @param  [out] p
    ///         The proximal gradient step,
    ///         @f$ p = \hat x - x \in \R^n @f$
    /// @return The nonsmooth function evaluated at x̂,
    ///         @f$ h(\hat x) @f$.
    /// @note   The vector @f$ p @f$ is often used in stopping criteria, so its
    ///         numerical accuracy is more important than that of @f$ \hat x @f$.
    real_t eval_proximal_gradient_step(real_t γ, crvec x, crvec grad_ψ, rvec x̂, rvec p) const;
    /// **[Optional]**
    /// Function that computes the inactive indices @f$ \mathcal J(x) @f$ for
    /// the evaluation of the linear Newton approximation of the residual, as in
    /// @cite pas2022alpaqa.
    /// @param  [in] γ
    ///         Step size, @f$ \gamma \in \R_{>0} @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] grad_ψ
    ///         Gradient of the subproblem cost, @f$ \nabla\psi(x) \in \R^n @f$
    /// @param  [out] J
    ///         The indices of the components of @f$ x @f$ that are in the
    ///         index set @f$ \mathcal J(x) @f$. In ascending order, at most n.
    /// @return The number of inactive constraints, @f$ \# \mathcal J(x) @f$.
    ///
    /// For example, in the case of box constraints, we have
    /// @f[ \mathcal J(x) \defeq \defset{i \in \N_{[0, n-1]}}{\underline x_i
    /// \lt x_i - \gamma\nabla_{\!x_i}\psi(x) \lt \overline x_i}. @f]
    [[nodiscard]] index_t eval_inactive_indices_res_lna(real_t γ, crvec x, crvec grad_ψ,
                                                        rindexvec J) const;

    /// @}

    /// @name Constraint sets
    /// @{

    /// **[Optional]**
    /// Get the rectangular constraint set of the decision variables,
    /// @f$ x \in C @f$.
    [[nodiscard]] const Box &get_variable_bounds() const;
    /// **[Optional]**
    /// Get the rectangular constraint set of the general constraint function,
    /// @f$ g(x) \in D @f$.
    [[nodiscard]] const Box &get_general_bounds() const;

    /// @}

    /// @name Functions for second-order solvers
    /// @{

    /// **[Optional]**
    /// Function that evaluates the nonzero values of the Jacobian matrix of the
    /// constraints, @f$ \jac_g(x) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [out] J_values
    ///         Nonzero values of the Jacobian
    ///         @f$ \jac_g(x) \in \R^{m\times n} @f$
    ///
    /// Required for second-order solvers only.
    void eval_constraints_jacobian(crvec x, rvec J_values) const;
    /// **[Optional]**
    /// Function that returns (a view of) the sparsity pattern of the Jacobian
    /// of the constraints.
    ///
    /// Required for second-order solvers only.
    [[nodiscard]] Sparsity get_constraints_jacobian_sparsity() const;
    /// **[Optional]**
    /// Function that evaluates the gradient of one specific constraint,
    /// @f$ \nabla g_i(x) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] i
    ///         Which constraint @f$ 0 \le i \lt m @f$
    /// @param  [out] grad_gi
    ///         Gradient of the constraint
    ///         @f$ \nabla g_i(x) \in \R^n @f$
    ///
    /// Required for second-order solvers only.
    void eval_grad_gi(crvec x, index_t i, rvec grad_gi) const;
    /// **[Optional]**
    /// Function that evaluates the Hessian of the Lagrangian multiplied by a
    /// vector,
    /// @f$ \nabla_{xx}^2L(x, y)\,v @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] y
    ///         Lagrange multipliers @f$ y \in \R^m @f$
    /// @param  [in] scale
    ///         Scale factor for the cost function.
    /// @param  [in] v
    ///         Vector to multiply by @f$ v \in \R^n @f$
    /// @param  [out] Hv
    ///         Hessian-vector product
    ///         @f$ \nabla_{xx}^2 L(x, y)\,v \in \R^{n} @f$
    ///
    /// Required for second-order solvers only.
    void eval_lagrangian_hessian_product(crvec x, crvec y, real_t scale, crvec v, rvec Hv) const;
    /// **[Optional]**
    /// Function that evaluates the nonzero values of the Hessian of the
    /// Lagrangian, @f$ \nabla_{xx}^2L(x, y) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] y
    ///         Lagrange multipliers @f$ y \in \R^m @f$
    /// @param  [in] scale
    ///         Scale factor for the cost function.
    /// @param  [out] H_values
    ///         Nonzero values of the Hessian
    ///         @f$ \nabla_{xx}^2 L(x, y) \in \R^{n\times n} @f$.
    ///
    /// Required for second-order solvers only.
    void eval_lagrangian_hessian(crvec x, crvec y, real_t scale, rvec H_values) const;
    /// **[Optional]**
    /// Function that returns (a view of) the sparsity pattern of the Hessian of
    /// the Lagrangian.
    ///
    /// Required for second-order solvers only.
    [[nodiscard]] Sparsity get_lagrangian_hessian_sparsity() const;
    /// **[Optional]**
    /// Function that evaluates the Hessian of the augmented Lagrangian
    /// multiplied by a vector,
    /// @f$ \nabla_{xx}^2L_\Sigma(x, y)\,v @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] y
    ///         Lagrange multipliers @f$ y \in \R^m @f$
    /// @param  [in] Σ
    ///         Penalty weights @f$ \Sigma @f$
    /// @param  [in] scale
    ///         Scale factor for the cost function.
    /// @param  [in] v
    ///         Vector to multiply by @f$ v \in \R^n @f$
    /// @param  [out] Hv
    ///         Hessian-vector product
    ///         @f$ \nabla_{xx}^2 L_\Sigma(x, y)\,v \in \R^{n} @f$
    ///
    /// Required for second-order solvers only.
    void eval_augmented_lagrangian_hessian_product(crvec x, crvec y, crvec Σ, real_t scale, crvec v,
                                                   rvec Hv) const;
    /// **[Optional]**
    /// Function that evaluates the nonzero values of the Hessian of the
    /// augmented Lagrangian, @f$ \nabla_{xx}^2L_\Sigma(x, y) @f$
    /// @param  [in] x
    ///         Decision variable @f$ x \in \R^n @f$
    /// @param  [in] y
    ///         Lagrange multipliers @f$ y \in \R^m @f$
    /// @param  [in] Σ
    ///         Penalty weights @f$ \Sigma @f$
    /// @param  [in] scale
    ///         Scale factor for the cost function.
    /// @param  [out] H_values
    ///         Nonzero values of the Hessian
    ///         @f$ \nabla_{xx}^2 L_\Sigma(x, y) \in \R^{n\times n} @f$
    ///
    /// Required for second-order solvers only.
    void eval_augmented_lagrangian_hessian(crvec x, crvec y, crvec Σ, real_t scale,
                                           rvec H_values) const;
    /// **[Optional]**
    /// Function that returns (a view of) the sparsity pattern of the Hessian of
    /// the augmented Lagrangian.
    ///
    /// Required for second-order solvers only.
    [[nodiscard]] Sparsity get_augmented_lagrangian_hessian_sparsity() const;

    /// @}

    /// @name Combined evaluations
    /// @{

    /// **[Optional]**
    /// Evaluate both @f$ f(x) @f$ and its gradient, @f$ \nabla f(x) @f$.
    /// @default_impl   ProblemVTable::default_eval_objective_and_gradient
    real_t eval_objective_and_gradient(crvec x, rvec grad_fx) const;
    /// **[Optional]**
    /// Evaluate both @f$ f(x) @f$ and @f$ g(x) @f$.
    /// @default_impl   ProblemVTable::default_eval_objective_and_constraints
    real_t eval_objective_and_constraints(crvec x, rvec g) const;
    /// **[Optional]**
    /// Evaluate both @f$ \nabla f(x) @f$ and @f$ \nabla g(x)\,y @f$.
    /// @default_impl   ProblemVTable::default_eval_objective_gradient_and_constraints_gradient_product
    void eval_objective_gradient_and_constraints_gradient_product(crvec x, crvec y, rvec grad_f,
                                                                  rvec grad_gxy) const;
    /// **[Optional]**
    /// Evaluate the gradient of the Lagrangian
    /// @f$ \nabla_x L(x, y) = \nabla f(x) + \nabla g(x)\,y @f$
    /// @default_impl   ProblemVTable::default_eval_lagrangian_gradient
    void eval_lagrangian_gradient(crvec x, crvec y, rvec grad_L, rvec work_n) const;

    /// @}

    /// @name Augmented Lagrangian
    /// @{

    /// **[Optional]**
    /// Calculate both ψ(x) and the vector ŷ that can later be used to compute
    /// ∇ψ.
    /// @f[ \psi(x) = f(x) + \tfrac{1}{2}
    ///   \text{dist}_\Sigma^2\left(g(x) + \Sigma^{-1}y,\;D\right) @f]
    /// @f[ \hat y = \Sigma\, \left(g(x) + \Sigma^{-1}y - \Pi_D\left(g(x)
    ///   + \Sigma^{-1}y\right)\right) @f]
    /// @default_impl   ProblemVTable::default_eval_augmented_lagrangian
    [[nodiscard]] real_t
    eval_augmented_lagrangian(crvec x, ///< [in]  Decision variable @f$ x @f$
                              crvec y, ///< [in]  Lagrange multipliers @f$ y @f$
                              crvec Σ, ///< [in]  Penalty weights @f$ \Sigma @f$
                              rvec ŷ   ///< [out] @f$ \hat y @f$
    ) const;
    /// **[Optional]**
    /// Calculate the gradient ∇ψ(x).
    /// @f[ \nabla \psi(x) = \nabla f(x) + \nabla g(x)\,\hat y(x) @f]
    /// @default_impl   ProblemVTable::default_eval_augmented_lagrangian_gradient
    void eval_augmented_lagrangian_gradient(crvec x,     ///< [in]  Decision variable @f$ x @f$
                                            crvec y,     ///< [in]  Lagrange multipliers @f$ y @f$
                                            crvec Σ,     ///< [in]  Penalty weights @f$ \Sigma @f$
                                            rvec grad_ψ, ///< [out] @f$ \nabla \psi(x) @f$
                                            rvec work_n, ///<       Dimension @f$ n @f$
                                            rvec work_m  ///<       Dimension @f$ m @f$
    ) const;
    /// **[Optional]**
    /// Calculate both ψ(x) and its gradient ∇ψ(x).
    /// @f[ \psi(x) = f(x) + \tfrac{1}{2}
    /// \text{dist}_\Sigma^2\left(g(x) + \Sigma^{-1}y,\;D\right) @f]
    /// @f[ \nabla \psi(x) = \nabla f(x) + \nabla g(x)\,\hat y(x) @f]
    /// @default_impl   ProblemVTable::default_eval_augmented_lagrangian_and_gradient
    [[nodiscard]] real_t
    eval_augmented_lagrangian_and_gradient(crvec x,     ///< [in]  Decision variable @f$ x @f$
                                           crvec y,     ///< [in]  Lagrange multipliers @f$ y @f$
                                           crvec Σ,     ///< [in]  Penalty weights @f$ \Sigma @f$
                                           rvec grad_ψ, ///< [out] @f$ \nabla \psi(x) @f$
                                           rvec work_n, ///<       Dimension @f$ n @f$
                                           rvec work_m  ///<       Dimension @f$ m @f$
    ) const;

    /// @}

    /// @name Checks
    /// @{

    /// **[Optional]**
    /// Check that the problem formulation is well-defined, the dimensions match,
    /// etc. Throws an exception if this is not the case.
    void check() const;

    /// @}

    /// @name Metadata
    /// @{

    /// **[Optional]**
    /// Get a descriptive name for the problem.
    [[nodiscard]] std::string get_name() const;

    /// @}

    /// @name Querying specialized implementations
    /// @{

    /// Returns true if the problem provides an implementation of
    /// @ref eval_inactive_indices_res_lna.
    [[nodiscard]] bool provides_eval_inactive_indices_res_lna() const {
        return vtable.eval_inactive_indices_res_lna != vtable.default_eval_inactive_indices_res_lna;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_constraints_jacobian.
    [[nodiscard]] bool provides_eval_constraints_jacobian() const {
        return vtable.eval_constraints_jacobian != vtable.default_eval_constraints_jacobian;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref get_constraints_jacobian_sparsity.
    [[nodiscard]] bool provides_get_constraints_jacobian_sparsity() const {
        return vtable.get_constraints_jacobian_sparsity !=
               vtable.default_get_constraints_jacobian_sparsity;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_grad_gi.
    [[nodiscard]] bool provides_eval_grad_gi() const {
        return vtable.eval_grad_gi != vtable.default_eval_grad_gi;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_lagrangian_hessian_product.
    [[nodiscard]] bool provides_eval_lagrangian_hessian_product() const {
        return vtable.eval_lagrangian_hessian_product !=
               vtable.default_eval_lagrangian_hessian_product;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_lagrangian_hessian.
    [[nodiscard]] bool provides_eval_lagrangian_hessian() const {
        return vtable.eval_lagrangian_hessian != vtable.default_eval_lagrangian_hessian;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref get_lagrangian_hessian_sparsity.
    [[nodiscard]] bool provides_get_lagrangian_hessian_sparsity() const {
        return vtable.get_lagrangian_hessian_sparsity !=
               vtable.default_get_lagrangian_hessian_sparsity;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_augmented_lagrangian_hessian_product.
    [[nodiscard]] bool provides_eval_augmented_lagrangian_hessian_product() const {
        return vtable.eval_augmented_lagrangian_hessian_product !=
               vtable.default_eval_augmented_lagrangian_hessian_product;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref eval_augmented_lagrangian_hessian.
    [[nodiscard]] bool provides_eval_augmented_lagrangian_hessian() const {
        return vtable.eval_augmented_lagrangian_hessian !=
               vtable.default_eval_augmented_lagrangian_hessian;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref get_augmented_lagrangian_hessian_sparsity.
    [[nodiscard]] bool provides_get_augmented_lagrangian_hessian_sparsity() const {
        return vtable.get_augmented_lagrangian_hessian_sparsity !=
               vtable.default_get_augmented_lagrangian_hessian_sparsity;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_objective_and_gradient, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_objective_and_gradient() const {
        return vtable.eval_objective_and_gradient != vtable.default_eval_objective_and_gradient;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_objective_and_constraints, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_objective_and_constraints() const {
        return vtable.eval_objective_and_constraints !=
               vtable.default_eval_objective_and_constraints;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_objective_gradient_and_constraints_gradient_product, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_objective_gradient_and_constraints_gradient_product() const {
        return vtable.eval_objective_gradient_and_constraints_gradient_product !=
               vtable.default_eval_objective_gradient_and_constraints_gradient_product;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_lagrangian_gradient, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_lagrangian_gradient() const {
        return vtable.eval_lagrangian_gradient != vtable.default_eval_lagrangian_gradient;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_augmented_lagrangian, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_augmented_lagrangian() const {
        return vtable.eval_augmented_lagrangian != vtable.default_eval_augmented_lagrangian;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_augmented_lagrangian_gradient, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_augmented_lagrangian_gradient() const {
        return vtable.eval_augmented_lagrangian_gradient !=
               vtable.default_eval_augmented_lagrangian_gradient;
    }
    /// Returns true if the problem provides a specialized implementation of
    /// @ref eval_augmented_lagrangian_and_gradient, false if it uses the default implementation.
    [[nodiscard]] bool provides_eval_augmented_lagrangian_and_gradient() const {
        return vtable.eval_augmented_lagrangian_and_gradient !=
               vtable.default_eval_augmented_lagrangian_and_gradient;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref get_variable_bounds.
    [[nodiscard]] bool provides_get_variable_bounds() const {
        return vtable.get_variable_bounds != vtable.default_get_variable_bounds;
    }
    /// Returns true if the problem provides an implementation of
    /// @ref get_general_bounds.
    [[nodiscard]] bool provides_get_general_bounds() const {
        return vtable.get_general_bounds != vtable.default_get_general_bounds;
    }
    /// Returns true if the problem provides an implementation of @ref check.
    [[nodiscard]] bool provides_check() const { return vtable.check != vtable.default_check; }
    /// Returns true if the problem provides an implementation of @ref get_name.
    [[nodiscard]] bool provides_get_name() const {
        return vtable.get_name != vtable.default_get_name;
    }

    /// @}

    /// @name Querying available functions
    /// @{

    /// Returns true if @ref eval_augmented_lagrangian_hessian_product can be called.
    [[nodiscard]] bool supports_eval_augmented_lagrangian_hessian_product() const {
        return provides_eval_augmented_lagrangian_hessian_product() ||
               (vtable.m == 0 && provides_eval_lagrangian_hessian_product());
    }
    /// Returns true if @ref eval_augmented_lagrangian_hessian can be called.
    [[nodiscard]] bool supports_eval_augmented_lagrangian_hessian() const {
        return provides_eval_augmented_lagrangian_hessian() ||
               (vtable.m == 0 && provides_eval_lagrangian_hessian());
    }

    /// @}

    /// @name Helpers
    /// @{

    /// Given g(x), compute the intermediate results ŷ and dᵀŷ that can later be
    /// used to compute ψ(x) and ∇ψ(x).
    ///
    /// Computes the result using the following algorithm:
    /// @f[ \begin{aligned}
    ///     \zeta &= g(x) + \Sigma^{-1} y \\[]
    ///     d &= \zeta - \Pi_D(\zeta)
    ///        = \operatorname{eval\_proj\_diff\_g}(\zeta, \zeta) \\[]
    ///     \hat y &= \Sigma d \\[]
    /// \end{aligned} @f]
    /// @see @ref page_math
    ///
    /// @param[inout]   g_ŷ
    ///                 Input @f$ g(x) @f$, outputs @f$ \hat y @f$
    /// @param[in]      y
    ///                 Lagrange multipliers @f$ y @f$
    /// @param[in]      Σ
    ///                 Penalty weights @f$ \Sigma @f$
    /// @return The inner product @f$ d^\top \hat y @f$
    real_t calc_ŷ_dᵀŷ(rvec g_ŷ, crvec y, crvec Σ) const;

    /// @}
};

/// @}

#ifndef DOXYGEN
template <class Tref>
explicit TypeErasedProblem(Tref &&d)
    -> TypeErasedProblem<typename std::remove_cvref_t<Tref>::config_t>;

template <class Tref, class Allocator>
explicit TypeErasedProblem(Tref &&d, Allocator alloc)
    -> TypeErasedProblem<typename std::remove_cvref_t<Tref>::config_t, Allocator>;
#endif

template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_num_variables() const -> length_t {
    return vtable.n;
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_num_constraints() const -> length_t {
    return vtable.m;
}

template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_projecting_difference_constraints(crvec z,
                                                                                rvec e) const {
    return call(vtable.eval_projecting_difference_constraints, z, e);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_projection_multipliers(rvec y, real_t M) const {
    return call(vtable.eval_projection_multipliers, y, M);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_proximal_gradient_step(real_t γ, crvec x,
                                                                     crvec grad_ψ, rvec x̂,
                                                                     rvec p) const -> real_t {
    return call(vtable.eval_proximal_gradient_step, γ, x, grad_ψ, x̂, p);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_inactive_indices_res_lna(
    real_t γ, crvec x, crvec grad_ψ, rindexvec J) const -> index_t {
    return call(vtable.eval_inactive_indices_res_lna, γ, x, grad_ψ, J);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_objective(crvec x) const -> real_t {
    return call(vtable.eval_objective, x);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_objective_gradient(crvec x, rvec grad_fx) const {
    return call(vtable.eval_objective_gradient, x, grad_fx);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_constraints(crvec x, rvec gx) const {
    return call(vtable.eval_constraints, x, gx);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_constraints_gradient_product(crvec x, crvec y,
                                                                           rvec grad_gxy) const {
    return call(vtable.eval_constraints_gradient_product, x, y, grad_gxy);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_grad_gi(crvec x, index_t i, rvec grad_gi) const {
    return call(vtable.eval_grad_gi, x, i, grad_gi);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_constraints_jacobian(crvec x, rvec J_values) const {
    return call(vtable.eval_constraints_jacobian, x, J_values);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_constraints_jacobian_sparsity() const -> Sparsity {
    return call(vtable.get_constraints_jacobian_sparsity);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_lagrangian_hessian_product(crvec x, crvec y,
                                                                         real_t scale, crvec v,
                                                                         rvec Hv) const {
    return call(vtable.eval_lagrangian_hessian_product, x, y, scale, v, Hv);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_lagrangian_hessian(crvec x, crvec y, real_t scale,
                                                                 rvec H_values) const {
    return call(vtable.eval_lagrangian_hessian, x, y, scale, H_values);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_lagrangian_hessian_sparsity() const -> Sparsity {
    return call(vtable.get_lagrangian_hessian_sparsity);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_augmented_lagrangian_hessian_product(
    crvec x, crvec y, crvec Σ, real_t scale, crvec v, rvec Hv) const {
    return call(vtable.eval_augmented_lagrangian_hessian_product, x, y, Σ, scale, v, Hv);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_augmented_lagrangian_hessian(crvec x, crvec y,
                                                                           crvec Σ, real_t scale,
                                                                           rvec H_values) const {
    return call(vtable.eval_augmented_lagrangian_hessian, x, y, Σ, scale, H_values);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_augmented_lagrangian_hessian_sparsity() const
    -> Sparsity {
    return call(vtable.get_augmented_lagrangian_hessian_sparsity);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_objective_and_gradient(crvec x,
                                                                     rvec grad_fx) const -> real_t {
    return call(vtable.eval_objective_and_gradient, x, grad_fx);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_objective_and_constraints(crvec x,
                                                                        rvec g) const -> real_t {
    return call(vtable.eval_objective_and_constraints, x, g);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_objective_gradient_and_constraints_gradient_product(
    crvec x, crvec y, rvec grad_f, rvec grad_gxy) const {
    return call(vtable.eval_objective_gradient_and_constraints_gradient_product, x, y, grad_f,
                grad_gxy);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_lagrangian_gradient(crvec x, crvec y, rvec grad_L,
                                                                  rvec work_n) const {
    return call(vtable.eval_lagrangian_gradient, x, y, grad_L, work_n);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_augmented_lagrangian(crvec x, crvec y, crvec Σ,
                                                                   rvec ŷ) const -> real_t {
    return call(vtable.eval_augmented_lagrangian, x, y, Σ, ŷ);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::eval_augmented_lagrangian_gradient(crvec x, crvec y,
                                                                            crvec Σ, rvec grad_ψ,
                                                                            rvec work_n,
                                                                            rvec work_m) const {
    return call(vtable.eval_augmented_lagrangian_gradient, x, y, Σ, grad_ψ, work_n, work_m);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::eval_augmented_lagrangian_and_gradient(
    crvec x, crvec y, crvec Σ, rvec grad_ψ, rvec work_n, rvec work_m) const -> real_t {
    return call(vtable.eval_augmented_lagrangian_and_gradient, x, y, Σ, grad_ψ, work_n, work_m);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::calc_ŷ_dᵀŷ(rvec g_ŷ, crvec y, crvec Σ) const -> real_t {
    return call(vtable.calc_ŷ_dᵀŷ, g_ŷ, y, Σ);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_variable_bounds() const -> const Box & {
    return call(vtable.get_variable_bounds);
}
template <Config Conf, class Allocator>
auto TypeErasedProblem<Conf, Allocator>::get_general_bounds() const -> const Box & {
    return call(vtable.get_general_bounds);
}
template <Config Conf, class Allocator>
void TypeErasedProblem<Conf, Allocator>::check() const {
    return call(vtable.check);
}
template <Config Conf, class Allocator>
std::string TypeErasedProblem<Conf, Allocator>::get_name() const {
    return call(vtable.get_name);
}

/// @addtogroup grp_Problems
/// @{

template <Config Conf>
void print_provided_functions(std::ostream &os, const TypeErasedProblem<Conf> &problem) {
    // clang-format off
    os << "                            eval_inactive_indices_res_lna: " << problem.provides_eval_inactive_indices_res_lna() << '\n'
       << "                                             eval_grad_gi: " << problem.provides_eval_grad_gi() << '\n'
       << "                                eval_constraints_jacobian: " << problem.provides_eval_constraints_jacobian() << '\n'
       << "                          eval_lagrangian_hessian_product: " << problem.provides_eval_lagrangian_hessian_product() << '\n'
       << "                                  eval_lagrangian_hessian: " << problem.provides_eval_lagrangian_hessian() << '\n'
       << "                eval_augmented_lagrangian_hessian_product: " << problem.provides_eval_augmented_lagrangian_hessian_product() << '\n'
       << "                        eval_augmented_lagrangian_hessian: " << problem.provides_eval_augmented_lagrangian_hessian() << '\n'
       << "                              eval_objective_and_gradient: " << problem.provides_eval_objective_and_gradient() << '\n'
       << "                           eval_objective_and_constraints: " << problem.provides_eval_objective_and_constraints() << '\n'
       << " eval_objective_gradient_and_constraints_gradient_product: " << problem.provides_eval_objective_gradient_and_constraints_gradient_product() << '\n'
       << "                                 eval_lagrangian_gradient: " << problem.provides_eval_lagrangian_gradient() << '\n'
       << "                                eval_augmented_lagrangian: " << problem.provides_eval_augmented_lagrangian() << '\n'
       << "                       eval_augmented_lagrangian_gradient: " << problem.provides_eval_augmented_lagrangian_gradient() << '\n'
       << "                   eval_augmented_lagrangian_and_gradient: " << problem.provides_eval_augmented_lagrangian_and_gradient() << '\n'
       << "                                      get_variable_bounds: " << problem.provides_get_variable_bounds() << '\n'
       << "                                       get_general_bounds: " << problem.provides_get_general_bounds() << '\n'
       << "                                                    check: " << problem.provides_check() << '\n'
       << "                                                 get_name: " << problem.provides_get_name() << '\n';
    // clang-format on
}

/// @}

} // namespace alpaqa