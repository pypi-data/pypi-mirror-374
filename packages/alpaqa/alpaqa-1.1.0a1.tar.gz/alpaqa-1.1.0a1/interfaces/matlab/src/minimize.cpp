// In separate file, because MATLAB operators clash with Eigen
// (could probably be resolved by removing the using namespace matlab::data).

#include <solver-builder.ipp>
#include <stream.hpp>

#include <alpaqa/casadi/CasADiProblem.hpp>
#include <alpaqa/casadi/CompleteCasADiProblem.hpp>
#include <alpaqa/problem/type-erased-problem.hpp>
#include <alpaqa/util/check-dim.hpp>
#include <alpaqa/util/span.hpp>

namespace alpaqa::mex {

namespace {

void init_problem_data(const ProblemDescription &problem,
                       alpaqa::CasADiProblem<config_t> &cs_problem) {
    auto n = cs_problem.get_num_variables(),
         m = cs_problem.get_num_constraints();
    if (!problem.C_lb.empty()) {
        util::check_dim("problem.C_lowerbound", problem.C_lb,
                        static_cast<size_t>(n));
        cs_problem.variable_bounds.lower = as_vec(std::span{problem.C_lb});
    }
    if (!problem.C_ub.empty()) {
        util::check_dim("problem.C_upperbound", problem.C_ub,
                        static_cast<size_t>(n));
        cs_problem.variable_bounds.upper = as_vec(std::span{problem.C_ub});
    }
    if (!problem.D_lb.empty()) {
        util::check_dim("problem.D_lowerbound", problem.D_lb,
                        static_cast<size_t>(m));
        cs_problem.general_bounds.lower = as_vec(std::span{problem.D_lb});
    }
    if (!problem.D_ub.empty()) {
        util::check_dim("problem.D_upperbound", problem.D_ub,
                        static_cast<size_t>(m));
        cs_problem.general_bounds.upper = as_vec(std::span{problem.D_ub});
    }
    if (!problem.l1_reg.empty()) {
        if (problem.l1_reg.size() != 1)
            util::check_dim("problem.l1_regularization", problem.l1_reg,
                            static_cast<size_t>(n));
        cs_problem.l1_reg = as_vec(std::span{problem.l1_reg});
    }
    if (!problem.param.empty()) {
        if (problem.param.size() != 1)
            util::check_dim("problem.param", problem.param,
                            static_cast<size_t>(problem.param.size()));
        cs_problem.param = as_vec(std::span{problem.param});
    }
}

} // namespace

SolverResults minimize(const ProblemDescription &problem,
                       std::span<const double> x0, std::span<const double> y0,
                       std::string_view method, const Options &options,
                       std::function<void(std::string_view)> write_utf8) {
    // Create CasADi problem
    auto cs_functions{
        casadi_loader::deserialize_problem({{
            {"f", problem.f},
            {"g", problem.g},
        }}),
    };
    casadi_loader::complete_problem(cs_functions);
    alpaqa::CasADiProblem<config_t> cs_problem{cs_functions};

    // Set problem data
    init_problem_data(problem, cs_problem);
    // Initial guess
    if (!x0.empty())
        util::check_dim("x0", x0,
                        static_cast<size_t>(cs_problem.get_num_variables()));
    if (!y0.empty())
        util::check_dim("y0", y0,
                        static_cast<size_t>(cs_problem.get_num_constraints()));

    // Redirect output stream
    streambuf buf{std::move(write_utf8)};
    std::ostream os{&buf};
    // Build a solver
    auto [builder, direction] = get_solver_builder(method, options);
    auto solver               = builder(direction, options);
    // Type-erase the problem
    alpaqa::TypeErasedProblem<config_t> te_problem(&cs_problem);
    // Solve the problem
    return solver(te_problem, as_vec(std::span{x0}), as_vec(std::span{y0}), os);
}

} // namespace alpaqa::mex