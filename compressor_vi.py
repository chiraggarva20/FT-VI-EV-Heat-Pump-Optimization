"""
compressor_vi.py — Student 4: Two-Stage Vapor-Injection Compressor & Heating Performance
=========================================================================================
Evaluates realistic two-stage CO2 vapor-injection compressor operation using the
operating conditions from Students 1-3 (config.py, baseline_cycle.py, eev.py, ftvi_eev.py).

Key physical extensions over Student 3's constant-efficiency compressor stub:
  1. Speed- and pressure-ratio-dependent isentropic efficiency map eta_is(N, PR)
     anchored to BRIEF['eta_is'] = 0.70 at the design point (N = 4000 rpm).
  2. Suction volumetric efficiency with injection back-leakage derating:
       eta_v = (EVO - EV1 * PR_total) * (1 - k_leak * xi_est)
  3. Explicit stage-by-stage compressor work (W1, W2, W_tot), discharge temperature
     (T_dis), useful cabin heating capacity (Q_h), heating COP (COP_h), and operating
     limit checks (T_dis <= 130 C, P_dis <= 12.0 MPa, N_min <= N <= N_max, Q_h >= 5 kW).
  4. Drop-in replacement signature matching ftvi_eev.compressor() so Student 3's cycle
     solver and Student 5's optimizer can call it directly.
"""

import numpy as np
from config import BRIEF, ASSUME
from co2_props import get_props
from baseline_cycle import baseline_cycle, calibrate_displacement
import eev
import ftvi_eev as fe

props = get_props()

# Compressor map calibration parameters (anchored at N_ref = 4000 rpm, eta_is = 0.70)
COMP_MAP = {
    "N_ref": 4000.0,       # rpm, design-point speed
    "PR_ref": 4.1733,      # design-point overall pressure ratio
    "k_N_low": 0.08,       # low-speed blow-by penalty coefficient
    "k_N_high": 0.06,      # high-speed valve/port friction penalty coefficient
    "k_PR": 0.015,         # off-design pressure-ratio penalty coefficient
    "k_leak_vi": 0.035,    # suction volumetric derating per unit injection ratio xi
    "eta_is_min": 0.45,    # physical lower bound on stage isentropic efficiency
    "eta_is_max": 0.82,    # physical upper bound on stage isentropic efficiency
}


def stage_isentropic_efficiency(N, PR_stage, eta_is_design=None, PR_stage_ref=2.04):
    """
    Off-design stage isentropic efficiency as a function of speed N and stage PR.
    Equals eta_is_design (0.70) at N = 4000 rpm and PR_stage = PR_stage_ref.
    """
    if eta_is_design is None:
        eta_is_design = BRIEF["eta_is"]

    n_ratio = N / COMP_MAP["N_ref"]
    if n_ratio < 1.0:
        speed_pen = COMP_MAP["k_N_low"] * (1.0 - n_ratio) ** 1.5
    else:
        speed_pen = COMP_MAP["k_N_high"] * (n_ratio - 1.0) ** 1.5

    pr_pen = COMP_MAP["k_PR"] * ((PR_stage - PR_stage_ref) / PR_stage_ref) ** 2
    eta = eta_is_design - speed_pen - pr_pen
    return float(np.clip(eta, COMP_MAP["eta_is_min"], COMP_MAP["eta_is_max"]))


