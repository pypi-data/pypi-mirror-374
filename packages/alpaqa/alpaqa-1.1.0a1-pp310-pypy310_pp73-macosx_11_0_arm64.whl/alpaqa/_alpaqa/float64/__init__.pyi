"""
Double precision
"""
from __future__ import annotations
import alpaqa._alpaqa
import datetime
import numpy
import typing
from . import functions
__all__: list[str] = ['ALMParams', 'ALMSolver', 'AndersonAccel', 'AndersonDirection', 'Box', 'BoxConstrProblem', 'CasADiProblem', 'ConvexNewtonDirection', 'DLProblem', 'FISTAParams', 'FISTAProgressInfo', 'FISTASolver', 'InnerSolveOptions', 'InnerSolver', 'KKTError', 'LBFGS', 'LBFGSDirection', 'LipschitzEstimateParams', 'NewtonTRDirection', 'NewtonTRDirectionParams', 'NoopDirection', 'PANOCDirection', 'PANOCParams', 'PANOCProgressInfo', 'PANOCSolver', 'PANTRDirection', 'PANTRParams', 'PANTRProgressInfo', 'PANTRSolver', 'Problem', 'ProblemWithCounters', 'SteihaugCGParams', 'StructuredLBFGSDirection', 'StructuredNewtonDirection', 'UnconstrProblem', 'ZeroFPRParams', 'ZeroFPRProgressInfo', 'ZeroFPRSolver', 'deserialize_casadi_problem', 'functions', 'kkt_error', 'load_casadi_problem', 'problem_with_counters', 'provided_functions', 'prox', 'prox_step']
M = typing.TypeVar("M", bound=int)
N = typing.TypeVar("N", bound=int)
class ALMParams:
    """
    C++ documentation: :cpp:class:`alpaqa::ALMParams`
    """
    dual_tolerance: float
    initial_penalty: float
    initial_penalty_factor: float
    initial_tolerance: float
    max_iter: int
    max_multiplier: float
    max_penalty: float
    max_time: datetime.timedelta
    min_penalty: float
    penalty_update_factor: float
    print_interval: int
    print_precision: int
    rel_penalty_increase_threshold: float
    single_penalty_factor: bool
    tolerance: float
    tolerance_update_factor: float
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class ALMSolver:
    """
    Main augmented Lagrangian solver.
    
    C++ documentation: :cpp:class:`alpaqa::ALMSolver`
    """
    def __call__(self, problem: Problem, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, *, asynchronous: bool = True, suppress_interrupt: bool = False) -> tuple:
        """
        Solve.
        
        :param problem: Problem to solve.
        :param x: Initial guess for decision variables :math:`x`
        
        :param y: Initial guess for Lagrange multipliers :math:`y`
        :param asynchronous: Release the GIL and run the solver on a separate thread
        :param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, don't propagate this exception back to the Python interpreter, but stop the solver early, and return a solution with the status set to :py:data:`alpaqa.SolverStatus.Interrupted`.
        :return: * Solution :math:`x`
                 * Lagrange multipliers :math:`y` at the solution
                 * Statistics
        """
    def __copy__(self) -> ALMSolver:
        ...
    def __deepcopy__(self, memo: dict) -> ALMSolver:
        ...
    @typing.overload
    def __init__(self, other: ALMSolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Build an ALM solver using Structured PANOC as inner solver.
        """
    @typing.overload
    def __init__(self, inner_solver: InnerSolver) -> None:
        """
        Build an ALM solver using the given inner solver.
        """
    @typing.overload
    def __init__(self, alm_params: ALMParams | dict, inner_solver: InnerSolver) -> None:
        """
        Build an ALM solver using the given inner solver.
        """
    def __str__(self) -> str:
        ...
    def stop(self) -> None:
        ...
    @property
    def inner_solver(self) -> typing.Any:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> typing.Any:
        ...
class AndersonAccel:
    """
    C++ documentation :cpp:class:`alpaqa::AndersonAccel`
    """
    class Params:
        """
        C++ documentation :cpp:class:`alpaqa::AndersonAccelParams`
        """
        memory: int
        min_div_fac: float
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    @typing.overload
    def __init__(self, params: AndersonAccel.Params | dict) -> None:
        ...
    @typing.overload
    def __init__(self, params: AndersonAccel.Params | dict, n: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @typing.overload
    def compute(self, g_k: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], r_k: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_k_aa: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def compute(self, g_k: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], r_k: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def initialize(self, g_0: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], r_0: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def reset(self) -> None:
        ...
    def resize(self, n: int) -> None:
        ...
    @property
    def Q(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        ...
    @property
    def R(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        ...
    @property
    def current_history(self) -> int:
        ...
    @property
    def history(self) -> int:
        ...
    @property
    def n(self) -> int:
        ...
    @property
    def params(self) -> AndersonAccel.Params:
        ...
class AndersonDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::AndersonDirection`
    """
    class DirectionParams:
        """
        C++ documentation: :cpp:class:`alpaqa::AndersonDirection::DirectionParams`
        """
        rescale_on_step_size_changes: bool
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    def __init__(self, anderson_params: AndersonAccel.Params | dict = {}, direction_params: AndersonDirection.DirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> tuple[AndersonAccel.Params, AndersonDirection.DirectionParams]:
        ...
class Box:
    """
    C++ documentation: :cpp:class:`alpaqa::Box`
    """
    lower: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]
    upper: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]
    def __copy__(self) -> Box:
        ...
    def __deepcopy__(self, memo: dict) -> Box:
        ...
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, other: Box) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, n: int) -> None:
        """
        Create an :math:`n`-dimensional box at with bounds at :math:`\\pm\\infty` (no constraints).
        """
    @typing.overload
    def __init__(self, *, lower: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], upper: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        """
        Create a box with the given bounds.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
class BoxConstrProblem:
    """
    C++ documentation: :cpp:class:`alpaqa::BoxConstrProblem`
    """
    def __copy__(self) -> BoxConstrProblem:
        ...
    def __deepcopy__(self, memo: dict) -> BoxConstrProblem:
        ...
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, other: BoxConstrProblem) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, num_variables: int, num_constraints: int) -> None:
        """
        :param num_variables: Number of decision variables
        :param num_constraints: Number of constraints
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]) -> int:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], e: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_projection_multipliers(self, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], M: float) -> None:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_hat: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], p: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], float]:
        ...
    def get_general_bounds(self) -> Box:
        ...
    def get_variable_bounds(self) -> Box:
        ...
    def resize(self, num_variables: int, num_constraints: int) -> None:
        ...
    @property
    def general_bounds(self) -> Box:
        """
        General constraint bounds, :math:`g(x) \\in D`
        """
    @general_bounds.setter
    def general_bounds(self, arg0: Box) -> None:
        ...
    @property
    def l1_reg(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        :math:`\\ell_1` regularization on :math:`x`
        """
    @l1_reg.setter
    def l1_reg(self, arg0: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @property
    def num_constraints(self) -> int:
        """
        Number of general constraints :math:`m`, dimension of :math:`g(x)`
        """
    @property
    def num_variables(self) -> int:
        """
        Number of decision variables :math:`n`, dimension of :math:`x`
        """
    @property
    def penalty_alm_split(self) -> int:
        """
        Index between quadratic penalty and augmented Lagrangian constraints
        """
    @penalty_alm_split.setter
    def penalty_alm_split(self, arg0: int) -> None:
        ...
    @property
    def variable_bounds(self) -> Box:
        """
        Box constraints on the decision variables, :math:`x\\in C`
        """
    @variable_bounds.setter
    def variable_bounds(self, arg0: Box) -> None:
        ...
class CasADiProblem(BoxConstrProblem):
    """
    C++ documentation: :cpp:class:`alpaqa::CasADiProblem`
    
    See :py:class:`alpaqa.Problem` for the full documentation.
    """
    def __copy__(self) -> CasADiProblem:
        ...
    def __deepcopy__(self, memo: dict) -> CasADiProblem:
        ...
    def __init__(self, other: CasADiProblem) -> None:
        """
        Create a copy
        """
    def __str__(self) -> str:
        ...
    def check(self) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], ŷ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_augmented_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the augmented Lagrangian and its symmetry.
        """
    def eval_augmented_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], gx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_constraints_jacobian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Jacobian of the constraints and its symmetry.
        """
    def eval_grad_gi(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], i: int, grad_gi: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]) -> int:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_L: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the Lagrangian and its symmetry.
        """
    def eval_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_objective(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], e: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_projection_multipliers(self, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], M: float) -> None:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_hat: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], p: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], float]:
        ...
    def get_general_bounds(self) -> Box:
        ...
    def get_variable_bounds(self) -> Box:
        ...
    def provides_eval_augmented_lagrangian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_and_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_eval_constraints_jacobian(self) -> bool:
        ...
    def provides_eval_grad_gi(self) -> bool:
        ...
    def provides_eval_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_get_variable_bounds(self) -> bool:
        ...
    @property
    def num_constraints(self) -> int:
        """
        Number of general constraints, dimension of :math:`g(x)`
        """
    @property
    def num_variables(self) -> int:
        """
        Number of decision variables, dimension of :math:`x`
        """
    @property
    def param(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Parameter vector :math:`p` of the problem
        """
    @param.setter
    def param(self, arg1: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
class ConvexNewtonDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection`
    """
    class AcceleratorParams:
        """
        C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection::AcceleratorParams`
        """
        ldlt: bool
        ζ: float
        ν: float
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    class DirectionParams:
        """
        C++ documentation: :cpp:class:`alpaqa::ConvexNewtonDirection::DirectionParams`
        """
        hessian_vec_factor: float
        quadratic: bool
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    def __init__(self, newton_params: ConvexNewtonDirection.AcceleratorParams | dict = {}, direction_params: ConvexNewtonDirection.DirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> ConvexNewtonDirection.DirectionParams:
        ...
class DLProblem(BoxConstrProblem):
    """
    C++ documentation: :cpp:class:`alpaqa::dl::DLProblem`
    
    See :py:class:`alpaqa.Problem` for the full documentation.
    """
    def __copy__(self) -> DLProblem:
        ...
    def __deepcopy__(self, memo: dict) -> DLProblem:
        ...
    @typing.overload
    def __init__(self, so_filename: str, *args, function_name: str = 'register_alpaqa_problem', user_param_str: bool = False, **kwargs) -> None:
        """
        Load a problem from the given shared library file.
        By default, extra arguments are passed to the problem as a void pointer to a ``std::tuple<pybind11::args, pybind11::kwargs>``.
        If the keyword argument ``user_param_str=True`` is used, the ``args`` is converted to a list of strings, and passed as a void pointer to a ``std::span<std::string_view>``.
        """
    @typing.overload
    def __init__(self, other: DLProblem) -> None:
        """
        Create a copy
        """
    def __str__(self) -> str:
        ...
    def call_extra_func(self, name: str, *args, **kwargs) -> typing.Any:
        """
        Call the given extra member function registered by the problem, with the signature ``pybind11::object(pybind11::args, pybind11::kwargs)``.
        """
    def check(self) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], ŷ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_augmented_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the augmented Lagrangian and its symmetry.
        """
    def eval_augmented_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], gx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_constraints_jacobian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Jacobian of the constraints and its symmetry.
        """
    def eval_grad_gi(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], i: int, grad_gi: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]) -> int:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_L: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the Lagrangian and its symmetry.
        """
    def eval_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_objective(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    def eval_objective_and_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], g: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_objective_gradient_and_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_f: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], e: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_projection_multipliers(self, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], M: float) -> None:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_hat: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], p: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], float]:
        ...
    def get_general_bounds(self) -> Box:
        ...
    def get_variable_bounds(self) -> Box:
        ...
    def provides_eval_augmented_lagrangian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_and_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_eval_constraints_jacobian(self) -> bool:
        ...
    def provides_eval_grad_gi(self) -> bool:
        ...
    def provides_eval_inactive_indices_res_lna(self) -> bool:
        ...
    def provides_eval_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_eval_objective_and_constraints(self) -> bool:
        ...
    def provides_eval_objective_and_gradient(self) -> bool:
        ...
    def provides_eval_objective_gradient_and_constraints_gradient_product(self) -> bool:
        ...
    def provides_get_augmented_lagrangian_hessian_sparsity(self) -> bool:
        ...
    def provides_get_constraints_jacobian_sparsity(self) -> bool:
        ...
    def provides_get_general_bounds(self) -> bool:
        ...
    def provides_get_lagrangian_hessian_sparsity(self) -> bool:
        ...
    def provides_get_variable_bounds(self) -> bool:
        ...
    @property
    def num_constraints(self) -> int:
        """
        Number of general constraints, dimension of :math:`g(x)`
        """
    @property
    def num_variables(self) -> int:
        """
        Number of decision variables, dimension of :math:`x`
        """
class FISTAParams:
    """
    C++ documentation: :cpp:class:`alpaqa::FISTAParams`
    """
    L_max: float
    L_min: float
    Lipschitz: LipschitzEstimateParams
    disable_acceleration: bool
    max_iter: int
    max_no_progress: int
    max_time: datetime.timedelta
    print_interval: int
    print_precision: int
    quadratic_upperbound_tolerance_factor: float
    stop_crit: alpaqa._alpaqa.PANOCStopCrit
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class FISTAProgressInfo:
    """
    Data passed to the FISTA progress callback.
    
    C++ documentation: :cpp:class:`alpaqa::FISTAProgressInfo`
    """
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\\left\\|p\\right\\| / \\gamma`
        """
    @property
    def grad_ψ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective :math:`\\nabla\\psi(x)`
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective at x̂ :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def k(self) -> int:
        """
        Iteration
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\\left\\|p\\right\\|^2`
        """
    @property
    def p(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Projected gradient step :math:`p`
        """
    @property
    def params(self) -> FISTAParams:
        """
        Solver parameters
        """
    @property
    def problem(self) -> Problem:
        """
        Problem being solved
        """
    @property
    def status(self) -> alpaqa._alpaqa.SolverStatus:
        """
        Current solver status
        """
    @property
    def t(self) -> float:
        """
        Acceleration parameter :math:`t`
        """
    @property
    def x(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable :math:`x`
        """
    @property
    def x_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable after projected gradient step :math:`\\hat x`
        """
    @property
    def y(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Lagrange multipliers :math:`y`
        """
    @property
    def y_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Candidate updated multipliers at x̂ :math:`\\hat y(\\hat x)`
        """
    @property
    def Σ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Penalty factor :math:`\\Sigma`
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\\gamma`
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\\varepsilon_k`
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\\varphi_\\gamma(x)`
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\\psi(x)`
        """
    @property
    def ψ_hat(self) -> float:
        """
        Objective at x̂ :math:`\\psi(\\hat x)`
        """
class FISTASolver:
    """
    C++ documentation: :cpp:class:`alpaqa::FISTASolver`
    """
    Params = FISTAParams
    def __call__(self, problem: Problem, opts: InnerSolveOptions = {}, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, *, asynchronous: bool = True, suppress_interrupt: bool = False) -> tuple:
        """
        Solve the given problem.
        
        :param problem: Problem to solve
        :param opts: Options (such as desired tolerance)
        :param x: Optional initial guess for the decision variables
        :param y: Lagrange multipliers (when used as ALM inner solver)
        :param Σ: Penalty factors (when used as ALM inner solver)
        :param asynchronous: Release the GIL and run the solver on a separate thread
        :param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, don't propagate this exception back to the Python interpreter, but stop the solver early, and return a solution with the status set to :py:data:`alpaqa.SolverStatus.Interrupted`.
        :return: * Solution :math:`x`
                 * Updated Lagrange multipliers (only if parameter ``y`` was not ``None``)
                 * Constraint violation (only if parameter ``y`` was not ``None``)
                 * Statistics
        """
    def __copy__(self) -> FISTASolver:
        ...
    def __deepcopy__(self, memo: dict) -> FISTASolver:
        ...
    @typing.overload
    def __init__(self, other: FISTASolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, fista_params: FISTAParams | dict = {}) -> None:
        """
        Create a FISTA solver using structured L-BFGS directions.
        """
    def __str__(self) -> str:
        ...
    def set_progress_callback(self, callback: typing.Callable[[FISTAProgressInfo], None]) -> FISTASolver:
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    def stop(self) -> None:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> FISTAParams:
        ...
class InnerSolveOptions:
    always_overwrite_results: bool
    max_time: datetime.timedelta | None
    tolerance: float
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class InnerSolver:
    def __copy__(self) -> InnerSolver:
        ...
    def __deepcopy__(self, memo: dict) -> InnerSolver:
        ...
    @typing.overload
    def __init__(self, other: InnerSolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, inner_solver: PANOCSolver) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, inner_solver: FISTASolver) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, inner_solver: ZeroFPRSolver) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, inner_solver: PANTRSolver) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, arg0: typing.Any) -> None:
        ...
    def __str__(self) -> str:
        ...
    def stop(self) -> None:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> typing.Any:
        ...
