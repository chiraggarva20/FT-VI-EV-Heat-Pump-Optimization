"""
compressor_vi.py  --  STUDENT 4 : two-stage vapour-injection compressor & heating performance
==============================================================================================
Builds on Students 1-3 without modifying them (config, baseline_cycle, eev, ftvi_eev).

Student 3's cycle uses a constant isentropic efficiency (0.70) in both stages and a volumetric
efficiency that depends only on the overall pressure ratio.  Student 4 replaces that stub by an
off-design compressor model and then evaluates the whole cycle:

  1. Stage isentropic efficiency map   eta_is(N, PR_stage)
        eta = eta_d - a_low (1-n)^2  [n<1]  - a_high (n-1)^2  [n>1]  - k_PR ln^2(PR/PR_ref)
        n = N / 4000 rpm.  Anchored so that eta = 0.70 at the design point
        (4000 rpm, stage pressure ratios of the -10 degC / 4.5 MPa / 50 % design case).
        low-speed term  = internal leakage / blow-by,  high-speed term = port & valve throttling.
  2. Volumetric efficiency with speed and injection back-leakage derating
        eta_v = (EV0 - EV1 * P_dis/P_evap) * f_N(N) * (1 - k_leak * xi)
        (EV0, EV1 from config.ASSUME = Student 1's trend;  xi = m_inj / m_suc)
  3. Stage-by-stage work   W1 = m_suc (h2 - h1),  W2 = m_tot (h4 - h3),  W = W1 + W2
  4. Useful heating capacity  Q_h = m_tot (h4 - h5),  COP_h = Q_h / W
  5. Operating-limit checker  (T_dis <= 130 C, P_dis <= 12 MPa, 2500 <= N <= 8000 rpm,
                               Q_h >= 5 kW, P_evap < P_port, P_FT < P_dis)
  6. Case A (single-stage) with the SAME map, so baseline vs FT-VI is a like-for-like comparison.

Regression guarantee: ftvi_real(..., realistic=False) switches the map OFF (constant eta, no
derating) and reproduces ftvi_eev.ftvi_eev() to machine precision (checked in run_task4.py).

Units as everywhere: P [MPa], T [degC], h [kJ/kg], m [kg/s], W/Q [kW], N [rpm], phi 0..1.
"""
import math
import numpy as np
from config import BRIEF, ASSUME
from co2_props import get_props
import baseline_cycle as bc
import eev
import ftvi_eev as fe

props = get_props()

# ----------------------------- Task 4 assumptions (stated in report) -------------------------
COMP = dict(
    N_ref=4000.0,       # rpm  design speed at which eta_is = 0.70 (Student 1)
    a_low=0.20,         # -    eta loss at N -> 0 is a_low (quadratic in 1-n): blow-by / internal leakage
    a_high=0.06,        # -    eta loss at n = 2 (8000 rpm): valve / port throttling
    k_PR=0.06,          # -    penalty for running away from the design stage pressure ratio (ln^2)
    eta_min=0.45, eta_max=0.80,
    k_vN=0.05,          # -    low-speed volumetric loss  eta_v *= 1 - k_vN (1-n)^2  for n < 1
    k_leak=0.03,        # -    suction-flow derating per unit injection ratio  (1 - k_leak * xi)
    derate_min=0.85,
)

# Design-point stage pressure ratios (-10 degC ambient, 4000 rpm, r_port = 1.5, P_dis = 9.5 MPa)
_T_EV_D = bc.evap_temperature(eev.EEV["design"]["T_amb"])
_P_EV_D = props.Psat(_T_EV_D)
PR1_REF = eev.EEV["r_port"]                                   # P_port / P_evap
PR2_REF = BRIEF["P_dis"] / (eev.EEV["r_port"] * _P_EV_D)      # P_dis / P_port
PRT_REF = BRIEF["P_dis"] / _P_EV_D                            # overall (single-stage Case A)


