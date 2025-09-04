#pragma once

#include <alpaqa/inner/inner-solve-options.hpp>
#if ALPAQA_WITH_OCP
#include <alpaqa/problem/ocproblem.hpp>
#endif
#include <alpaqa/problem/type-erased-problem.hpp>
#include <guanaqo/demangled-typename.hpp>
#include <functional>
#include <optional>
#include <stdexcept>
#include <variant>

#include <dict/stats-to-dict.hpp>
#include <inner/type-erased-inner-solver.hpp>
#include <inner/type-erased-solver-stats.hpp>
#include <util/async.hpp>

#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

namespace alpaqa {

using guanaqo::required_function_t;

/**
 * Type erasing the @ref ALMSolver class, so that it can be instantiated with
 * inner solvers of different problem types (e.g. @ref TypeErasedProblem and
 * @ref TypeErasedControlProblem).
 * 
 * To this end, it represents the possible problems as a variant, and then
 * std::visits the variant in the @ref call method, throwing an exception if
 * the given problem type does not match the inner solver's problem type.
 */
template <Config Conf>
struct ALMSolverVTable : guanaqo::BasicVTable {
    USING_ALPAQA_CONFIG(Conf);
    using Stats = typename ALMSolver<TypeErasedInnerSolver<Conf, TypeErasedProblem<Conf>>>::Stats;
    using Problem =
#if ALPAQA_WITH_OCP
        std::variant<const TypeErasedProblem<Conf> *, const TypeErasedControlProblem<Conf> *>;
#else
        std::variant<const TypeErasedProblem<Conf> *>;
#endif

    // clang-format off
    required_function_t<py::tuple(const Problem &, std::optional<vec> x, std::optional<vec> y, bool async, bool suppress_interrupt)>
        call = nullptr;
    required_function_t<void()>
        stop = nullptr;
    required_function_t<std::string() const>
        get_name = nullptr;
    required_function_t<py::object() const>
        get_params = nullptr;
    required_function_t<py::object() const>
        get_inner_solver = nullptr;
    // clang-format on

    template <class T>
    ALMSolverVTable(std::in_place_t, T &t) : guanaqo::BasicVTable{std::in_place, t} {
        stop       = guanaqo::type_erased_wrapped<T, &T::stop>();
        get_name   = guanaqo::type_erased_wrapped<T, &T::get_name>();
        get_params = [](const void *self_) -> py::object {
            auto &self = *std::launder(reinterpret_cast<const T *>(self_));
            return py::cast(self.get_params());
        };
        get_inner_solver = [](const void *self_) -> py::object {
            auto &self = *std::launder(reinterpret_cast<const T *>(self_));
            return py::cast(self.inner_solver);
        };
        call = [](void *self_, const Problem &p, std::optional<vec> x, std::optional<vec> y,
                  bool async, bool suppress_interrupt) {
            auto &self       = *std::launder(reinterpret_cast<T *>(self_));
            auto call_solver = [&]<class P>(const P *p) -> py::tuple {
                if constexpr (!std::is_same_v<P, typename T::Problem>)
                    throw std::invalid_argument(
                        "Unsupported problem type (expected '" +
                        guanaqo::demangled_typename(typeid(typename T::Problem)) + "', got '" +
                        guanaqo::demangled_typename(typeid(P)) + "')");
                else
                    return safe_call_solver(self, p, x, y, async, suppress_interrupt);
            };
            return std::visit(call_solver, p);
        };
    }
    ALMSolverVTable() = default;

    template <class T>
    static decltype(auto) safe_call_solver(T &self, const auto &p, std::optional<vec> &x,
                                           std::optional<vec> &y, bool async,
                                           bool suppress_interrupt) {
        using InnerSolver = typename T::InnerSolver;
        alpaqa::util::check_dim_msg<vec>(
            x, p->get_num_variables(),
            "Length of x does not match problem size problem.num_variables");
        alpaqa::util::check_dim_msg<vec>(
            y, p->get_num_constraints(),
            "Length of y does not match problem size problem.num_constraints");
        auto invoke_solver = [&] { return self(*p, *x, *y); };
        auto stats         = async_solve(async, suppress_interrupt, self, invoke_solver, *p);
        return py::make_tuple(std::move(*x), std::move(*y),
                              alpaqa::conv::stats_to_dict<InnerSolver>(std::move(stats)));
    }
};

template <Config Conf = DefaultConfig, class Allocator = std::allocator<std::byte>>
class TypeErasedALMSolver : public guanaqo::TypeErased<ALMSolverVTable<Conf>, Allocator> {
  public:
    USING_ALPAQA_CONFIG(Conf);
    using VTable         = ALMSolverVTable<Conf>;
    using allocator_type = Allocator;
    using TypeErased     = guanaqo::TypeErased<VTable, allocator_type>;
    using Stats          = typename VTable::Stats;
    using Problem        = typename VTable::Problem;
    using TypeErased::TypeErased;

  protected:
    using TypeErased::call;
    using TypeErased::self;
    using TypeErased::vtable;

  public:
    template <class T, class... Args>
    static TypeErasedALMSolver make(Args &&...args) {
        return TypeErased::template make<TypeErasedALMSolver, T>(std::forward<Args>(args)...);
    }

    decltype(auto) operator()(const Problem &p, std::optional<vec> x, std::optional<vec> y,
                              bool async, bool suppress_interrupt) {
        return call(vtable.call, p, x, y, async, suppress_interrupt);
    }
    decltype(auto) stop() { return call(vtable.stop); }
    decltype(auto) get_name() const { return call(vtable.get_name); }
    decltype(auto) get_params() const { return call(vtable.get_params); }
    decltype(auto) get_inner_solver() const { return call(vtable.get_inner_solver); }
};

} // namespace alpaqa