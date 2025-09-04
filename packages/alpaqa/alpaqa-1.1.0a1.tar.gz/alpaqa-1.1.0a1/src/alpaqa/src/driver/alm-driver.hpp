#pragma once

#include <alpaqa/inner/internal/panoc-stop-crit.hpp>
#include <alpaqa/outer/alm.hpp>
#include <alpaqa/params/params.hpp>

#include "options.hpp"
#include "problem.hpp"
#include "results.hpp"

template <class InnerSolver>
auto make_alm_solver(InnerSolver &&inner_solver, Options &opts) {
    // Settings for the ALM solver
    using ALMSolver = alpaqa::ALMSolver<InnerSolver>;
    typename ALMSolver::Params alm_param;
    alm_param.max_iter        = 200;
    alm_param.tolerance       = 1e-8;
    alm_param.dual_tolerance  = 1e-8;
    alm_param.print_interval  = 1;
    alm_param.print_precision = 1;
    set_params(alm_param, "alm", opts);
    return ALMSolver{alm_param, std::forward<InnerSolver>(inner_solver)};
}

USING_ALPAQA_CONFIG(alpaqa::DefaultConfig);

template <class InnerSolver>
auto make_inner_solver(Options &opts) {
    // Settings for the solver
    typename InnerSolver::Params solver_param;
    solver_param.max_iter       = 50'000;
    solver_param.print_interval = 0;
    solver_param.stop_crit      = alpaqa::PANOCStopCrit::ProjGradUnitNorm;
    set_params(solver_param, "solver", opts);

    if constexpr (requires { typename InnerSolver::Direction; }) {
        // Settings for the direction provider
        using Direction = typename InnerSolver::Direction;
        typename Direction::DirectionParams dir_param;
        typename Direction::AcceleratorParams accel_param;
        set_params(dir_param, "dir", opts);
        set_params(accel_param, "accel", opts);
        return InnerSolver{
            solver_param,
            Direction{{
                .accelerator = accel_param,
                .direction   = dir_param,
            }},
        };
    } else {
        return InnerSolver{solver_param};
    }
}

template <class Solver>
SolverResults run_alm_solver(LoadedProblem &problem, Solver &solver,
                             std::ostream &os, unsigned N_exp) {

    solver.os = &os;

    // Initial guess
    vec x = problem.initial_guess_x, y = problem.initial_guess_y;
    // Final penalties
    vec Σ = vec::Constant(problem.problem.get_num_constraints(),
                          alpaqa::NaN<config_t>);

    // Solve the problem
    auto stats = solver(problem.problem, x, y, Σ);

    // Solve the problems again to average runtimes
    auto avg_duration = stats.elapsed_time;
    os.setstate(std::ios_base::badbit); // suppress output
    for (unsigned i = 0; i < N_exp; ++i) {
        x      = problem.initial_guess_x;
        y      = problem.initial_guess_y;
        auto s = solver(problem.problem, x, y);
        if (s.status == alpaqa::SolverStatus::Interrupted) {
            os.clear();
            os << "\rInterrupted after " << i << " runs" << std::endl;
            N_exp = i;
            break;
        }
        avg_duration += s.elapsed_time;
    }
    os.clear();
    avg_duration /= (N_exp + 1);

    solver.os = &std::cout;

    // Store the evaluation counters
    auto evals = *problem.evaluations;

    // Results
    real_t final_γ = 0, final_h = 0;
    if constexpr (requires { stats.inner.final_γ; })
        final_γ = stats.inner.final_γ;
    if constexpr (requires { stats.inner.final_h; })
        final_h = stats.inner.final_h;
    decltype(SolverResults::extra) extra{};
    if constexpr (requires { stats.inner.linesearch_failures; })
        extra.emplace_back(
            "linesearch_failures",
            static_cast<index_t>(stats.inner.linesearch_failures));
    if constexpr (requires { stats.inner.linesearch_backtracks; })
        extra.emplace_back(
            "linesearch_backtracks",
            static_cast<index_t>(stats.inner.linesearch_backtracks));
    if constexpr (requires { stats.inner.stepsize_backtracks; })
        extra.emplace_back(
            "stepsize_backtracks",
            static_cast<index_t>(stats.inner.stepsize_backtracks));
    if constexpr (requires { stats.inner.direction_failures; })
        extra.emplace_back(
            "direction_failures",
            static_cast<index_t>(stats.inner.direction_failures));
    if constexpr (requires { stats.inner.direction_update_rejected; })
        extra.emplace_back(
            "direction_update_rejected",
            static_cast<index_t>(stats.inner.direction_update_rejected));
    if constexpr (requires { stats.inner.accelerated_step_rejected; })
        extra.emplace_back(
            "accelerated_step_rejected",
            static_cast<index_t>(stats.inner.accelerated_step_rejected));
    if constexpr (requires { stats.inner.direction_failures; })
        extra.emplace_back(
            "direction_failures",
            static_cast<index_t>(stats.inner.direction_failures));
    if constexpr (requires { stats.inner.direction_update_rejected; })
        extra.emplace_back(
            "direction_update_rejected",
            static_cast<index_t>(stats.inner.direction_update_rejected));
    return SolverResults{
        .status             = enum_name(stats.status),
        .success            = stats.status == alpaqa::SolverStatus::Converged,
        .evals              = evals,
        .duration           = avg_duration,
        .solver             = solver.get_name(),
        .h                  = final_h,
        .δ                  = stats.δ,
        .ε                  = stats.ε,
        .γ                  = final_γ,
        .Σ                  = stats.norm_penalty,
        .solution           = x,
        .multipliers        = y,
        .multipliers_bounds = vec(0),
        .penalties          = Σ,
        .outer_iter         = static_cast<index_t>(stats.outer_iterations),
        .inner_iter         = static_cast<index_t>(stats.inner.iterations),
        .extra              = std::move(extra),
    };
}