/**
 * @file
 * This file defines mappings from Python dicts (kwargs) to simple parameter
 * structs.
 */

#pragma once

#if ALPAQA_WITH_OCP
#include <alpaqa/inner/panoc-ocp.hpp>
#endif
#if ALPAQA_WITH_LBFGSB
#include <alpaqa/lbfgsb/lbfgsb-adapter.hpp>
#endif
#include <alpaqa/inner/fista.hpp>
#include <alpaqa/inner/panoc.hpp>
#include <alpaqa/inner/pantr.hpp>
#include <alpaqa/inner/zerofpr.hpp>

#include <pybind11/chrono.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;

namespace alpaqa {

template <class Inner>
class ALMSolver;

} // namespace alpaqa

namespace alpaqa::conv {

template <Config Conf>
py::dict stats_to_dict(const PANOCStats<Conf> &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                    = s.status,
        "ε"_a                         = s.ε,
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const InnerStatsAccumulator<PANOCStats<Conf>> &s) {
    using namespace py::literals;
    return py::dict{
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const FISTAStats<Conf> &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                 = s.status,
        "ε"_a                      = s.ε,
        "elapsed_time"_a           = s.elapsed_time,
        "time_progress_callback"_a = s.time_progress_callback,
        "iterations"_a             = s.iterations,
        "stepsize_backtracks"_a    = s.stepsize_backtracks,
        "final_γ"_a                = s.final_γ,
        "final_ψ"_a                = s.final_ψ,
        "final_h"_a                = s.final_h,
    };
}

template <Config Conf>
py::dict stats_to_dict(const InnerStatsAccumulator<FISTAStats<Conf>> &s) {
    using namespace py::literals;
    return py::dict{
        "elapsed_time"_a = s.elapsed_time, "time_progress_callback"_a = s.time_progress_callback,
        "iterations"_a = s.iterations,     "stepsize_backtracks"_a = s.stepsize_backtracks,
        "final_γ"_a = s.final_γ,           "final_ψ"_a = s.final_ψ,
        "final_h"_a = s.final_h,
    };
}

#if ALPAQA_WITH_LBFGSB

inline py::dict stats_to_dict(const lbfgsb::LBFGSBStats &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                    = s.status,
        "ε"_a                         = s.ε,
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "final_ψ"_a                   = s.final_ψ,
        "direction_update_rejected"_a = s.direction_update_rejected,
    };
}

inline py::dict stats_to_dict(const InnerStatsAccumulator<lbfgsb::LBFGSBStats> &s) {
    using namespace py::literals;
    return py::dict{
        "iterations"_a                = s.iterations,
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "final_ψ"_a                   = s.final_ψ,
        "direction_update_rejected"_a = s.direction_update_rejected,
    };
}

#endif

#if ALPAQA_WITH_OCP

template <Config Conf>
py::dict stats_to_dict(const PANOCOCPStats<Conf> &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                    = s.status,
        "ε"_a                         = s.ε,
        "elapsed_time"_a              = s.elapsed_time,
        "time_forward"_a              = s.time_forward,
        "time_backward"_a             = s.time_backward,
        "time_jacobians"_a            = s.time_jacobians,
        "time_hessians"_a             = s.time_hessians,
        "time_indices"_a              = s.time_indices,
        "time_lqr_factor"_a           = s.time_lqr_factor,
        "time_lqr_solve"_a            = s.time_lqr_solve,
        "time_lbfgs_indices"_a        = s.time_lbfgs_indices,
        "time_lbfgs_apply"_a          = s.time_lbfgs_apply,
        "time_lbfgs_update"_a         = s.time_lbfgs_update,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const InnerStatsAccumulator<PANOCOCPStats<Conf>> &s) {
    using namespace py::literals;
    return py::dict{
        "elapsed_time"_a              = s.elapsed_time,
        "iterations"_a                = s.iterations,
        "time_forward"_a              = s.time_forward,
        "time_backward"_a             = s.time_backward,
        "time_jacobians"_a            = s.time_jacobians,
        "time_hessians"_a             = s.time_hessians,
        "time_indices"_a              = s.time_indices,
        "time_lqr_factor"_a           = s.time_lqr_factor,
        "time_lqr_solve"_a            = s.time_lqr_solve,
        "time_lbfgs_indices"_a        = s.time_lbfgs_indices,
        "time_lbfgs_apply"_a          = s.time_lbfgs_apply,
        "time_lbfgs_update"_a         = s.time_lbfgs_update,
        "time_progress_callback"_a    = s.time_progress_callback,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

#endif

template <Config Conf>
py::dict stats_to_dict(const ZeroFPRStats<Conf> &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                    = s.status,
        "ε"_a                         = s.ε,
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const InnerStatsAccumulator<ZeroFPRStats<Conf>> &s) {
    using namespace py::literals;
    return py::dict{
        "elapsed_time"_a              = s.elapsed_time,
        "iterations"_a                = s.iterations,
        "time_progress_callback"_a    = s.time_progress_callback,
        "linesearch_failures"_a       = s.linesearch_failures,
        "linesearch_backtracks"_a     = s.linesearch_backtracks,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "τ_1_accepted"_a              = s.τ_1_accepted,
        "count_τ"_a                   = s.count_τ,
        "sum_τ"_a                     = s.sum_τ,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const PANTRStats<Conf> &s) {
    using namespace py::literals;
    return py::dict{
        "status"_a                    = s.status,
        "ε"_a                         = s.ε,
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "accelerated_step_rejected"_a = s.accelerated_step_rejected,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <Config Conf>
py::dict stats_to_dict(const InnerStatsAccumulator<PANTRStats<Conf>> &s) {
    using namespace py::literals;
    return py::dict{
        "elapsed_time"_a              = s.elapsed_time,
        "time_progress_callback"_a    = s.time_progress_callback,
        "iterations"_a                = s.iterations,
        "accelerated_step_rejected"_a = s.accelerated_step_rejected,
        "stepsize_backtracks"_a       = s.stepsize_backtracks,
        "direction_failures"_a        = s.direction_failures,
        "direction_update_rejected"_a = s.direction_update_rejected,
        "final_γ"_a                   = s.final_γ,
        "final_ψ"_a                   = s.final_ψ,
        "final_h"_a                   = s.final_h,
        "final_φγ"_a                  = s.final_φγ,
    };
}

template <class Inner>
py::dict stats_to_dict(const typename ALMSolver<Inner>::Stats &s) {
    using namespace py::literals;
    return py::dict{
        "outer_iterations"_a           = s.outer_iterations,
        "elapsed_time"_a               = s.elapsed_time,
        "inner_convergence_failures"_a = s.inner_convergence_failures,
        "ε"_a                          = s.ε,
        "δ"_a                          = s.δ,
        "norm_penalty"_a               = s.norm_penalty,
        "status"_a                     = s.status,
        "inner"_a                      = *s.inner.as_dict,
    };
}

} // namespace alpaqa::conv
