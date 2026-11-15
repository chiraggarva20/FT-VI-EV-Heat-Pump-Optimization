"""
run_task4.py -- STUDENT 4: compressor & heating-performance studies, CSV results, figures, hand-over file.
Usage:  python run_task4.py      (needs CoolProp for report numbers; same backend logic as run_all.py)
Outputs go to  results_task4/  and  figures_task4/

Studies
  0  design point (Case A / Case B, constant-eta vs realistic map) + regression check vs Student 3
  1  compressor map  eta_is(N, PR),  eta_v(N, xi)
  2  cold-weather comparison  T_amb = -5 (sens.), -10 (design), -15 (sens.) degC, fixed 4000 rpm
  3  load-matched speed (lowest rpm that delivers 5.0 kW) and the power it costs
  4  stage-work breakdown vs P_FT and EEV opening
  5  compressor speed sweep 2500-8000 rpm (sensitivity at -5 and -15 degC)
  6  discharge-pressure sweep 7.5-12.5 MPa (sensitivity at -5 and -15 degC)
  7  operating envelopes (T_amb -15...-5 degC x N) and (P_FT x P_dis)
  8  design-point state table + P-h diagram
  9  hand-over to Student 5
"""
import os, csv, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from config import BRIEF, ASSUME, SENS_AMBIENTS
from co2_props import get_props
import baseline_cycle as bc
import eev
import ftvi_eev as fe
import compressor_vi as cv

props = get_props()
HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, "results_task4"), os.path.join(HERE, "figures_task4")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)

# ----------------------------- plot style (identical to run_task3.py) ----------------------
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE_ORD = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
plt.rcParams.update({
    "font.size": 9, "figure.dpi": 160, "savefig.dpi": 200,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.8,
    "legend.frameon": False, "axes.titlesize": 9.5, "axes.titleweight": "bold",
})
C_A, C_B50, C_B100 = CAT[1], CAT[0], CAT[2]          # Case A / Case B @ 50 % / Case B @ 100 %


def save_csv(name, rows, keys=None):
    keys = keys or [k for k in rows[0].keys() if not isinstance(rows[0][k], (dict, list))]
    with open(os.path.join(RES, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k in keys})


def limit_line(ax, y, text, where="right", va="bottom"):
    ax.axhline(y, color=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=1)
    x = 0.99 if where == "right" else 0.01
    ax.text(x, y, text, transform=ax.get_yaxis_transform(), ha=where, va=va, color=INK2, fontsize=7.5)


