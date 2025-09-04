#include <alpaqa/inner/directions/panoc/anderson.hpp>
#include <alpaqa/inner/directions/panoc/convex-newton.hpp>
#include <alpaqa/inner/directions/panoc/lbfgs.hpp>
#include <alpaqa/inner/directions/panoc/structured-lbfgs.hpp>
#include <alpaqa/inner/panoc.hpp>
#include <alpaqa/inner/zerofpr.hpp>
#include <guanaqo/string-util.hpp>

#include "alm-driver.hpp"
#include "cancel.hpp"
#include "extra-stats.hpp"
#include "panoc-driver.hpp"
#include "solver-driver.hpp"

namespace {

template <class T>
struct tag_t {};

template <template <class Direction> class Solver>
SharedSolverWrapper make_panoc_like_driver(std::string_view direction,
                                           Options &opts) {
    USING_ALPAQA_CONFIG(alpaqa::DefaultConfig);
    auto builder = []<class Direction>(tag_t<Direction>) {
        return [](std::string_view, Options &opts) -> SharedSolverWrapper {
            using collector_t = AlpaqaSolverStatsCollector<config_t>;
            std::shared_ptr<collector_t> collector;
            auto inner_solver = make_inner_solver<Solver<Direction>>(opts);
            bool extra_stats  = false;
            set_params(extra_stats, "extra_stats", opts);
            if (extra_stats) {
                collector = std::make_shared<collector_t>();
                inner_solver.set_progress_callback(
                    [collector](const auto &progress_info) {
                        collector->update_iter(progress_info);
                    });
            }
            auto solver    = make_alm_solver(std::move(inner_solver), opts);
            unsigned N_exp = 0;
            set_params(N_exp, "num_exp", opts);
            auto run = [solver{std::move(solver)},
                        N_exp](LoadedProblem &problem,
                               std::ostream &os) mutable -> SolverResults {
                auto cancel = alpaqa::attach_cancellation(solver);
                return run_alm_solver(problem, solver, os, N_exp);
            };
            return std::make_shared<AlpaqaSolverWrapperStats<config_t>>(
                std::move(run), std::move(collector));
        };
    };
    std::map<std::string_view, solver_builder_func> builders{
        {"lbfgs", //
         builder(tag_t<alpaqa::LBFGSDirection<config_t>>())},
        {"anderson", //
         builder(tag_t<alpaqa::AndersonDirection<config_t>>())},
        {"struclbfgs", //
         builder(tag_t<alpaqa::StructuredLBFGSDirection<config_t>>())},
        {"convex-newton", //
         builder(tag_t<alpaqa::ConvexNewtonDirection<config_t>>())},
    };
    if (direction.empty())
        direction = "lbfgs";
    auto builder_it = builders.find(direction);
    if (builder_it != builders.end())
        return builder_it->second(direction, opts);
    else
        throw std::invalid_argument("Unknown direction '" +
                                    std::string(direction) + "'\n" +
                                    "  Available directions: " +
                                    guanaqo::join(std::views::keys(builders)));
}

} // namespace

SharedSolverWrapper make_panoc_driver(std::string_view direction,
                                      Options &opts) {
    return make_panoc_like_driver<alpaqa::PANOCSolver>(direction, opts);
}

SharedSolverWrapper make_zerofpr_driver(std::string_view direction,
                                        Options &opts) {
    return make_panoc_like_driver<alpaqa::ZeroFPRSolver>(direction, opts);
}
