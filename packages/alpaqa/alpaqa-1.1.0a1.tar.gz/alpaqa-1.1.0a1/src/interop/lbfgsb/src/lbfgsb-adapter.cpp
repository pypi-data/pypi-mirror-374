#include <alpaqa/lbfgsb/lbfgsb-adapter.hpp>
#include <alpaqa/util/print.hpp>
#include <guanaqo/timed.hpp>

#include <iomanip>
#include <stdexcept>

extern "C" {
void alpaqa_setulb_c(int n, int m, double *x, const double *l, const double *u,
                     const int *nbd, double &f, double *g, double factr,
                     double pgtol, double *wa, int *iwa, char *task, int iprint,
                     char *csave, bool *lsave, int *isave, double *dsave);
}

namespace alpaqa::lbfgsb {

std::string LBFGSBSolver::get_name() const { return "LBFGSBSolver"; }
auto LBFGSBSolver::operator()(
    /// [in]    Problem description
    const Problem &problem,
    /// [in]    Solve options
    const SolveOptions &opts,
    /// [inout] Decision variable @f$ x @f$
    rvec x,
    /// [inout] Lagrange multipliers @f$ y @f$
    rvec y,
    /// [in]    Constraint weights @f$ \Sigma @f$
    crvec Σ,
    /// [out]   Slack variable error @f$ g(x) - \Pi_D(g(x) + \Sigma^{-1} y) @f$
    rvec err_z) -> Stats {

    if (opts.check)
        problem.check();

    using std::chrono::nanoseconds;
    using clock     = std::chrono::steady_clock;
    auto start_time = clock::now();
    auto *os        = opts.os ? opts.os : this->os;
    auto max_time   = params.max_time;
    if (opts.max_time)
        max_time = std::min(max_time, *opts.max_time);
    Stats s;

    if (!problem.provides_get_variable_bounds())
        throw std::invalid_argument("LBFGSBSolver requires box constraints");
    if (params.stop_crit != PANOCStopCrit::ProjGradUnitNorm)
        throw std::invalid_argument("LBFGSBSolver only supports "
                                    "PANOCStopCrit::ProjGradUnitNorm");

    const auto n        = problem.get_num_variables();
    const auto m_constr = problem.get_num_constraints();
    const auto &C       = problem.get_variable_bounds();
    const auto mem      = static_cast<length_t>(params.memory);

    auto do_progress_cb = [this, &s, &problem, &Σ, &y,
                           &opts](unsigned k, crvec x, real_t ψx, crvec grad_ψx,
                                  real_t τ_max, real_t τ, real_t ε,
                                  SolverStatus status) {
        if (!progress_cb)
            return;
        ScopedMallocAllower ma;
        guanaqo::Timed t{s.time_progress_callback};
        progress_cb(ProgressInfo{
            .k          = k,
            .status     = status,
            .x          = x,
            .ψ          = ψx,
            .grad_ψ     = grad_ψx,
            .τ_max      = τ_max,
            .τ          = τ,
            .ε          = ε,
            .Σ          = Σ,
            .y          = y,
            .outer_iter = opts.outer_iter,
            .problem    = &problem,
            .params     = &params,
        });
    };

    using intvec = Eigen::VectorX<int>;

    vec work_n(n), work_m(m_constr);
    vec grad_ψ(n);
    real_t ψ = NaN<config_t>;
    vec wa(2 * mem * n + 5 * n + 11 * mem * mem + 8 * mem);
    vec dsave(29);
    intvec iwa(3 * n), isave(44);
    std::array<bool, 4> lsave{};
    std::array<char, 60> task{}, csave{};

    // Determine constraint type for each variable
    intvec nbd(n);
    for (index_t i = 0; i < n; ++i) {
        static constexpr int nbd_legend[2][2] /* NOLINT(*c-arrays) */ {{0, 3},
                                                                       {1, 2}};
        int lowerbounded = C.lower(i) == -inf<config_t> ? 0 : 1;
        int upperbounded = C.upper(i) == +inf<config_t> ? 0 : 1;
        nbd(i)           = nbd_legend[lowerbounded][upperbounded];
    }

    vec x_solve = x;

    real_t factr = 0;
    real_t pgtol = 0;
    int print    = params.print;

    std::string_view task_sv{task.begin(), task.end()};
    const int &num_iter          = isave.coeffRef(29);
    const int &lbfgs_skipped     = isave.coeffRef(25);
    const int &num_free_var      = isave.coeffRef(37);
    const real_t &q_norm         = dsave.coeffRef(3);
    const real_t &τ_max          = dsave.coeffRef(11);
    const real_t &proj_grad_norm = dsave.coeffRef(12);
    const real_t &τ_rel          = dsave.coeffRef(13);
    // const int &lbfgs_tot         = isave.coeffRef(30);

    auto set_task = [&](std::string_view s) {
        std::fill(std::copy(s.begin(), s.end(), task.begin()), task.end(), ' ');
    };

    std::array<char, 64> print_buf;
    auto print_real = [this, &print_buf](real_t x) {
        return float_to_str_vw(print_buf, x, params.print_precision);
    };
    auto print_real3 = [&print_buf](real_t x) {
        return float_to_str_vw(print_buf, x, 3);
    };
    auto print_progress_1 = [&](unsigned k, real_t ψₖ, crvec grad_ψₖ,
                                real_t εₖ) {
        if (k == 0)
            *os << "┌─[LBFGSB]\n";
        else
            *os << "├─ " << std::setw(6) << k << " ──\n";
        *os << "│    ψ = " << print_real(ψₖ)             //
            << ", ‖∇ψ‖ = " << print_real(grad_ψₖ.norm()) //
            << ",    ε = " << print_real(εₖ) << '\n';
    };
    auto print_progress_2 = [&](real_t q_norm, real_t τ_max, real_t τ_rel,
                                int nJ) {
        const auto thres  = std::sqrt(std::numeric_limits<real_t>::epsilon());
        const char *color = τ_rel == 1      ? "\033[0;32m"
                            : τ_rel > thres ? "\033[0;33m"
                                            : "\033[0;35m";
        *os << "│  ‖q‖ = " << print_real(q_norm)                       //
            << ",    τ = " << color << print_real3(τ_rel) << "\033[0m" //
            << ", τ_max = " << print_real3(τ_max)                      //
            << ",   #J = " << std::setw(6) << nJ
            << std::endl; // Flush for Python buffering
    };
    auto print_progress_n = [&](SolverStatus status) {
        *os << "└─ " << status << " ──"
            << std::endl; // Flush for Python buffering
    };
    bool did_print = false;

    // Start solving
    set_task("START");

    while (true) {
        // Invoke solver
        alpaqa_setulb_c(static_cast<int>(n), static_cast<int>(mem),
                        x_solve.data(), C.lower.data(), C.upper.data(),
                        nbd.data(), ψ, grad_ψ.data(), factr, pgtol, wa.data(),
                        iwa.data(), task.data(), print, csave.data(),
                        lsave.data(), isave.data(), dsave.data());

        // New evaluation
        if (task_sv.starts_with("FG")) {
            ψ = problem.eval_augmented_lagrangian_and_gradient(
                x_solve, y, Σ, grad_ψ, work_n, work_m);
        }
        // Converged
        else if (task_sv.starts_with(
                     "CONVERGENCE: NORM_OF_PROJECTED_GRADIENT_<=_PGTOL")) {
            s.status = SolverStatus::Converged;
            break;
        }
        // Next iteration
        else if (task_sv.starts_with("NEW_X")) {
            // Check termination
            if (proj_grad_norm <= opts.tolerance) {
                s.status = SolverStatus::Converged;
                set_task("STOP: projected gradient norm");
                break;
            } else if (clock::now() - start_time >= max_time) {
                s.status = SolverStatus::MaxTime;
                set_task("STOP: time");
                break;
            } else if (static_cast<unsigned>(num_iter) >= params.max_iter) {
                s.status = SolverStatus::MaxIter;
                set_task("STOP: number iterations");
                break;
            } else if (stop_signal.stop_requested()) {
                s.status = SolverStatus::Interrupted;
                set_task("STOP: user request");
                break;
            } else {
                auto k        = static_cast<unsigned>(num_iter) - 1;
                bool do_print = params.print_interval != 0 &&
                                k % params.print_interval == 0;
                // Print info
                if (std::exchange(did_print, do_print))
                    print_progress_2(q_norm, τ_max, τ_rel, num_free_var);
                if (std::exchange(do_print, false))
                    print_progress_1(k, ψ, grad_ψ, proj_grad_norm);
                // Progress callback
                do_progress_cb(k, x, ψ, grad_ψ, τ_max, τ_rel, proj_grad_norm,
                               SolverStatus::Busy);
            }
        }
        // Stop
        else if (task_sv.starts_with("CONVERGENCE: REL_REDUCTION_OF_F")) {
            s.status = SolverStatus::NoProgress;
            break;
        }
        // Unexpected status
        else {
            s.status = SolverStatus::Exception;
            break;
        }
    }

    // Print info
    auto k = static_cast<unsigned>(num_iter) - 1;
    if (std::exchange(did_print, false))
        print_progress_2(q_norm, τ_max, τ_rel, num_free_var);
    else if (params.print_interval != 0)
        print_progress_1(k, ψ, grad_ψ, proj_grad_norm);
    // Error reporting
    if (s.status == SolverStatus::Exception) {
        std::string_view task_trimmed = task_sv;
        auto trim_pos                 = task_sv.find('\0');
        trim_pos                      = task_sv.find_last_not_of(' ', trim_pos);
        if (trim_pos != task_trimmed.npos)
            task_trimmed.remove_suffix(task_trimmed.size() - trim_pos);
        *os << "│ \033[0;31mLBFGSB failure\033[0m: '\033[0;33m" << task_trimmed
            << "\033[0m'" << std::endl;
    }
    if (params.print_interval != 0)
        print_progress_n(s.status);

    // Progress callback
    do_progress_cb(k, x, ψ, grad_ψ, τ_max, τ_rel, proj_grad_norm, s.status);

    auto time_elapsed           = clock::now() - start_time;
    s.elapsed_time              = duration_cast<nanoseconds>(time_elapsed);
    s.direction_update_rejected = static_cast<unsigned>(lbfgs_skipped);
    s.iterations                = static_cast<unsigned>(num_iter);

    // Check final error
    s.ε = proj_grad_norm;
    // Update result vectors
    if (s.status == SolverStatus::Converged ||
        s.status == SolverStatus::Interrupted ||
        opts.always_overwrite_results) {
        auto &ŷ   = work_m;
        s.final_ψ = problem.eval_augmented_lagrangian(x_solve, y, Σ, ŷ);
        if (err_z.size() > 0)
            err_z = (ŷ - y).cwiseQuotient(Σ);
        x = x_solve;
        y = ŷ;
    }
    return s;
}

} // namespace alpaqa::lbfgsb