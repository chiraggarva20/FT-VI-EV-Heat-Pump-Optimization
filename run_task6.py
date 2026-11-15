"""
run_task6.py -- STUDENT 6 : Case C (two-stage intercooled) studies, CSV results, figures, hand-over file.
Usage:  python run_task6.py      (needs CoolProp for report numbers; same backend logic as run_all.py)
Outputs go to  results_task6/  and  figures_task6/   (same naming scheme as Task 4)

Studies (every point is load-matched: compressor speed is solved so that USEFUL heat = 5.0 kW)
  1  intermediate-pressure x intercooler-outlet-temperature sweep at -5 / -10 / -15 degC,
     for both intercooler options (reject to ambient / preheat cabin air)
  2  feasible optimum per ambient and option (+ local refinement), compared with sqrt(P_evap * P_dis)
  3  intercooler outlet-temperature sensitivity at P_i = 4.5 MPa (-10 degC)
  4  Case A / Case B / Case C at equal 5.0 kW, from the SAME repository functions (Student 4's)
  5  hand-over to Student 5
"""
import os, csv, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import BRIEF, ASSUME, SENS_AMBIENTS
from co2_props import get_props
import baseline_cycle as bc
import compressor_vi as cv
import two_stage_intercooled as ts

props = get_props()
HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, "results_task6"), os.path.join(HERE, "figures_task6")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)

SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": AXIS,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.grid": True, "grid.color": GRID, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})

MODES = ("reject", "recover")
MODE_LABEL = {"reject": "IC heat rejected to ambient", "recover": "IC heat preheats cabin air"}
P_GRID = np.round(np.arange(3.5, 6.0 + 1e-9, 0.1), 3)       # brief: 3.5 - 6.0 MPa
N_TIC = 14                                                   # intercooler-outlet temperatures per pressure
SOFT_ERR = (ValueError, ArithmeticError, OverflowError, RuntimeError)
KEYS = ["T_amb", "mode", "P_i", "T_ic", "N", "Q_h", "W", "W1", "W2", "COP_h", "Q_ic", "Q_gc", "T2", "T_dis",
        "m_dot", "eta1", "eta2", "eta_v", "T_air_gc_in", "T_air_out", "energy_balance_err",
        "pressure_geomean", "feasible", "violations"]


