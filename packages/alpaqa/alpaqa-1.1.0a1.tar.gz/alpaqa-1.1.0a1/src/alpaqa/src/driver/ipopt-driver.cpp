#ifdef ALPAQA_WITH_IPOPT

#include <alpaqa/ipopt/ipopt-adapter.hpp>
#include <alpaqa/ipopt/ipopt-enums.hpp>
#include <IpIpoptApplication.hpp>

#include <stdexcept>
#include <string>

#include "results.hpp"
#include "solver-driver.hpp"

namespace {

SolverResults run_ipopt_solver(auto &problem,
                               Ipopt::SmartPtr<Ipopt::IpoptApplication> &solver,
                               std::ostream &os, unsigned N_exp) {
    // Ipopt problem adapter
    using Problem                    = alpaqa::IpoptAdapter;
    Ipopt::SmartPtr<Ipopt::TNLP> nlp = new Problem(problem.problem);
    auto *my_nlp                     = dynamic_cast<Problem *>(GetRawPtr(nlp));

    USING_ALPAQA_CONFIG(Problem::config_t);

    // Dimensions
    length_t n = problem.problem.get_num_variables(),
             m = problem.problem.get_num_constraints();

    // Initial guess
    if (auto sz = problem.initial_guess_x.size(); sz != n)
        throw std::invalid_argument(
            "Invalid size for initial_guess_x (expected " + std::to_string(n) +
            ", but got " + std::to_string(sz) + ")");
    if (auto sz = problem.initial_guess_y.size(); sz != m)
        throw std::invalid_argument(
            "Invalid size for initial_guess_y (expected " + std::to_string(m) +
            ", but got " + std::to_string(sz) + ")");
    my_nlp->initial_guess             = problem.initial_guess_x;
    my_nlp->initial_guess_multipliers = problem.initial_guess_y;
    if (auto sz = problem.initial_guess_w.size(); sz > 0) {
        if (sz != n)
            throw std::invalid_argument(
                "Invalid size for initial_guess_w (expected " +
                std::to_string(n) + ", but got " + std::to_string(sz) + ")");
        my_nlp->initial_guess_bounds_multipliers = problem.initial_guess_w;
    }

    // Solve the problem
    auto t0     = std::chrono::steady_clock::now();
    auto status = solver->OptimizeTNLP(nlp);
    auto t1     = std::chrono::steady_clock::now();

    // Solve the problems again to average runtimes
    using ns          = std::chrono::nanoseconds;
    auto avg_duration = duration_cast<ns>(t1 - t0);
    os.setstate(std::ios_base::badbit);
    for (unsigned i = 0; i < N_exp; ++i) {
        my_nlp->initial_guess                    = problem.initial_guess_x;
        my_nlp->initial_guess_multipliers        = problem.initial_guess_y;
        my_nlp->initial_guess_bounds_multipliers = problem.initial_guess_w;

        auto t0 = std::chrono::steady_clock::now();
        solver->OptimizeTNLP(nlp);
        auto t1 = std::chrono::steady_clock::now();
        avg_duration += duration_cast<ns>(t1 - t0);
    }
    os.clear();
    avg_duration /= (N_exp + 1);
    auto evals = *problem.evaluations;

    // Results
    auto &nlp_res = my_nlp->results;
    if (nlp_res.status == Ipopt::SolverReturn::UNASSIGNED) {
        nlp_res.solution_x   = vec::Constant(n, alpaqa::NaN<config_t>);
        nlp_res.solution_y   = vec::Constant(m, alpaqa::NaN<config_t>);
        nlp_res.solution_z_L = vec::Constant(n, alpaqa::NaN<config_t>);
        nlp_res.solution_z_U = vec::Constant(n, alpaqa::NaN<config_t>);
    }
    SolverResults results{
        .status             = std::string(enum_name(status)),
        .success            = status == Ipopt::Solve_Succeeded,
        .evals              = evals,
        .duration           = avg_duration,
        .solver             = "Ipopt",
        .h                  = 0,
        .δ                  = nlp_res.infeasibility,
        .ε                  = nlp_res.nlp_error,
        .γ                  = 0,
        .Σ                  = 0,
        .solution           = nlp_res.solution_x,
        .multipliers        = nlp_res.solution_y,
        .multipliers_bounds = nlp_res.combine_bounds_multipliers(),
        .penalties          = vec::Zero(n),
        .outer_iter         = nlp_res.iter_count,
        .inner_iter         = nlp_res.iter_count,
        .extra              = {},
    };
    return results;
}

auto make_ipopt_solver(Options &opts) {
    using namespace Ipopt;

    // We are using the factory, since this allows us to compile this
    // example with an Ipopt Windows DLL
    SmartPtr<IpoptApplication> app = IpoptApplicationFactory();
    app->RethrowNonIpoptException(true);

    app->Options()->SetNumericValue("tol", 1e-8);
    app->Options()->SetNumericValue("constr_viol_tol", 1e-8);
    app->Options()->SetStringValue("linear_solver", "mumps");
    // app->Options()->SetStringValue("print_timing_statistics", "yes");
    // app->Options()->SetStringValue("timing_statistics", "yes");
    app->Options()->SetStringValue("hessian_approximation", "exact");

    set_params(*app, "solver", opts);

    // Initialize the IpoptApplication and process the options
    ApplicationReturnStatus status = app->Initialize();
    if (status != Solve_Succeeded)
        throw std::runtime_error("Error during Ipopt initialization: " +
                                 std::string(enum_name(status)));

    return app;
}

template <class LoadedProblem>
SharedSolverWrapper make_ipopt_drive_impl(std::string_view direction,
                                          Options &opts) {
    if (!direction.empty())
        throw std::invalid_argument(
            "Ipopt solver does not support any directions");
    auto solver    = make_ipopt_solver(opts);
    unsigned N_exp = 0;
    set_params(N_exp, "num_exp", opts);
    return std::make_shared<SolverWrapper>(
        [solver{std::move(solver)}, N_exp](
            LoadedProblem &problem, std::ostream &os) mutable -> SolverResults {
            return run_ipopt_solver(problem, solver, os, N_exp);
        });
}

} // namespace

SharedSolverWrapper make_ipopt_driver(std::string_view direction,
                                      Options &opts) {
    static constexpr bool valid_config =
        std::is_same_v<LoadedProblem::config_t, alpaqa::IpoptAdapter::config_t>;
    if constexpr (valid_config)
        return make_ipopt_drive_impl<LoadedProblem>(direction, opts);
    else
        throw std::invalid_argument(
            "Ipopt solver only supports double precision");
}

#else

#include "solver-driver.hpp"

SharedSolverWrapper make_ipopt_driver(std::string_view, Options &) {
    throw std::invalid_argument(
        "This version of alpaqa was compiled without Ipopt support.");
}

#endif
