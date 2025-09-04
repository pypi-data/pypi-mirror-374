from copy import copy, deepcopy
import pickle
import alpaqa as pa
import numpy as np
from pprint import pprint
import pytest


@pytest.mark.skipif(not pa.with_casadi, reason="requires CasADi")
def test_alm():
    import alpaqa.casadi_loader as cl

    pp = pa.PANOCParams()
    lbfgs = pa.LBFGSDirection()
    panoc = pa.PANOCSolver(pp, lbfgs)
    pprint(panoc.direction.params)
    solver = pa.ALMSolver(pa.ALMParams(), panoc)
    print(f"Solver: {solver} "
          f"({solver.__class__.__module__}.{solver.__class__.__qualname__})")

    import casadi as cs

    n = 2
    m = 2
    x = cs.SX.sym("x", n)

    Q = np.array([[1.5, 0.5], [0.5, 1.5]])
    f_ = 0.5 * x.T @ Q @ x
    g_ = x
    f = cs.Function("f", [x], [f_])
    g = cs.Function("g", [x], [g_])

    name = "testproblem"
    p = cl.generate_and_compile_casadi_problem(f, g, name=name)
    p = copy(p) # test copying/cloning
    p = deepcopy(p) # test copying/cloning
    print(p)
    print("C", p.variable_bounds.lower, p.variable_bounds.upper)
    print("D", p.general_bounds.lower, p.general_bounds.upper)
    p.general_bounds.lower = [-np.inf, 0.5]
    p.general_bounds.upper = [+np.inf, +np.inf]
    solver = pa.PANOCSolver(
        pa.PANOCParams(max_iter=200, print_interval=1),
        pa.LBFGSDirection(pa.LBFGS.Params(memory=5)),
    )
    almparams = pa.ALMParams(max_iter=20, print_interval=1, tolerance=1e-12, dual_tolerance=1e-12)
    almsolver = pa.ALMSolver(almparams, solver)
    cnt = pa.problem_with_counters(p)
    x0 = np.array([3, 3])
    y0 = np.zeros((m, ))
    
    x, y, stats = almsolver(cnt.problem, x=x0, y=y0)

    print()
    print(cnt.evaluations)
    print(stats["status"])
    print("x", x)
    print("y", y)
    pprint(stats)
    assert stats['status'] == pa.SolverStatus.Converged
    assert np.linalg.norm(x - [-1/6, 0.5]) < 1e-5
    assert np.linalg.norm(y - [0, -2/3]) < 1e-5


@pytest.mark.skipif(not pa.with_casadi, reason="requires CasADi")
def test_alm_pyapi_compile():
    import casadi as cs

    n = 2
    m = 2
    x = cs.SX.sym("x", n)

    Q = np.array([[1.5, 0.5], [0.5, 1.5]])
    f = 0.5 * x.T @ Q @ x
    g = x
    D = [-np.inf, 0.5], [+np.inf, +np.inf]
    p = pa.minimize(f, x).subject_to(g, D).compile()
    p = copy(p) # test copying/cloning
    p = deepcopy(p) # test copying/cloning
    print(p)
    solver = pa.PANOCSolver(
        pa.PANOCParams(max_iter=200, print_interval=1),
        pa.LBFGSDirection(pa.LBFGS.Params(memory=5)),
    )
    almparams = pa.ALMParams(max_iter=20, print_interval=1, tolerance=1e-12, dual_tolerance=1e-12)
    almsolver = pa.ALMSolver(almparams, solver)
    cnt = pa.problem_with_counters(p)
    x0 = np.array([3, 3])
    y0 = np.zeros((m, ))
    
    x, y, stats = almsolver(cnt.problem, x=x0, y=y0)

    print()
    print(cnt.evaluations)
    print(stats["status"])
    print("x", x)
    print("y", y)
    pprint(stats)
    assert stats['status'] == pa.SolverStatus.Converged
    assert np.linalg.norm(x - [-1/6, 0.5]) < 1e-5
    assert np.linalg.norm(y - [0, -2/3]) < 1e-5


