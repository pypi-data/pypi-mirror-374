#pragma once

#include <alpaqa/config/config.hpp>
#include <guanaqo/tag-invoke.hpp>

namespace alpaqa {

using guanaqo::guanaqo_tag_invoke;
using guanaqo::tag_t;

/// Proximal mapping customization point.
/// @see https://wg21.link/P1895R0
struct prox_fn {
    template <class T>
        requires requires {
            // The proximable function type T should define a valid
            // configuration typedef.
            typename T::config_t;
            requires is_config_v<typename T::config_t>;
            // The proximable function type T should opt in to the prox_fn
            // tag to provide a custom implementation for the proximal operator.
            requires guanaqo::tag_invocable<
                prox_fn, T &, typename T::config_t::crmat,
                typename T::config_t::rmat, typename T::config_t::real_t>;
            // The return type of that proximal operator should be real_t.
            requires std::is_same_v<
                guanaqo::tag_invoke_result_t<
                    prox_fn, T &, typename T::config_t::crmat,
                    typename T::config_t::rmat, typename T::config_t::real_t>,
                typename T::config_t::real_t>;
        }
    auto operator()(T &func, typename T::config_t::crmat in,
                    typename T::config_t::rmat out,
                    typename T::config_t::real_t γ = 1) const
        noexcept(guanaqo::is_nothrow_tag_invocable_v<
                 prox_fn, T &, typename T::config_t::crmat,
                 typename T::config_t::rmat, typename T::config_t::real_t>) ->
        typename T::config_t::real_t {
        return guanaqo::guanaqo_tag_invoke(*this, func, std::move(in),
                                           std::move(out), γ);
    }
}
/**
 * Compute the proximal mapping.
 * @f[ \begin{aligned}
 * \mathrm{out} &\leftarrow \prox_{\gamma\, \mathrm{func}}
 * \left( \mathrm{in} \right).
 * \end{aligned}
 * @f]
 * @param       func
 *              The proximable function @f$ h : \Rn \to \Rn @f$ to apply the
 *              proximal mapping of.
 * @param[in]   in
 *              Input vector or matrix @f$ x @f$, e.g. current iterate.
 * @param[out]  out
 *              Proximal mapping of @f$ (\gamma\, h) @f$ at @f$ x @f$.  
 *              @f$ \hat x \leftarrow \prox_{\gamma\, h}\left( x \right) @f$
 * @param[in]   γ
 *              Proximal step size @f$ \gamma @f$.
 * @return      The value of the function evaluated in the output,
 *              @f$ h(\hat x) @f$.
 * @ingroup grp_Functions
 */
inline constexpr prox;

/// Proximal mapping customization point for forward-backward steps.
/// @see https://wg21.link/P1895R0
struct prox_step_fn {
    template <class T>
        requires requires {
            // The proximable function type T should define a valid
            // configuration typedef.
            typename T::config_t;
            requires is_config_v<typename T::config_t>;
            // The proximable function type T should opt in to the prox_step_fn
            // tag to provide a custom implementation for the proximal operator.
            requires guanaqo::tag_invocable<
                prox_step_fn, T &, typename T::config_t::crmat,
                typename T::config_t::crmat, typename T::config_t::rmat,
                typename T::config_t::rmat, typename T::config_t::real_t,
                typename T::config_t::real_t>;
            // The return type of that proximal operator should be real_t.
            requires std::is_same_v<
                guanaqo::tag_invoke_result_t<
                    prox_step_fn, T &, typename T::config_t::crmat,
                    typename T::config_t::crmat, typename T::config_t::rmat,
                    typename T::config_t::rmat, typename T::config_t::real_t,
                    typename T::config_t::real_t>,
                typename T::config_t::real_t>;
        }
    auto operator()(T &func, typename T::config_t::crmat in,
                    typename T::config_t::crmat fwd_step,
                    typename T::config_t::rmat out,
                    typename T::config_t::rmat fb_step,
                    typename T::config_t::real_t γ     = 1,
                    typename T::config_t::real_t γ_fwd = -1) const
        noexcept(guanaqo::is_nothrow_tag_invocable_v<
                 prox_step_fn, T &, typename T::config_t::crmat,
                 typename T::config_t::crmat, typename T::config_t::rmat,
                 typename T::config_t::rmat, typename T::config_t::real_t,
                 typename T::config_t::real_t>) ->
        typename T::config_t::real_t {
        return guanaqo::guanaqo_tag_invoke(*this, func, std::move(in),
                                           std::move(fwd_step), std::move(out),
                                           std::move(fb_step), γ, γ_fwd);
    }

