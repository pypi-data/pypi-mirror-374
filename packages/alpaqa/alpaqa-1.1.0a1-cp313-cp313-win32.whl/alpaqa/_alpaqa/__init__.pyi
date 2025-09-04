"""
Python interface to alpaqa's C++ implementation.
"""
from __future__ import annotations
import datetime
import typing
from . import float64
from . import longdouble
__all__: list[str] = ['ApproxKKT', 'ApproxKKT2', 'BasedOnCurvature', 'BasedOnExternalStepSize', 'Busy', 'Converged', 'DynamicLoadFlags', 'EvalCounter', 'FPRNorm', 'FPRNorm2', 'Interrupted', 'Ipopt', 'LBFGSBpp', 'LBFGSStepsize', 'Lower', 'MaxIter', 'MaxTime', 'NoProgress', 'NotFinite', 'OCPEvalCounter', 'PANOCStopCrit', 'ProjGradNorm', 'ProjGradNorm2', 'ProjGradUnitNorm', 'ProjGradUnitNorm2', 'SolverStatus', 'Symmetry', 'Unsymmetric', 'Upper', 'build_time', 'commit_hash', 'float64', 'longdouble', 'not_implemented_error', 'with_casadi', 'with_casadi_ocp', 'with_external_casadi', 'with_ipopt']
class DynamicLoadFlags:
    """
    C++ documentation: :cpp:class:`guanaqo::DynamicLoadFlags`
    """
    deepbind: bool
    global_: bool
    lazy: bool
    nodelete: bool
    @typing.overload
    def __init__(self, params: dict) -> None:
        ...
    @typing.overload
    def __init__(self, **kwargs) -> None:
        ...
    def to_dict(self) -> dict:
        ...
class EvalCounter:
    """
    C++ documentation: :cpp:class:`alpaqa::EvalCounter`
    
    """
    class EvalTimer:
        """
        C++ documentation: :cpp:class:`alpaqa::EvalCounter::EvalTimer`
        
        """
        augmented_lagrangian: datetime.timedelta
        augmented_lagrangian_and_gradient: datetime.timedelta
        augmented_lagrangian_gradient: datetime.timedelta
        augmented_lagrangian_hessian: datetime.timedelta
        augmented_lagrangian_hessian_product: datetime.timedelta
        constraints: datetime.timedelta
        constraints_gradient_product: datetime.timedelta
        constraints_jacobian: datetime.timedelta
        grad_gi: datetime.timedelta
        inactive_indices_res_lna: datetime.timedelta
        lagrangian_gradient: datetime.timedelta
        lagrangian_hessian: datetime.timedelta
        lagrangian_hessian_product: datetime.timedelta
        objective: datetime.timedelta
        objective_and_constraints: datetime.timedelta
        objective_and_gradient: datetime.timedelta
        objective_gradient: datetime.timedelta
        objective_gradient_and_constraints_gradient_product: datetime.timedelta
        projecting_difference_constraints: datetime.timedelta
        projection_multipliers: datetime.timedelta
        proximal_gradient_step: datetime.timedelta
        def __getstate__(self) -> tuple:
            ...
        def __setstate__(self, arg0: tuple) -> None:
            ...
    augmented_lagrangian: int
    augmented_lagrangian_and_gradient: int
    augmented_lagrangian_gradient: int
    augmented_lagrangian_hessian: int
    augmented_lagrangian_hessian_product: int
    constraints: int
    constraints_gradient_product: int
    constraints_jacobian: int
    grad_gi: int
    inactive_indices_res_lna: int
    lagrangian_gradient: int
    lagrangian_hessian: int
    lagrangian_hessian_product: int
    objective: int
    objective_and_constraints: int
    objective_and_gradient: int
    objective_gradient: int
    objective_gradient_and_constraints_gradient_product: int
    projecting_difference_constraints: int
    projection_multipliers: int
    proximal_gradient_step: int
    time: EvalCounter.EvalTimer
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def __str__(self) -> str:
        ...
