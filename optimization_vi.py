"""
optimization_vi.py  --  STUDENT 5 : system integration & multi-objective optimization
======================================================================================
Integrates the complete thermodynamic models developed by Students 1–4 into a unified
steady-state heat pump system model and performs multi-objective optimization:

Architecture Integration:
  - Student 1 (Kartik Gupta): Baseline single-stage cycle, CO2 properties, compressor displacement calibration.
  - Student 2 (Durgesh Nimse): Flash tank mass and energy balances, intermediate pressure flashing.
  - Student 3 (Disha Jain): Compressible orifice EEV model, choking limit, vapor cap, valve sizing.
  - Student 4 (Garva Chirag): Two-stage compressor map with off-design isentropic efficiency,
    volumetric efficiency derating (speed & back-leakage), and hard operating-limit checker.
  - Student 6 (Tarang Gupta): Two-stage intercooled cycle (Case C) integrated for multi-architecture comparison.

Student 5 Core Capabilities:
  1. System Integration & Residual Checking:
     - evaluate_system(phi, P_FT, N, ...): unified function returning complete cycle state,
       flows, power, heating capacity, COP, discharge temperature, and constraint margins.
     - verify_balances(res): rigorous check of overall mass, energy, and flash-tank closure.
  2. Multi-Objective Optimization:
     - Decision variables: Flash-tank pressure P_FT in [3.5, 6.0] MPa,
                           Injection EEV opening phi in [0.0, 1.0],
                           Compressor speed N in [2500, 8000] rpm.
     - Objectives: Maximize Heating COP (COP_h), Maximize Heating Capacity (Q_h),
                   Minimize Compressor Discharge Temperature (T_dis).
     - Hard Constraints: T_dis <= 130 degC, P_dis <= 12.0 MPa, Q_h >= 5.0 kW,
                         2500 <= N <= 8000 rpm, P_evap < P_port < P_dis, P_evap < P_FT < P_dis.
  3. Pareto Frontier & Multi-Criteria Decision Making (MCDM):
     - Fast non-dominated sorting to extract the 3D Pareto frontier.
     - TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) and
       Utopia Knee-Point analysis to identify the single recommended operating point.
  4. Cross-Architecture Comparative Analysis:
     - Benchmark Case A (Baseline), Case B (FT-VI baseline), Case B-Opt (Optimized FT-VI),
       and Case C (Two-stage intercooled with & without heat recovery) across ambient temperatures
       (-5, -10, -15 degC) at nominal speed and load-matched speed (delivering 5.0 kW).

Units: P [MPa], T [degC], h [kJ/kg], s [kJ/kg-K], m [kg/s], W/Q [kW], N [rpm], phi [0..1].
"""

import os
import math
import numpy as np
from config import BRIEF, ASSUME, SENS_AMBIENTS
from co2_props import get_props
import baseline_cycle as bc
import flash_tank_vi as fv
import eev
import ftvi_eev as fe
import compressor_vi as cv
import two_stage_intercooled as tsi

props = get_props()
HERE = os.path.dirname(os.path.abspath(__file__))


# ======================================================================================
# 1. System Integration & Evaluation
# ======================================================================================
def evaluate_system(phi=BRIEF["eev_open"] / 100.0,
                    P_FT=BRIEF["P_inj"],
                    N=BRIEF["N"],
                    T_amb=BRIEF["T_amb"],
                    P_dis=BRIEF["P_dis"],
                    T_gc_out=BRIEF["T_gc_out"],
                    T_evap=None,
                    CdA_max=None,
                    r_port=None,
                    realistic=True):
    """
    Unified steady-state evaluation of the FT-VI EV heat pump system.
    Integrates Students 1 to 4 models into one callable interface.
    """
    if T_evap is None:
        T_evap = bc.evap_temperature(T_amb)

    # Call Student 4's realistic FT-VI solver
    r = cv.ftvi_real(phi=phi, P_FT=P_FT, T_evap=T_evap, N=N,
                     P_dis=P_dis, T_gc_out=T_gc_out,
                     CdA_max=CdA_max, r_port=r_port, realistic=realistic)
    r["T_amb"] = T_amb

    # Perform rigorous mass and energy balance checks
    bal = verify_balances(r)
    r.update(bal)
    return r