@pytest.mark.skipif(not pa.with_external_casadi, reason="requires CasADi")
def test_alm_pyapi_build():
    import casadi as cs

    n = 2
    m = 2
    x = cs.SX.sym("x", n)

    Q = np.array([[1.5, 0.5], [0.5, 1.5]])
    f = 0.5 * x.T @ Q @ x
    g = x
    D = [-np.inf, 0.5], [+np.inf, +np.inf]
    p = pa.minimize(f, x).subject_to(g, D).build()
    p = copy(p) # test copying/cloning
    p = deepcopy(p) # test copying/cloning
    print(p)
    solver = pa.PANOCSolver(
        pa.PANOCParams(max_iter=200, print_interval=1),
        pa.LBFGSDirection(pa.LBFGS.Params(memory=5)),
    )
    almparams = pa.ALMParams(max_iter=20, print_interval=1, tolerance=1e-12, dual_tolerance=1e-12)
    almsolver = pa.ALMSolver(almparams, solver)
    cnt = pa.problem_with_counters(p)
    x0 = np.array([3, 3])
    y0 = np.zeros((m, ))
    
    x, y, stats = almsolver(cnt.problem, x=x0, y=y0)

    print()
    print(cnt.evaluations)
    print(stats["status"])
    print("x", x)
    print("y", y)
    pprint(stats)
    assert stats['status'] == pa.SolverStatus.Converged
    assert np.linalg.norm(x - [-1/6, 0.5]) < 1e-5
    assert np.linalg.norm(y - [0, -2/3]) < 1e-5


class MyProblem(pa.BoxConstrProblem):
    vec = np.ndarray
    Q = np.array([[1.5, 0.5], [0.5, 1.5]])
    A = np.eye(2)

    def __init__(self) -> None:
        super().__init__(self.Q.shape[0], self.A.shape[0])

    def eval_objective(self, x: vec) -> float:
        return 0.5 * x.T @ self.Q @ x

    def eval_objective_gradient(self, x: vec, grad_fx: vec):
        grad_fx[:] = self.Q @ x

    def eval_constraints(self, x: vec, gx: vec):
        gx[:] = self.A @ x

    def eval_constraints_gradient_product(self, x: vec, y: vec, g: vec):
        g[:] = self.A.T @ y


def get_pickled_problem():
    p = MyProblem()
    p.general_bounds.lower = [-np.inf, 0.5]
    p.general_bounds.upper = [+np.inf, +np.inf]
    return pickle.dumps(p)


def test_alm_inherit():

    p = pickle.loads(get_pickled_problem())
    solver = pa.PANOCSolver(
        pa.PANOCParams(max_iter=200, print_interval=1),
        pa.LBFGSDirection(pa.LBFGS.Params(memory=5)),
    )
    almparams = pa.ALMParams(max_iter=20, print_interval=1, tolerance=1e-12, dual_tolerance=1e-12)
    almsolver = pa.ALMSolver(almparams, solver)
    cnt = pa.problem_with_counters(p)
    x0 = np.array([3, 3])
    y0 = np.array([0, 0])
    x, y, stats = almsolver(pa.Problem(p), x=x0, y=y0)
    x, y, stats = almsolver(cnt.problem, x=x0, y=y0)

    print()
    print(cnt.evaluations)
    print(stats["status"])
    print("x", x)
    print("y", y)
    pprint(stats)
    assert stats['status'] == pa.SolverStatus.Converged
    assert np.linalg.norm(x - [-1/6, 0.5]) < 1e-5
    assert np.linalg.norm(y - [0, -2/3]) < 1e-5


def test_alm_structured_inherit():

    p = pickle.loads(get_pickled_problem())
    solver = pa.PANOCSolver(
        pa.PANOCParams(max_iter=200, print_interval=1),
        pa.StructuredLBFGSDirection(pa.LBFGS.Params(memory=5)),
    )
    pprint(solver.direction.params)
    almparams = pa.ALMParams(max_iter=20, print_interval=1, tolerance=1e-12, dual_tolerance=1e-12)
    almsolver = pa.ALMSolver(almparams, solver)
    cnt = pa.problem_with_counters(p)
    x0 = np.array([3, 3])
    y0 = np.array([0, 0])
    x, y, stats = almsolver(pa.Problem(p), x=x0, y=y0)
    x, y, stats = almsolver(cnt.problem, x=x0, y=y0)

    print()
    print(almsolver)
    print(cnt.evaluations)
    print(stats["status"])
    print("x", x)
    print("y", y)
    pprint(stats)
    assert stats['status'] == pa.SolverStatus.Converged
    assert np.linalg.norm(x - [-1/6, 0.5]) < 1e-5
    assert np.linalg.norm(y - [0, -2/3]) < 1e-5


if __name__ == '__main__':
    test_alm()
    test_alm_inherit()
    test_alm_structured_inherit()