def compressor_realistic(P_evap, T1, P_port, P_dis, N, V_disp, eta_is, m_inj):
    """
    Swappable compressor model with the EXACT same 8-input / 11-output signature
    as ftvi_eev.compressor():
      Inputs:  (P_evap, T1, P_port, P_dis, N, V_disp, eta_is, m_inj)
      Returns: (m_suc, h2, T2, h3, T3, h4, T4, W1, W2, W, eta_v)
    """
    PR_tot = P_dis / P_evap
    PR1 = P_port / P_evap
    PR2 = P_dis / P_port

    # Base volumetric efficiency + mild injection back-leakage derating
    eta_v_base = max(0.10, ASSUME["EVO"] - ASSUME["EV1"] * PR_tot)
    rho1 = props.D_PT(P_evap, T1)
    m_suc_base = rho1 * V_disp * (N / 60.0) * eta_v_base

    xi_est = (m_inj / m_suc_base) if (m_suc_base > 0.0 and m_inj > 0.0) else 0.0
    derate = max(0.85, 1.0 - COMP_MAP["k_leak_vi"] * xi_est)
    eta_v = eta_v_base * derate
    m_suc = m_suc_base * derate

    # Stage 1: suction (1) -> port pressure (2)
    h1 = props.H_PT(P_evap, T1)
    s1 = props.S_PT(P_evap, T1)
    eta_is1 = stage_isentropic_efficiency(N, PR1, eta_is_design=eta_is, PR_stage_ref=1.50)
    h2s = props.H_PS(P_port, s1)
    h2 = h1 + (h2s - h1) / eta_is1
    T2 = props.T_PH(P_port, h2)

    # Adiabatic mixing at injection port (State 2 + State 7a -> State 3)
    h7a = props.H_P_satV(P_port) if m_inj <= 0.0 else None  # overridden by cycle energy balance below
    # Note: in ftvi_eev(), State 3 mixing uses h7a = h7 (isenthalpic across EEV).
    # When called standalone without h7 passed, we compute h7a from flash-tank default or caller.
    if hasattr(compressor_realistic, "_current_h7a") and compressor_realistic._current_h7a is not None:
        h_inj_port = compressor_realistic._current_h7a
    else:
        h_inj_port = props.H_P_satV(BRIEF["P_inj"])

    m_tot = m_suc + m_inj
    h3 = (m_suc * h2 + m_inj * h_inj_port) / m_tot
    T3 = props.T_PH(P_port, h3)
    s3 = props.S_PH(P_port, h3)

    # Stage 2: port pressure (3) -> discharge pressure (4)
    eta_is2 = stage_isentropic_efficiency(N, PR2, eta_is_design=eta_is, PR_stage_ref=2.78)
    h4s = props.H_PS(P_dis, s3)
    h4 = h3 + (h4s - h3) / eta_is2
    T4 = props.T_PH(P_dis, h4)

    W1 = m_suc * (h2 - h1)
    W2 = m_tot * (h4 - h3)
    W = W1 + W2
    return m_suc, h2, T2, h3, T3, h4, T4, W1, W2, W, eta_v


compressor_realistic._current_h7a = None


def check_operating_limits(res):
    """
    Evaluates all compressor and system operating constraints from config.py:
      - Discharge temperature: T_dis <= T_dis_max (130.0 C)
      - Discharge pressure:    P_dis <= P_max (12.0 MPa)
      - Compressor speed:      N_min (2500 rpm) <= N <= N_max (8000 rpm)
      - Heating capacity:      Q_h >= Q_load (5.0 kW)
      - Pressure ordering:     P_evap < P_port < P_dis
    Returns a dict of individual boolean flags, margins, and overall feasibility.
    """
    T_margin = BRIEF["T_dis_max"] - res["T_dis"]
    P_margin = BRIEF["P_max"] - res["P_dis"]
    Q_margin = res["Q_h"] - BRIEF["Q_load"]

    ok_T = res["T_dis"] <= BRIEF["T_dis_max"]
    ok_P = res["P_dis"] <= BRIEF["P_max"]
    ok_N = BRIEF["N_min"] <= res["N"] <= BRIEF["N_max"]
    ok_Q = res["Q_h"] >= BRIEF["Q_load"]
    ok_order = (res["P_evap"] < res["P_port"] < res["P_dis"])

    violations = []
    if not ok_T:
        violations.append(f"T_dis={res['T_dis']:.1f}C > {BRIEF['T_dis_max']:.1f}C")
    if not ok_P:
        violations.append(f"P_dis={res['P_dis']:.2f}MPa > {BRIEF['P_max']:.2f}MPa")
    if not ok_N:
        violations.append(f"N={res['N']:.0f}rpm out of [{BRIEF['N_min']:.0f},{BRIEF['N_max']:.0f}]")
    if not ok_Q:
        violations.append(f"Q_h={res['Q_h']:.2f}kW < {BRIEF['Q_load']:.2f}kW")
    if not ok_order:
        violations.append("Invalid pressure ordering")

    return {
        "ok_T_dis": bool(ok_T),
        "ok_P_dis": bool(ok_P),
        "ok_speed": bool(ok_N),
        "ok_Q_load": bool(ok_Q),
        "ok_pressure_order": bool(ok_order),
        "all_limits_ok": bool(ok_T and ok_P and ok_N and ok_Q and ok_order),
        "T_dis_margin_C": float(T_margin),
        "P_dis_margin_MPa": float(P_margin),
        "Q_load_margin_kW": float(Q_margin),
        "violations": "; ".join(violations) if violations else "NONE",
    }


