#include <alpaqa/config/config.hpp>
#include <guanaqo/not-implemented.hpp>
#include <alpaqa-version.h>

#include <pybind11/pybind11.h>
namespace py = pybind11;
using namespace py::literals;

void register_misc(py::module_ &m);
void register_counters(py::module_ &m);
void register_enums(py::module_ &m);

template <alpaqa::Config Conf>
void register_problems(py::module_ &m);

template <alpaqa::Config Conf>
void register_inner_solver(py::module_ &m);

template <alpaqa::Config Conf>
void register_lbfgs(py::module_ &m);

template <alpaqa::Config Conf>
void register_anderson(py::module_ &m);

template <alpaqa::Config Conf>
void register_panoc_directions(py::module_ &m);

template <alpaqa::Config Conf>
void register_pantr_directions(py::module_ &m);

template <alpaqa::Config Conf>
void register_panoc(py::module_ &m);

template <alpaqa::Config Conf>
void register_fista(py::module_ &m);

template <alpaqa::Config Conf>
void register_zerofpr(py::module_ &m);

template <alpaqa::Config Conf>
void register_pantr(py::module_ &m);

template <alpaqa::Config Conf>
void register_alm(py::module_ &m);

template <alpaqa::Config Conf>
void register_prox(py::module_ &m);

#if ALPAQA_WITH_OCP
template <alpaqa::Config Conf>
void register_control_problems(py::module_ &m);

template <alpaqa::Config Conf>
void register_panoc_ocp(py::module_ &m);

template <alpaqa::Config Conf>
void register_ocp(py::module_ &m);
#else
template <alpaqa::Config Conf>
void register_control_problems(py::module_ &) {}

template <alpaqa::Config Conf>
void register_panoc_ocp(py::module_ &) {}

template <alpaqa::Config Conf>
void register_ocp(py::module_ &) {}
#endif

#if ALPAQA_WITH_LBFGSB
template <alpaqa::Config Conf>
void register_lbfgsb(py::module_ &m);
#else
template <alpaqa::Config Conf>
void register_lbfgsb(py::module_ &) {}
#endif

template <alpaqa::Config Conf>
void register_python_inner_solver(py::module_ &m);

#if ALPAQA_WITH_IPOPT
void register_ipopt(py::module_ &m);
#else
void register_ipopt(py::module_ &) {}
#endif

template <alpaqa::Config Conf>
void register_classes_for(py::module_ &m) {
    register_problems<Conf>(m);
    register_control_problems<Conf>(m);
    register_inner_solver<Conf>(m);
    register_lbfgs<Conf>(m);
    register_anderson<Conf>(m);
    register_panoc_directions<Conf>(m);
    register_pantr_directions<Conf>(m);
    register_panoc<Conf>(m);
    register_fista<Conf>(m);
    register_lbfgsb<Conf>(m);
    register_panoc_ocp<Conf>(m);
    register_zerofpr<Conf>(m);
    register_pantr<Conf>(m);
    register_ocp<Conf>(m);
    register_alm<Conf>(m);
    register_prox<Conf>(m);
    register_python_inner_solver<Conf>(m);
}

PYBIND11_MODULE(MODULE_NAME, m) {
    m.doc()               = "Python interface to alpaqa's C++ implementation.";
    m.attr("__version__") = ALPAQA_VERSION_FULL;
    m.attr("build_time")  = ALPAQA_BUILD_TIME;
    m.attr("commit_hash") = ALPAQA_COMMIT_HASH;
#if ALPAQA_WITH_CASADI
    m.attr("with_casadi") = true;
#else
    m.attr("with_casadi") = false;
#endif
#if ALPAQA_WITH_EXTERNAL_CASADI
    m.attr("with_external_casadi") = true;
#else
    m.attr("with_external_casadi") = false;
#endif
#if ALPAQA_WITH_CASADI_OCP
    m.attr("with_casadi_ocp") = true;
#else
    m.attr("with_casadi_ocp") = false;
#endif
#if ALPAQA_WITH_IPOPT
    m.attr("with_ipopt") = true;
#else
    m.attr("with_ipopt") = false;
#endif

    py::register_exception<guanaqo::not_implemented_error>(m, "not_implemented_error",
                                                           PyExc_NotImplementedError);

    register_misc(m);
    register_counters(m);
    register_enums(m);

    auto m_double = m.def_submodule("float64", "Double precision");
    register_classes_for<alpaqa::EigenConfigd>(m_double);
    ALPAQA_IF_FLOAT(auto m_single = m.def_submodule("float32", "Single precision");
                    register_classes_for<alpaqa::EigenConfigf>(m_single);)
    ALPAQA_IF_LONGD(auto m_long_double = m.def_submodule("longdouble", "Long double precision");
                    register_classes_for<alpaqa::EigenConfigl>(m_long_double);)
    // Note: this is usually disabled because NumPy doesn't support it.
    ALPAQA_IF_QUADF(auto m_quad = m.def_submodule("float128", "Quadruple precision");
                    register_classes_for<alpaqa::EigenConfigq>(m_quad);)

    register_ipopt(m_double);
}
