#include <guanaqo/quadmath/quadmath.hpp>

#include <pybind11/chrono.h>
#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace py::literals;

#include <alpaqa/inner/directions/panoc/anderson.hpp>
#include <alpaqa/inner/directions/panoc/convex-newton.hpp>
#include <alpaqa/inner/directions/panoc/lbfgs.hpp>
#include <alpaqa/inner/directions/panoc/noop.hpp>
#include <alpaqa/inner/directions/panoc/structured-lbfgs.hpp>
#include <alpaqa/inner/directions/panoc/structured-newton.hpp>

#include <dict/kwargs-to-struct.hpp>
#include <dict/stats-to-dict.hpp>
#include <inner/type-erased-panoc-direction.hpp>

template <alpaqa::Config Conf>
void register_panoc_directions(py::module_ &m) {
    USING_ALPAQA_CONFIG(Conf);

    // ----------------------------------------------------------------------------------------- //
    using TypeErasedPANOCDirection = alpaqa::TypeErasedPANOCDirection<Conf>;
    py::class_<TypeErasedPANOCDirection> te_direction(m, "PANOCDirection");
    te_direction //
        .def_property_readonly("params", &TypeErasedPANOCDirection::template get_params<>)
        .def("__str__", &TypeErasedPANOCDirection::template get_name<>);

    // ----------------------------------------------------------------------------------------- //
    using NoopDir = alpaqa::NoopDirection<config_t>;

    py::class_<NoopDir> noop(m, "NoopDirection",
                             "C++ documentation: :cpp:class:`alpaqa::NoopDirection`");
    noop //
        .def(py::init())
        .def("__str__", &NoopDir::get_name);
    noop.attr("DirectionParams")   = py::none();
    noop.attr("AcceleratorParams") = py::none();
    noop.attr("params")            = py::none();

    te_direction.def(py::init(&alpaqa::erase_direction_with_params_dict<NoopDir, const NoopDir &>),
                     "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<NoopDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    using LBFGSDir       = alpaqa::LBFGSDirection<config_t>;
    using LBFGSParams    = alpaqa::LBFGSParams<config_t>;
    using LBFGSDirParams = alpaqa::LBFGSDirectionParams<config_t>;

    py::class_<LBFGSDir> lbfgs(m, "LBFGSDirection",
                               "C++ documentation: :cpp:class:`alpaqa::LBFGSDirection`");
    register_dataclass<LBFGSDirParams>(
        lbfgs, "DirectionParams",
        "C++ documentation: :cpp:class:`alpaqa::LBFGSDirection::DirectionParams`");
    lbfgs //
        .def(py::init([](params_or_dict<LBFGSParams> lbfgs_params,
                         params_or_dict<LBFGSDirParams> direction_params) {
                 return LBFGSDir{var_kwargs_to_struct(lbfgs_params),
                                 var_kwargs_to_struct(direction_params)};
             }),
             "lbfgs_params"_a = py::dict{}, "direction_params"_a = py::dict{})
        .def_property_readonly(
            "params",
            py::cpp_function(&LBFGSDir::get_params, py::return_value_policy::reference_internal))
        .def("__str__", &LBFGSDir::get_name);

    te_direction.def(
        py::init(&alpaqa::erase_direction_with_params_dict<LBFGSDir, const LBFGSDir &>),
        "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<LBFGSDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    using StructuredLBFGSDir  = alpaqa::StructuredLBFGSDirection<config_t>;
    using StrucLBFGSDirParams = alpaqa::StructuredLBFGSDirectionParams<config_t>;

    py::class_<StructuredLBFGSDir> struc_lbfgs(
        m, "StructuredLBFGSDirection",
        "C++ documentation: :cpp:class:`alpaqa::StructuredLBFGSDirection`");
    register_dataclass<StrucLBFGSDirParams>(
        struc_lbfgs, "DirectionParams",
        "C++ documentation: :cpp:class:`alpaqa::StructuredLBFGSDirection::DirectionParams`");
    struc_lbfgs //
        .def(py::init([](params_or_dict<LBFGSParams> lbfgs_params,
                         params_or_dict<StrucLBFGSDirParams> direction_params) {
                 return StructuredLBFGSDir{var_kwargs_to_struct(lbfgs_params),
                                           var_kwargs_to_struct(direction_params)};
             }),
             "lbfgs_params"_a = py::dict{}, "direction_params"_a = py::dict{})
        .def_property_readonly("params",
                               py::cpp_function(&StructuredLBFGSDir::get_params,
                                                py::return_value_policy::reference_internal))
        .def("__str__", &StructuredLBFGSDir::get_name);

    te_direction.def(
        py::init(&alpaqa::erase_direction_with_params_dict<StructuredLBFGSDir,
                                                           const StructuredLBFGSDir &>),
        "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<StructuredLBFGSDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    using StructuredNewtonDir  = alpaqa::StructuredNewtonDirection<config_t>;
    using StrucNewtonDirParams = alpaqa::StructuredNewtonDirectionParams<config_t>;

    py::class_<StructuredNewtonDir> struc_newton(
        m, "StructuredNewtonDirection",
        "C++ documentation: :cpp:class:`alpaqa::StructuredNewtonDirection`");
    register_dataclass<StrucNewtonDirParams>(
        struc_newton, "DirectionParams",
        "C++ documentation: :cpp:class:`alpaqa::StructuredNewtonDirection::DirectionParams`");
    struc_newton //
        .def(py::init([](params_or_dict<StrucNewtonDirParams> direction_params) {
                 return StructuredNewtonDir{{.direction = var_kwargs_to_struct(direction_params)}};
             }),
             "direction_params"_a = py::dict{})
        .def_property_readonly("params",
                               py::cpp_function(&StructuredNewtonDir::get_params,
                                                py::return_value_policy::reference_internal))
        .def("__str__", &StructuredNewtonDir::get_name);

    te_direction.def(
        py::init(&alpaqa::erase_direction_with_params_dict<StructuredNewtonDir,
                                                           const StructuredNewtonDir &>),
        "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<StructuredNewtonDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    using ConvexNewtonDir         = alpaqa::ConvexNewtonDirection<config_t>;
    using ConvexNewtonDirParams   = typename ConvexNewtonDir::DirectionParams;
    using ConvexNewtonAccelParams = typename ConvexNewtonDir::AcceleratorParams;

    py::class_<ConvexNewtonDir> convex_newton(
        m, "ConvexNewtonDirection",
        "C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection`");
    register_dataclass<ConvexNewtonDirParams>(
        convex_newton, "DirectionParams",
        "C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection::DirectionParams`");
    register_dataclass<ConvexNewtonAccelParams>(
        convex_newton, "AcceleratorParams",
        "C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection::AcceleratorParams`");
    convex_newton //
        .def(py::init([](params_or_dict<ConvexNewtonAccelParams> newton_params,
                         params_or_dict<ConvexNewtonDirParams> direction_params) {
                 return ConvexNewtonDir{{.accelerator = var_kwargs_to_struct(newton_params),
                                         .direction   = var_kwargs_to_struct(direction_params)}};
             }),
             "newton_params"_a = py::dict{}, "direction_params"_a = py::dict{})
        .def_property_readonly("params",
                               py::cpp_function(&ConvexNewtonDir::get_params,
                                                py::return_value_policy::reference_internal))
        .def("__str__", &ConvexNewtonDir::get_name);

    te_direction.def(
        py::init(
            &alpaqa::erase_direction_with_params_dict<ConvexNewtonDir, const ConvexNewtonDir &>),
        "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<ConvexNewtonDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    using AndersonDir       = alpaqa::AndersonDirection<config_t>;
    using AndersonParams    = alpaqa::AndersonAccelParams<config_t>;
    using AndersonDirParams = alpaqa::AndersonDirectionParams<config_t>;

    py::class_<AndersonDir> anderson(m, "AndersonDirection",
                                     "C++ documentation: :cpp:class:`alpaqa::AndersonDirection`");
    register_dataclass<AndersonDirParams>(
        anderson, "DirectionParams",
        "C++ documentation: :cpp:class:`alpaqa::AndersonDirection::DirectionParams`");
    anderson //
        .def(py::init([](params_or_dict<AndersonParams> anderson_params,
                         params_or_dict<AndersonDirParams> direction_params) {
                 return AndersonDir{var_kwargs_to_struct(anderson_params),
                                    var_kwargs_to_struct(direction_params)};
             }),
             "anderson_params"_a = py::dict{}, "direction_params"_a = py::dict{})
        .def_property_readonly(
            "params",
            py::cpp_function(&AndersonDir::get_params, py::return_value_policy::reference_internal))
        .def("__str__", &AndersonDir::get_name);

    te_direction.def(
        py::init(&alpaqa::erase_direction_with_params_dict<AndersonDir, const AndersonDir &>),
        "direction"_a, "Explicit conversion.");
    py::implicitly_convertible<AndersonDir, TypeErasedPANOCDirection>();

    // ----------------------------------------------------------------------------------------- //
    // Catch-all, must be last
    te_direction //
        .def(py::init([](py::object o) {
                 struct {
                     using Problem = alpaqa::TypeErasedProblem<Conf>;
                     void initialize(const Problem &problem, crvec y, crvec Σ, real_t γ_0,
                                     crvec x_0, crvec x̂_0, crvec p_0, crvec grad_ψx_0) {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         o.attr("initialize")(problem, y, Σ, γ_0, x_0, x̂_0, p_0, grad_ψx_0);
                     }
                     bool update(real_t γₖ, real_t γₙₑₓₜ, crvec xₖ, crvec xₙₑₓₜ, crvec pₖ,
                                 crvec pₙₑₓₜ, crvec grad_ψxₖ, crvec grad_ψxₙₑₓₜ) {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         return py::cast<bool>(o.attr("update")(γₖ, γₙₑₓₜ, xₖ, xₙₑₓₜ, pₖ, pₙₑₓₜ,
                                                                grad_ψxₖ, grad_ψxₙₑₓₜ));
                     }
                     bool has_initial_direction() const {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         return py::cast<bool>(o.attr("has_initial_direction")());
                     }
                     bool apply(real_t γₖ, crvec xₖ, crvec x̂ₖ, crvec pₖ, crvec grad_ψxₖ,
                                rvec qₖ) const {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         return py::cast<bool>(o.attr("apply")(γₖ, xₖ, x̂ₖ, pₖ, grad_ψxₖ, qₖ));
                     }
                     void changed_γ(real_t γₖ, real_t old_γₖ) {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         o.attr("changed_γ")(γₖ, old_γₖ);
                     }
                     void reset() {
                         alpaqa::ScopedMallocAllower ma;
                         py::gil_scoped_acquire gil;
                         o.attr("reset")();
                     }
                     std::string get_name() const {
                         py::gil_scoped_acquire gil;
                         return py::cast<std::string>(py::str(o));
                     }
                     py::object get_params() const {
                         py::gil_scoped_acquire gil;
                         return py::getattr(o, "params");
                     }

                     py::object o;
                 } s{std::move(o)};
                 return TypeErasedPANOCDirection{std::move(s)};
             }),
             "direction"_a, "Explicit conversion from a custom Python class.");
}

template void register_panoc_directions<alpaqa::EigenConfigd>(py::module_ &);
ALPAQA_IF_FLOAT(template void register_panoc_directions<alpaqa::EigenConfigf>(py::module_ &);)
ALPAQA_IF_LONGD(template void register_panoc_directions<alpaqa::EigenConfigl>(py::module_ &);)
ALPAQA_IF_QUADF(template void register_panoc_directions<alpaqa::EigenConfigq>(py::module_ &);)
