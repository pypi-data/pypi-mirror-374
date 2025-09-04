#include <alpaqa/config/config.hpp>
#include <pybind11/attr.h>
#include <pybind11/eigen.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <variant>

namespace py = pybind11;
using namespace py::literals;

#include <alpaqa/problem/ocproblem.hpp>
#include <alpaqa/util/check-dim.hpp>
#if ALPAQA_WITH_CASADI_OCP
#include <alpaqa/casadi/CasADiControlProblem.hpp>
#endif

#include <util/copy.hpp>

template <alpaqa::Config Conf>
void register_control_problems(py::module_ &m) {
    USING_ALPAQA_CONFIG(Conf);
    using alpaqa::util::check_dim;

    using ControlProblem = alpaqa::TypeErasedControlProblem<config_t>;
    py::class_<ControlProblem> te_problem(
        m, "ControlProblem", "C++ documentation: :cpp:class:`alpaqa::TypeErasedControlProblem`");
    default_copy_methods(te_problem);

    // ProblemWithCounters
    struct ControlProblemWithCounters {
        ControlProblem problem;
        std::shared_ptr<alpaqa::OCPEvalCounter> evaluations;
    };
    py::class_<ControlProblemWithCounters>(m, "ControlProblemWithCounters")
        .def_readonly("problem", &ControlProblemWithCounters::problem)
        .def_readonly("evaluations", &ControlProblemWithCounters::evaluations);
    if constexpr (std::is_same_v<typename Conf::real_t, double>) {

#if ALPAQA_WITH_CASADI_OCP
        static constexpr auto te_pwc = []<class P>(P &&p) -> ControlProblemWithCounters {
            using PwC = alpaqa::ControlProblemWithCounters<P>;
            auto te_p = ControlProblem::template make<PwC>(std::forward<P>(p));
            auto eval = te_p.template as<PwC>().evaluations;
            return {std::move(te_p), std::move(eval)};
        };
        using CasADiControlProblem       = alpaqa::CasADiControlProblem<config_t>;
        auto load_CasADi_control_problem = [](const char *so_name, unsigned N) {
            return std::make_unique<CasADiControlProblem>(so_name, N);
        };
#else
        struct CasADiControlProblem {};
        auto load_CasADi_control_problem = [](const char *,
                                              unsigned) -> std::unique_ptr<CasADiControlProblem> {
            throw std::runtime_error(
                "This version of alpaqa was compiled without CasADi optimal control support");
        };
#endif

        py::class_<CasADiControlProblem> casadi_ctrl_prblm(
            m, "CasADiControlProblem",
            "C++ documentation: :cpp:class:`alpaqa::CasADiControlProblem`\n\n"
            "See :py:class:`alpaqa.ControlProblem` for the full documentation.");
        default_copy_methods(casadi_ctrl_prblm);
#if ALPAQA_WITH_CASADI_OCP
        casadi_ctrl_prblm //
            .def_readonly("N", &CasADiControlProblem::N)
            .def_readonly("nx", &CasADiControlProblem::nx)
            .def_readonly("nu", &CasADiControlProblem::nu)
            .def_readonly("nh", &CasADiControlProblem::nh)
            .def_readonly("nh_N", &CasADiControlProblem::nh_N)
            .def_readonly("nc", &CasADiControlProblem::nc)
            .def_readonly("nc_N", &CasADiControlProblem::nc_N)
            .def_readwrite("U", &CasADiControlProblem::U)
            .def_readwrite("D", &CasADiControlProblem::D)
            .def_readwrite("D_N", &CasADiControlProblem::D_N)
            .def_property(
                "x_init", [](CasADiControlProblem &p) -> rvec { return p.x_init; },
                [](CasADiControlProblem &p, crvec x_init) {
                    if (x_init.size() != p.x_init.size())
                        throw std::invalid_argument("Invalid x_init dimension: got " +
                                                    std::to_string(x_init.size()) + ", should be " +
                                                    std::to_string(p.x_init.size()) + ".");
                    p.x_init = x_init;
                },
                "Initial state vector :math:`x^0` of the problem")
            .def_property(
                "param", [](CasADiControlProblem &p) -> rvec { return p.param; },
                [](CasADiControlProblem &p, crvec param) {
                    if (param.size() != p.param.size())
                        throw std::invalid_argument("Invalid parameter dimension: got " +
                                                    std::to_string(param.size()) + ", should be " +
                                                    std::to_string(p.param.size()) + ".");
                    p.param = param;
                },
                "Parameter vector :math:`p` of the problem");

        te_problem.def(py::init<const CasADiControlProblem &>(), "problem"_a,
                       "Explicit conversion");
        py::implicitly_convertible<CasADiControlProblem, ControlProblem>();
#endif
        m.def("load_casadi_control_problem", load_CasADi_control_problem, "so_name"_a, "N"_a,
              "Load a compiled CasADi optimal control problem.\n\n");

#if ALPAQA_WITH_CASADI_OCP
        m.def(
            "control_problem_with_counters", [](CasADiControlProblem &p) { return te_pwc(p); },
            py::keep_alive<0, 1>(), "problem"_a,
            "Wrap the problem to count all function evaluations.\n\n"
            ":param problem: The original problem to wrap. Copied.\n"
            ":return: * Wrapped problem.\n"
            "         * Counters for wrapped problem.\n\n");
#endif
    }
}

template void register_control_problems<alpaqa::EigenConfigd>(py::module_ &);
ALPAQA_IF_FLOAT(template void register_control_problems<alpaqa::EigenConfigf>(py::module_ &);)
ALPAQA_IF_LONGD(template void register_control_problems<alpaqa::EigenConfigl>(py::module_ &);)
ALPAQA_IF_QUADF(template void register_control_problems<alpaqa::EigenConfigq>(py::module_ &);)
