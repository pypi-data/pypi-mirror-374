#pragma once

#include "casadi-namespace.hpp"
#include "casadi-types.hpp"

#include <guanaqo/dl.hpp>
#include <cassert>

namespace alpaqa {
BEGIN_ALPAQA_CASADI_LOADER_NAMESPACE
namespace casadi {

// clang-format off
using fname_incref       = ExternalFunction<"_incref", void(void)>;
using fname_decref       = ExternalFunction<"_decref", void(void)>;
using fname_n_in         = ExternalFunction<"_n_in", casadi_int(void)>;
using fname_n_out        = ExternalFunction<"_n_out", casadi_int(void)>;
using fname_name_in      = ExternalFunction<"_name_in", const char *(casadi_int ind)>;
using fname_name_out     = ExternalFunction<"_name_out", const char *(casadi_int ind)>;
using fname_sparsity_in  = ExternalFunction<"_sparsity_in", const casadi_int *(casadi_int ind)>;
using fname_sparsity_out = ExternalFunction<"_sparsity_out", const casadi_int *(casadi_int ind)>;
using fname_alloc_mem    = ExternalFunction<"_alloc_mem", int(void)>;
using fname_init_mem     = ExternalFunction<"_init_mem", int(int mem)>;
using fname_free_mem     = ExternalFunction<"_free_mem", void(int mem)>;
using fname_work         = ExternalFunction<"_work", int(casadi_int *sz_arg, casadi_int *sz_res, casadi_int *sz_iw, casadi_int *sz_w)>;
using fname              = ExternalFunction<"", int(const casadi_real **arg, casadi_real **res, casadi_int *iw, casadi_real *w, int mem)>;
// clang-format on

template <Name Nm, class Sgn>
auto ExternalFunction<Nm, Sgn>::load(void *handle,
                                     std::string fname) -> signature_t * {
    static_assert(name.value.back() == '\0');
    fname += name.value.data();
    using guanaqo::load_func;
    auto func = reinterpret_cast<signature_t *>(load_func(handle, fname));
    assert(func);
    return func;
}

} // namespace casadi
END_ALPAQA_CASADI_LOADER_NAMESPACE
} // namespace alpaqa