def vline(ax, x, text, va="top"):
    ax.axvline(x, color=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.text(x, 0.98 if va == "top" else 0.02, " " + text, transform=ax.get_xaxis_transform(),
            ha="left", va=va, color=INK2, fontsize=7.5)


def end_label(ax, x, y, text, color=INK2, dy=0):
    ax.annotate(text, (x, y), xytext=(4, dy), textcoords="offset points", va="center", fontsize=7.5, color=color)


def fig_save(fig, name):
    fig.savefig(os.path.join(FIG, name), bbox_inches="tight")
    plt.close(fig)


def col(rows, k):
    return np.array([r[k] for r in rows], dtype=float)


R = {"backend": props.name}
TAMB = np.array(sorted(SENS_AMBIENTS, reverse=True), dtype=float)   # -5, -10, -15 degC: design case + the two sensitivity cases of the brief
TAMB_MAP = np.arange(-15.0, -4.99, 1.0)                             # continuous map axis, same -15...-5 degC range
COLS = ["case", "T_amb", "T_evap", "P_evap", "P_FT", "P_port", "P_dis", "N", "phi", "eta_is1", "eta_is2", "eta_is",
        "eta_v", "x", "xi", "m_suc", "m_inj", "m_tot", "Q_h", "W", "W1", "W2", "COP_h", "T_dis",
        "T_dis_margin", "Q_margin", "T_dis_ok", "P_dis_ok", "N_ok", "Q_ok", "feasible", "violations"]


def tag(r, case, T_amb):
    r = dict(r); r["case"] = case; r["T_amb"] = T_amb
    return r


def caseA(Ta, **kw):
    return tag(cv.baseline_real(T_evap=bc.evap_temperature(Ta), **kw), "A", Ta)


def caseB(Ta, phi=0.5, **kw):
    return tag(cv.ftvi_real(phi=phi, T_evap=bc.evap_temperature(Ta), **kw), "B%d" % round(phi * 100), Ta)


# ======================================================================================
# 0. Design point and regression check against Students 1-3
# ======================================================================================
V = fe.V_disp(); CdA = fe.CdA_design()
R["V_disp_cc"] = V * 1e6; R["CdA_mm2"] = CdA * 1e6
R["COMP"] = dict(cv.COMP); R["PR_ref"] = dict(stage1=cv.PR1_REF, stage2=cv.PR2_REF, overall=cv.PRT_REF)

dp = []
A0 = tag(cv.baseline_real(realistic=False), "A  (S1, const eta)", -10)
A1 = tag(cv.baseline_real(), "A  (S4 map)", -10)
B0 = tag(cv.ftvi_real(realistic=False), "B  (S3, const eta)", -10)
B1 = tag(cv.ftvi_real(), "B  (S4 map)", -10)
for r in (A0, A1, B0, B1):
    dp.append(r)
save_csv("T4_design_point_comparison.csv", dp, COLS)
R["design_point"] = {r["case"].strip(): dict(Q_h=r["Q_h"], W=r["W"], COP_h=r["COP_h"], T_dis=r["T_dis"], xi=r["xi"],
                                              eta_v=r["eta_v"], feasible=r["feasible"]) for r in dp}

val = []
for (Ta, p, f, n, Pd) in [(-10, 4.5, 0.5, 4000, 9.5), (-10, 3.5, 0.2, 4000, 9.5), (-15, 6.0, 1.0, 2500, 9.5),
                          (-5, 4.0, 0.7, 8000, 10.5), (-15, 4.5, 0.5, 5000, 9.0), (-10, 4.5, 0.0, 4000, 9.5)]:
    Te = bc.evap_temperature(Ta)
    s3 = fe.ftvi_eev(phi=f, P_FT=p, T_evap=Te, N=n, P_dis=Pd)
    s4 = cv.ftvi_real(phi=f, P_FT=p, T_evap=Te, N=n, P_dis=Pd, realistic=False)
    val.append(dict(T_amb=Ta, P_FT=p, phi=f, N=n, P_dis=Pd,
                    **{f"S3_{k}": s3[k] for k in ("Q_h", "W", "COP_h", "T_dis", "xi")},
                    **{f"S4off_{k}": s4[k] for k in ("Q_h", "W", "COP_h", "T_dis", "xi")},
                    max_rel_diff=max(abs(s4[k] - s3[k]) / max(abs(s3[k]), 1e-9)
                                     for k in ("Q_h", "W", "COP_h", "T_dis", "xi", "m_suc"))))
save_csv("T4_validation_vs_student3.csv", val)
R["validation_max_rel_diff"] = max(v["max_rel_diff"] for v in val)
Aref = bc.baseline(V_disp=V)
R["validation_caseA_rel_diff"] = abs(cv.baseline_real(realistic=False)["Q_h"] / Aref["Q_h"] - 1)

# ======================================================================================
# 1. Compressor map
# ======================================================================================
NG = np.arange(2000.0, 8000.1, 250.0)
PRG = np.arange(1.2, 4.01, 0.1)
map_eta = [dict(N=n, PR_stage=pr, eta_is_s1=cv.stage_efficiency(n, pr, cv.PR1_REF), eta_is_s2=cv.stage_efficiency(n, pr, cv.PR2_REF))
           for n in (2500.0, 4000.0, 6000.0, 8000.0) for pr in PRG]
save_csv("T4_map_eta_is.csv", map_eta)
map_ev = [dict(N=n, xi=xi, eta_v=cv.vol_eff_real(n, BRIEF["P_dis"], _P, xi))
          for _P in [props.Psat(-15.0)] for n in NG for xi in (0.0, 0.2, 0.4, 0.6)]
save_csv("T4_map_eta_v.csv", map_ev)

# ======================================================================================
# 2. Cold-weather comparison at fixed 4000 rpm
# ======================================================================================
CW = []
for Ta in TAMB:
    CW += [caseA(Ta), caseB(Ta, 0.5), caseB(Ta, 1.0)]
save_csv("T4_cold_weather.csv", CW, COLS)
cwA = [r for r in CW if r["case"] == "A"]; cwB = [r for r in CW if r["case"] == "B50"]; cwB1 = [r for r in CW if r["case"] == "B100"]
R["cold_weather_4000rpm"] = {f"{r['T_amb']:g}": dict(A=dict(Q=a["Q_h"], COP=a["COP_h"], T=a["T_dis"], feas=a["violations"]),
                                                      B50=dict(Q=r["Q_h"], COP=r["COP_h"], T=r["T_dis"], feas=r["violations"]))
                            for a, r in zip(cwA, cwB)}
R["feasible_4000rpm"] = {f"{a['T_amb']:g}": dict(A=a["feasible"], B50=b["feasible"], B100=c["feasible"])
                        for a, b, c in zip(cwA, cwB, cwB1)}

# ======================================================================================
# 3. Load matching : lowest rpm that delivers 5.0 kW
# ======================================================================================
LM = []
for Ta in TAMB:
    Te = bc.evap_temperature(Ta)
    for name, fn, kw in (("A", cv.baseline_real, {}), ("B50", cv.ftvi_real, dict(phi=0.5)), ("B100", cv.ftvi_real, dict(phi=1.0))):
        n, r = cv.required_speed(fn, T_evap=Te, **kw)
        r = tag(r, name, Ta)
        r["N_req"] = n if n is not None else float("nan")
        r["reaches_load"] = n is not None
        LM.append(r)
save_csv("T4_load_matched_speed.csv", LM, COLS + ["N_req", "reaches_load"])
R["load_matched"] = {f"{r['T_amb']:g}_{r['case']}": dict(N_req=r["N_req"], W=r["W"], COP=r["COP_h"], T_dis=r["T_dis"],
                                                         feasible=r["feasible"]) for r in LM}

# ======================================================================================
# 4. Stage-work breakdown vs P_FT and phi  (-10 degC, 4000 rpm)
# ======================================================================================
PFT = np.round(np.arange(3.5, 6.01, 0.25), 3)
PHIS = [0.25, 0.5, 0.75, 1.0]
SW = [tag(cv.ftvi_real(phi=f, P_FT=p), "B", -10.0) for f in PHIS for p in PFT]
save_csv("T4_stage_work.csv", SW, COLS)
best = max(SW, key=lambda r: r["COP_h"])
R["stage_work_best_COP"] = dict(P_FT=best["P_FT"], phi=best["phi"], COP=best["COP_h"], Q=best["Q_h"], T=best["T_dis"])

# ======================================================================================
# 5. Speed sweep
# ======================================================================================
NS = np.arange(2500.0, 8000.1, 250.0)
SP_T = [-5.0, -15.0]
SP = []
for Ta in SP_T:
    for n in NS:
        SP += [caseA(Ta, N=float(n)), caseB(Ta, 0.5, N=float(n))]
save_csv("T4_speed_sweep.csv", SP, COLS)

# ======================================================================================
# 6. Discharge-pressure sweep
# ======================================================================================
PD = np.arange(7.5, 12.51, 0.25)
PD_T = [-5.0, -15.0]
PS = []
for Ta in PD_T:
    for pd_ in PD:
        PS += [caseA(Ta, P_dis=float(pd_)), caseB(Ta, 0.5, P_dis=float(pd_))]
save_csv("T4_pdis_sweep.csv", PS, COLS)
for Ta in PD_T:
    for c_ in ("A", "B50"):
        sub = [r for r in PS if r["T_amb"] == Ta and r["case"] == c_ and r["T_dis_ok"]]
        b_ = max(sub, key=lambda r: r["COP_h"])
        R[f"pdis_opt_{c_}_{Ta:g}"] = dict(P_dis=b_["P_dis"], COP=b_["COP_h"], Q=b_["Q_h"], T=b_["T_dis"])

# ======================================================================================
# 7. Envelopes
# ======================================================================================
NE = np.arange(2500.0, 8000.1, 250.0)
EV1 = []
for Ta in TAMB_MAP:
    for n in NE:
        EV1 += [caseA(Ta, N=float(n)), caseB(Ta, 0.5, N=float(n))]
save_csv("T4_envelope_Tamb_N.csv", EV1, COLS)
PFT_E = np.round(np.arange(3.5, 6.01, 0.25), 3)
PD_E = np.arange(8.0, 12.51, 0.25)
EV2 = [tag(cv.ftvi_real(P_FT=float(p), P_dis=float(d), T_evap=bc.evap_temperature(-15.0)), "B50", -15.0)
       for d in PD_E for p in PFT_E]
save_csv("T4_envelope_PFT_Pdis.csv", EV2, COLS)
R["envelope_feasible_fraction"] = dict(
    A=float(np.mean([r["feasible"] for r in EV1 if r["case"] == "A"])),
    B50=float(np.mean([r["feasible"] for r in EV1 if r["case"] == "B50"])))

# ======================================================================================
# 8. State table at the design point (Case B, S4 map, phi = 50 %)
# ======================================================================================
D = B1
st = [("1", "Suction", D["P_evap"], D["T1"], D["h1"], "SH vapour"),
      ("2", "End of stage 1", D["P_port"], D["T2"], D["h2"], "SH vapour"),
      ("7", "Flash-tank vapour", D["P_FT"], D["T_FT"], D["h7"], "x = 1"),
      ("7a", "After injection EEV", D["P_port"], D["T7a"], D["h7a"], "SH vapour"),
      ("3", "After mixing", D["P_port"], D["T3"], D["h3"], "SH vapour"),
      ("4", "Discharge", D["P_dis"], D["T4"], D["h4"], "SC fluid"),
      ("5", "Gas-cooler outlet", D["P_dis"], BRIEF["T_gc_out"], D["h5"], "SC fluid"),
      ("6", "EEV-1 outlet", D["P_FT"], D["T_FT"], D["h6"], f"x = {D['x']:.3f}"),
      ("8", "Tank outlet to EEV-2", D["P_FT"], D["T_FT"], D["h8"], f"x = {D['x8']:.3f}"),
      ("9", "Evaporator inlet", D["P_evap"], props.Tsat(D["P_evap"]), D["h9"], f"x = {D['x9']:.3f}")]
with open(os.path.join(RES, "T4_state_table_design.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["state", "description", "P_MPa", "T_C", "h_kJkg", "phase"])
    for r in st: w.writerow([r[0], r[1], round(r[2], 4), round(r[3], 2), round(r[4], 2), r[5]])
R["state_table"] = st

# ======================================================================================
# 9. Hand-over for Student 5
# ======================================================================================
tests = []
for (Ta, p, f, n, d) in [(-10, 4.5, 0.5, 4000, 9.5), (-10, 4.5, 1.0, 4000, 9.5), (-10, 3.5, 0.5, 4000, 9.5),
                         (-10, 6.0, 0.3, 4000, 9.5), (-5, 4.5, 0.5, 4000, 9.5), (-15, 6.0, 1.0, 4000, 9.5),
                         (-15, 4.5, 0.5, 6000, 9.5), (-10, 5.0, 0.8, 8000, 9.5), (-5, 6.0, 0.3, 2500, 9.5),
                         (-15, 3.5, 0.5, 4000, 9.5)]:
    r = cv.ftvi_real(phi=f, P_FT=p, T_evap=bc.evap_temperature(Ta), N=n, P_dis=d)
    tests.append(dict(T_amb=Ta, P_FT=p, phi=f, N=n, P_dis=d, m_suc=r["m_suc"], m_inj=r["m_inj"], xi=r["xi"],
                      eta_is1=r["eta_is1"], eta_is2=r["eta_is2"], eta_v=r["eta_v"], W1=r["W1"], W2=r["W2"], W=r["W"],
                      Q_h=r["Q_h"], COP_h=r["COP_h"], T_dis=r["T_dis"], feasible=r["feasible"], violations=r["violations"]))
save_csv("T4_handover_testcases.csv", tests)
handover = dict(
    function="compressor_vi.ftvi_real(phi, P_FT, T_evap, N, P_dis, ...) -> full cycle dict incl. Q_h, W, W1, W2, COP_h, T_dis, "
             "xi, eta_is1, eta_is2, eta_v and the constraint flags (feasible, violations, T_dis_margin, Q_margin)",
    baseline="compressor_vi.baseline_real(T_evap, P_dis, N) -> Case A with the same compressor map",
    limits="compressor_vi.check_limits(result) -> dict of boolean flags + margins",
    load_match="compressor_vi.required_speed(fn, T_evap=..., ...) -> (N_req, result) lowest rpm delivering 5.0 kW",
    units="P [MPa], T [degC], h [kJ/kg], m [kg/s], W/Q [kW], N [rpm], phi 0..1",
    objectives=dict(maximise=["COP_h", "Q_h"], minimise=["T_dis"]),
    constraints=dict(T_dis_max_C=BRIEF["T_dis_max"], P_dis_max_MPa=BRIEF["P_max"], N_range_rpm=[BRIEF["N_min"], BRIEF["N_max"]],
                     Q_h_min_kW=BRIEF["Q_load"], pressure_order="P_evap < P_port, P_FT < P_dis"),
    compressor_map=dict(COMP=cv.COMP, PR_ref=dict(stage1=cv.PR1_REF, stage2=cv.PR2_REF, overall=cv.PRT_REF)),
    constants=dict(V_disp_m3=V, CdA_max_m2=CdA, r_port=eev.EEV["r_port"], Cd=eev.EEV["Cd"], k=eev.EEV["k"]),
    decision_variable_ranges=dict(P_FT_MPa=[3.5, 6.0], phi=[0.0, 1.0], N_rpm=[BRIEF["N_min"], BRIEF["N_max"]]),
    notes=["m_suc and m_inj are coupled (back-leakage) and solved by fixed-point iteration inside ftvi_real",
           "ftvi_real(realistic=False) reproduces ftvi_eev.ftvi_eev exactly (regression check)",
           "ambient cases follow the brief: design -10 degC, sensitivity -5 and -15 degC; at -15 degC Case A (4000 rpm, 9.5 MPa) "
           "violates Q_h and T_dis while Case B is feasible"],
    test_cases=tests,
)
with open(os.path.join(RES, "T4_handover_student5.json"), "w") as f:
    json.dump(handover, f, indent=2, default=float)

# ======================================================================================
# FIGURES
# ======================================================================================
# ---- Fig 1 : compressor map ---------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(11.2, 3.5))
a = ax[0]
for i, n in enumerate((2500.0, 4000.0, 6000.0, 8000.0)):
    rows = [r for r in map_eta if r["N"] == n]
    a.plot(col(rows, "PR_stage"), col(rows, "eta_is_s2"), color=BLUE_ORD[i + 1], label=f"{n:.0f} rpm")
    end_label(a, rows[-1]["PR_stage"], rows[-1]["eta_is_s2"], f"{n:.0f}", BLUE_ORD[i + 1])
a.axvline(cv.PR2_REF, color=MUTED, ls=(0, (4, 3)), lw=1); a.text(cv.PR2_REF, 0.455, " design PR", fontsize=7.5, color=INK2)
a.set_xlabel("stage pressure ratio [-]"); a.set_ylabel("stage isentropic efficiency [-]")
a.set_title("a  eta_is vs pressure ratio (stage 2)"); a.set_ylim(0.45, 0.76)
a = ax[1]
Ng = np.arange(2000.0, 8000.1, 100.0)
a.plot(Ng, [cv.stage_efficiency(n, cv.PR1_REF, cv.PR1_REF) for n in Ng], color=CAT[2], label="stage 1 (PR 1.5)")
a.plot(Ng, [cv.stage_efficiency(n, cv.PR2_REF, cv.PR2_REF) for n in Ng], color=CAT[0], label="stage 2 (PR 2.77)", ls="--")
for Ta, c_ in ((-15.0, CAT[1]),):
    Pe = props.Psat(bc.evap_temperature(Ta)); Pp = eev.port_pressure(Pe)
    a.plot(Ng, [cv.stage_efficiency(n, Pp / Pe, cv.PR1_REF) for n in Ng], color=c_, lw=1.2, label=f"stage 1 at {Ta:g} degC")
    a.plot(Ng, [cv.stage_efficiency(n, BRIEF["P_dis"] / Pp, cv.PR2_REF) for n in Ng], color=c_, lw=1.2, ls="--", label=f"stage 2 at {Ta:g} degC")
a.plot([4000], [0.70], "o", color=INK, ms=4, zorder=5); a.annotate("anchor 0.70", (4000, 0.70), xytext=(6, 6), textcoords="offset points", fontsize=7.5, color=INK2)
a.set_xlabel("compressor speed [rpm]"); a.set_ylabel("eta_is [-]"); a.set_title("b  eta_is vs speed"); a.legend(fontsize=7, loc="lower center")
a = ax[2]
for i, xi in enumerate((0.0, 0.2, 0.4, 0.6)):
    rows = [r for r in map_ev if r["xi"] == xi]
    a.plot(col(rows, "N"), col(rows, "eta_v"), color=BLUE_ORD[i + 1])
    end_label(a, rows[-1]["N"], rows[-1]["eta_v"], f"xi={xi:g}", BLUE_ORD[i + 1])
a.set_xlabel("compressor speed [rpm]"); a.set_ylabel("eta_v [-]"); a.set_title("c  volumetric eff. vs speed, injection ratio")
a.set_xlim(2000, 8900)
fig.tight_layout(); fig_save(fig, "fig_T4_1_compressor_map.png")

# ---- Fig 2 : cold-weather comparison ---------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(9.4, 6.4))
for a, (k, yl, ttl) in zip(ax.ravel(), (("Q_h", "heating capacity [kW]", "a  Q_h"), ("COP_h", "COP_h [-]", "b  COP_h"),
                                          ("T_dis", "discharge temperature [degC]", "c  T_dis"), ("W", "compressor power [kW]", "d  W"))):
    for rows, c_, lab in ((cwA, C_A, "A"), (cwB, C_B50, "B 50 %"), (cwB1, C_B100, "B 100 %")):
        a.plot(col(rows, "T_amb"), col(rows, k), color=c_, marker="o", ms=3, label=lab)
    a.set_xlabel("ambient temperature [degC]"); a.set_ylabel(yl); a.set_title(ttl)
    if k == "Q_h": limit_line(a, BRIEF["Q_load"], "5.0 kW target", "right", "top")
    if k == "T_dis": limit_line(a, BRIEF["T_dis_max"], "130 degC limit", "right", "bottom")
ax[0, 0].legend(loc="upper left", fontsize=7.5)
fig.suptitle("Cold-weather performance at 4000 rpm, 9.5 MPa, P_FT = 4.5 MPa", fontsize=10, fontweight="bold")
fig.tight_layout(); fig_save(fig, "fig_T4_2_cold_weather.png")

# ---- Fig 3 : stage work breakdown ------------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(9.4, 6.4))
for a, (k, yl, ttl) in zip(ax.ravel(), (("W1", "stage-1 power [kW]", "a  W1 (low stage)"), ("W2", "stage-2 power [kW]", "b  W2 (high stage)"),
                                          ("COP_h", "COP_h [-]", "c  COP_h"), ("T_dis", "discharge temperature [degC]", "d  T_dis"))):
    for i, f in enumerate(PHIS):
        rows = [r for r in SW if r["phi"] == f]
        a.plot(col(rows, "P_FT"), col(rows, k), color=BLUE_ORD[i + 1], marker="o", ms=3)
        end_label(a, rows[-1]["P_FT"], rows[-1][k], f"{f*100:.0f} %", BLUE_ORD[i + 1])
    a.set_xlabel("flash-tank pressure P_FT [MPa]"); a.set_ylabel(yl); a.set_title(ttl); a.set_xlim(3.4, 6.5)
    if k == "T_dis": limit_line(a, BRIEF["T_dis_max"], "130 degC limit", "left", "top")
fig.suptitle("Stage-work split vs P_FT and EEV opening (-10 degC, 4000 rpm)", fontsize=10, fontweight="bold")
fig.tight_layout(); fig_save(fig, "fig_T4_3_stage_work.png")

# ---- Fig 4 : speed sweep --------------------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(9.4, 6.4))
for a, (k, yl, ttl) in zip(ax.ravel(), (("Q_h", "heating capacity [kW]", "a  Q_h"), ("COP_h", "COP_h [-]", "b  COP_h"),
                                          ("T_dis", "discharge temperature [degC]", "c  T_dis"), ("eta_is2", "stage-2 eta_is [-]", "d  stage-2 efficiency"))):
    for i, Ta in enumerate(SP_T):
        for c_, ls, lab in (("B50", "-", "B"), ("A", "--", "A")):
            rows = [r for r in SP if r["T_amb"] == Ta and r["case"] == c_]
            if k == "eta_is2" and c_ == "A":
                y = col(rows, "eta_is")
            else:
                y = col(rows, k)
            a.plot(col(rows, "N"), y, color=CAT[i], ls=ls, lw=1.6)
        end_label(a, NS[-1], [r for r in SP if r["T_amb"] == Ta and r["case"] == "B50"][-1][k], f"{Ta:g} degC", CAT[i])
    a.set_xlabel("compressor speed [rpm]"); a.set_ylabel(yl); a.set_title(ttl); a.set_xlim(2400, 9200)
    if k == "Q_h": limit_line(a, BRIEF["Q_load"], "5.0 kW target", "left", "bottom")
    if k == "T_dis": limit_line(a, BRIEF["T_dis_max"], "130 degC limit", "left", "bottom")
ax[0, 0].plot([], [], color=INK2, ls="-", label="Case B (50 %)"); ax[0, 0].plot([], [], color=INK2, ls="--", label="Case A")
ax[0, 0].legend(loc="upper left", fontsize=7.5)
fig.suptitle("Compressor speed sweep (9.5 MPa, P_FT = 4.5 MPa)", fontsize=10, fontweight="bold")
fig.tight_layout(); fig_save(fig, "fig_T4_4_speed_sweep.png")

# ---- Fig 5 : discharge-pressure sweep ---------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(11.2, 3.5))
for a, (k, yl, ttl) in zip(ax, (("Q_h", "heating capacity [kW]", "a  Q_h"), ("COP_h", "COP_h [-]", "b  COP_h"),
                                  ("T_dis", "discharge temperature [degC]", "c  T_dis"))):
    for i, Ta in enumerate(PD_T):
        for c_, ls in (("B50", "-"), ("A", "--")):
            rows = [r for r in PS if r["T_amb"] == Ta and r["case"] == c_]
            a.plot(col(rows, "P_dis"), col(rows, k), color=CAT[i], ls=ls)
        end_label(a, PD[-1], [r for r in PS if r["T_amb"] == Ta and r["case"] == "B50"][-1][k], f"{Ta:g} degC", CAT[i])
    a.set_xlabel("discharge pressure [MPa]"); a.set_ylabel(yl); a.set_title(ttl); a.set_xlim(7.4, 13.6)
    vline(a, BRIEF["P_max"], "12 MPa limit", "bottom")
    if k == "Q_h": limit_line(a, BRIEF["Q_load"], "5.0 kW target", "left", "bottom")
    if k == "T_dis": limit_line(a, BRIEF["T_dis_max"], "130 degC limit", "left", "bottom")
ax[0].plot([], [], color=INK2, ls="-", label="Case B (50 %)"); ax[0].plot([], [], color=INK2, ls="--", label="Case A"); ax[0].legend(fontsize=7.5)
fig.tight_layout(); fig_save(fig, "fig_T4_5_discharge_pressure.png")

# ---- Fig 6 : operating envelopes -------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(11.6, 3.7))
cmap = ListedColormap(["#e8e7e0", "#a6dcc4"])
for a, c_, ttl in ((ax[0], "A", "a  Case A: feasible region"), (ax[1], "B50", "b  Case B: feasible region")):
    rows = [r for r in EV1 if r["case"] == c_]
    Z = np.array([[next(r for r in rows if r["T_amb"] == Ta and r["N"] == n) for n in NE] for Ta in TAMB_MAP], dtype=object)
    feas = np.vectorize(lambda r: float(r["feasible"]))(Z)
    Qh = np.vectorize(lambda r: r["Q_h"])(Z); Td = np.vectorize(lambda r: r["T_dis"])(Z)
    a.pcolormesh(NE, TAMB_MAP, feas, cmap=cmap, vmin=0, vmax=1, shading="nearest")
    cs1 = a.contour(NE, TAMB_MAP, Qh, levels=[BRIEF["Q_load"]], colors=[CAT[0]], linewidths=1.4)
    cs2 = a.contour(NE, TAMB_MAP, Td, levels=[BRIEF["T_dis_max"]], colors=[CAT[1]], linewidths=1.4)
    a.clabel(cs1, fmt="Q = 5 kW", fontsize=7); a.clabel(cs2, fmt="T = 130 C", fontsize=7)
    a.set_xlabel("compressor speed [rpm]"); a.set_ylabel("ambient temperature [degC]"); a.set_title(ttl); a.grid(False)
a = ax[2]
Z = np.array([[next(r for r in EV2 if r["P_dis"] == float(d) and r["P_FT"] == float(p)) for p in PFT_E] for d in PD_E], dtype=object)
feas = np.vectorize(lambda r: float(r["feasible"]))(Z); Td = np.vectorize(lambda r: r["T_dis"])(Z); Qh = np.vectorize(lambda r: r["Q_h"])(Z)
a.pcolormesh(PFT_E, PD_E, feas, cmap=cmap, vmin=0, vmax=1, shading="nearest")
cs = a.contour(PFT_E, PD_E, Td, levels=[BRIEF["T_dis_max"]], colors=[CAT[1]], linewidths=1.4); a.clabel(cs, fmt="T = 130 C", fontsize=7)
cs = a.contour(PFT_E, PD_E, Qh, levels=[BRIEF["Q_load"]], colors=[CAT[0]], linewidths=1.4); a.clabel(cs, fmt="Q = 5 kW", fontsize=7)
a.axhline(BRIEF["P_max"], color=MUTED, ls=(0, (4, 3)), lw=1); a.text(PFT_E[0], BRIEF["P_max"], " 12 MPa limit", va="bottom", fontsize=7.5, color=INK2)
a.set_xlabel("flash-tank pressure P_FT [MPa]"); a.set_ylabel("discharge pressure [MPa]"); a.set_title("c  Case B at -15 degC, 4000 rpm"); a.grid(False)
fig.tight_layout(); fig_save(fig, "fig_T4_6_operating_envelope.png")

# ---- Fig 7 : load-matched speed -------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(11.2, 3.5))
for a, (k, yl, ttl) in zip(ax, (("N_req", "speed to deliver 5.0 kW [rpm]", "a  required speed"),
                                  ("W", "compressor power at 5.0 kW [kW]", "b  power at load"),
                                  ("T_dis", "discharge temperature [degC]", "c  T_dis at load"))):
    for c_, col_, lab in (("A", C_A, "A"), ("B50", C_B50, "B 50 %"), ("B100", C_B100, "B 100 %")):
        rows = [r for r in LM if r["case"] == c_ and r["reaches_load"]]
        a.plot(col(rows, "T_amb"), col(rows, k), color=col_, marker="o", ms=3)
        end_label(a, rows[0]["T_amb"], rows[0][k], lab, col_)
    a.set_xlabel("ambient temperature [degC]"); a.set_ylabel(yl); a.set_title(ttl); a.set_xlim(-16.5, -3.5)
    if k == "N_req": limit_line(a, BRIEF["N_max"], "8000 rpm limit", "right", "top")
    if k == "T_dis": limit_line(a, BRIEF["T_dis_max"], "130 degC limit", "right", "bottom")
fig.tight_layout(); fig_save(fig, "fig_T4_7_load_matched.png")

# ---- Fig 8 : P-h diagram (design point, A vs B) ------------------------------------------------
fig, a = plt.subplots(figsize=(6.4, 4.6))
Pd = np.linspace(0.8, 7.3, 80)
a.plot([props.hf(p) for p in Pd], Pd, color=MUTED, lw=1.2); a.plot([props.hg(p) for p in Pd], Pd, color=MUTED, lw=1.2)
Ad = A1
a.plot([Ad["h1"], Ad["h2"], Ad["h3"], Ad["h4"], Ad["h1"]], [Ad["P_evap"], Ad["P_dis"], Ad["P_dis"], Ad["P_evap"], Ad["P_evap"]],
       color=C_A, marker="o", ms=3, label="Case A")
a.plot([D["h1"], D["h2"], D["h3"], D["h4"]], [D["P_evap"], D["P_port"], D["P_port"], D["P_dis"]], color=C_B50, marker="o", ms=3, label="Case B compression")
a.plot([D["h4"], D["h5"], D["h6"], D["h8"], D["h9"], D["h1"]], [D["P_dis"], D["P_dis"], D["P_FT"], D["P_FT"], D["P_evap"], D["P_evap"]],
       color=C_B50, marker="o", ms=3)
a.plot([D["h6"], D["h7"], D["h7a"], D["h3"]], [D["P_FT"], D["P_FT"], D["P_port"], D["P_port"]], color=C_B100, marker="o", ms=3, ls="--", label="injection branch")
for nm, hh, pp in (("1", D["h1"], D["P_evap"]), ("2", D["h2"], D["P_port"]), ("3", D["h3"], D["P_port"]), ("4", D["h4"], D["P_dis"]),
                   ("5", D["h5"], D["P_dis"]), ("6", D["h6"], D["P_FT"]), ("7", D["h7"], D["P_FT"]), ("8", D["h8"], D["P_FT"]), ("9", D["h9"], D["P_evap"])):
    a.annotate(nm, (hh, pp), xytext=(3, 3), textcoords="offset points", fontsize=7.5, color=INK2)
a.set_yscale("log"); a.set_yticks([1, 2, 3, 4.5, 7, 10]); a.set_yticklabels(["1", "2", "3", "4.5", "7", "10"])
a.set_xlabel("specific enthalpy [kJ/kg]"); a.set_ylabel("pressure [MPa]"); a.set_title("P-h diagram, -10 degC, 4000 rpm, S4 compressor map")
a.legend(fontsize=7.5, loc="upper left")
fig.tight_layout(); fig_save(fig, "fig_T4_8_ph.png")

# ======================================================================================
# summary file + console
# ======================================================================================
with open(os.path.join(RES, "T4_summary.json"), "w") as f:
    json.dump(R, f, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else (bool(o) if isinstance(o, np.bool_) else str(o)))

print("Backend:", props.name)
print("Regression vs Student 3 (map OFF): max rel diff = %.2e ; Case A = %.2e" % (R["validation_max_rel_diff"], R["validation_caseA_rel_diff"]))
print("\nDesign point (-10 degC, 4000 rpm, 9.5 MPa, P_FT 4.5 MPa, 50 %):")
for r in dp:
    print("  %-20s Q=%.3f W=%.3f COP=%.3f Tdis=%.1f xi=%.3f eta_v=%.3f %s" % (r["case"], r["Q_h"], r["W"], r["COP_h"], r["T_dis"], r["xi"], r["eta_v"], r["violations"]))
print("\nCold weather @4000 rpm (A | B50 | B100):")
for a_, b_, c_ in zip(cwA, cwB, cwB1):
    print("  %6.1f  A Q%.2f COP%.2f T%.0f [%s] | B Q%.2f COP%.2f T%.0f [%s] | B100 Q%.2f T%.0f" % (
        a_["T_amb"], a_["Q_h"], a_["COP_h"], a_["T_dis"], a_["violations"], b_["Q_h"], b_["COP_h"], b_["T_dis"], b_["violations"], c_["Q_h"], c_["T_dis"]))
print("Feasible @4000 rpm:", R["feasible_4000rpm"])
print("\nLoad-matched speed (5.0 kW):")
for Ta in TAMB:
    s = []
    for c_ in ("A", "B50"):
        r = next(r for r in LM if r["T_amb"] == Ta and r["case"] == c_)
        s.append("%s N=%s W=%.2f COP=%.2f T=%.0f [%s]" % (c_, "%.0f" % r["N_req"] if r["reaches_load"] else "n/a", r["W"], r["COP_h"], r["T_dis"], r["violations"]))
    print("  %5.1f  %s" % (Ta, " | ".join(s)))
print("\nBest COP in stage-work grid:", R["stage_work_best_COP"])
for k in sorted(k for k in R if k.startswith("pdis_opt")): print(" ", k, R[k])
print("Envelope feasible fraction:", R["envelope_feasible_fraction"])
print("\nResults ->", RES, "\nFigures ->", FIG)
