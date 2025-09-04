#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/util/print.hpp>
#include "solver-driver.hpp"

#include <chrono>
#include <memory>

template <alpaqa::Config Conf>
struct AlpaqaSolverStatsCollector {
    USING_ALPAQA_CONFIG(Conf);
    static constexpr real_t NaN = alpaqa::NaN<Conf>;
    struct Record {
        unsigned outer_iter, inner_iter;
        double time;
        real_t gamma = NaN, eps = NaN, delta = NaN, psi = NaN, psi_hat = NaN,
               fbe = NaN, tau = NaN, radius = NaN, rho = NaN;
    };
    std::vector<Record> stats{};
    std::chrono::steady_clock::time_point t0;

    void update_iter(const auto &progress_info) {
        using alpaqa::vec_util::norm_inf;
        auto t = std::chrono::steady_clock::now();
        if (progress_info.outer_iter == 0 && progress_info.k == 0)
            t0 = t;
        Record r{
            .outer_iter = progress_info.outer_iter,
            .inner_iter = progress_info.k,
            .time       = std::chrono::duration<double>{t - t0}.count(),
        };
        if constexpr (requires { progress_info.γ; })
            r.gamma = progress_info.γ;
        if constexpr (requires { progress_info.ε; })
            r.eps = progress_info.ε;
        if constexpr (requires { progress_info.ψ; })
            r.psi = progress_info.ψ;
        if constexpr (requires { progress_info.ψ_hat; })
            r.psi_hat = progress_info.ψ_hat;
        if constexpr (requires { progress_info.φγ; })
            r.fbe = progress_info.φγ;
        if constexpr (requires { progress_info.τ; })
            r.tau = progress_info.τ;
        if constexpr (requires { progress_info.Δ; })
            r.radius = progress_info.Δ;
        if constexpr (requires { progress_info.ρ; })
            r.rho = progress_info.ρ;
        if constexpr (requires {
                          progress_info.y;
                          progress_info.ŷ;
                          progress_info.Σ;
                      })
            r.delta = norm_inf((progress_info.ŷ - progress_info.y)
                                   .cwiseQuotient(progress_info.Σ));
        stats.push_back(r);
    }
};

template <alpaqa::Config Conf>
struct AlpaqaSolverWrapperStats : SolverWrapper {
    USING_ALPAQA_CONFIG(Conf);
    using collector_t =
        std::shared_ptr<const AlpaqaSolverStatsCollector<config_t>>;
    AlpaqaSolverWrapperStats(solver_func_t run, collector_t collector)
        : SolverWrapper(std::move(run)), collector(std::move(collector)) {}
    collector_t collector;
    [[nodiscard]] bool has_statistics() const override {
        return collector && !collector->stats.empty();
    }
    void write_statistics_to_stream(std::ostream &os) override {
        std::array<char, 64> buf;
        os << "outer_iter,inner_iter,time,gamma,eps,delta,psi,psi_hat,fbe,tau,"
              "radius,rho\n";
        for (const auto &r : collector->stats) {
            os << r.outer_iter << ',' << r.inner_iter << ','
               << alpaqa::float_to_str_vw(buf, r.time) << ','
               << alpaqa::float_to_str_vw(buf, r.gamma) << ','
               << alpaqa::float_to_str_vw(buf, r.eps) << ','
               << alpaqa::float_to_str_vw(buf, r.delta) << ','
               << alpaqa::float_to_str_vw(buf, r.psi) << ','
               << alpaqa::float_to_str_vw(buf, r.psi_hat) << ','
               << alpaqa::float_to_str_vw(buf, r.fbe) << ','
               << alpaqa::float_to_str_vw(buf, r.tau) << ','
               << alpaqa::float_to_str_vw(buf, r.radius) << ','
               << alpaqa::float_to_str_vw(buf, r.rho) << '\n';
        }
    }
};