import math, os, time, logging
import traceback
import pyomo.environ as pyo
from causara.optimization.Bounds import DecisionVars
from causara.optimization.Model import Model
from causara.optimization.Solver.solver import get_allowed_solvers
import numpy as np
import causara


def demo_couenne(p, c):
    FeasibilityTol = 1e-6

    """Non-convex MINLP with quadratic distance constraints."""
    sizeQ, P, d, z = float(p["sizeOfQ"]), int(p["maxPoints"]), float(p["d"]), float(p["z"])
    Mdist = 2.0 * sizeQ * math.sqrt(2)

    m = pyo.ConcreteModel()
    m.I  = pyo.RangeSet(0, P-1)
    m.L  = pyo.Set(initialize=[0, 1])
    m.PR = pyo.Set(dimen=2, initialize=lambda md: [(i, j) for i in md.I for j in md.I if i < j])

    # Variables
    m.points    = pyo.Var(m.I, m.L, bounds=(0.0, sizeQ))
    m.pointUsed = pyo.Var(m.I, within=pyo.Binary)
    m.chk12     = pyo.Var(m.PR, within=pyo.Binary)
    m.chk_d     = pyo.Var(m.PR, within=pyo.Binary)
    m.chk_ok    = pyo.Var(m.PR, within=pyo.Binary)
    m.dist      = pyo.Var(m.PR, within=pyo.NonNegativeReals)
    m.q         = pyo.Var(domain=pyo.NonNegativeIntegers)

    # Linking logic
    m.chk12_lo  = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk12[i,j] >= md.pointUsed[i] + md.pointUsed[j] - 1)
    m.chk12_hi1 = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk12[i,j] <= md.pointUsed[i])
    m.chk12_hi2 = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk12[i,j] <= md.pointUsed[j])

    # Distance^2 definition
    m.dist_sq = pyo.Constraint(
        m.PR, rule=lambda md,i,j:
        md.dist[i,j]**2 == (md.points[i,0] - md.points[j,0])**2 + (md.points[i,1] - md.points[j,1])**2
    )

    # z-separation for used points
    m.rule1 = pyo.Constraint(
        m.PR, rule=lambda md,i,j:
        md.dist[i,j] + Mdist*(1 - md.chk12[i,j]) >= z + FeasibilityTol
    )

    # d-range indicator
    m.chk_d_up = pyo.Constraint(
        m.PR, rule=lambda md,i,j:
        md.dist[i,j] <= d - FeasibilityTol + Mdist*(1 - md.chk_d[i,j])
    )
    m.chk_d_lo = pyo.Constraint(
        m.PR, rule=lambda md,i,j:
        md.dist[i,j] >= d + FeasibilityTol - Mdist*md.chk_d[i,j]
    )

    # chk_ok = chk12 AND chk_d
    m.chk_ok_lo  = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk_ok[i,j] >= md.chk12[i,j] + md.chk_d[i,j] - 1)
    m.chk_ok_hi1 = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk_ok[i,j] <= md.chk12[i,j])
    m.chk_ok_hi2 = pyo.Constraint(m.PR, rule=lambda md,i,j: md.chk_ok[i,j] <= md.chk_d[i,j])

    # Counter & objective
    m.ct_qeq  = pyo.Constraint(expr=m.q == pyo.quicksum(m.chk_ok[i,j] for i,j in m.PR))
    m.ct_qmax = pyo.Constraint(expr=m.q <= 4)
    m.obj     = pyo.Objective(expr=pyo.quicksum(m.pointUsed[i] for i in m.I), sense=pyo.maximize)
    return m

def demo_bonmin(p, c):
    """
    Simple convex MINLP:
      x ∈ [0,10], y ∈ {0,1}
      minimize (x - 4)^2 + 10*y
      subject to x >= 2*y
    """
    m = pyo.ConcreteModel()
    m.x = pyo.Var(bounds=(0, 10))
    m.y = pyo.Var(within=pyo.Binary)

    # coupling constraint
    m.coupling = pyo.Constraint(expr=m.x >= 2*m.y)

    # convex quadratic objective
    m.obj = pyo.Objective(expr=(m.x - 4)**2 + 10*m.y, sense=pyo.minimize)
    return m

def demo_highs(p, c):
    """
    A big linear knapsack:
      p['numItems'] : number of items
      p['capacity'] : knapsack capacity
    """
    N, C = int(p['numItems']), float(p['capacity'])
    weights = [ (i % 37) + 1       for i in range(N) ]
    values  = [ (N - i)  % 50 + 10 for i in range(N) ]

    m = pyo.ConcreteModel()
    m.I  = pyo.RangeSet(0, N-1)
    m.x  = pyo.Var(m.I, within=pyo.Binary)
    m.cap= pyo.Constraint(expr=pyo.quicksum(weights[i]*m.x[i] for i in m.I) <= C)
    m.obj= pyo.Objective(expr=pyo.quicksum(values[i]*m.x[i] for i in m.I), sense=pyo.maximize)
    return m

def demo_scip(p, c):
    """
    Quadratic 0-1 model:
      v[i] ∈ {0,1} for i = 0,…,N-1
      maximize sum_{i<j} w[i,j] * v[i] * v[j],
      where w[i,j] ∼ Uniform(0,1)
    """
    import random

    # number of binary variables
    N = int(p["num_vars"])

    # generate random weights for i<j
    weights = {
        (i, j): random.random() * 2 - 1
        for i in range(N) for j in range(i+1, N)
    }

    m = pyo.ConcreteModel()
    m.I = pyo.RangeSet(0, N-1)

    # binary decision variables v[i]
    m.v = pyo.Var(m.I, within=pyo.Binary)

    # quadratic objective: maximize sum_{i<j} w[i,j] * v[i] * v[j]
    m.obj = pyo.Objective(
        expr=sum(weights[i, j] * m.v[i] * m.v[j] for i, j in weights),
        sense=pyo.maximize
    )

    return m