def evaluate_ftvi_compressor(
    T_amb=None,
    P_FT=None,
    phi=None,
    P_dis=None,
    T_gc_out=None,
    N=None,
    V_disp=None,
    CdA_max=None,
    use_realistic_map=True,
):
    """
    Full coupled FT-VI + EEV + Compressor evaluation for Task 4.
    Uses Students 1-3 modules and augments with stage efficiencies, pressure ratios,
    and operating-limit diagnostics.
    """
    if T_amb is None:
        T_amb = BRIEF["T_amb"]
    if P_FT is None:
        P_FT = BRIEF["P_inj"]
    if phi is None:
        phi = BRIEF["eev_open"] / 100.0
    if P_dis is None:
        P_dis = BRIEF["P_dis"]
    if T_gc_out is None:
        T_gc_out = BRIEF["T_gc_out"]
    if N is None:
        N = BRIEF["N"]
    if V_disp is None:
        V_disp = calibrate_displacement()
    if CdA_max is None:
        CdA_max = fe.CdA_design()

    # Pre-compute h7 at P_FT so compressor_realistic uses exact flash-tank vapor enthalpy
    compressor_realistic._current_h7a = props.H_P_satV(P_FT)

    orig_comp = fe.compressor
    if use_realistic_map:
        fe.compressor = compressor_realistic

    try:
        res = fe.ftvi_eev(
            T_amb=T_amb,
            P_FT=P_FT,
            phi=phi,
            P_dis=P_dis,
            T_gc_out=T_gc_out,
            N=N,
            V_disp=V_disp,
            CdA_max=CdA_max,
        )
    finally:
        fe.compressor = orig_comp
        compressor_realistic._current_h7a = None

    PR_tot = res["P_dis"] / res["P_evap"]
    PR1 = res["P_port"] / res["P_evap"]
    PR2 = res["P_dis"] / res["P_port"]

    if use_realistic_map:
        eta_is1 = stage_isentropic_efficiency(N, PR1, PR_stage_ref=1.50)
        eta_is2 = stage_isentropic_efficiency(N, PR2, PR_stage_ref=2.78)
    else:
        eta_is1 = BRIEF["eta_is"]
        eta_is2 = BRIEF["eta_is"]

    limits = check_operating_limits(res)

    out = dict(res)
    out.update({
        "PR_total": float(PR_tot),
        "PR1": float(PR1),
        "PR2": float(PR2),
        "eta_is1": float(eta_is1),
        "eta_is2": float(eta_is2),
        "w1_spec": float(res["W1"] / res["m_suc"]),
        "w2_spec": float(res["W2"] / res["m_tot"]),
        "w_tot_spec": float(res["W"] / res["m_tot"]),
        "COP_c": float(res["Q_e"] / res["W"]),
        "realistic_map": bool(use_realistic_map),
    })
    out.update(limits)
    return out