    /// Default implementation for prox_step if only prox is provided.
    template <class T>
        requires requires {
            typename T::config_t;
            requires is_config_v<typename T::config_t>;
            // Only enable if no implementation exists,
            requires !guanaqo::tag_invocable<
                prox_step_fn, T &, typename T::config_t::crmat,
                typename T::config_t::crmat, typename T::config_t::rmat,
                typename T::config_t::rmat, typename T::config_t::real_t,
                typename T::config_t::real_t>;
            // and only enable if prox is provided.
            requires std::invocable<prox_fn, T &, typename T::config_t::crmat,
                                    typename T::config_t::rmat,
                                    typename T::config_t::real_t>;
        }
    auto operator()(T &func, typename T::config_t::crmat in,
                    typename T::config_t::crmat fwd_step,
                    typename T::config_t::rmat out,
                    typename T::config_t::rmat fb_step,
                    typename T::config_t::real_t γ     = 1,
                    typename T::config_t::real_t γ_fwd = -1) const
        noexcept(std::is_nothrow_invocable_v<
                 prox_fn, T &, typename T::config_t::crmat,
                 typename T::config_t::rmat, typename T::config_t::real_t>) ->
        typename T::config_t::real_t {
        fb_step      = in + γ_fwd * fwd_step;
        auto &&h_out = prox(func, fb_step, out, γ);
        fb_step      = out - in;
        return h_out;
    }
}
/**
 * Compute a generalized forward-backward step
 * @f[ \begin{aligned}
 * \mathrm{out} &\leftarrow \prox_{\gamma\, \mathrm{func}}
 * \left( \mathrm{in} + \gamma_\mathrm{fwd}\, \mathrm{fwd\_step} \right) \\
 * \mathrm{fb\_step} &\leftarrow \mathrm{out} - \mathrm{in}.
 * \end{aligned}
 * @f]
 * @param       func
 *              The proximable function @f$ h : \Rn \to \Rn @f$ to apply the
 *              proximal mapping of.
 * @param[in]   in
 *              Input vector or matrix @f$ x @f$, e.g. current iterate.
 * @param[in]   fwd_step
 *              Step @f$ d @f$ to add to @f$ x @f$ before computing the
 *              proximal mapping. Scaled by @f$ \gamma_\text{fwd} @f$.
 * @param[out]  out
 *              Proximal mapping of @f$ (\gamma\, h) @f$ at
 *              @f$ x + \gamma_\text{fwd}\, d @f$.  
 *              @f$ \hat x \leftarrow \prox_{\gamma\, h}\left(
 *              x + \gamma_\text{fwd}\, d \right) @f$
 * @param[out]  fb_step
 *              Forward-backward step @f$ p @f$.  
 *              @f$ p = \hat x - \hat x @f$
 * @param[in]   γ
 *              Proximal step size @f$ \gamma @f$.
 * @param[in]   γ_fwd
 *              Forward step size @f$ \gamma_\mathrm{fwd} @f$.
 * @return      The value of the function evaluated in the output,
 *              @f$ h(\hat x) @f$.
 * @ingroup grp_Functions
 *
 * This function can be used to implement the @ref TypeErasedProblem::eval_proximal_gradient_step function:
 *
 * ```cpp
 * struct Problem {
 *     alpaqa::functions::NuclearNorm<config_t> h{λ, rows, cols};
 *     real_t eval_proximal_gradient_step(real_t γ, crvec x, crvec grad_ψ, rvec x̂, rvec p) const {
 *         return alpaqa::prox_step(h, x, grad_ψ, x̂, p, γ, -γ);
 *     }
 * };
 * ```
 * Note the negative sign for the forward step size.
 */
inline constexpr prox_step;

} // namespace alpaqa