class KKTError:
    """
    C++ documentation: :cpp:class:`alpaqa::KKTError`
    """
    bounds_violation: float
    complementarity: float
    constr_violation: float
    stationarity: float
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
class LBFGS:
    """
    C++ documentation :cpp:class:`alpaqa::LBFGS`
    """
    class Params:
        """
        C++ documentation :cpp:class:`alpaqa::LBFGSParams`
        """
        class CBFGS:
            """
            C++ documentation :cpp:class:`alpaqa::CBFGSParams`
            """
            α: float
            ϵ: float
            @typing.overload
            def __init__(self, params: dict) -> None:
                ...
            @typing.overload
            def __init__(self, **kwargs) -> None:
                ...
            def to_dict(self) -> dict:
                ...
        cbfgs: LBFGS.Params.CBFGS
        force_pos_def: bool
        memory: int
        min_abs_s: float
        min_div_fac: float
        stepsize: alpaqa._alpaqa.LBFGSStepsize
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    class Sign:
        """
        C++ documentation :cpp:enum:`alpaqa::LBFGS::Sign`
        
        Members:
        
          Positive
        
          Negative
        """
        Negative: typing.ClassVar[LBFGS.Sign]  # value = <Sign.Negative: 1>
        Positive: typing.ClassVar[LBFGS.Sign]  # value = <Sign.Positive: 0>
        __members__: typing.ClassVar[dict[str, LBFGS.Sign]]  # value = {'Positive': <Sign.Positive: 0>, 'Negative': <Sign.Negative: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    Negative: typing.ClassVar[LBFGS.Sign]  # value = <Sign.Negative: 1>
    Positive: typing.ClassVar[LBFGS.Sign]  # value = <Sign.Positive: 0>
    @staticmethod
    def update_valid(params: LBFGS.Params, yᵀs: float, sᵀs: float, pᵀp: float) -> bool:
        ...
    @typing.overload
    def __init__(self, params: LBFGS.Params | dict) -> None:
        ...
    @typing.overload
    def __init__(self, params: LBFGS.Params | dict, n: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    def apply(self, q: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], γ: float) -> bool:
        ...
    def apply_masked(self, q: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], γ: float, J: list[int]) -> bool:
        ...
    def current_history(self) -> int:
        ...
    def reset(self) -> None:
        ...
    def resize(self, n: int) -> None:
        ...
    def s(self, i: int) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def scale_y(self, factor: float) -> None:
        ...
    def update(self, xk: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], xkp1: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], pk: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], pkp1: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], sign: LBFGS.Sign = LBFGS.Sign.Positive, forced: bool = False) -> bool:
        ...
    def update_sy(self, sk: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], yk: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], pkp1Tpkp1: float, forced: bool = False) -> bool:
        ...
    def y(self, i: int) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def α(self, i: int) -> float:
        ...
    def ρ(self, i: int) -> float:
        ...
    @property
    def n(self) -> int:
        ...
    @property
    def params(self) -> LBFGS.Params:
        ...
class LBFGSDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::LBFGSDirection`
    """
    class DirectionParams:
        """
        C++ documentation: :cpp:class:`alpaqa::LBFGSDirection::DirectionParams`
        """
        rescale_on_step_size_changes: bool
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    def __init__(self, lbfgs_params: LBFGS.Params | dict = {}, direction_params: LBFGSDirection.DirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> tuple[LBFGS.Params, LBFGSDirection.DirectionParams]:
        ...
class LipschitzEstimateParams:
    """
    C++ documentation: :cpp:class:`alpaqa::LipschitzEstimateParams`
    """
    L_0: float
    Lγ_factor: float
    δ: float
    ε: float
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class NewtonTRDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::NewtonTRDirection`
    """
    def __init__(self, accelerator_params: SteihaugCGParams | dict = {}, direction_params: NewtonTRDirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> tuple[SteihaugCGParams, NewtonTRDirectionParams]:
        ...
class NewtonTRDirectionParams:
    """
    C++ documentation: :cpp:class:`alpaqa::NewtonTRDirectionParams`
    """
    finite_diff: bool
    finite_diff_stepsize: float
    hessian_vec_factor: float
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class NoopDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::NoopDirection`
    """
    AcceleratorParams = None
    DirectionParams = None
    params = None
    def __init__(self) -> None:
        ...
    def __str__(self) -> str:
        ...