class LBFGSStepsize:
    """
    C++ documentation: :cpp:enum:`alpaqa::LBFGSStepSize`
    
    Members:
    
      BasedOnExternalStepSize
    
      BasedOnCurvature
    """
    BasedOnCurvature: typing.ClassVar[LBFGSStepsize]  # value = <LBFGSStepsize.BasedOnCurvature: 1>
    BasedOnExternalStepSize: typing.ClassVar[LBFGSStepsize]  # value = <LBFGSStepsize.BasedOnExternalStepSize: 0>
    __members__: typing.ClassVar[dict[str, LBFGSStepsize]]  # value = {'BasedOnExternalStepSize': <LBFGSStepsize.BasedOnExternalStepSize: 0>, 'BasedOnCurvature': <LBFGSStepsize.BasedOnCurvature: 1>}
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
class OCPEvalCounter:
    """
    C++ documentation: :cpp:class:`alpaqa::OCPEvalCounter`
    
    """
    class OCPEvalTimer:
        """
        C++ documentation: :cpp:class:`alpaqa::OCPEvalCounter::OCPEvalTimer`
        
        """
        add_Q: datetime.timedelta
        add_Q_N: datetime.timedelta
        add_R_masked: datetime.timedelta
        add_R_prod_masked: datetime.timedelta
        add_S_masked: datetime.timedelta
        add_S_prod_masked: datetime.timedelta
        add_gn_hess_constr: datetime.timedelta
        add_gn_hess_constr_N: datetime.timedelta
        constr: datetime.timedelta
        constr_N: datetime.timedelta
        f: datetime.timedelta
        grad_constr_prod: datetime.timedelta
        grad_constr_prod_N: datetime.timedelta
        grad_f_prod: datetime.timedelta
        h: datetime.timedelta
        h_N: datetime.timedelta
        jac_f: datetime.timedelta
        l: datetime.timedelta
        l_N: datetime.timedelta
        q_N: datetime.timedelta
        qr: datetime.timedelta
        def __getstate__(self) -> tuple:
            ...
        def __setstate__(self, arg0: tuple) -> None:
            ...
    add_Q: int
    add_Q_N: int
    add_R_masked: int
    add_R_prod_masked: int
    add_S_masked: int
    add_S_prod_masked: int
    add_gn_hess_constr: int
    add_gn_hess_constr_N: int
    constr: int
    constr_N: int
    f: int
    grad_constr_prod: int
    grad_constr_prod_N: int
    grad_f_prod: int
    h: int
    h_N: int
    jac_f: int
    l: int
    l_N: int
    q_N: int
    qr: int
    time: OCPEvalCounter.OCPEvalTimer
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def __str__(self) -> str:
        ...
class PANOCStopCrit:
    """
    C++ documentation: :cpp:enum:`alpaqa::PANOCStopCrit`
    
    Members:
    
      ApproxKKT
    
      ApproxKKT2
    
      ProjGradNorm
    
      ProjGradNorm2
    
      ProjGradUnitNorm
    
      ProjGradUnitNorm2
    
      FPRNorm
    
      FPRNorm2
    
      Ipopt
    
      LBFGSBpp
    """
    ApproxKKT: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ApproxKKT: 0>
    ApproxKKT2: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ApproxKKT2: 1>
    FPRNorm: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.FPRNorm: 6>
    FPRNorm2: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.FPRNorm2: 7>
    Ipopt: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.Ipopt: 8>
    LBFGSBpp: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.LBFGSBpp: 9>
    ProjGradNorm: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ProjGradNorm: 2>
    ProjGradNorm2: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ProjGradNorm2: 3>
    ProjGradUnitNorm: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ProjGradUnitNorm: 4>
    ProjGradUnitNorm2: typing.ClassVar[PANOCStopCrit]  # value = <PANOCStopCrit.ProjGradUnitNorm2: 5>
    __members__: typing.ClassVar[dict[str, PANOCStopCrit]]  # value = {'ApproxKKT': <PANOCStopCrit.ApproxKKT: 0>, 'ApproxKKT2': <PANOCStopCrit.ApproxKKT2: 1>, 'ProjGradNorm': <PANOCStopCrit.ProjGradNorm: 2>, 'ProjGradNorm2': <PANOCStopCrit.ProjGradNorm2: 3>, 'ProjGradUnitNorm': <PANOCStopCrit.ProjGradUnitNorm: 4>, 'ProjGradUnitNorm2': <PANOCStopCrit.ProjGradUnitNorm2: 5>, 'FPRNorm': <PANOCStopCrit.FPRNorm: 6>, 'FPRNorm2': <PANOCStopCrit.FPRNorm2: 7>, 'Ipopt': <PANOCStopCrit.Ipopt: 8>, 'LBFGSBpp': <PANOCStopCrit.LBFGSBpp: 9>}
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
class SolverStatus:
    """
    C++ documentation: :cpp:enum:`alpaqa::SolverStatus`
    
    Members:
    
      Busy : In progress.
    
      Converged : Converged and reached given tolerance
    
      MaxTime : Maximum allowed execution time exceeded
    
      MaxIter : Maximum number of iterations exceeded
    
      NotFinite : Intermediate results were infinite or NaN
    
      NoProgress : No progress was made in the last iteration
    
      Interrupted : Solver was interrupted by the user
    """
    Busy: typing.ClassVar[SolverStatus]  # value = <SolverStatus.Busy: 0>
    Converged: typing.ClassVar[SolverStatus]  # value = <SolverStatus.Converged: 1>
    Interrupted: typing.ClassVar[SolverStatus]  # value = <SolverStatus.Interrupted: 6>
    MaxIter: typing.ClassVar[SolverStatus]  # value = <SolverStatus.MaxIter: 3>
    MaxTime: typing.ClassVar[SolverStatus]  # value = <SolverStatus.MaxTime: 2>
    NoProgress: typing.ClassVar[SolverStatus]  # value = <SolverStatus.NoProgress: 5>
    NotFinite: typing.ClassVar[SolverStatus]  # value = <SolverStatus.NotFinite: 4>
    __members__: typing.ClassVar[dict[str, SolverStatus]]  # value = {'Busy': <SolverStatus.Busy: 0>, 'Converged': <SolverStatus.Converged: 1>, 'MaxTime': <SolverStatus.MaxTime: 2>, 'MaxIter': <SolverStatus.MaxIter: 3>, 'NotFinite': <SolverStatus.NotFinite: 4>, 'NoProgress': <SolverStatus.NoProgress: 5>, 'Interrupted': <SolverStatus.Interrupted: 6>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __ge__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __gt__(self, other: typing.Any) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __le__(self, other: typing.Any) -> bool:
        ...
    def __lt__(self, other: typing.Any) -> bool:
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
class Symmetry:
    """
    C++ documentation: :cpp:enum:`alpaqa::sparsity::Symmetry`
    
    Members:
    
      Unsymmetric
    
      Upper
    
      Lower
    """
    Lower: typing.ClassVar[Symmetry]  # value = <Symmetry.Lower: 2>
    Unsymmetric: typing.ClassVar[Symmetry]  # value = <Symmetry.Unsymmetric: 0>
    Upper: typing.ClassVar[Symmetry]  # value = <Symmetry.Upper: 1>
    __members__: typing.ClassVar[dict[str, Symmetry]]  # value = {'Unsymmetric': <Symmetry.Unsymmetric: 0>, 'Upper': <Symmetry.Upper: 1>, 'Lower': <Symmetry.Lower: 2>}
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
class not_implemented_error(NotImplementedError):
    pass
