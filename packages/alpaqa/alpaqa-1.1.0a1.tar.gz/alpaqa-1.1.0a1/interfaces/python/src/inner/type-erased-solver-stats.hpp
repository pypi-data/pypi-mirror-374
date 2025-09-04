#pragma once

#include <alpaqa/config/config.hpp>
#include <guanaqo/type-erasure.hpp>

#include <any>
#include <new>
#include <optional>
#include <stdexcept>
#include <type_traits>

#include "../dict/stats-to-dict.hpp"

#include <pybind11/gil.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;

namespace alpaqa {

template <class InnerSolverStats>
struct InnerStatsAccumulator;

template <Config Conf>
struct TypeErasedInnerSolverStats;

namespace detail {
inline auto make_dict_threadsafe() {
    struct deleter {
        void operator()(py::dict *self) const {
            py::gil_scoped_acquire gil;
            delete self;
        }
    };
    py::gil_scoped_acquire gil;
    return std::unique_ptr<py::dict, deleter>{new py::dict};
}
using safe_dict_t = decltype(make_dict_threadsafe());
} // namespace detail

template <Config Conf>
struct InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> {
    std::any accumulator;
    detail::safe_dict_t as_dict = detail::make_dict_threadsafe();
};

template <Config Conf, class Stats>
InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &
operator+=(InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &acc, const Stats &stats) {
    using ActualAccumulator = InnerStatsAccumulator<Stats>;
    if (!acc.accumulator.has_value())
        acc.accumulator = ActualAccumulator{};
    auto *act_acc = std::any_cast<ActualAccumulator>(&acc.accumulator);
    if (!act_acc)
        throw std::logic_error("Cannot combine different types of solver stats");
    *act_acc += stats;
    {
        py::gil_scoped_acquire gil;
        *acc.as_dict = conv::stats_to_dict(*act_acc);
    }
    return acc;
}

template <Config Conf>
InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &
operator+=(InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &acc, const py::object &stats) {
    py::gil_scoped_acquire gil;
    stats.attr("accumulate")(*(acc.as_dict));
    return acc;
}

template <Config Conf>
struct TypeErasedInnerSolverStats {
    USING_ALPAQA_CONFIG(Conf);
    using Accumulator = InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>>;
    void (*combine_p)(Accumulator &acc, const std::any &stats) = nullptr;
    py::dict (*to_dict_p)(const std::any &self)                = nullptr;
    SolverStatus status;
    real_t ε;
    unsigned iterations;

    std::any stats;

    template <class StatsR>
    TypeErasedInnerSolverStats(StatsR &&stats)
        : status(stats.status), ε(stats.ε), iterations(stats.iterations),
          stats(std::forward<StatsR>(stats)) {
        using Stats = std::remove_cvref_t<StatsR>;
        combine_p   = [](Accumulator &acc, const std::any &stats) {
            auto *act_stats = std::any_cast<Stats>(&stats);
            assert(act_stats);
            acc += *act_stats;
        };
        to_dict_p = [](const std::any &self) {
            auto *act_self = std::any_cast<Stats>(&self);
            assert(act_self);
            return conv::stats_to_dict(*act_self);
        };
    }

    TypeErasedInnerSolverStats(py::object &&stats) {
        py::gil_scoped_acquire gil;
        status     = py::cast<SolverStatus>(stats.attr("status"));
        ε          = py::cast<real_t>(stats.attr("ε"));
        iterations = py::cast<unsigned>(stats.attr("iterations"));
        struct Wrapped {
            std::optional<py::object> stats;
            Wrapped(py::object &&stats) : stats{std::move(stats)} {}
            Wrapped(const Wrapped &o) {
                py::gil_scoped_acquire gil;
                this->stats = o.stats;
            }
            Wrapped(Wrapped &&) = default;
            ~Wrapped() {
                py::gil_scoped_acquire gil;
                stats.reset();
            }
        };
        this->stats = Wrapped{std::move(stats)};
        combine_p   = [](Accumulator &acc, const std::any &stats) {
            py::gil_scoped_acquire gil;
            auto *act_stats = std::any_cast<Wrapped>(&stats);
            assert(act_stats);
            assert(act_stats->stats);
            acc += *act_stats->stats;
        };
        to_dict_p = [](const std::any &self) {
            py::gil_scoped_acquire gil;
            auto *act_self = std::any_cast<Wrapped>(&self);
            assert(act_self);
            assert(act_self->stats);
            return py::cast<py::dict>(act_self->stats->attr("to_dict")());
        };
    }

    void combine(Accumulator &acc) const { return combine_p(acc, stats); }
    py::dict to_dict() const { return to_dict_p(stats); }
};

template <Config Conf>
InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &
operator+=(InnerStatsAccumulator<TypeErasedInnerSolverStats<Conf>> &acc,
           const TypeErasedInnerSolverStats<Conf> &stats) {
    stats.combine(acc);
    return acc;
}

} // namespace alpaqa