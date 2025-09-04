import casadi as cs
from .. import alpaqa as pa
from ..casadi_generator import SECOND_ORDER_SPEC as SECOND_ORDER_SPEC
from .ocp import generate_and_compile_casadi_control_problem as generate_and_compile_casadi_control_problem
from pathlib import Path

def generate_and_compile_casadi_problem_no_load(f: cs.Function, g: cs.Function, *, C=None, D=None, param=None, l1_reg=None, penalty_alm_split=None, second_order: SECOND_ORDER_SPEC = 'no', name: str = 'alpaqa_problem', **kwargs) -> Path: ...
def generate_and_compile_casadi_problem(*args, **kwargs) -> pa.CasADiProblem: ...
