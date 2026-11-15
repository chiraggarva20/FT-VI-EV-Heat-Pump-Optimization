"""
two_stage_intercooled.py  --  STUDENT 6 : Case C, two-stage intercooled transcritical R744 heat pump
====================================================================================================
Builds on Students 1-4 WITHOUT modifying them (config, co2_props, baseline_cycle, ftvi_eev, compressor_vi).

State points
  1  evaporator outlet / stage-1 suction     (P_evap , T_evap + SH)
  2  stage-1 discharge                       (P_i    , h2 = h1 + (h2s-h1)/eta1)
  3  intercooler outlet / stage-2 suction    (P_i    , T_ic)            [vapour only]
  4  stage-2 discharge                       (P_dis  , h4 = h3 + (h4s-h3)/eta2)
  5  gas-cooler outlet                       (P_dis  , T_gc_out)
  6  EEV outlet (isenthalpic)                (P_evap , h6 = h5)

Two intercooler options
  mode = 'reject'   intercooler heat Q_ic is dumped to ambient air   -> Q_use = Q_gc
  mode = 'recover'  intercooler heat Q_ic preheats the cabin air     -> Q_use = Q_gc + Q_ic
                    (cabin air passes the intercooler first, then the gas cooler)

What is shared with Cases A and B (so that A / B / C are compared on ONE basis)
  * compressor size                 fe.V_disp()  (Student 1 calibration, Case A = 5.0 kW at 4000 rpm)
  * stage isentropic efficiency     cv.stage_efficiency(N, PR_stage)   (Student 4 map, same reference ratios)
  * volumetric efficiency           cv.vol_eff_real(N, P_dis, P_evap)  (overall pressure ratio, as in A and B)
  * limit checker                   cv.check_limits()   (T_dis, P_dis, N range, Q_h >= 5 kW)
  * load matching                   solve_for_load()  == lowest speed that gives exactly 5.0 kW useful heat

Units: P [MPa], T [degC], h [kJ/kg], s [kJ/kg-K], m [kg/s], W/Q [kW], N [rpm].
"""
import math
from config import BRIEF, ASSUME
from co2_props import get_props
import baseline_cycle as bc
import ftvi_eev as fe
import compressor_vi as cv

props = get_props()

# ----------------------------- Student 6 assumptions (all stated in the report) -----------------
S6 = dict(
    dT_approach=5.0,      # K  minimum temperature approach in every air-side heat exchanger (assumption)
    dT_sat_margin=2.0,    # K  intercooler outlet must stay at least this far above Tsat(P_i)  (vapour only)
    dT_stage2_gap=1.0,    # K  intercooler outlet must be at least this far below stage-1 discharge T2
)


def air_inlet_temperature(T_amb):
    """Air entering the heat-pump air-side exchangers [degC]: fresh air (m_vent at T_amb) mixed with
    recirculated cabin air (rest of m_air_gc at ASSUME['T_air_gc_in']).  12 degC at -10 degC ambient."""
    m, mv = ASSUME["m_air_gc"], ASSUME["m_vent"]
    return (mv * T_amb + (m - mv) * ASSUME["T_air_gc_in"]) / m