# ----------------------------------------------------------------------------------------
# compressor map
# ----------------------------------------------------------------------------------------
def stage_efficiency(N, PR, PR_ref, eta_d=None):
    """Off-design stage isentropic efficiency eta_is(N, PR).  = eta_d at (N_ref, PR_ref)."""
    eta_d = BRIEF["eta_is"] if eta_d is None else eta_d
    n = N / COMP["N_ref"]
    speed = COMP["a_low"] * (1.0 - n) ** 2 if n < 1.0 else COMP["a_high"] * (n - 1.0) ** 2
    ratio = COMP["k_PR"] * math.log(PR / PR_ref) ** 2
    return float(np.clip(eta_d - speed - ratio, COMP["eta_min"], COMP["eta_max"]))


def speed_vol_factor(N):
    n = N / COMP["N_ref"]
    return 1.0 - COMP["k_vN"] * (1.0 - n) ** 2 if n < 1.0 else 1.0


def vol_eff_real(N, P_dis, P_evap, xi=0.0):
    """Suction volumetric efficiency incl. low-speed leakage and injection back-leakage."""
    base = bc.vol_eff(P_dis, P_evap) * speed_vol_factor(N)
    return base * max(COMP["derate_min"], 1.0 - COMP["k_leak"] * xi)


# ----------------------------------------------------------------------------------------
# swappable two-stage compressor (same outputs as ftvi_eev.compressor, plus N-dependent eta)
# ----------------------------------------------------------------------------------------
def compressor(P_evap, h1, s1, P_port, P_dis, m_suc, m_inj, h_inj, N=BRIEF["N"],
               eta_is=BRIEF["eta_is"], realistic=True):
    """Two-stage compression with mid-compression injection.  Returns dict with
    h2, T2, h3, T3, s3, h4, T4 (= T_dis), W1, W2, W, eta1, eta2."""
    if realistic:
        eta1 = stage_efficiency(N, P_port / P_evap, PR1_REF, eta_is)
        eta2 = stage_efficiency(N, P_dis / P_port, PR2_REF, eta_is)
    else:
        eta1 = eta2 = eta_is
    h2 = h1 + (props.h_ps(P_port, s1) - h1) / eta1
    m_tot = m_suc + m_inj
    h3 = (m_suc * h2 + m_inj * h_inj) / m_tot
    T3 = props.T_ph(P_port, h3)
    s3 = props.s(P_port, T3)
    h4 = h3 + (props.h_ps(P_dis, s3) - h3) / eta2
    T4 = props.T_ph(P_dis, h4)
    W1, W2 = m_suc * (h2 - h1), m_tot * (h4 - h3)
    return dict(h2=h2, T2=props.T_ph(P_port, h2), h3=h3, T3=T3, s3=s3, h4=h4, T4=T4,
                W1=W1, W2=W2, W=W1 + W2, eta1=eta1, eta2=eta2)


# ----------------------------------------------------------------------------------------
# operating-limit checker
# ----------------------------------------------------------------------------------------
def check_limits(r, Q_target=BRIEF["Q_load"]):
    """Hard constraints of the brief.  Margins are positive when the limit is respected."""
    P_port = r.get("P_port", r["P_evap"] * 1.0001)
    P_FT = r.get("P_FT", r["P_evap"] * 1.0001)
    if P_FT != P_FT:                                  # NaN for the single-stage case
        P_FT = r["P_evap"] * 1.0001
    flags = dict(
        T_dis_ok=bool(r["T_dis"] <= BRIEF["T_dis_max"]),
        P_dis_ok=bool(r["P_dis"] <= BRIEF["P_max"]),
        N_ok=bool(BRIEF["N_min"] <= r["N"] <= BRIEF["N_max"]),
        Q_ok=bool(r["Q_h"] >= Q_target - 1e-6),            # 1 mW tolerance: Case A is calibrated to exactly 5.0 kW
        P_order_ok=bool(r["P_evap"] < P_port < r["P_dis"] and r["P_evap"] < P_FT < r["P_dis"]),
    )
    flags["feasible"] = all(flags.values())
    flags["T_dis_margin"] = BRIEF["T_dis_max"] - r["T_dis"]
    flags["P_dis_margin"] = BRIEF["P_max"] - r["P_dis"]
    flags["Q_margin"] = r["Q_h"] - Q_target
    names = (("T_dis", "T_dis_ok"), ("P_dis", "P_dis_ok"), ("N", "N_ok"), ("Q_h", "Q_ok"),
             ("P_order", "P_order_ok"))
    viol = [n for n, k in names if not flags[k]]
    flags["violations"] = ",".join(viol) if viol else "none"
    return flags