def save_csv(name, rows, keys=None):
    if not rows:
        return
    keys = keys or list(rows[0])
    with open(os.path.join(RES, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def solve(amb, P, T, mode):
    try:
        return ts.solve_for_load(amb, float(P), float(T), mode)
    except SOFT_ERR:
        return None


# ----------------------------- 1. coarse sweep ------------------------------------------------
sweep, windows = [], {}
for amb in SENS_AMBIENTS:
    for mode in MODES:
        for P in P_GRID:
            try:
                lo, hi = ts.T_ic_window(amb, float(P), mode)
            except SOFT_ERR:
                continue
            if hi <= lo:
                continue
            windows[(amb, mode, float(P))] = (lo, hi)
            for T in np.linspace(lo, hi, N_TIC):
                r = solve(amb, P, T, mode)
                if r is not None:
                    sweep.append(r)
save_csv("case_c_sweep.csv", sweep, KEYS)
print("sweep points:", len(sweep))

# ----------------------------- 2. optima (+ local refinement) ---------------------------------
optima, profile = {}, []
for amb in SENS_AMBIENTS:
    for mode in MODES:
        rows = [r for r in sweep if r["T_amb"] == amb and r["mode"] == mode]
        for P in P_GRID:                                    # best feasible COP at each pressure
            g = [r for r in rows if abs(r["P_i"] - P) < 1e-9 and r["feasible"]]
            if g:
                b = max(g, key=lambda r: r["COP_h"])
                profile.append(dict(T_amb=amb, mode=mode, P_i=float(P), T_ic=b["T_ic"], COP_h=b["COP_h"],
                                    N=b["N"], T_dis=b["T_dis"], Q_ic=b["Q_ic"]))
        feas = [r for r in rows if r["feasible"]]
        if not feas:
            print("No feasible 5-kW point (N <= %d rpm, T_dis <= %d C): T_amb = %g, %s"
                  % (BRIEF["N_max"], BRIEF["T_dis_max"], amb, mode))
            optima[(amb, mode)] = None
            continue
        best = max(feas, key=lambda r: r["COP_h"])
        lo, hi = windows[(amb, mode, best["P_i"])]
        dT = (hi - lo) / (N_TIC - 1)
        cand = [best]
        for P in np.arange(max(3.5, best["P_i"] - 0.1), min(6.0, best["P_i"] + 0.1) + 1e-9, 0.02):
            try:
                lo2, hi2 = ts.T_ic_window(amb, float(P), mode)
            except SOFT_ERR:
                continue
            for T in np.arange(max(lo2, best["T_ic"] - dT), min(hi2, best["T_ic"] + dT) + 1e-9, dT / 6):
                r = solve(amb, P, T, mode)
                if r is not None and r["feasible"]:
                    cand.append(r)
        best = max(cand, key=lambda r: r["COP_h"])
        lo, hi = ts.T_ic_window(amb, best["P_i"], mode)
        best = dict(best)
        best["at_P_edge"] = bool(best["P_i"] <= 3.5 + 1e-9 or best["P_i"] >= 6.0 - 1e-9)
        best["at_Tic_lower_bound"] = bool(best["T_ic"] <= lo + 0.05)
        best["at_Tic_upper_bound"] = bool(best["T_ic"] >= hi - 0.05)
        optima[(amb, mode)] = best
save_csv("case_c_Pi_profile.csv", profile)
opt_rows = [o for o in optima.values() if o]
save_csv("case_c_optima.csv", opt_rows,
         KEYS + ["at_P_edge", "at_Tic_lower_bound", "at_Tic_upper_bound"])

# ----------------------------- 3. T_ic sensitivity at 4.5 MPa, -10 degC ------------------------
sens = []
for mode in MODES:
    lo, hi = ts.T_ic_window(-10.0, BRIEF["P_inj"], mode)
    for T in np.linspace(lo, hi, 16):
        r = solve(-10.0, BRIEF["P_inj"], T, mode)
        if r is not None:
            sens.append(r)
save_csv("case_c_Tic_sensitivity_4p5MPa.csv", sens, KEYS)

# ----------------------------- 4. A / B / C at equal 5.0 kW -----------------------------------
def tagrow(r, case, amb, N_req, note=""):
    return dict(T_amb=amb, case=case, N_required=N_req, Q_h=r["Q_h"], W=r["W"], COP_h=r["COP_h"],
                T_dis=r["T_dis"], P_i=r.get("P_i", r.get("P_FT", float("nan"))), T_ic=r.get("T_ic", float("nan")),
                Q_ic=r.get("Q_ic", float("nan")), feasible=r["feasible"], violations=r.get("violations", ""),
                note=note)


comp = []
for amb in SENS_AMBIENTS:
    Te = bc.evap_temperature(amb)
    for name, fn, kw in (("A", cv.baseline_real, {}),
                         ("B (phi 50 %)", cv.ftvi_real, dict(phi=0.5)),
                         ("B (phi 100 %)", cv.ftvi_real, dict(phi=1.0))):
        try:
            n, r = cv.required_speed(fn, T_evap=Te, **kw)
            comp.append(tagrow(r, name, amb, n if n else float("nan"),
                               "" if n else "5 kW not reachable up to N_max; row shown at N_max"))
        except SOFT_ERR as e:
            comp.append(dict(T_amb=amb, case=name, note="not evaluated: %s" % e))
    for mode in MODES:
        o = optima.get((amb, mode))
        if o:
            comp.append(tagrow(o, "C (%s)" % mode, amb, o["N"]))
        else:
            comp.append(dict(T_amb=amb, case="C (%s)" % mode, note="no feasible 5-kW point"))
save_csv("case_c_comparison.csv", comp,
         ["T_amb", "case", "N_required", "Q_h", "W", "COP_h", "T_dis", "P_i", "T_ic", "Q_ic",
          "feasible", "violations", "note"])

# ----------------------------- checks ---------------------------------------------------------
eb = max(abs(r["energy_balance_err"]) for r in sweep)
print("max |energy balance| over sweep = %.2e kW" % eb)
assert eb < 1e-9, "energy balance violated"
print("\nOptima (equal 5 kW):")
for (amb, mode), o in optima.items():
    if o:
        print("  %5.0f degC  %-8s P_i=%.2f MPa  T_ic=%.1f C  N=%.0f rpm  COP=%.3f  W=%.3f kW  T_dis=%.1f C  Q_ic=%.3f kW  (geo-mean %.2f)"
              % (amb, mode, o["P_i"], o["T_ic"], o["N"], o["COP_h"], o["W"], o["T_dis"], o["Q_ic"], o["pressure_geomean"]))

# ----------------------------- figures --------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 3.6), sharey=False)
for ax, amb in zip(axs, SENS_AMBIENTS):
    for c, mode in zip(CAT, MODES):
        pr = [p for p in profile if p["T_amb"] == amb and p["mode"] == mode]
        if pr:
            ax.plot([p["P_i"] for p in pr], [p["COP_h"] for p in pr], color=c, lw=1.8, label=MODE_LABEL[mode])
        o = optima.get((amb, mode))
        if o:
            ax.plot(o["P_i"], o["COP_h"], "o", color=c, ms=6)
    geo = math.sqrt(props.Psat(bc.evap_temperature(amb)) * BRIEF["P_dis"])
    ax.axvline(geo, color=CAT[2], ls=":", lw=1.2, label="sqrt(P_evap P_dis) = %.2f" % geo)
    ax.set_title("T_amb = %g C" % amb); ax.set_xlabel("Intermediate pressure P_i [MPa]")
axs[0].set_ylabel("COP_h at 5.0 kW (best T_ic at each P_i)"); axs[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "T6_pressure_sweep.png"), dpi=170); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
cases = []
for row in comp:
    if row["case"] not in cases:
        cases.append(row["case"])
w = 0.8 / len(cases)
for i, cs in enumerate(cases):
    for ax, key in zip(axs, ("COP_h", "N_required")):
        vals = [next((r.get(key, float("nan")) for r in comp if r["T_amb"] == a and r["case"] == cs), float("nan"))
                for a in SENS_AMBIENTS]
        ax.bar(np.arange(3) + i * w, [v if v == v else 0 for v in vals], w * 0.92, color=CAT[i % 8], label=cs)
for ax, t in zip(axs, ("COP_h at 5.0 kW useful heat", "Compressor speed needed for 5.0 kW [rpm]")):
    ax.set_xticks(np.arange(3) + w * (len(cases) - 1) / 2); ax.set_xticklabels(["%g C" % a for a in SENS_AMBIENTS])
    ax.set_title(t)
axs[0].legend(fontsize=7, ncol=2)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "T6_comparison_A_B_C.png"), dpi=170); plt.close(fig)

fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
for c, mode in zip(CAT, MODES):
    s = [r for r in sens if r["mode"] == mode]
    for ax, key in zip(axs, ("COP_h", "Q_ic", "T_dis")):
        ax.plot([r["T_ic"] for r in s], [r[key] for r in s], color=c, lw=1.8, label=MODE_LABEL[mode])
for ax, t in zip(axs, ("COP_h", "Q_ic [kW]", "T_dis [C]")):
    ax.set_ylabel(t); ax.set_xlabel("Intercooler outlet temperature T_ic [C]")
axs[0].set_title("P_i = 4.5 MPa, -10 C, speed solved for 5.0 kW"); axs[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "T6_Tic_sensitivity.png"), dpi=170); plt.close(fig)

# ----------------------------- 5. hand-over to Student 5 --------------------------------------
hand = dict(
    student="6", case="C two-stage intercooled", backend=props.name, basis="equal 5.0 kW useful heat, speed solved",
    function="two_stage_intercooled.case_c(T_amb, P_i, T_ic, N, mode) / solve_for_load(T_amb, P_i, T_ic, mode)",
    assumptions=dict(ts.S6, m_air_gc=ASSUME["m_air_gc"], m_vent=ASSUME["m_vent"], T_recirc=ASSUME["T_air_gc_in"]),
    optima={"%g_%s" % k: ({kk: (v if not isinstance(v, (np.floating, np.bool_)) else v.item())
                           for kk, v in o.items() if kk in KEYS + ["at_P_edge", "at_Tic_lower_bound", "at_Tic_upper_bound"]}
                          if o else None) for k, o in optima.items()},
)
with open(os.path.join(RES, "hand_over_student5_task6.json"), "w") as f:
    json.dump(hand, f, indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x))
print("\nBackend:", props.name, "| results ->", RES, "| figures ->", FIG)