def verify_balances(r):
    """
    Rigorous checks of conservation laws across the integrated heat pump cycle:
      - Mass balance: m_tot - (m_suc + m_inj)
      - Adiabatic flash tank energy balance: m_tot * h5 - (m_inj * h7 + m_suc * h8)
      - First law cycle energy balance: Q_h - (Q_e + W)
      - Compressor stage power balance: W - (W1 + W2)
    """
    m_suc = r["m_suc"]
    m_inj = r["m_inj"]
    m_tot = r["m_tot"]
    h5 = r["h5"]
    h7 = r["h7"]
    h8 = r["h8"]

    mass_err = m_tot - (m_suc + m_inj)
    tank_energy_err = m_tot * h5 - (m_inj * h7 + m_suc * h8)
    first_law_err = r["Q_h"] - (r["Q_e"] + r["W"])
    comp_power_err = r["W"] - (r["W1"] + r["W2"])

    mass_ok = abs(mass_err) < 1e-7
    tank_ok = abs(tank_energy_err) < 1e-4
    first_law_ok = abs(first_law_err) < 1e-4
    comp_power_ok = abs(comp_power_err) < 1e-6

    balances_ok = mass_ok and tank_ok and first_law_ok and comp_power_ok

    return {
        "mass_balance_err": mass_err,
        "tank_energy_balance_err": tank_energy_err,
        "cycle_energy_balance_err": first_law_err,
        "comp_power_balance_err": comp_power_err,
        "balances_verified": balances_ok
    }


# ======================================================================================
# 2. Multi-Objective Optimization & Pareto Sorting
# ======================================================================================
def non_dominated_sort(candidates):
    """
    Extracts the non-dominated Pareto frontier for a set of candidate solutions.
    Each candidate is a dict or object with:
      Objectives:
        1. Maximize COP_h
        2. Maximize Q_h
        3. Minimize T_dis
    Returns:
      pareto_list: list of non-dominated candidates
      pareto_indices: array of boolean flags indicating Pareto efficiency
    """
    # Costs array where smaller is better: [-COP_h, -Q_h, +T_dis]
    costs = np.array([[-c["COP_h"], -c["Q_h"], c["T_dis"]] for c in candidates], dtype=float)
    n_points = len(costs)
    is_efficient = np.ones(n_points, dtype=bool)

    for i in range(n_points):
        if is_efficient[i]:
            # Keep any point that has at least one cost strictly better than point i
            # or is not dominated by point i
            is_efficient[is_efficient] = np.any(costs[is_efficient] < costs[i], axis=1)
            is_efficient[i] = True  # Self-comparison is always retained

    pareto_list = [candidates[i] for i in range(n_points) if is_efficient[i]]
    return pareto_list, is_efficient


def run_sampling_optimization(T_amb=BRIEF["T_amb"],
                              P_dis=BRIEF["P_dis"],
                              P_FT_steps=21,
                              phi_steps=15,
                              N_steps=23,
                              Q_target=BRIEF["Q_load"]):
    """
    Explores the complete 3D decision variable space:
      P_FT in [3.5, 6.0] MPa
      phi  in [0.05, 1.0]
      N    in [2500, 8000] rpm
    Filters by feasibility and calculates the Pareto frontier.
    """
    p_ft_grid = np.linspace(BRIEF["P_inj_range"][0], BRIEF["P_inj_range"][1], P_FT_steps)
    phi_grid = np.linspace(0.05, 1.0, phi_steps)
    n_grid = np.linspace(BRIEF["N_min"], BRIEF["N_max"], N_steps)

    all_results = []
    feasible_results = []

    for p in p_ft_grid:
        for phi in phi_grid:
            for n in n_grid:
                res = evaluate_system(phi=phi, P_FT=p, N=n, T_amb=T_amb, P_dis=P_dis)
                all_results.append(res)
                if res["feasible"] and res["Q_h"] >= Q_target - 1e-5:
                    feasible_results.append(res)

    pareto_front, _ = non_dominated_sort(feasible_results)
    return all_results, feasible_results, pareto_front