# ----------------------------------------------------------------------------------------
# Case B : FT-VI cycle with the realistic compressor
# ----------------------------------------------------------------------------------------
def ftvi_real(phi=BRIEF["eev_open"] / 100.0, P_FT=BRIEF["P_inj"], T_evap=BRIEF["T_evap"],
              N=BRIEF["N"], P_dis=BRIEF["P_dis"], T_gc_out=BRIEF["T_gc_out"],
              eta_is=BRIEF["eta_is"], SH=ASSUME["superheat"], CdA_max=None, r_port=None,
              P_port=None, realistic=True):
    """Same cycle as ftvi_eev.ftvi_eev (state numbering 1..9, 7a) but with the Student-4
    compressor.  m_suc and m_inj are coupled (back-leakage derates m_suc, the vapour cap
    x/(1-x)*m_suc depends on m_suc) and are solved by fixed-point iteration."""
    CdA_max = fe.CdA_design() if CdA_max is None else CdA_max
    P_e = props.Psat(T_evap)
    P_port = eev.port_pressure(P_e, r_port) if P_port is None else P_port
    if not (P_e < P_port < P_dis and P_e < P_FT < P_dis):
        raise ValueError("Constraint violated: need P_evap < P_port, P_FT < P_dis")
    T1 = T_evap + SH
    h1, s1, rho1 = props.h(P_e, T1), props.s(P_e, T1), props.rho(P_e, T1)
    swept = rho1 * fe.V_disp() * N / 60.0

    h5 = props.h(P_dis, T_gc_out)
    x = eev.flash_quality(P_FT, h5)
    h7 = props.hg(P_FT)

    eta_v = vol_eff_real(N, P_dis, P_e, 0.0) if realistic else bc.vol_eff(P_dis, P_e)
    m_suc = swept * eta_v
    for _ in range(60):                                   # fixed point: m_suc <-> m_inj
        inj = eev.m_inj(phi, P_FT, P_port, m_suc, x, CdA_max)
        if realistic:
            eta_v = vol_eff_real(N, P_dis, P_e, inj["xi"])
        m_new = swept * eta_v
        if abs(m_new - m_suc) < 1e-12:
            m_suc = m_new
            break
        m_suc = m_new
    inj = eev.m_inj(phi, P_FT, P_port, m_suc, x, CdA_max)
    m_i = inj["m_inj"]
    m_tot = m_suc + m_i

    c = compressor(P_e, h1, s1, P_port, P_dis, m_suc, m_i, h7, N, eta_is, realistic)

    h8 = (m_tot * h5 - m_i * h7) / m_suc
    hf_e, hg_e = props.hf(P_e), props.hg(P_e)
    x9 = (h8 - hf_e) / (hg_e - hf_e)
    x8 = (h8 - props.hf(P_FT)) / (h7 - props.hf(P_FT))

    Q_h = m_tot * (c["h4"] - h5)
    Q_e = m_suc * (h1 - h8)
    W = c["W"]
    r = dict(
        phi=phi, P_FT=P_FT, P_port=P_port, T_evap=T_evap, P_evap=P_e, P_dis=P_dis, N=N,
        T_FT=props.Tsat(P_FT), eta_v=eta_v, x=x,
        eta_is1=c["eta1"], eta_is2=c["eta2"],
        h1=h1, T1=T1, h2=c["h2"], T2=c["T2"], h3=c["h3"], T3=c["T3"], h4=c["h4"], T4=c["T4"],
        h5=h5, h6=h5, h7=h7, h7a=h7, T7a=props.T_ph(P_port, h7), h8=h8, x8=x8, h9=h8, x9=x9,
        m_suc=m_suc, m_inj=m_i, m_tot=m_tot, xi=inj["xi"], xi_max=inj["m_inj_max"] / m_suc,
        m_valve=inj["m_valve"], limited_by=inj["limited_by"], choked=inj["choked"],
        Q_h=Q_h, Q_e=Q_e, W=W, W1=c["W1"], W2=c["W2"], COP_h=Q_h / W, T_dis=c["T4"],
        w1_spec=c["W1"] / m_suc, w2_spec=c["W2"] / m_tot,
        energy_balance_err=Q_h - Q_e - W,
    )
    r.update(check_limits(r))
    return r


