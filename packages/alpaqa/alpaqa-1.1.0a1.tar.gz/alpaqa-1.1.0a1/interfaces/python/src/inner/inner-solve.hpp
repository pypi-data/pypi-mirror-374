#pragma once

#include <guanaqo/quadmath/quadmath.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
using namespace py::literals;

#include <alpaqa/config/config.hpp>
#include <alpaqa/inner/inner-solve-options.hpp>
#include <alpaqa/util/check-dim.hpp>

#include <dict/stats-to-dict.hpp>
#include <inner/type-erased-inner-solver.hpp>

/// Python interface to the inner solvers, checks the argument sizes and
/// presence, and returns a Python tuple.
template <class Solver, class Problem>
auto checked_inner_solve() {
    USING_ALPAQA_CONFIG_TEMPLATE(Solver::config_t);
    return [](Solver &solver, const Problem &problem,
              const alpaqa::InnerSolveOptions<config_t> &opts, std::optional<vec> x,
              std::optional<vec> y, std::optional<vec> Σ, bool async, bool suppress_interrupt) {
        alpaqa::util::check_dim_msg<vec>(
            x, problem.get_num_variables(),
            "Length of x does not match problem size problem.num_variables");
        bool ret_y = y.has_value();
        if (!y && problem.get_num_constraints() > 0)
            throw std::invalid_argument("Missing argument y");
        alpaqa::util::check_dim_msg<vec>(
            y, problem.get_num_constraints(),
            "Length of y does not match problem size problem.num_constraints");
        if (!Σ && problem.get_num_constraints() > 0)
            throw std::invalid_argument("Missing argument Σ");
        alpaqa::util::check_dim_msg<vec>(
            Σ, problem.get_num_constraints(),
            "Length of Σ does not match problem size problem.num_constraints");
        vec err_z          = vec::Zero(problem.get_num_constraints());
        auto invoke_solver = [&] { return solver(problem, opts, *x, *y, *Σ, err_z); };
        auto &&stats       = async_solve(async, suppress_interrupt, solver, invoke_solver, problem);
        return ret_y ? py::make_tuple(std::move(*x), std::move(*y), std::move(err_z),
                                      alpaqa::conv::stats_to_dict(stats))
                     : py::make_tuple(std::move(*x), alpaqa::conv::stats_to_dict(stats));
    };
}

inline const char *checked_inner_solve_doc() {
    return "Solve the given problem.\n\n"
           ":param problem: Problem to solve\n"
           ":param opts: Options (such as desired tolerance)\n"
           ":param x: Optional initial guess for the decision variables\n"
           ":param y: Lagrange multipliers (when used as ALM inner solver)\n"
           ":param Σ: Penalty factors (when used as ALM inner solver)\n"
           ":param asynchronous: Release the GIL and run the solver on a separate thread\n"
           ":param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, "
           "don't propagate this exception back to the Python interpreter, but stop the solver "
           "early, and return a solution with the status set to "
           ":py:data:`alpaqa.SolverStatus.Interrupted`.\n"
           ":return: * Solution :math:`x`\n"
           "         * Updated Lagrange multipliers (only if parameter ``y`` was not ``None``)\n"
           "         * Constraint violation (only if parameter ``y`` was not ``None``)\n"
           "         * Statistics\n\n";
}

template <class Solver, class Problem, class InnerSolverType>
void register_inner_solver_methods(py::class_<Solver> &cls) {
    cls.def("__call__", checked_inner_solve<Solver, Problem>(), "problem"_a, "opts"_a = py::dict(),
            "x"_a = py::none(), "y"_a = py::none(), "Σ"_a = py::none(), py::kw_only{},
            "asynchronous"_a = true, "suppress_interrupt"_a = false, checked_inner_solve_doc())
        .def_property_readonly("name", &Solver::get_name)
        .def("stop", &Solver::stop)
        .def("__str__", &Solver::get_name)
        .def_property_readonly("params", &Solver::get_params);
    if constexpr (requires { &Solver::set_progress_callback; })
        cls.def(
            "set_progress_callback", &Solver::set_progress_callback, "callback"_a,
            "Specify a callable that is invoked with some intermediate results on each iteration "
            "of the algorithm.");
    inner_solver_class<InnerSolverType>.template implicitly_convertible_to<Solver>();
}