# ======================================================================================
# 3. Multi-Criteria Decision Making (MCDM): TOPSIS & Knee Point
# ======================================================================================
def topsis_rank(pareto_front, weights=(0.40, 0.30, 0.30)):
    """
    Applies the TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    method on the Pareto frontier.
    Weights correspond to: [w_COP, w_Qh, w_Tdis].
    All objectives are normalized using Min-Max scaling:
      - COP_h: benefit (maximize) -> (x - min) / (max - min)
      - Q_h  : benefit (maximize) -> (x - min) / (max - min)
      - T_dis: cost    (minimize) -> (max - x) / (max - min)
    """
    if not pareto_front:
        raise ValueError("Pareto front is empty!")

    cops = np.array([p["COP_h"] for p in pareto_front], dtype=float)
    qhs = np.array([p["Q_h"] for p in pareto_front], dtype=float)
    tdis = np.array([p["T_dis"] for p in pareto_front], dtype=float)

    # Min-max normalization (0 to 1 scale where 1 is best)
    def norm_benefit(arr):
        span = arr.max() - arr.min()
        return np.ones_like(arr) if span < 1e-9 else (arr - arr.min()) / span

    def norm_cost(arr):
        span = arr.max() - arr.min()
        return np.ones_like(arr) if span < 1e-9 else (arr.max() - arr) / span

    r_cop = norm_benefit(cops)
    r_qh = norm_benefit(qhs)
    r_tdis = norm_cost(tdis)

    # Weighted normalized matrix
    w_cop, w_qh, w_tdis = weights
    w_sum = w_cop + w_qh + w_tdis
    w_cop, w_qh, w_tdis = w_cop / w_sum, w_qh / w_sum, w_tdis / w_sum

    v_cop = r_cop * w_cop
    v_qh = r_qh * w_qh
    v_tdis = r_tdis * w_tdis

    # Ideal positive solution (PIS) and Ideal negative solution (NIS)
    pis = np.array([v_cop.max(), v_qh.max(), v_tdis.max()])
    nis = np.array([v_cop.min(), v_qh.min(), v_tdis.min()])

    V = np.column_stack([v_cop, v_qh, v_tdis])
    d_plus = np.sqrt(np.sum((V - pis) ** 2, axis=1))
    d_minus = np.sqrt(np.sum((V - nis) ** 2, axis=1))

    closeness = d_minus / (d_plus + d_minus + 1e-12)

    ranked_indices = np.argsort(closeness)[::-1]
    best_idx = ranked_indices[0]

    for i, idx in enumerate(ranked_indices):
        pareto_front[idx]["topsis_closeness"] = float(closeness[idx])
        pareto_front[idx]["topsis_rank"] = int(i + 1)

    return pareto_front[best_idx], closeness, ranked_indices


def knee_point_rank(pareto_front):
    """
    Identifies the Knee Point on the Pareto frontier:
    The point with the minimum normalized Euclidean distance to the Utopia (Ideal) point.
    """
    cops = np.array([p["COP_h"] for p in pareto_front], dtype=float)
    qhs = np.array([p["Q_h"] for p in pareto_front], dtype=float)
    tdis = np.array([p["T_dis"] for p in pareto_front], dtype=float)

    # Normalize to [0, 1]
    span_cop = cops.max() - cops.min() or 1.0
    span_qh = qhs.max() - qhs.min() or 1.0
    span_tdis = tdis.max() - tdis.min() or 1.0

    norm_cop = (cops - cops.min()) / span_cop
    norm_qh = (qhs - qhs.min()) / span_qh
    norm_tdis = (tdis.max() - tdis) / span_tdis  # lower T_dis is better, so 1 is min T_dis

    # Distance to Utopia point (1, 1, 1)
    dist_to_utopia = np.sqrt((1.0 - norm_cop) ** 2 + (1.0 - norm_qh) ** 2 + (1.0 - norm_tdis) ** 2)
    best_knee_idx = np.argmin(dist_to_utopia)

    for i, p in enumerate(pareto_front):
        p["knee_distance"] = float(dist_to_utopia[i])

    return pareto_front[best_knee_idx], dist_to_utopia


# ======================================================================================
# 4. Multi-Architecture Comparison (Cases A, B, B-Opt, C)
# ======================================================================================
def compare_architectures(T_amb=-10.0,
                          N=4000.0,
                          P_dis=9.5,
                          P_FT_opt=4.25,
                          phi_opt=1.0,
                          P_i_case_c=4.5,
                          T_ic_case_c=25.0):
    """
    Compares all four key thermodynamic architectures at given ambient condition:
      - Case A: Baseline conventional cycle (Student 1) with realistic compressor map
      - Case B (Standard): Baseline FT-VI (4000 rpm, P_FT=4.5 MPa, phi=0.50)
      - Case B (Optimized): Pareto-recommended FT-VI operating point
      - Case C (Intercooled, no recov): Student 6 two-stage intercooled cycle rejecting IC heat
      - Case C (Intercooled, with recov): Student 6 two-stage intercooled cycle recovering IC heat for cabin
    """
    V = fe.V_disp()
    T_ev = bc.evap_temperature(T_amb)

    # Case A
    res_A = cv.baseline_real(T_evap=T_ev, P_dis=P_dis, N=N)
    res_A["case"] = "Case A (Baseline)"

    # Case B (Standard baseline)
    res_B = evaluate_system(phi=0.50, P_FT=4.5, N=N, T_amb=T_amb, P_dis=P_dis)
    res_B["case"] = "Case B (FT-VI Nominal)"

    # Case B (Optimized)
    res_B_opt = evaluate_system(phi=phi_opt, P_FT=P_FT_opt, N=N, T_amb=T_amb, P_dis=P_dis)
    res_B_opt["case"] = "Case B (FT-VI Optimized)"

    # Case C (Intercooled without recovery)
    res_C_norec = tsi.case_c(T_amb=T_amb, P_i=P_i_case_c, T_ic=T_ic_case_c, N=N, V_disp=V,
                             mode="reject")
    res_C_norec["case"] = "Case C (Two-Stage IC, No Recovery)"

    # Case C (Intercooled with recovery)
    res_C_rec = tsi.case_c(T_amb=T_amb, P_i=P_i_case_c, T_ic=T_ic_case_c, N=N, V_disp=V,
                           mode="recover")
    res_C_rec["case"] = "Case C (Two-Stage IC, With Recovery)"

    all_cases = [res_A, res_B, res_B_opt, res_C_norec, res_C_rec]
    return all_cases


