#pragma once

#include <alpaqa/config/config.hpp>
#include <alpaqa/inner/directions/panoc-direction-update.hpp>
#include <alpaqa/inner/directions/panoc/lbfgs.hpp>
#include <guanaqo/type-erasure.hpp>

#include <dict/dict-tup.hpp>
#include <dict/kwargs-to-struct.hpp>

#include <new>
#include <string>
#include <type_traits>
#include <utility>

#include <pybind11/pytypes.h>
namespace py = pybind11;

namespace alpaqa {

using guanaqo::required_function_t;

template <Config Conf>
struct PANOCDirectionVTable : guanaqo::BasicVTable {
    USING_ALPAQA_CONFIG(Conf);
    using Problem = TypeErasedProblem<config_t>;

    // clang-format off
    required_function_t<void(const Problem &problem, crvec y, crvec Σ, real_t γ_0, crvec x_0, crvec x̂_0, crvec p_0, crvec grad_ψx_0)>
        initialize = nullptr;
    required_function_t<bool(real_t γₖ, real_t γₙₑₓₜ, crvec xₖ, crvec xₙₑₓₜ, crvec pₖ, crvec pₙₑₓₜ, crvec grad_ψxₖ, crvec grad_ψxₙₑₓₜ)>
        update = nullptr;
    required_function_t<bool() const>
        has_initial_direction = nullptr;
    required_function_t<bool(real_t γₖ, crvec xₖ, crvec x̂ₖ, crvec pₖ, crvec grad_ψxₖ, rvec qₖ) const>
        apply = nullptr;
    required_function_t<void(real_t γₖ, real_t old_γₖ)>
        changed_γ = nullptr;
    required_function_t<void()>
        reset = nullptr;
    required_function_t<py::object() const>
        get_params = nullptr;
    required_function_t<std::string() const>
        get_name = nullptr;
    // clang-format on

    template <class T>
    PANOCDirectionVTable(std::in_place_t, T &t) : guanaqo::BasicVTable{std::in_place, t} {
        initialize            = guanaqo::type_erased_wrapped<T, &T::initialize>();
        update                = guanaqo::type_erased_wrapped<T, &T::update>();
        has_initial_direction = guanaqo::type_erased_wrapped<T, &T::has_initial_direction>();
        apply                 = guanaqo::type_erased_wrapped<T, &T::apply>();
        changed_γ             = guanaqo::type_erased_wrapped<T, &T::changed_γ>();
        reset                 = guanaqo::type_erased_wrapped<T, &T::reset>();
        get_params            = guanaqo::type_erased_wrapped<T, &T::get_params>();
        get_name              = guanaqo::type_erased_wrapped<T, &T::get_name>();
    }
    PANOCDirectionVTable() = default;
};

template <Config Conf>
constexpr size_t te_pd_buff_size = guanaqo::required_te_buffer_size_for<LBFGSDirection<Conf>>();

template <Config Conf = DefaultConfig, class Allocator = std::allocator<std::byte>>
class TypeErasedPANOCDirection
    : public guanaqo::TypeErased<PANOCDirectionVTable<Conf>, Allocator, te_pd_buff_size<Conf>> {
  public:
    USING_ALPAQA_CONFIG(Conf);
    using VTable         = PANOCDirectionVTable<Conf>;
    using allocator_type = Allocator;
    using TypeErased     = guanaqo::TypeErased<VTable, allocator_type, te_pd_buff_size<Conf>>;
    using TypeErased::TypeErased;
    using Problem = TypeErasedProblem<config_t>;

  private:
    using TypeErased::call;
    using TypeErased::self;
    using TypeErased::vtable;

  public:
    template <class T, class... Args>
    static TypeErasedPANOCDirection make(Args &&...args) {
        return TypeErased::template make<TypeErasedPANOCDirection, T>(std::forward<Args>(args)...);
    }

    template <class... Args>
    decltype(auto) initialize(Args &&...args) {
        return call(vtable.initialize, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) update(Args &&...args) {
        return call(vtable.update, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) has_initial_direction(Args &&...args) const {
        return call(vtable.has_initial_direction, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) apply(Args &&...args) const {
        return call(vtable.apply, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) changed_γ(Args &&...args) {
        return call(vtable.changed_γ, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) reset(Args &&...args) {
        return call(vtable.reset, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) get_params(Args &&...args) const {
        return call(vtable.get_params, std::forward<Args>(args)...);
    }
    template <class... Args>
    decltype(auto) get_name(Args &&...args) const {
        return call(vtable.get_name, std::forward<Args>(args)...);
    }
};

template <class T, class... Args>
auto erase_direction_with_params_dict(Args &&...args) {
    static constexpr bool void_params = requires(const T &t) {
        { t.get_params() } -> std::same_as<void>;
    };
    struct DirectionWrapper : T {
        DirectionWrapper(const T &d) : T{d} {}
        DirectionWrapper(T &&d) : T{std::move(d)} {}
        using T::T;
        py::object get_params() const {
            if constexpr (void_params)
                return py::none();
            else
                return to_dict_tup(T::get_params());
        }
    };
    return TypeErasedPANOCDirection<typename T::config_t>::template make<DirectionWrapper>(
        std::forward<Args>(args)...);
}

} // namespace alpaqa