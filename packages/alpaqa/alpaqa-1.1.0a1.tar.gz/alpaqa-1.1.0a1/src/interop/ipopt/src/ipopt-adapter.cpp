#include <alpaqa/ipopt/ipopt-adapter.hpp>

#include <alpaqa/util/span.hpp>

#include <IpIpoptCalculatedQuantities.hpp>
#include <stdexcept>

namespace alpaqa {

IpoptAdapter::IpoptAdapter(const Problem &problem) : problem(problem) {}

bool IpoptAdapter::get_nlp_info(Index &n, Index &m, Index &nnz_jac_g,
                                Index &nnz_h_lag, IndexStyleEnum &index_style) {
    n         = static_cast<Index>(problem.get_num_variables());
    m         = static_cast<Index>(problem.get_num_constraints());
    nnz_jac_g = static_cast<Index>(cvt_sparsity_jac_g.get_sparsity().nnz());
    nnz_h_lag = static_cast<Index>(cvt_sparsity_hess_L.get_sparsity().nnz());
    auto jac_g_index  = cvt_sparsity_jac_g.get_sparsity().first_index;
    auto hess_L_index = cvt_sparsity_hess_L.get_sparsity().first_index;
    if (jac_g_index != hess_L_index)
        throw std::invalid_argument(
            "All problem matrices should use the same index convention");
    if (jac_g_index != 0 && jac_g_index != 1)
        throw std::invalid_argument(
            "Sparse matrix indices should start at 0 or 1");
    index_style     = jac_g_index == 0 ? TNLP::C_STYLE : TNLP::FORTRAN_STYLE;
    auto hess_L_sym = cvt_sparsity_hess_L.get_sparsity().symmetry;
    using enum sparsity::Symmetry;
    if (hess_L_sym != Upper && hess_L_sym != Lower)
        throw std::invalid_argument("Hessian matrix should be symmetric");
    return true;
}

bool IpoptAdapter::get_bounds_info(Index n, Number *x_l, Number *x_u, Index m,
                                   Number *g_l, Number *g_u) {
    const auto &C = problem.get_variable_bounds();
    mvec{x_l, n}  = C.lower;
    mvec{x_u, n}  = C.upper;
    const auto &D = problem.get_general_bounds();
    mvec{g_l, m}  = D.lower;
    mvec{g_u, m}  = D.upper;
    return true;
}

bool IpoptAdapter::get_starting_point(Index n, bool init_x, Number *x,
                                      bool init_z, Number *z_L, Number *z_U,
                                      Index m, bool init_lambda,
                                      Number *lambda) {
    if (init_x) {
        if (initial_guess.size() > 0)
            mvec{x, n} = initial_guess;
        else
            mvec{x, n}.setZero();
    }
    if (init_z) {
        if (initial_guess_bounds_multipliers.size() > 0)
            mvec{z_L, n} = (initial_guess_bounds_multipliers.array() < 0)
                               .select(initial_guess_bounds_multipliers, 0);
        else
            mvec{z_L, n}.setZero();
        if (initial_guess_bounds_multipliers.size() > 0)
            mvec{z_U, n} = (initial_guess_bounds_multipliers.array() > 0)
                               .select(initial_guess_bounds_multipliers, 0);
        else
            mvec{z_U, n}.setZero();
    }
    if (init_lambda) {
        if (initial_guess_multipliers.size() > 0)
            mvec{lambda, m} = initial_guess_multipliers;
        else
            mvec{lambda, m}.setZero();
    }
    return true;
}

bool IpoptAdapter::eval_f(Index n, const Number *x, [[maybe_unused]] bool new_x,
                          Number &obj_value) {
    obj_value = problem.eval_objective(cmvec{x, n});
    return true;
}

bool IpoptAdapter::eval_grad_f(Index n, const Number *x,
                               [[maybe_unused]] bool new_x, Number *grad_f) {
    problem.eval_objective_gradient(cmvec{x, n}, mvec{grad_f, n});
    return true;
}

bool IpoptAdapter::eval_g(Index n, const Number *x, [[maybe_unused]] bool new_x,
                          Index m, Number *g) {
    problem.eval_constraints(cmvec{x, n}, mvec{g, m});
    return true;
}

bool IpoptAdapter::eval_jac_g(Index n, const Number *x,
                              [[maybe_unused]] bool new_x,
                              [[maybe_unused]] Index m, Index nele_jac,
                              Index *iRow, Index *jCol, Number *values) {
    if (!problem.provides_eval_constraints_jacobian())
        throw std::logic_error(
            "Missing required function: eval_constraints_jacobian");
    if (values == nullptr) { // Initialize sparsity
        std::ranges::copy(cvt_sparsity_jac_g.get_sparsity().row_indices, iRow);
        std::ranges::copy(cvt_sparsity_jac_g.get_sparsity().col_indices, jCol);
    } else { // Evaluate values
        cvt_sparsity_jac_g.convert_values_into(
            std::span{values, static_cast<size_t>(nele_jac)},
            [&](std::span<real_t> v) {
                problem.eval_constraints_jacobian(cmvec{x, n}, as_vec(v));
            });
        // TODO: reuse workspace
    }
    return true;
}

bool IpoptAdapter::eval_h(Index n, const Number *x, [[maybe_unused]] bool new_x,
                          Number obj_factor, Index m, const Number *lambda,
                          [[maybe_unused]] bool new_lambda, Index nele_hess,
                          Index *iRow, Index *jCol, Number *values) {
    if (!problem.provides_eval_lagrangian_hessian())
        throw std::logic_error(
            "Missing required function: eval_lagrangian_hessian");
    if (values == nullptr) { // Initialize sparsity
        std::ranges::copy(cvt_sparsity_hess_L.get_sparsity().row_indices, iRow);
        std::ranges::copy(cvt_sparsity_hess_L.get_sparsity().col_indices, jCol);
    } else { // Evaluate values
        cvt_sparsity_hess_L.convert_values_into(
            std::span{values, static_cast<size_t>(nele_hess)},
            [&](std::span<real_t> v) {
                problem.eval_lagrangian_hessian(cmvec{x, n}, cmvec{lambda, m},
                                                obj_factor, as_vec(v));
            });
        // TODO: reuse workspace
    }
    return true;
}
void IpoptAdapter::finalize_solution(Ipopt::SolverReturn status, Index n,
                                     const Number *x, const Number *z_L,
                                     const Number *z_U, Index m,
                                     const Number *g, const Number *lambda,
                                     Number obj_value,
                                     const Ipopt::IpoptData *ip_data,
                                     Ipopt::IpoptCalculatedQuantities *ip_cq) {
    results.status        = status;
    results.solution_x    = cmvec{x, n};
    results.solution_z_L  = cmvec{z_L, n};
    results.solution_z_U  = cmvec{z_U, n};
    results.solution_y    = cmvec{lambda, m};
    results.solution_g    = cmvec{g, m};
    results.solution_f    = obj_value;
    results.infeasibility = ip_cq->curr_constraint_violation();
    results.nlp_error     = ip_cq->unscaled_curr_nlp_error();
    results.iter_count    = ip_data->iter_count();
}

} // namespace alpaqa
