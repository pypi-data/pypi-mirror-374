#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/export.hpp>
#include <alpaqa/inner/directions/panoc-direction-update.hpp>
#include <alpaqa/inner/internal/panoc-helpers.hpp>
#include <alpaqa/problem/sparsity.hpp>
#include <alpaqa/problem/type-erased-problem.hpp>
#include <alpaqa/util/alloc-check.hpp>
#include <alpaqa/util/index-set.hpp>
#include <alpaqa/util/print.hpp>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>

#include <Eigen/Cholesky>
#include <Eigen/Eigenvalues>

namespace alpaqa {

/// Parameters for the @ref StructuredNewtonDirection class.
/// @ingroup grp_Parameters
template <Config Conf>
struct StructuredNewtonRegularizationParams {
    USING_ALPAQA_CONFIG(Conf);
    /// Minimum eigenvalue of the Hessian, scaled by
    /// @f$ 1 + |\lambda_\mathrm{max}| @f$, enforced by regularization using
    /// a multiple of identity.
    real_t min_eig = std::cbrt(std::numeric_limits<real_t>::epsilon());
    /// Print the minimum and maximum eigenvalue of the Hessian.
    bool print_eig = false;
};

/// Parameters for the @ref StructuredNewtonDirection class.
/// @ingroup grp_Parameters
template <Config Conf>
struct StructuredNewtonDirectionParams {
    USING_ALPAQA_CONFIG(Conf);
    /// Set this option to a nonzero value to include the Hessian-vector product
    /// @f$ \nabla^2_{x_\mathcal{J}x_\mathcal{K}}\psi(x) q_\mathcal{K} @f$ from
    /// equation 12b in @cite pas2022alpaqa, scaled by this parameter.
    /// Set it to zero to leave out that term.
    real_t hessian_vec_factor = 0;
};

/// @ingroup grp_DirectionProviders
template <Config Conf = DefaultConfig>
struct StructuredNewtonDirection {
    USING_ALPAQA_CONFIG(Conf);
    using Problem           = TypeErasedProblem<config_t>;
    using DirectionParams   = StructuredNewtonDirectionParams<config_t>;
    using AcceleratorParams = StructuredNewtonRegularizationParams<config_t>;

    struct Params {
        AcceleratorParams accelerator = {};
        DirectionParams direction     = {};
    };

    StructuredNewtonDirection() = default;
    StructuredNewtonDirection(const Params &params)
        : reg_params(params.accelerator), direction_params(params.direction) {}
    StructuredNewtonDirection(const AcceleratorParams &params,
                              const DirectionParams &directionparams = {})
        : reg_params(params), direction_params(directionparams) {}

    /// @see @ref PANOCDirection::initialize
    void initialize(const Problem &problem, crvec y, crvec Σ,
                    [[maybe_unused]] real_t γ_0, [[maybe_unused]] crvec x_0,
                    [[maybe_unused]] crvec x̂_0, [[maybe_unused]] crvec p_0,
                    [[maybe_unused]] crvec grad_ψx_0) {
        if (!(problem.provides_get_variable_bounds() &&
              problem.provides_get_general_bounds()))
            throw std::invalid_argument(
                "Structured Newton only supports box-constrained problems");
        // TODO: support eval_inactive_indices_res_lna
        if (!problem.supports_eval_augmented_lagrangian_hessian())
            throw std::invalid_argument("Structured Newton requires hess_ψ");
        // Store references to problem and ALM variables
        this->problem = &problem;
        this->y.emplace(y);
        this->Σ.emplace(Σ);
        // Allocate workspaces
        const auto n = problem.get_num_variables();
        JK.resize(n);
        H.resize(n, n);
        HJ_storage.resize(n * n);
        if (!is_dense(problem.get_augmented_lagrangian_hessian_sparsity()))
            throw std::logic_error("Sparse hessians not yet implemented");
    }

    /// @see @ref PANOCDirection::has_initial_direction
    bool has_initial_direction() const { return true; }

    /// @see @ref PANOCDirection::update
    bool update([[maybe_unused]] real_t γₖ, [[maybe_unused]] real_t γₙₑₓₜ,
                [[maybe_unused]] crvec xₖ, [[maybe_unused]] crvec xₙₑₓₜ,
                [[maybe_unused]] crvec pₖ, [[maybe_unused]] crvec pₙₑₓₜ,
                [[maybe_unused]] crvec grad_ψxₖ,
                [[maybe_unused]] crvec grad_ψxₙₑₓₜ) {
        return true;
    }

