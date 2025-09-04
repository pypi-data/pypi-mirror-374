#include <guanaqo/quadmath/quadmath.hpp>

#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace py::literals;

#include <alpaqa/accelerators/lbfgs.hpp>
#include <alpaqa/util/check-dim.hpp>

#include <dict/kwargs-to-struct.hpp>
#include <dict/stats-to-dict.hpp>

template <alpaqa::Config Conf>
void register_lbfgs(py::module_ &m) {
    USING_ALPAQA_CONFIG(Conf);

    using LBFGS = alpaqa::LBFGS<config_t>;
    py::class_<LBFGS> lbfgs(m, "LBFGS", "C++ documentation :cpp:class:`alpaqa::LBFGS`");
    using LBFGSParams = typename LBFGS::Params;
    py::class_<LBFGSParams> lbfgsparams(lbfgs, "Params",
                                        "C++ documentation :cpp:class:`alpaqa::LBFGSParams`");
    using CBFGS = alpaqa::CBFGSParams<config_t>;
    register_dataclass<CBFGS>(lbfgsparams, "CBFGS",
                              "C++ documentation :cpp:class:`alpaqa::CBFGSParams`");
    using LBFGSSign = typename LBFGS::Sign;
    py::enum_<LBFGSSign> lbfgssign(lbfgs, "Sign",
                                   "C++ documentation :cpp:enum:`alpaqa::LBFGS::Sign`");
    make_dataclass(lbfgsparams);
    lbfgssign //
        .value("Positive", LBFGSSign::Positive)
        .value("Negative", LBFGSSign::Negative)
        .export_values();

    auto safe_lbfgs_update = [](LBFGS &self, crvec xk, crvec xkp1, crvec pk, crvec pkp1,
                                LBFGSSign sign, bool forced) {
        alpaqa::util::check_dim("xk", xk, self.n());
        alpaqa::util::check_dim("xkp1", xkp1, self.n());
        alpaqa::util::check_dim("pk", pk, self.n());
        alpaqa::util::check_dim("pkp1", pkp1, self.n());
        return self.update(xk, xkp1, pk, pkp1, sign, forced);
    };
    auto safe_lbfgs_update_sy = [](LBFGS &self, crvec sk, crvec yk, real_t pkp1Tpkp1, bool forced) {
        alpaqa::util::check_dim("sk", sk, self.n());
        alpaqa::util::check_dim("yk", yk, self.n());
        return self.update_sy(sk, yk, pkp1Tpkp1, forced);
    };
    auto safe_lbfgs_apply = [](LBFGS &self, rvec q, real_t γ) {
        alpaqa::util::check_dim("q", q, self.n());
        return self.apply(q, γ);
    };

    lbfgs //
        .def(py::init([](params_or_dict<LBFGSParams> params) {
                 return LBFGS{var_kwargs_to_struct(params)};
             }),
             "params"_a)
        .def(py::init([](params_or_dict<LBFGSParams> params, length_t n) {
                 return LBFGS{var_kwargs_to_struct(params), n};
             }),
             "params"_a, "n"_a)
        .def_static("update_valid", LBFGS::update_valid, "params"_a, "yᵀs"_a, "sᵀs"_a, "pᵀp"_a)
        .def("update", safe_lbfgs_update, "xk"_a, "xkp1"_a, "pk"_a, "pkp1"_a,
             "sign"_a = LBFGS::Sign::Positive, "forced"_a = false)
        .def("update_sy", safe_lbfgs_update_sy, "sk"_a, "yk"_a, "pkp1Tpkp1"_a, "forced"_a = false)
        .def("apply", safe_lbfgs_apply, "q"_a, "γ"_a)
        .def("apply_masked",
             py::overload_cast<rvec, real_t, const std::vector<index_t> &>(&LBFGS::apply_masked,
                                                                           py::const_),
             // [](LBFGS &self, rvec q, real_t γ, const std::vector<index_t> &J) {
             //     return self.apply_masked(q, γ, J);
             // },
             "q"_a, "γ"_a, "J"_a)
        .def("reset", &LBFGS::reset)
        .def("current_history", &LBFGS::current_history)
        .def("resize", &LBFGS::resize, "n"_a)
        .def("scale_y", &LBFGS::scale_y, "factor"_a)
        .def_property_readonly("n", &LBFGS::n)
        .def(
            "s", [](LBFGS &self, index_t i) -> rvec { return self.s(i); },
            py::return_value_policy::reference_internal, "i"_a)
        .def(
            "y", [](LBFGS &self, index_t i) -> rvec { return self.y(i); },
            py::return_value_policy::reference_internal, "i"_a)
        .def(
            "ρ", [](LBFGS &self, index_t i) -> real_t & { return self.ρ(i); },
            py::return_value_policy::reference_internal, "i"_a)
        .def(
            "α", [](LBFGS &self, index_t i) -> real_t & { return self.α(i); },
            py::return_value_policy::reference_internal, "i"_a)
        .def_property_readonly("params", &LBFGS::get_params)
        .def("__str__", &LBFGS::get_name);
}

template void register_lbfgs<alpaqa::EigenConfigd>(py::module_ &);
ALPAQA_IF_FLOAT(template void register_lbfgs<alpaqa::EigenConfigf>(py::module_ &);)
ALPAQA_IF_LONGD(template void register_lbfgs<alpaqa::EigenConfigl>(py::module_ &);)
ALPAQA_IF_QUADF(template void register_lbfgs<alpaqa::EigenConfigq>(py::module_ &);)