ApproxKKT: PANOCStopCrit  # value = <PANOCStopCrit.ApproxKKT: 0>
ApproxKKT2: PANOCStopCrit  # value = <PANOCStopCrit.ApproxKKT2: 1>
BasedOnCurvature: LBFGSStepsize  # value = <LBFGSStepsize.BasedOnCurvature: 1>
BasedOnExternalStepSize: LBFGSStepsize  # value = <LBFGSStepsize.BasedOnExternalStepSize: 0>
Busy: SolverStatus  # value = <SolverStatus.Busy: 0>
Converged: SolverStatus  # value = <SolverStatus.Converged: 1>
FPRNorm: PANOCStopCrit  # value = <PANOCStopCrit.FPRNorm: 6>
FPRNorm2: PANOCStopCrit  # value = <PANOCStopCrit.FPRNorm2: 7>
Interrupted: SolverStatus  # value = <SolverStatus.Interrupted: 6>
Ipopt: PANOCStopCrit  # value = <PANOCStopCrit.Ipopt: 8>
LBFGSBpp: PANOCStopCrit  # value = <PANOCStopCrit.LBFGSBpp: 9>
Lower: Symmetry  # value = <Symmetry.Lower: 2>
MaxIter: SolverStatus  # value = <SolverStatus.MaxIter: 3>
MaxTime: SolverStatus  # value = <SolverStatus.MaxTime: 2>
NoProgress: SolverStatus  # value = <SolverStatus.NoProgress: 5>
NotFinite: SolverStatus  # value = <SolverStatus.NotFinite: 4>
ProjGradNorm: PANOCStopCrit  # value = <PANOCStopCrit.ProjGradNorm: 2>
ProjGradNorm2: PANOCStopCrit  # value = <PANOCStopCrit.ProjGradNorm2: 3>
ProjGradUnitNorm: PANOCStopCrit  # value = <PANOCStopCrit.ProjGradUnitNorm: 4>
ProjGradUnitNorm2: PANOCStopCrit  # value = <PANOCStopCrit.ProjGradUnitNorm2: 5>
Unsymmetric: Symmetry  # value = <Symmetry.Unsymmetric: 0>
Upper: Symmetry  # value = <Symmetry.Upper: 1>
__version__: str = '1.1.0a1'
build_time: str = '2025-09-03T21:56:03Z'
commit_hash: str = '2cc06d006231f4ec254f89b61a3ee14d3621af4d'
with_casadi: bool = True
with_casadi_ocp: bool = False
with_external_casadi: bool = True
with_ipopt: bool = False
