#include <guanaqo/quadmath/quadmath.hpp>

#include <pybind11/chrono.h>
#include <pybind11/eigen.h>
#include <pybind11/gil.h>
#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace py::literals;

#include <chrono>
#include <exception>
#include <future>
#include <stdexcept>
using namespace std::chrono_literals;

#include <alpaqa/implementation/inner/panoc.tpp>
#include <alpaqa/implementation/outer/alm.tpp>
#include <alpaqa/inner/directions/panoc/structured-lbfgs.hpp>
#include <alpaqa/inner/panoc.hpp>
#include <alpaqa/outer/alm.hpp>
#include <alpaqa/util/check-dim.hpp>

#include "type-erased-alm-solver.hpp"
#include <dict/kwargs-to-struct.hpp>
#include <inner/type-erased-inner-solver.hpp>
#include <util/async.hpp>
#include <util/copy.hpp>
#include <util/member.hpp>

template <alpaqa::Config Conf>
void register_alm(py::module_ &m) {
    USING_ALPAQA_CONFIG(Conf);

    using TEProblem          = alpaqa::TypeErasedProblem<config_t>;
    using InnerSolver        = alpaqa::TypeErasedInnerSolver<config_t, TEProblem>;
    using DefaultInnerSolver = alpaqa::PANOCSolver<alpaqa::StructuredLBFGSDirection<config_t>>;

    using ALMSolver   = alpaqa::ALMSolver<InnerSolver>;
    using ALMParams   = alpaqa::ALMParams<config_t>;
    using TEALMSolver = alpaqa::TypeErasedALMSolver<config_t>;
#if ALPAQA_WITH_OCP
    using TEOCProblem    = alpaqa::TypeErasedControlProblem<config_t>;
    using InnerOCPSolver = alpaqa::TypeErasedInnerSolver<config_t, TEOCProblem>;
    using ALMOCPSolver   = alpaqa::ALMSolver<InnerOCPSolver>;
#endif
    register_dataclass<ALMParams>(m, "ALMParams",
                                  "C++ documentation: :cpp:class:`alpaqa::ALMParams`");

    py::class_<TEALMSolver> almsolver(m, "ALMSolver",
                                      "Main augmented Lagrangian solver.\n\n"
                                      "C++ documentation: :cpp:class:`alpaqa::ALMSolver`");
    default_copy_methods(almsolver);
    almsolver
        // Default constructor
        .def(py::init([] {
                 return std::make_unique<TEALMSolver>(
                     std::in_place_type<ALMSolver>, ALMParams{},
                     InnerSolver::template make<DefaultInnerSolver>(
                         alpaqa::PANOCParams<config_t>{}));
             }),
             "Build an ALM solver using Structured PANOC as inner solver.")
        // Solver only
        .def(py::init([](const InnerSolver &inner) {
                 return std::make_unique<TEALMSolver>(std::in_place_type<ALMSolver>, ALMParams{},
                                                      inner);
             }),
             "inner_solver"_a, "Build an ALM solver using the given inner solver.")
#if ALPAQA_WITH_OCP
        .def(py::init([](const InnerOCPSolver &inner) {
                 return std::make_unique<TEALMSolver>(std::in_place_type<ALMOCPSolver>, ALMParams{},
                                                      inner);
             }),
             "inner_solver"_a, "Build an ALM solver using the given inner solver.")
#endif
        // Params and solver
        .def(py::init([](params_or_dict<ALMParams> params, const InnerSolver &inner) {
                 return std::make_unique<TEALMSolver>(std::in_place_type<ALMSolver>,
                                                      var_kwargs_to_struct(params), inner);
             }),
             "alm_params"_a, "inner_solver"_a, "Build an ALM solver using the given inner solver.")
#if ALPAQA_WITH_OCP
        .def(py::init([](params_or_dict<ALMParams> params, const InnerOCPSolver &inner) {
                 return std::make_unique<TEALMSolver>(std::in_place_type<ALMOCPSolver>,
                                                      var_kwargs_to_struct(params), inner);
             }),
             "alm_params"_a, "inner_solver"_a, "Build an ALM solver using the given inner solver.")
#endif
        // Other functions and properties
        .def_property_readonly("inner_solver", &TEALMSolver::get_inner_solver)
        .def("__call__", &TEALMSolver::operator(), "problem"_a, "x"_a = std::nullopt,
             "y"_a = std::nullopt, py::kw_only{}, "asynchronous"_a = true,
             "suppress_interrupt"_a = false,
             "Solve.\n\n"
             ":param problem: Problem to solve.\n"
             ":param x: Initial guess for decision variables :math:`x`\n\n"
             ":param y: Initial guess for Lagrange multipliers :math:`y`\n"
             ":param asynchronous: Release the GIL and run the solver on a separate thread\n"
             ":param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, "
             "don't propagate this exception back to the Python interpreter, but stop the solver "
             "early, and return a solution with the status set to "
             ":py:data:`alpaqa.SolverStatus.Interrupted`.\n"
             ":return: * Solution :math:`x`\n"
             "         * Lagrange multipliers :math:`y` at the solution\n"
             "         * Statistics\n\n")
        .def("stop", &TEALMSolver::stop)
        .def_property_readonly("name", &TEALMSolver::get_name)
        .def("__str__", &TEALMSolver::get_name)
        .def_property_readonly("params", &TEALMSolver::get_params);
}

template void register_alm<alpaqa::EigenConfigd>(py::module_ &);
ALPAQA_IF_FLOAT(template void register_alm<alpaqa::EigenConfigf>(py::module_ &);)
ALPAQA_IF_LONGD(template void register_alm<alpaqa::EigenConfigl>(py::module_ &);)
ALPAQA_IF_QUADF(template void register_alm<alpaqa::EigenConfigq>(py::module_ &);)