    /// @see @ref PANOCDirection::apply
    bool apply(real_t γₖ, crvec xₖ, [[maybe_unused]] crvec x̂ₖ, crvec pₖ,
               crvec grad_ψxₖ, rvec qₖ) const {

        const auto n  = problem->get_num_variables();
        const auto &C = problem->get_variable_bounds();

        // Find inactive indices J
        auto nJ = 0;
        for (index_t i = 0; i < n; ++i) {
            real_t gd = xₖ(i) - γₖ * grad_ψxₖ(i);
            if (gd <= C.lower(i)) {        // i ∊ J̲ ⊆ K
                qₖ(i) = pₖ(i);             //
            } else if (C.upper(i) <= gd) { // i ∊ J̅ ⊆ K
                qₖ(i) = pₖ(i);             //
            } else {                       // i ∊ J
                JK(nJ++) = i;
                qₖ(i)    = -grad_ψxₖ(i);
            }
        }

        // There are no inactive indices J
        if (nJ == 0) {
            // No free variables, no Newton step possible
            return false; // Simply use the projection step
        }

        // Compute the Hessian
        problem->eval_augmented_lagrangian_hessian(xₖ, *y, *Σ, 1, H.reshaped());

        // There are no active indices K
        if (nJ == n) {
            // If all indices are free, we can factor the entire matrix.
            // Find the minimum eigenvalue to regularize the Hessian matrix and
            // make it positive definite.
            ScopedMallocAllower ma;
            // Find the minimum eigenvalue to regularize the Hessian matrix and
            // make it positive definite.
            Eigen::SelfAdjointEigenSolver<mat> eig{H,
                                                   Eigen::ComputeEigenvectors};

            auto λ_min = eig.eigenvalues().minCoeff(),
                 λ_max = eig.eigenvalues().maxCoeff();

            if (reg_params.print_eig)
                std::cout << "λ(H):    " << float_to_str(λ_min, 3) << ", "
                          << float_to_str(λ_max, 3) << std::endl;
            // Regularization
            real_t ε = reg_params.min_eig * (1 + std::abs(λ_max)); // TODO
            // Solve the system
            qₖ = eig.eigenvectors().transpose() * qₖ;
            qₖ = eig.eigenvalues().cwiseMax(ε).asDiagonal().inverse() * qₖ;
            qₖ = eig.eigenvectors() * qₖ;
            return true;
        }

        // There are active indices K
        crindexvec J = JK.topRows(nJ);
        rindexvec K  = JK.bottomRows(n - nJ);
        detail::IndexSet<config_t>::compute_complement(J, K, n);

        // Compute right-hand side of 6.1c
        if (direction_params.hessian_vec_factor != 0)
            qₖ(J).noalias() -=
                direction_params.hessian_vec_factor * (H(J, K) * qₖ(K));

        // If there are active indices, we need to solve the Newton system with
        // just the inactive indices.
        mmat HJ{HJ_storage.data(), nJ, nJ};
        // We copy the inactive block of the Hessian to a temporary dense matrix.
        // Since it's symmetric, only the lower part is copied.
        HJ.template triangularView<Eigen::Lower>() =
            H(J, J).template triangularView<Eigen::Lower>();

        ScopedMallocAllower ma;
        // Find the minimum eigenvalue to regularize the Hessian matrix and
        // make it positive definite.
        Eigen::SelfAdjointEigenSolver<mat> eig{HJ, Eigen::ComputeEigenvectors};

        auto λ_min = eig.eigenvalues().minCoeff(),
             λ_max = eig.eigenvalues().maxCoeff();

        if (reg_params.print_eig)
            std::cout << "λ(H_JJ): " << float_to_str(λ_min, 3) << ", "
                      << float_to_str(λ_max, 3) << std::endl;
        // Regularization
        real_t ε = reg_params.min_eig * (1 + std::abs(λ_max)); // TODO
        // Solve the system
        auto qJ = H.col(0).topRows(nJ);
        qJ      = qₖ(J);
        qJ      = eig.eigenvectors().transpose() * qJ;
        qJ      = eig.eigenvalues().cwiseMax(ε).asDiagonal().inverse() * qJ;
        qₖ(J)   = eig.eigenvectors() * qJ;
        return true;
    }

    /// @see @ref PANOCDirection::changed_γ
    void changed_γ([[maybe_unused]] real_t γₖ, [[maybe_unused]] real_t old_γₖ) {
    }

    /// @see @ref PANOCDirection::reset
    void reset() {}

    /// @see @ref PANOCDirection::get_name
    std::string get_name() const {
        return "StructuredNewtonDirection<" +
               std::string(config_t::get_name()) + '>';
    }

    const auto &get_params() const { return direction_params; }

  private:
    const Problem *problem = nullptr;
#ifndef _WIN32
    std::optional<crvec> y = std::nullopt;
    std::optional<crvec> Σ = std::nullopt;
#else
    std::optional<vec> y = std::nullopt;
    std::optional<vec> Σ = std::nullopt;
#endif

    mutable indexvec JK;
    mutable mat H;
    mutable vec HJ_storage;

  public:
    AcceleratorParams reg_params;
    DirectionParams direction_params;
};

// clang-format off
ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, StructuredNewtonDirection, EigenConfigd);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, StructuredNewtonDirection, EigenConfigf);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, StructuredNewtonDirection, EigenConfigl);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_EXTERN_TEMPLATE(struct, StructuredNewtonDirection, EigenConfigq);)
// clang-format on

} // namespace alpaqa
