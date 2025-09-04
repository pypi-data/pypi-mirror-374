#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/functions/prox.hpp>
#include <Eigen/SVD>

namespace alpaqa::functions {

#if EIGEN_VERSION_AT_LEAST(3, 4, 1)
template <Config Conf>
using DefaultSVD = Eigen::BDCSVD<typename Conf::mat,
                                 Eigen::ComputeThinU | Eigen::ComputeThinV>;
#else
template <Config Conf>
using DefaultSVD = Eigen::BDCSVD<typename Conf::mat>;
#endif

/// Nuclear norm (ℓ₁-norm of singular values).
/// @ingroup grp_Functions
template <Config Conf, class SVD = DefaultSVD<Conf>>
struct NuclearNorm {
    USING_ALPAQA_CONFIG(Conf);

    /// Construct without pre-allocation.
    NuclearNorm(real_t λ = 1) : λ{λ} {
        if (λ < 0 || !std::isfinite(λ))
            throw std::invalid_argument("NuclearNorm::λ must be nonnegative");
    }
    /// Construct with pre-allocation.
    NuclearNorm(real_t λ, length_t rows, length_t cols)
        : λ{λ}, rows{rows}, cols{cols},
#if EIGEN_VERSION_AT_LEAST(3, 4, 1)
          svd{rows, cols},
#else
          svd{rows, cols, Eigen::ComputeThinU | Eigen::ComputeThinV},
#endif
          singular_values{std::min(rows, cols)} {
        if (λ < 0 || !std::isfinite(λ))
            throw std::invalid_argument("NuclearNorm::λ must be nonnegative");
    }

    real_t λ;
    length_t rows = 0, cols = 0;
    SVD svd;
    vec singular_values;

    real_t prox(crmat in, rmat out, real_t γ = 1) {
        if (λ == 0) {
            out = in;
            return 0;
        }
        if (rows == 0 || cols == 0) { // dynamic size
            assert(in.rows() == out.rows());
            assert(in.cols() == out.cols());
#if EIGEN_VERSION_AT_LEAST(3, 4, 1)
            svd.compute(in);
#else
            svd.compute(in, Eigen::ComputeThinU | Eigen::ComputeThinV);
#endif
        } else { // fixed size
            assert(in.size() == rows * cols);
            assert(out.size() == rows * cols);
#if EIGEN_VERSION_AT_LEAST(3, 4, 1)
            svd.compute(in.reshaped(rows, cols));
#else
            svd.compute(in.reshaped(rows, cols),
                        Eigen::ComputeThinU | Eigen::ComputeThinV);
#endif
        }
        const length_t n = svd.singularValues().size();
        auto step        = vec::Constant(n, λ * γ);
        singular_values  = vec::Zero(n).cwiseMax(svd.singularValues() - step);
        using vec_util::norm_1;
        real_t value = λ * norm_1(singular_values);
        auto it0 = std::find(singular_values.begin(), singular_values.end(), 0);
        index_t rank = it0 - singular_values.begin();
        using Eigen::placeholders::all, Eigen::seqN;
        auto sel = seqN(0, rank);
        auto &&U = svd.matrixU(), &&V = svd.matrixV();
        auto &&U1                = U(all, sel);
        auto &&Σ1                = singular_values(sel).asDiagonal();
        auto &&V1T               = V.transpose()(sel, all);
        out.reshaped().noalias() = (U1 * Σ1 * V1T).reshaped();
        return value;
    }

    friend real_t guanaqo_tag_invoke(tag_t<alpaqa::prox>, NuclearNorm &self,
                                     crmat in, rmat out, real_t γ) {
        return self.prox(std::move(in), std::move(out), γ);
    }
};

} // namespace alpaqa::functions