def load_matched_comparison(T_amb=-10.0, Q_target=BRIEF["Q_load"]):
    """
    Calculates the load-matched performance for all cycles:
    Finds the exact compressor speed N required to deliver exactly Q_target = 5.0 kW.
    """
    V = fe.V_disp()
    T_ev = bc.evap_temperature(T_amb)

    # 1. Case A
    N_A, res_A = cv.required_speed(lambda N: cv.baseline_real(T_evap=T_ev, N=N), Q_target=Q_target)
    res_A["case"] = "Case A (Baseline)"
    res_A["N_matched"] = N_A

    # 2. Case B Nominal (P_FT=4.5 MPa, phi=0.5)
    N_B, res_B = cv.required_speed(lambda N: evaluate_system(phi=0.5, P_FT=4.5, N=N, T_amb=T_amb),
                                   Q_target=Q_target)
    res_B["case"] = "Case B (FT-VI Nominal)"
    res_B["N_matched"] = N_B

    # 3. Case B Optimized (P_FT=4.25 MPa, phi=1.0)
    N_Bopt, res_Bopt = cv.required_speed(lambda N: evaluate_system(phi=1.0, P_FT=4.25, N=N, T_amb=T_amb),
                                         Q_target=Q_target)
    res_Bopt["case"] = "Case B (FT-VI Optimized)"
    res_Bopt["N_matched"] = N_Bopt

    # 4. Case C (Student 6) from official handover if available, else simulate
    res_Cnorec = None
    res_Crec = None
    handover_csv = os.path.join(HERE, "results_task6", "case_c_comparison.csv")
    if os.path.exists(handover_csv):
        import csv
        with open(handover_csv, "r") as f:
            for row in csv.DictReader(f):
                if abs(float(row["T_amb"]) - T_amb) < 1e-4:
                    if row["case"] == "C (reject)":
                        res_Cnorec = {
                            "case": "Case C (Two-Stage IC, No Recovery)",
                            "N_matched": float(row["N_required"]),
                            "Q_h": float(row["Q_h"]),
                            "W": float(row["W"]),
                            "COP_h": float(row["COP_h"]),
                            "T_dis": float(row["T_dis"]),
                            "feasible": row["feasible"] == "True"
                        }
                    elif row["case"] == "C (recover)":
                        res_Crec = {
                            "case": "Case C (Two-Stage IC, With Recovery)",
                            "N_matched": float(row["N_required"]),
                            "Q_h": float(row["Q_h"]),
                            "W": float(row["W"]),
                            "COP_h": float(row["COP_h"]),
                            "T_dis": float(row["T_dis"]),
                            "feasible": row["feasible"] == "True"
                        }

    if res_Cnorec is None or res_Crec is None:
        def solve_case_c(mode):
            try:
                r = tsi.solve_for_load(T_amb=T_amb, P_i=4.5, T_ic=25.0, mode=mode, Q_target=Q_target)
                r["N_matched"] = r["N"]
                return r["N"], r
            except Exception:
                return None, None

        if res_Cnorec is None:
            _, res_Cnorec = solve_case_c(mode="reject")
            if res_Cnorec:
                res_Cnorec["case"] = "Case C (Two-Stage IC, No Recovery)"
        if res_Crec is None:
            _, res_Crec = solve_case_c(mode="recover")
            if res_Crec:
                res_Crec["case"] = "Case C (Two-Stage IC, With Recovery)"

    cases = [c for c in [res_A, res_B, res_Bopt, res_Cnorec, res_Crec] if c is not None]
    return cases