class PANOCDirection:
    @typing.overload
    def __init__(self, direction: NoopDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: LBFGSDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: StructuredLBFGSDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: StructuredNewtonDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: ConvexNewtonDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: AndersonDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: typing.Any) -> None:
        """
        Explicit conversion from a custom Python class.
        """
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> typing.Any:
        ...
class PANOCParams:
    """
    C++ documentation: :cpp:class:`alpaqa::PANOCParams`
    """
    L_max: float
    L_min: float
    Lipschitz: LipschitzEstimateParams
    eager_gradient_eval: bool
    force_linesearch: bool
    linesearch_coefficient_update_factor: float
    linesearch_strictness_factor: float
    linesearch_tolerance_factor: float
    max_iter: int
    max_no_progress: int
    max_time: datetime.timedelta
    min_linesearch_coefficient: float
    print_interval: int
    print_precision: int
    quadratic_upperbound_tolerance_factor: float
    recompute_last_prox_step_after_stepsize_change: bool
    stop_crit: alpaqa._alpaqa.PANOCStopCrit
    update_direction_in_candidate: bool
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class PANOCProgressInfo:
    """
    Data passed to the PANOC progress callback.
    
    C++ documentation: :cpp:class:`alpaqa::PANOCProgressInfo`
    """
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\\left\\|p\\right\\| / \\gamma`
        """
    @property
    def grad_ψ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective :math:`\\nabla\\psi(x)`
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective at x̂ :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def k(self) -> int:
        """
        Iteration
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\\left\\|p\\right\\|^2`
        """
    @property
    def p(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Projected gradient step :math:`p`
        """
    @property
    def params(self) -> PANOCParams:
        """
        Solver parameters
        """
    @property
    def problem(self) -> Problem:
        """
        Problem being solved
        """
    @property
    def q(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Previous quasi-Newton step :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def status(self) -> alpaqa._alpaqa.SolverStatus:
        """
        Current solver status
        """
    @property
    def x(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable :math:`x`
        """
    @property
    def x_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable after projected gradient step :math:`\\hat x`
        """
    @property
    def y(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Lagrange multipliers :math:`y`
        """
    @property
    def y_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Candidate updated multipliers at x̂ :math:`\\hat y(\\hat x)`
        """
    @property
    def Σ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Penalty factor :math:`\\Sigma`
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\\gamma`
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\\varepsilon_k`
        """
    @property
    def τ(self) -> float:
        """
        Previous line search parameter :math:`\\tau`
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\\varphi_\\gamma(x)`
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\\psi(x)`
        """
    @property
    def ψ_hat(self) -> float:
        """
        Objective at x̂ :math:`\\psi(\\hat x)`
        """
class PANOCSolver:
    """
    C++ documentation: :cpp:class:`alpaqa::PANOCSolver`
    """
    Params = PANOCParams
    def __call__(self, problem: Problem, opts: InnerSolveOptions = {}, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, *, asynchronous: bool = True, suppress_interrupt: bool = False) -> tuple:
        """
        Solve the given problem.
        
        :param problem: Problem to solve
        :param opts: Options (such as desired tolerance)
        :param x: Optional initial guess for the decision variables
        :param y: Lagrange multipliers (when used as ALM inner solver)
        :param Σ: Penalty factors (when used as ALM inner solver)
        :param asynchronous: Release the GIL and run the solver on a separate thread
        :param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, don't propagate this exception back to the Python interpreter, but stop the solver early, and return a solution with the status set to :py:data:`alpaqa.SolverStatus.Interrupted`.
        :return: * Solution :math:`x`
                 * Updated Lagrange multipliers (only if parameter ``y`` was not ``None``)
                 * Constraint violation (only if parameter ``y`` was not ``None``)
                 * Statistics
        """
    def __copy__(self) -> PANOCSolver:
        ...
    def __deepcopy__(self, memo: dict) -> PANOCSolver:
        ...
    @typing.overload
    def __init__(self, other: PANOCSolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, panoc_params: PANOCParams | dict = {}, lbfgs_params: LBFGS.Params | dict = {}, direction_params: StructuredLBFGSDirection.DirectionParams | dict = {}) -> None:
        """
        Create a PANOC solver using structured L-BFGS directions.
        """
    @typing.overload
    def __init__(self, panoc_params: PANOCParams | dict, direction: PANOCDirection) -> None:
        """
        Create a PANOC solver using a custom direction.
        """
    def __str__(self) -> str:
        ...
    def set_progress_callback(self, callback: typing.Callable[[PANOCProgressInfo], None]) -> PANOCSolver:
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    def stop(self) -> None:
        ...
    @property
    def direction(self) -> PANOCDirection:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> PANOCParams:
        ...
class PANTRDirection:
    @typing.overload
    def __init__(self, direction: NewtonTRDirection) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, direction: typing.Any) -> None:
        """
        Explicit conversion from a custom Python class.
        """
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> typing.Any:
        ...
class PANTRParams:
    """
    C++ documentation: :cpp:class:`alpaqa::PANTRParams`
    """
    L_max: float
    L_min: float
    Lipschitz: LipschitzEstimateParams
    TR_tolerance_factor: float
    compute_ratio_using_new_stepsize: bool
    disable_acceleration: bool
    initial_radius: float
    max_iter: int
    max_no_progress: int
    max_time: datetime.timedelta
    min_radius: float
    print_interval: int
    print_precision: int
    quadratic_upperbound_tolerance_factor: float
    radius_factor_acceptable: float
    radius_factor_good: float
    radius_factor_rejected: float
    ratio_approx_fbe_quadratic_model: bool
    ratio_threshold_acceptable: float
    ratio_threshold_good: float
    recompute_last_prox_step_after_direction_reset: bool
    stop_crit: alpaqa._alpaqa.PANOCStopCrit
    update_direction_on_prox_step: bool
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class PANTRProgressInfo:
    """
    Data passed to the PANTR progress callback.
    
    C++ documentation: :cpp:class:`alpaqa::PANTRProgressInfo`
    """
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\\left\\|p\\right\\| / \\gamma`
        """
    @property
    def grad_ψ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective :math:`\\nabla\\psi(x)`
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective at x̂ :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def k(self) -> int:
        """
        Iteration
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\\left\\|p\\right\\|^2`
        """
    @property
    def p(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Projected gradient step :math:`p`
        """
    @property
    def params(self) -> PANTRParams:
        """
        Solver parameters
        """
    @property
    def problem(self) -> Problem:
        """
        Problem being solved
        """
    @property
    def q(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Previous quasi-Newton step :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def status(self) -> alpaqa._alpaqa.SolverStatus:
        """
        Current solver status
        """
    @property
    def x(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable :math:`x`
        """
    @property
    def x_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable after projected gradient step :math:`\\hat x`
        """
    @property
    def y(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Lagrange multipliers :math:`y`
        """
    @property
    def y_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Candidate updated multipliers at x̂ :math:`\\hat y(\\hat x)`
        """
    @property
    def Δ(self) -> float:
        """
        Previous trust radius :math:`\\Delta`
        """
    @property
    def Σ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Penalty factor :math:`\\Sigma`
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\\gamma`
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\\varepsilon_k`
        """
    @property
    def ρ(self) -> float:
        """
        Previous decrease ratio :math:`\\rho`
        """
    @property
    def τ(self) -> float:
        """
        Acceptance (1) or rejection (0) of previous accelerated step :math:`\\tau`
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\\varphi_\\gamma(x)`
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\\psi(x)`
        """
    @property
    def ψ_hat(self) -> float:
        """
        Objective at x̂ :math:`\\psi(\\hat x)`
        """
class PANTRSolver:
    """
    C++ documentation: :cpp:class:`alpaqa::PANTRSolver`
    """
    Params = PANTRParams
    def __call__(self, problem: Problem, opts: InnerSolveOptions = {}, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, *, asynchronous: bool = True, suppress_interrupt: bool = False) -> tuple:
        """
        Solve the given problem.
        
        :param problem: Problem to solve
        :param opts: Options (such as desired tolerance)
        :param x: Optional initial guess for the decision variables
        :param y: Lagrange multipliers (when used as ALM inner solver)
        :param Σ: Penalty factors (when used as ALM inner solver)
        :param asynchronous: Release the GIL and run the solver on a separate thread
        :param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, don't propagate this exception back to the Python interpreter, but stop the solver early, and return a solution with the status set to :py:data:`alpaqa.SolverStatus.Interrupted`.
        :return: * Solution :math:`x`
                 * Updated Lagrange multipliers (only if parameter ``y`` was not ``None``)
                 * Constraint violation (only if parameter ``y`` was not ``None``)
                 * Statistics
        """
    def __copy__(self) -> PANTRSolver:
        ...
    def __deepcopy__(self, memo: dict) -> PANTRSolver:
        ...
    @typing.overload
    def __init__(self, other: PANTRSolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, pantr_params: PANTRParams | dict = {}, steihaug_params: SteihaugCGParams | dict = {}, direction_params: NewtonTRDirectionParams | dict = {}) -> None:
        """
        Create a PANTR solver using a structured Newton CG subproblem solver.
        """
    @typing.overload
    def __init__(self, pantr_params: PANTRParams | dict, direction: PANTRDirection) -> None:
        """
        Create a PANTR solver using a custom direction.
        """
    def __str__(self) -> str:
        ...
    def set_progress_callback(self, callback: typing.Callable[[PANTRProgressInfo], None]) -> PANTRSolver:
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    def stop(self) -> None:
        ...
    @property
    def direction(self) -> PANTRDirection:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> PANTRParams:
        ...
class Problem:
    """
    C++ documentation: :cpp:class:`alpaqa::TypeErasedProblem`
    """
    def __copy__(self) -> Problem:
        ...
    def __deepcopy__(self, memo: dict) -> Problem:
        ...
    @typing.overload
    def __init__(self, other: Problem) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, problem: CasADiProblem) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, problem: DLProblem) -> None:
        """
        Explicit conversion.
        """
    @typing.overload
    def __init__(self, problem: typing.Any) -> None:
        """
        Explicit conversion from a custom Python class.
        """
    def __str__(self) -> str:
        ...
    def check(self) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], ŷ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_augmented_lagrangian_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[float, numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]]:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_m: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_augmented_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_augmented_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the augmented Lagrangian and its symmetry.
        """
    def eval_augmented_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], gx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_constraints_jacobian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Jacobian of the constraints and its symmetry.
        """
    def eval_grad_gi(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], i: int, grad_gi: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]) -> int:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_L: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], work_n: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_lagrangian_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_lagrangian_hessian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float = 1.0) -> tuple[typing.Any, alpaqa._alpaqa.Symmetry]:
        """
        Returns the Hessian of the Lagrangian and its symmetry.
        """
    def eval_lagrangian_hessian_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], scale: float, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], Hv: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_objective(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    def eval_objective_and_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], g: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_objective_and_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_fx: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_objective_gradient(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_objective_gradient_and_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_f: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], e: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_projection_multipliers(self, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], M: float) -> None:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_hat: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], p: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], float]:
        ...
    def get_general_bounds(self) -> Box:
        ...
    def get_variable_bounds(self) -> Box:
        ...
    def provides_check(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_and_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_augmented_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_eval_constraints_jacobian(self) -> bool:
        ...
    def provides_eval_grad_gi(self) -> bool:
        ...
    def provides_eval_inactive_indices_res_lna(self) -> bool:
        ...
    def provides_eval_lagrangian_gradient(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian(self) -> bool:
        ...
    def provides_eval_lagrangian_hessian_product(self) -> bool:
        ...
    def provides_eval_objective_and_constraints(self) -> bool:
        ...
    def provides_eval_objective_and_gradient(self) -> bool:
        ...
    def provides_eval_objective_gradient_and_constraints_gradient_product(self) -> bool:
        ...
    def provides_get_augmented_lagrangian_hessian_sparsity(self) -> bool:
        ...
    def provides_get_constraints_jacobian_sparsity(self) -> bool:
        ...
    def provides_get_general_bounds(self) -> bool:
        ...
    def provides_get_lagrangian_hessian_sparsity(self) -> bool:
        ...
    def provides_get_variable_bounds(self) -> bool:
        ...
    @property
    def num_constraints(self) -> int:
        """
        Number of general constraints, dimension of :math:`g(x)`
        """
    @property
    def num_variables(self) -> int:
        """
        Number of decision variables, dimension of :math:`x`
        """
class ProblemWithCounters:
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
    @property
    def evaluations(self) -> alpaqa._alpaqa.EvalCounter:
        ...
    @property
    def problem(self) -> Problem:
        ...
class SteihaugCGParams:
    """
    C++ documentation: :cpp:class:`alpaqa::SteihaugCGParams`
    """
    max_iter_factor: float
    tol_max: float
    tol_scale: float
    tol_scale_root: float
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class StructuredLBFGSDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::StructuredLBFGSDirection`
    """
    class DirectionParams:
        """
        C++ documentation: :cpp:class:`alpaqa::StructuredLBFGSDirection::DirectionParams`
        """
        full_augmented_hessian: bool
        hessian_vec_factor: float
        hessian_vec_finite_differences: bool
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    def __init__(self, lbfgs_params: LBFGS.Params | dict = {}, direction_params: StructuredLBFGSDirection.DirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> tuple[LBFGS.Params, StructuredLBFGSDirection.DirectionParams]:
        ...
class StructuredNewtonDirection:
    """
    C++ documentation: :cpp:class:`alpaqa::StructuredNewtonDirection`
    """
    class DirectionParams:
        """
        C++ documentation: :cpp:class:`alpaqa::StructuredNewtonDirection::DirectionParams`
        """
        hessian_vec_factor: float
        @typing.overload
        def __init__(self, params: dict) -> None:
            ...
        @typing.overload
        def __init__(self, **kwargs) -> None:
            ...
        def to_dict(self) -> dict:
            ...
    def __init__(self, direction_params: StructuredNewtonDirection.DirectionParams | dict = {}) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def params(self) -> StructuredNewtonDirection.DirectionParams:
        ...
class UnconstrProblem:
    """
    C++ documentation: :cpp:class:`alpaqa::UnconstrProblem`
    """
    def __copy__(self) -> UnconstrProblem:
        ...
    def __deepcopy__(self, memo: dict) -> UnconstrProblem:
        ...
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, other: UnconstrProblem) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, num_variables: int) -> None:
        """
        :param num_variables: Number of decision variables
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def eval_constraints(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], g: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_constraints_gradient_product(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_gxy: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_constraints_jacobian(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J_values: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def eval_grad_gi(self, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], i: int, grad_gi: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], J: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]) -> int:
        ...
    @typing.overload
    def eval_inactive_indices_res_lna(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.int64]]:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], e: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def eval_projecting_difference_constraints(self, z: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def eval_projection_multipliers(self, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], M: float) -> None:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], x_hat: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], p: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> float:
        ...
    @typing.overload
    def eval_proximal_gradient_step(self, γ: float, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], grad_ψ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> tuple[numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], float]:
        ...
    def resize(self, num_variables: int) -> None:
        ...
    @property
    def num_constraints(self) -> int:
        """
        Number of general constraints, dimension of :math:`g(x)`
        """
    @property
    def num_variables(self) -> int:
        """
        Number of decision variables, dimension of :math:`x`
        """
class ZeroFPRParams:
    """
    C++ documentation: :cpp:class:`alpaqa::ZeroFPRParams`
    """
    L_max: float
    L_min: float
    Lipschitz: LipschitzEstimateParams
    force_linesearch: bool
    linesearch_strictness_factor: float
    linesearch_tolerance_factor: float
    max_iter: int
    max_no_progress: int
    max_time: datetime.timedelta
    min_linesearch_coefficient: float
    print_interval: int
    print_precision: int
    quadratic_upperbound_tolerance_factor: float
    recompute_last_prox_step_after_stepsize_change: bool
    stop_crit: alpaqa._alpaqa.PANOCStopCrit
    update_direction_from_prox_step: bool
    update_direction_in_accel: bool
    update_direction_in_candidate: bool
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class ZeroFPRProgressInfo:
    """
    Data passed to the ZeroFPR progress callback.
    
    C++ documentation: :cpp:class:`alpaqa::ZeroFPRProgressInfo`
    """
    @staticmethod
    def __init__(*args, **kwargs):
        """
        --
        
        Initialize self. See help(type(self)) for accurate signature.
        """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\\left\\|p\\right\\| / \\gamma`
        """
    @property
    def grad_ψ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective :math:`\\nabla\\psi(x)`
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Gradient of objective at x̂ :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def k(self) -> int:
        """
        Iteration
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\\left\\|p\\right\\|^2`
        """
    @property
    def p(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Projected gradient step :math:`p`
        """
    @property
    def params(self) -> ZeroFPRParams:
        """
        Solver parameters
        """
    @property
    def problem(self) -> Problem:
        """
        Problem being solved
        """
    @property
    def q(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Previous quasi-Newton step :math:`\\nabla\\psi(\\hat x)`
        """
    @property
    def status(self) -> alpaqa._alpaqa.SolverStatus:
        """
        Current solver status
        """
    @property
    def x(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable :math:`x`
        """
    @property
    def x_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Decision variable after projected gradient step :math:`\\hat x`
        """
    @property
    def y(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Lagrange multipliers :math:`y`
        """
    @property
    def y_hat(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Candidate updated multipliers at x̂ :math:`\\hat y(\\hat x)`
        """
    @property
    def Σ(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Penalty factor :math:`\\Sigma`
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\\gamma`
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\\varepsilon_k`
        """
    @property
    def τ(self) -> float:
        """
        Previous line search parameter :math:`\\tau`
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\\varphi_\\gamma(x)`
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\\psi(x)`
        """
    @property
    def ψ_hat(self) -> float:
        """
        Objective at x̂ :math:`\\psi(\\hat x)`
        """
class ZeroFPRSolver:
    """
    C++ documentation: :cpp:class:`alpaqa::ZeroFPRSolver`
    """
    Params = ZeroFPRParams
    def __call__(self, problem: Problem, opts: InnerSolveOptions = {}, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, Σ: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]] | None = None, *, asynchronous: bool = True, suppress_interrupt: bool = False) -> tuple:
        """
        Solve the given problem.
        
        :param problem: Problem to solve
        :param opts: Options (such as desired tolerance)
        :param x: Optional initial guess for the decision variables
        :param y: Lagrange multipliers (when used as ALM inner solver)
        :param Σ: Penalty factors (when used as ALM inner solver)
        :param asynchronous: Release the GIL and run the solver on a separate thread
        :param suppress_interrupt: If the solver is interrupted by a ``KeyboardInterrupt``, don't propagate this exception back to the Python interpreter, but stop the solver early, and return a solution with the status set to :py:data:`alpaqa.SolverStatus.Interrupted`.
        :return: * Solution :math:`x`
                 * Updated Lagrange multipliers (only if parameter ``y`` was not ``None``)
                 * Constraint violation (only if parameter ``y`` was not ``None``)
                 * Statistics
        """
    def __copy__(self) -> ZeroFPRSolver:
        ...
    def __deepcopy__(self, memo: dict) -> ZeroFPRSolver:
        ...
    @typing.overload
    def __init__(self, other: ZeroFPRSolver) -> None:
        """
        Create a copy
        """
    @typing.overload
    def __init__(self, zerofpr_params: ZeroFPRParams | dict = {}, lbfgs_params: LBFGS.Params | dict = {}, direction_params: StructuredLBFGSDirection.DirectionParams | dict = {}) -> None:
        """
        Create a ZeroFPR solver using structured L-BFGS directions.
        """
    @typing.overload
    def __init__(self, zerofpr_params: ZeroFPRParams | dict, direction: PANOCDirection) -> None:
        """
        Create a ZeroFPR solver using a custom direction.
        """
    def __str__(self) -> str:
        ...
    def set_progress_callback(self, callback: typing.Callable[[ZeroFPRProgressInfo], None]) -> ZeroFPRSolver:
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    def stop(self) -> None:
        ...
    @property
    def direction(self) -> PANOCDirection:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def params(self) -> ZeroFPRParams:
        ...
def deserialize_casadi_problem(functions: dict[str, str]) -> CasADiProblem:
    """
    Deserialize a CasADi problem from the given serialized functions.
    """
def kkt_error(problem: Problem, x: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], y: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> KKTError:
    ...
def load_casadi_problem(so_name: str) -> CasADiProblem:
    """
    Load a compiled CasADi problem.
    """
@typing.overload
def problem_with_counters(problem: CasADiProblem) -> ProblemWithCounters:
    """
    Wrap the problem to count all function evaluations.
    
    :param problem: The original problem to wrap. Copied.
    :return: * Wrapped problem.
             * Counters for wrapped problem.
    """
@typing.overload
def problem_with_counters(problem: DLProblem) -> ProblemWithCounters:
    """
    Wrap the problem to count all function evaluations.
    
    :param problem: The original problem to wrap. Copied.
    :return: * Wrapped problem.
             * Counters for wrapped problem.
    """
@typing.overload
def problem_with_counters(problem: typing.Any) -> ProblemWithCounters:
    ...
def provided_functions(problem: Problem) -> str:
    """
    Returns a string representing the functions provided by the problem.
    """
@typing.overload
def prox(self: functions.NuclearNorm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: functions.NuclearNorm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: functions.L1Norm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: functions.L1Norm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: functions.L1NormElementwise, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: functions.L1NormElementwise, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: Box, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox(self: Box, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox`
    Compute the proximal mapping of ``self`` at ``in`` with step size ``γ``. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox_step`
    """
@typing.overload
def prox_step(self: functions.NuclearNorm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: functions.NuclearNorm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: functions.L1Norm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: functions.L1Norm, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: functions.L1NormElementwise, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: functions.L1NormElementwise, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: Box, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], output_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> float:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version overwrites the given output arguments.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
@typing.overload
def prox_step(self: Box, input: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], input_step: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], γ: float = 1, γ_step: float = -1) -> tuple[float, numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]]:
    """
    C++ documentation: :cpp:var:`alpaqa::prox_step`
    Compute a generalized forward-backward step. This version returns the outputs as a tuple.
    
    .. seealso:: :py:func:`alpaqa.prox`
    """