# ----------------------------------------------------------------------------------------
# Case A : single-stage baseline with the SAME map (like-for-like comparison)
# ----------------------------------------------------------------------------------------
def baseline_real(T_evap=BRIEF["T_evap"], P_dis=BRIEF["P_dis"], N=BRIEF["N"],
                  T_gc_out=BRIEF["T_gc_out"], eta_is=BRIEF["eta_is"], realistic=True):
    V = fe.V_disp()
    P_e = props.Psat(T_evap)
    T1 = T_evap + ASSUME["superheat"]
    rho1 = props.rho(P_e, T1)
    PR = P_dis / P_e
    if realistic:
        eta = stage_efficiency(N, PR, PRT_REF, eta_is)
        eta_v = vol_eff_real(N, P_dis, P_e, 0.0)
    else:
        eta, eta_v = eta_is, bc.vol_eff(P_dis, P_e)
    r = bc.baseline(T_evap=T_evap, P_dis=P_dis, T_gc_out=T_gc_out, N=N, V_disp=V, eta_is=eta,
                    m_dot=rho1 * V * N / 60.0 * eta_v)
    r["eta_v"], r["eta_is"] = eta_v, eta
    r["P_FT"] = float("nan")
    r["W1"], r["W2"] = r["W"], 0.0
    r["m_suc"], r["m_tot"], r["m_inj"], r["xi"] = r["m_dot"], r["m_dot"], 0.0, 0.0
    flags = check_limits(r)
    r.update(flags)
    return r


# ----------------------------------------------------------------------------------------
# load matching : lowest speed that delivers the target heating capacity
# ----------------------------------------------------------------------------------------
def required_speed(fn, Q_target=BRIEF["Q_load"], step=100.0, **kw):
    """Smallest N in [N_min, N_max] with Q_h >= Q_target for cycle function `fn(N=..., **kw)`.
    Returns (N, result) or (None, result at N_max) when the target cannot be reached."""
    from scipy.optimize import brentq
    grid = np.arange(BRIEF["N_min"], BRIEF["N_max"] + 1e-9, step)
    prev = None
    r = None
    for n in grid:
        r = fn(N=float(n), **kw)
        if r["Q_h"] >= Q_target:
            if prev is None:
                return float(n), r
            N_star = brentq(lambda v: fn(N=v, **kw)["Q_h"] - Q_target, float(prev), float(n), xtol=0.1)
            N_star = min(N_star + 0.5, float(n))          # land just above the target, never below it
            return N_star, fn(N=N_star, **kw)
        prev = n
    return None, r


if __name__ == "__main__":
    print("Backend:", props.name)
    print("Reference stage PR: PR1 = %.3f  PR2 = %.3f  overall = %.3f" % (PR1_REF, PR2_REF, PRT_REF))
    print("eta_is at design point (stage 1 / stage 2 / single stage): %.3f / %.3f / %.3f" % (
        stage_efficiency(4000, PR1_REF, PR1_REF), stage_efficiency(4000, PR2_REF, PR2_REF),
        stage_efficiency(4000, PRT_REF, PRT_REF)))
    a = baseline_real()
    b = ftvi_real()
    print("Case A : Q=%.3f W=%.3f COP=%.3f Tdis=%.1f feasible=%s" % (a["Q_h"], a["W"], a["COP_h"], a["T_dis"], a["feasible"]))
    print("Case B : Q=%.3f W=%.3f (W1=%.3f W2=%.3f) COP=%.3f Tdis=%.1f xi=%.3f feasible=%s" % (
        b["Q_h"], b["W"], b["W1"], b["W2"], b["COP_h"], b["T_dis"], b["xi"], b["feasible"]))