def case_c(T_amb=-10.0, P_i=4.5, T_ic=25.0, N=None, V_disp=None, mode="reject",
           realistic=True, eta_is=None, **kwargs):
    """One Case C operating point at speed N.  Raises ValueError for a thermodynamically or
    thermally impossible point (outside the pressure window, liquid at stage-2 suction, no
    temperature approach in the intercooler or gas cooler)."""
    # Backward compatibility with older kwargs if any
    if "recover_intercooler" in kwargs:
        mode = "recover" if kwargs["recover_intercooler"] else "reject"

    if mode not in ("reject", "recover"):
        raise ValueError("mode must be 'reject' or 'recover'")
    N = BRIEF["N"] if N is None else N
    eta_is = BRIEF["eta_is"] if eta_is is None else eta_is
    V = fe.V_disp() if V_disp is None else V_disp

    T_e = bc.evap_temperature(T_amb)
    P_e = props.Psat(T_e)
    P_d = BRIEF["P_dis"]
    if not (P_e < P_i < P_d):
        raise ValueError("Intermediate pressure must lie between P_evap and P_dis")

    T1 = T_e + ASSUME["superheat"]
    h1, s1, rho1 = props.h(P_e, T1), props.s(P_e, T1), props.rho(P_e, T1)

    if realistic:                                   # Student 4 compressor map (same as Cases A and B)
        eta1 = cv.stage_efficiency(N, P_i / P_e, cv.PR1_REF, eta_is)
        eta2 = cv.stage_efficiency(N, P_d / P_i, cv.PR2_REF, eta_is)
        eta_v = cv.vol_eff_real(N, P_d, P_e, 0.0)
    else:                                           # constant-efficiency model of Students 1-3
        eta1 = eta2 = eta_is
        eta_v = bc.vol_eff(P_d, P_e)
    m = rho1 * V * (N / 60.0) * eta_v

    h2 = h1 + (props.h_ps(P_i, s1) - h1) / eta1
    T2 = props.T_ph(P_i, h2)
    T_sat = props.Tsat(P_i)
    if T_ic < T_sat + S6["dT_sat_margin"]:
        raise ValueError("Intercooler outlet too close to saturation (liquid at stage-2 suction)")
    if T_ic > T2 - S6["dT_stage2_gap"]:
        raise ValueError("Intercooler outlet must be cooler than stage-1 discharge")
    h3, s3 = props.h(P_i, T_ic), props.s(P_i, T_ic)
    h4 = h3 + (props.h_ps(P_d, s3) - h3) / eta2
    T4 = props.T_ph(P_d, h4)
    T_gc = BRIEF["T_gc_out"]
    h5 = props.h(P_d, T_gc)
    h6 = h5

    W1, W2 = m * (h2 - h1), m * (h4 - h3)
    Q_ic, Q_gc = m * (h2 - h3), m * (h4 - h5)
    Q_e = m * (h1 - h6)
    Q_use = Q_gc + (Q_ic if mode == "recover" else 0.0)
    W = W1 + W2

    # ---- air side: real temperature approaches (replaces the old "ideal full recovery" assumption)
    mcp = ASSUME["m_air_gc"] * ASSUME["cp_air"]           # kW/K
    dTa = S6["dT_approach"]
    T_mix = air_inlet_temperature(T_amb)
    if mode == "recover":
        T_air_ic_out = T_mix + Q_ic / mcp
        if T_ic < T_mix + dTa:
            raise ValueError("Intercooler outlet leaves < dT_approach to the cabin-air inlet")
        if T2 < T_air_ic_out + dTa:
            raise ValueError("Intercooler hot end leaves < dT_approach to the heated air")
        T_air_gc_in = T_air_ic_out
    else:
        T_air_ic_out = float("nan")
        if T_ic < T_amb + dTa:
            raise ValueError("Intercooler outlet leaves < dT_approach to ambient air")
        T_air_gc_in = T_mix
    T_air_out = T_air_gc_in + Q_gc / mcp
    if T_gc < T_air_gc_in + dTa:
        raise ValueError("Gas-cooler cold end leaves < dT_approach")
    if T4 < T_air_out + dTa:
        raise ValueError("Gas-cooler hot end leaves < dT_approach")

    r = dict(
        case="C", mode=mode, T_amb=T_amb, T_evap=T_e, P_evap=P_e, P_i=P_i, P_dis=P_d, N=N,
        T_ic=T_ic, T_sat_i=T_sat, eta1=eta1, eta2=eta2, eta_v=eta_v, m_dot=m,
        T1=T1, h1=h1, s1=s1, T2=T2, h2=h2, T3=T_ic, h3=h3, s3=s3, T4=T4, h4=h4,
        T5=T_gc, h5=h5, h6=h6,
        W1=W1, W2=W2, W=W, Q_ic=Q_ic, Q_gc=Q_gc, Q_h=Q_use, Q_e=Q_e,
        COP_h=Q_use / W, T_dis=T4, energy_balance_err=Q_gc + Q_ic - Q_e - W,
        T_air_in=T_mix, T_air_after_ic=T_air_ic_out, T_air_gc_in=T_air_gc_in, T_air_out=T_air_out,
        pressure_geomean=math.sqrt(P_e * P_d), P_port=P_i, P_FT=P_i,
    )
    r.update(cv.check_limits(r))
    return r


def solve_for_load(T_amb, P_i, T_ic, mode="reject", Q_target=BRIEF["Q_load"], realistic=True,
                   V_disp=None, tol=1e-9, max_iter=40):
    """Compressor speed at which the USEFUL heat equals Q_target (5.0 kW) -- equal-capacity basis.
    Q is almost proportional to N, so N <- N * Q_target / Q converges in a few steps.  The speed is
    clamped to [N_min, N_max]; if 5 kW cannot be reached the point is returned at N_max with
    feasible = False (violation 'Q_h')."""
    N = BRIEF["N"]
    r = case_c(T_amb, P_i, T_ic, N, V_disp, mode, realistic)
    for _ in range(max_iter):
        if abs(r["Q_h"] - Q_target) < tol:
            break
        N_new = min(max(N * Q_target / r["Q_h"], BRIEF["N_min"]), BRIEF["N_max"])
        if N_new == N:
            break
        N = N_new
        r = case_c(T_amb, P_i, T_ic, N, V_disp, mode, realistic)
    return r


def T_ic_window(T_amb, P_i, mode):
    """Lowest and highest admissible intercooler outlet temperature at pressure P_i (at 4000 rpm)."""
    r_hi = case_c_stage1(T_amb, P_i)
    lo = props.Tsat(P_i) + S6["dT_sat_margin"]
    if mode == "recover":
        lo = max(lo, air_inlet_temperature(T_amb) + S6["dT_approach"])
    else:
        lo = max(lo, T_amb + S6["dT_approach"])
    return lo, r_hi - S6["dT_stage2_gap"]


def case_c_stage1(T_amb, P_i, N=None):
    """Stage-1 discharge temperature T2 [degC] (used to bound the intercooler-outlet sweep)."""
    N = BRIEF["N"] if N is None else N
    T_e = bc.evap_temperature(T_amb)
    P_e = props.Psat(T_e)
    T1 = T_e + ASSUME["superheat"]
    h1, s1 = props.h(P_e, T1), props.s(P_e, T1)
    eta1 = cv.stage_efficiency(N, P_i / P_e, cv.PR1_REF, BRIEF["eta_is"])
    return props.T_ph(P_i, h1 + (props.h_ps(P_i, s1) - h1) / eta1)