def compare_baseline_vs_ftvi(T_amb_list=(-20.0, -15.0, -10.0, -5.0, 0.0), P_FT=4.5, phi=0.50, N=4000.0):
    """
    Compares Student 1's single-stage baseline cycle against Student 4's FT-VI cycle
    across selected cold-weather ambient conditions.
    """
    V_disp = calibrate_displacement()
    rows = []
    for T_amb in T_amb_list:
        T_evap = T_amb - ASSUME["dT_evap_approach"]
        base = baseline_cycle(T_evap=T_evap, P_dis=BRIEF["P_dis"], T_gc_out=BRIEF["T_gc_out"], N=N, V_disp=V_disp)
        ftvi = evaluate_ftvi_compressor(T_amb=T_amb, P_FT=P_FT, phi=phi, N=N, V_disp=V_disp)

        rows.append({
            "T_amb_C": T_amb,
            "T_evap_C": T_evap,
            "P_evap_MPa": base["P_evap"],
            "Base_Q_h_kW": base["Q_h"],
            "Base_W_kW": base["W"],
            "Base_COP_h": base["COP_h"],
            "Base_T_dis_C": base["T_dis"],
            "Base_Feasible": base["feasible"],
            "FTVI_Q_h_kW": ftvi["Q_h"],
            "FTVI_W_kW": ftvi["W"],
            "FTVI_COP_h": ftvi["COP_h"],
            "FTVI_T_dis_C": ftvi["T_dis"],
            "FTVI_xi": ftvi["xi"],
            "FTVI_PR1": ftvi["PR1"],
            "FTVI_PR2": ftvi["PR2"],
            "FTVI_Feasible": ftvi["all_limits_ok"],
            "Delta_Q_h_pct": 100.0 * (ftvi["Q_h"] - base["Q_h"]) / base["Q_h"],
            "Delta_COP_pct": 100.0 * (ftvi["COP_h"] - base["COP_h"]) / base["COP_h"],
            "Delta_T_dis_C": ftvi["T_dis"] - base["T_dis"],
            "FTVI_Violations": ftvi["violations"],
        })
    return rows


if __name__ == "__main__":
    print("Backend:", props.name)
    d_const = evaluate_ftvi_compressor(use_realistic_map=False)
    d_real = evaluate_ftvi_compressor(use_realistic_map=True)
    print(f"Design Point (Const eta_is):  Q_h={d_const['Q_h']:.3f} kW, W={d_const['W']:.3f} kW, COP_h={d_const['COP_h']:.3f}, T_dis={d_const['T_dis']:.2f} C, OK={d_const['all_limits_ok']}")
    print(f"Design Point (Realistic Map): Q_h={d_real['Q_h']:.3f} kW, W={d_real['W']:.3f} kW, COP_h={d_real['COP_h']:.3f}, T_dis={d_real['T_dis']:.2f} C, OK={d_real['all_limits_ok']}")
    print("\nCold-Weather Comparison (Baseline vs FT-VI at phi=50%, P_FT=4.5 MPa, N=4000 rpm):")
    for r in compare_baseline_vs_ftvi():
        print(
            f"T_amb={r['T_amb_C']:+5.1f}C | Base: Q={r['Base_Q_h_kW']:.2f}kW, COP={r['Base_COP_h']:.2f}, Tdis={r['Base_T_dis_C']:.1f}C (OK={r['Base_Feasible']}) | "
            f"FT-VI: Q={r['FTVI_Q_h_kW']:.2f}kW ({r['Delta_Q_h_pct']:+.1f}%), COP={r['FTVI_COP_h']:.2f} ({r['Delta_COP_pct']:+.1f}%), "
            f"Tdis={r['FTVI_T_dis_C']:.1f}C ({r['Delta_T_dis_C']:+.1f}K) (OK={r['FTVI_Feasible']})"
        )