def demo_ipopt(p, c):
    """
    Large dense separable quadratic program:
      p['numVars'] : dimensionality
    """
    n = int(p['numVars'])
    m = pyo.ConcreteModel()
    m.I = pyo.RangeSet(0, n-1)
    m.x = pyo.Var(m.I, bounds=(-5.0, 5.0))

    # Objective: sum (x_i - target_i)^2
    m.obj = pyo.Objective(expr=pyo.quicksum((m.x[i] - (i % 3 + 1))**2 for i in m.I))

    # One long linear coupling constraint
    m.sum_pos = pyo.Constraint(expr=pyo.quicksum(m.x[i] for i in m.I) >= 0.0)
    return m

def cell_tower(p, c, x):
    desired_coverage = p["desired_coverage"]
    size = int(p["size"])
    cell_towers = x["cell_towers"]

    # Calculate tower positions in the finer resolution (10x finer than the coarse resolution)
    fine_size = size * 10
    tower_positions = []
    for i in range(size):
        for j in range(size):
            if cell_towers[i][j] == 1:
                tower_positions.append((i * 10 + 5, j * 10 + 5)) # Center of the coarse cell (i, j) in the fine grid

    # Calculate coverage in the finer resolution with circles instead of squares
    coverage = np.zeros((fine_size, fine_size))
    for i in range(fine_size):
        for j in range(fine_size):
            for tower_x, tower_y in tower_positions:
                distance = np.sqrt((i - tower_x)**2 + (j - tower_y)**2)
                if distance <= 40:  # Radius of 40 in the fine grid corresponds to 4 in coarse grid
                    coverage[i][j] += 1

    # Calculate the number of cells for which the coverage does not meet the desired coverage
    insufficient_cell_coverage = np.zeros((fine_size, fine_size))
    for i in range(fine_size):
        for j in range(fine_size):
            if coverage[i][j] < desired_coverage[i][j]:
                insufficient_cell_coverage[i][j] = 1

    total_towers = np.sum(cell_towers)

    return 100 * total_towers + np.sum(insufficient_cell_coverage)

def get_decision_vars_couenne(p, c):
    P = int(p["maxPoints"])
    decision_vars = DecisionVars()
    decision_vars.add_binary_vars("pointUsed", P)
    return decision_vars

def get_decision_vars_bonmin(p, c):
    decision_vars = DecisionVars()
    decision_vars.add_binary_vars("y", 1)
    return decision_vars

def get_decision_vars_highs(p, c):
    N = int(p["numItems"])
    decision_vars = DecisionVars()
    decision_vars.add_binary_vars("x", N)
    return decision_vars

def get_decision_vars_scip(p, c):
    N = int(p["num_vars"])
    decision_vars = DecisionVars()
    decision_vars.add_binary_vars("v", N)
    return decision_vars

def get_decision_vars_ipopt(p, c):
    n = int(p["numVars"])
    decision_vars = DecisionVars()
    decision_vars.add_continuous_vars("x", shape=n, minimum=-5.0, maximum=5.0)
    return decision_vars

def get_decision_vars_causara(p, c):
    size = p["size"]
    decision_vars = DecisionVars()
    decision_vars.add_binary_vars("cell_towers", (size, size))
    return decision_vars

def test_solvers():

    p_couenne = {
        "sizeOfQ": 50.0,
        "maxPoints": 10,
        "d": 2.5,
        "z": 1.0
    }

    p_bonmin = {}

    p_highs = {
        "numItems": 300000,
        "capacity": 600_000.0
    }

    p_scip = {
        "num_vars": 100
    }

    p_ipopt = {
        "numVars": 200_000
    }

    p_gurobi = {
        "num_vars": 5
    }

    num_solutions = 1

    if "gurobi" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="gurobi")
        model.compile(decision_vars_func=get_decision_vars_scip, pyomo_func=demo_scip, sense=-1)
        for time_limit in [90, 2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_gurobi, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Gurobi: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "scip" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="scip")
        model.compile(decision_vars_func=get_decision_vars_scip, pyomo_func=demo_scip, sense=-1)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_scip, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Scip: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "causara" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="cell_towers")
        model.compile(decision_vars_func=get_decision_vars_causara, obj_func=cell_tower, sense=+1, time_limit=30)
        P_test = causara.Demos.Cell_tower.generate_P(n=20, size=10)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=P_test.iloc[0], num_solutions=num_solutions, time_limit=time_limit)
            print(f"Causara: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "couenne" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="couenne")
        model.compile(decision_vars_func=get_decision_vars_couenne, pyomo_func=demo_couenne, sense=-1)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_couenne, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Couenne: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "bonmin" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="bonmin")
        model.compile(decision_vars_func=get_decision_vars_bonmin, pyomo_func=demo_bonmin, sense=+1)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_bonmin, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Bonmin: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "highs" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="highs")
        model.compile(decision_vars_func=get_decision_vars_highs, pyomo_func=demo_highs, sense=-1)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_highs, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Highs: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()

    if "ipopt" in get_allowed_solvers():
        model = Model(key="AHfi5hIOFAsGKeyJP7V2IVk8igMVoS", model_name="test", solver="ipopt")
        model.compile(decision_vars_func=get_decision_vars_ipopt, pyomo_func=demo_ipopt, sense=+1)
        for time_limit in [90,2]:
            start_time = time.perf_counter()
            data = model.optimize(p=p_ipopt, num_solutions=num_solutions, time_limit=time_limit)
            print(f"Ipopt: {time.perf_counter() - start_time}, objective value: {data.pyomo_values}")
        print()
