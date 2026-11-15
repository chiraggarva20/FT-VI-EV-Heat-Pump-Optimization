"""
run_task4.py — Student 4: Comprehensive Compressor & Heating Performance Studies
================================================================================
Generates:
  results_task4/
    - T4_design_point_comparison.csv     (Baseline vs Constant-eta FT-VI vs Realistic-Map FT-VI)
    - T4_cold_weather_comparison.csv     (Baseline vs FT-VI across T_amb = -25 C to 0 C)
    - T4_speed_sweep.csv                 (Compressor RPM sweep 2500 to 8000 rpm)
    - T4_pdis_sweep.csv                  (Discharge pressure sweep 7.5 to 12.5 MPa)
    - T4_pft_phi_operating_limits.csv    (2D envelope of T_dis, Q_h, COP_h, and constraint flags)
    - T4_summary.json                    (Complete numerical summary for report)
    - T4_handover_student5.json          (Compressor map & constraint bounds for Student 5)
  figures_task4/
    - fig_T4_1_compressor_map.png        (Stage efficiencies eta_v, eta_is1, eta_is2 vs speed & PR)
    - fig_T4_2_cold_weather_compare.png  (Baseline vs FT-VI Q_h, COP_h, T_dis, W across T_amb)
    - fig_T4_3_stage_work_breakdown.png  (Stage 1 vs Stage 2 work & specific work vs P_FT & phi)
    - fig_T4_4_speed_performance.png     (Heating capacity, COP, discharge temp & limits vs RPM)
    - fig_T4_5_discharge_pressure.png    (High-side P_dis sweep: COP peak vs T_dis & P_max limits)
    - fig_T4_6_operating_envelope.png    (2D feasibility map in (T_amb, N) & (P_FT, P_dis) space)
"""

import os
import json
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import BRIEF, ASSUME
from baseline_cycle import baseline_cycle, calibrate_displacement
import eev
import ftvi_eev as fe
import compressor_vi as cvi

os.makedirs("results_task4", exist_ok=True)
os.makedirs("figures_task4", exist_ok=True)

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 8.5,
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3,
})


def save_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    V_disp = calibrate_displacement()
    T_evap_des = BRIEF["T_amb"] - ASSUME["dT_evap_approach"]

    # 1. Design Point Comparison (Baseline vs Task 3 Stub vs Task 4 Realistic Compressor)
    base_des = baseline_cycle(T_evap=T_evap_des, P_dis=BRIEF["P_dis"], T_gc_out=BRIEF["T_gc_out"], N=BRIEF["N"], V_disp=V_disp)
    t3_des = cvi.evaluate_ftvi_compressor(use_realistic_map=False)
    t4_des = cvi.evaluate_ftvi_compressor(use_realistic_map=True)

    design_rows = [
        {
            "Model": "Student 1: Baseline Single-Stage",
            "m_suc_gps": round(base_des["m_dot"] * 1e3, 3),
            "m_inj_gps": 0.0,
            "xi": 0.0,
            "eta_v": round(base_des["eta_v"], 4),
            "W1_kW": round(base_des["W"], 4),
            "W2_kW": 0.0,
            "W_tot_kW": round(base_des["W"], 4),
            "Q_h_kW": round(base_des["Q_h"], 4),
            "Q_e_kW": round(base_des["Q_e"], 4),
            "COP_h": round(base_des["COP_h"], 4),
            "T_dis_C": round(base_des["T_dis"], 2),
            "Feasible": base_des["feasible"],
        },
        {
            "Model": "Student 3: FT-VI (phi=50%, Const eta_is)",
            "m_suc_gps": round(t3_des["m_suc"] * 1e3, 3),
            "m_inj_gps": round(t3_des["m_inj"] * 1e3, 3),
            "xi": round(t3_des["xi"], 4),
            "eta_v": round(t3_des["eta_v"], 4),
            "W1_kW": round(t3_des["W1"], 4),
            "W2_kW": round(t3_des["W2"], 4),
            "W_tot_kW": round(t3_des["W"], 4),
            "Q_h_kW": round(t3_des["Q_h"], 4),
            "Q_e_kW": round(t3_des["Q_e"], 4),
            "COP_h": round(t3_des["COP_h"], 4),
            "T_dis_C": round(t3_des["T_dis"], 2),
            "Feasible": t3_des["all_limits_ok"],
        },
        {
            "Model": "Student 4: FT-VI (phi=50%, Realistic Map)",
            "m_suc_gps": round(t4_des["m_suc"] * 1e3, 3),
            "m_inj_gps": round(t4_des["m_inj"] * 1e3, 3),
            "xi": round(t4_des["xi"], 4),
            "eta_v": round(t4_des["eta_v"], 4),
            "W1_kW": round(t4_des["W1"], 4),
            "W2_kW": round(t4_des["W2"], 4),
            "W_tot_kW": round(t4_des["W"], 4),
            "Q_h_kW": round(t4_des["Q_h"], 4),
            "Q_e_kW": round(t4_des["Q_e"], 4),
            "COP_h": round(t4_des["COP_h"], 4),
            "T_dis_C": round(t4_des["T_dis"], 2),
            "Feasible": t4_des["all_limits_ok"],
        },
    ]
    save_csv("results_task4/T4_design_point_comparison.csv", design_rows)

    # 2. Cold-Weather Comparison (-25 C to 0 C)
    T_amb_grid = np.linspace(-25.0, 0.0, 26)
    cold_rows = cvi.compare_baseline_vs_ftvi(T_amb_list=T_amb_grid, P_FT=4.5, phi=0.50, N=4000.0)
    save_csv("results_task4/T4_cold_weather_comparison.csv", cold_rows)

    # 3. Compressor Speed Sweep (2500 to 8000 rpm at T_amb = -10 C and -20 C)
    N_grid = np.linspace(BRIEF["N_min"], BRIEF["N_max"], 23)
    speed_rows = []
    for T_amb in (-10.0, -20.0):
        T_evap = T_amb - ASSUME["dT_evap_approach"]
        for N_val in N_grid:
            b = baseline_cycle(T_evap=T_evap, P_dis=BRIEF["P_dis"], T_gc_out=BRIEF["T_gc_out"], N=N_val, V_disp=V_disp)
            f50 = cvi.evaluate_ftvi_compressor(T_amb=T_amb, P_FT=4.5, phi=0.50, N=N_val, V_disp=V_disp)
            f80 = cvi.evaluate_ftvi_compressor(T_amb=T_amb, P_FT=4.5, phi=0.80, N=N_val, V_disp=V_disp)
            speed_rows.append({
                "T_amb_C": T_amb,
                "N_rpm": round(float(N_val), 1),
                "Base_Q_h_kW": round(b["Q_h"], 4),
                "Base_COP_h": round(b["COP_h"], 4),
                "Base_T_dis_C": round(b["T_dis"], 2),
                "FTVI50_Q_h_kW": round(f50["Q_h"], 4),
                "FTVI50_W_kW": round(f50["W"], 4),
                "FTVI50_COP_h": round(f50["COP_h"], 4),
                "FTVI50_T_dis_C": round(f50["T_dis"], 2),
                "FTVI50_xi": round(f50["xi"], 4),
                "FTVI50_eta_is1": round(f50["eta_is1"], 4),
                "FTVI50_eta_is2": round(f50["eta_is2"], 4),
                "FTVI50_OK": f50["all_limits_ok"],
                "FTVI80_Q_h_kW": round(f80["Q_h"], 4),
                "FTVI80_COP_h": round(f80["COP_h"], 4),
                "FTVI80_T_dis_C": round(f80["T_dis"], 2),
                "FTVI80_OK": f80["all_limits_ok"],
            })
    save_csv("results_task4/T4_speed_sweep.csv", speed_rows)

    # 4. Discharge Pressure Sweep (7.5 to 12.5 MPa)
    P_dis_grid = np.linspace(7.5, 12.5, 21)
    pdis_rows = []
    for P_d in P_dis_grid:
        b = baseline_cycle(T_evap=T_evap_des, P_dis=float(P_d), T_gc_out=BRIEF["T_gc_out"], N=4000.0, V_disp=V_disp)
        f = cvi.evaluate_ftvi_compressor(T_amb=-10.0, P_FT=4.5, phi=0.50, P_dis=float(P_d), N=4000.0, V_disp=V_disp)
        pdis_rows.append({
            "P_dis_MPa": round(float(P_d), 3),
            "Base_Q_h_kW": round(b["Q_h"], 4),
            "Base_COP_h": round(b["COP_h"], 4),
            "Base_T_dis_C": round(b["T_dis"], 2),
            "Base_OK": b["feasible"],
            "FTVI_Q_h_kW": round(f["Q_h"], 4),
            "FTVI_W_kW": round(f["W"], 4),
            "FTVI_COP_h": round(f["COP_h"], 4),
            "FTVI_T_dis_C": round(f["T_dis"], 2),
            "FTVI_PR_tot": round(f["PR_total"], 3),
            "FTVI_OK": f["all_limits_ok"],
            "Violations": f["violations"],
        })
    save_csv("results_task4/T4_pdis_sweep.csv", pdis_rows)

    # 5. Operating Limits Grid across (P_FT, phi)
    P_FT_grid = np.linspace(3.5, 6.0, 11)
    phi_grid = np.linspace(0.0, 1.0, 11)
    limit_rows = []
    for pft in P_FT_grid:
        for ph in phi_grid:
            f = cvi.evaluate_ftvi_compressor(T_amb=-10.0, P_FT=float(pft), phi=float(ph), N=4000.0, V_disp=V_disp)
            limit_rows.append({
                "P_FT_MPa": round(float(pft), 2),
                "phi": round(float(ph), 2),
                "W1_kW": round(f["W1"], 4),
                "W2_kW": round(f["W2"], 4),
                "W_tot_kW": round(f["W"], 4),
                "Q_h_kW": round(f["Q_h"], 4),
                "COP_h": round(f["COP_h"], 4),
                "T_dis_C": round(f["T_dis"], 2),
                "ok_T_dis": f["ok_T_dis"],
                "ok_Q_load": f["ok_Q_load"],
                "all_limits_ok": f["all_limits_ok"],
            })
    save_csv("results_task4/T4_pft_phi_operating_limits.csv", limit_rows)

    # =========================================================================
    # GENERATE 6 FIGURES
    # =========================================================================

    # Fig 1: Compressor efficiency map vs Speed
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    speeds = np.linspace(2500, 8000, 50)
    eta1_curve = [cvi.stage_isentropic_efficiency(n, 1.50, PR_stage_ref=1.50) for n in speeds]
    eta2_curve = [cvi.stage_isentropic_efficiency(n, 2.78, PR_stage_ref=2.78) for n in speeds]
    ax1.plot(speeds, eta1_curve, label="Stage 1 Isentropic Eff. (PR1 = 1.50)", lw=2)
    ax1.plot(speeds, eta2_curve, "--", label="Stage 2 Isentropic Eff. (PR2 = 2.78)", lw=2)
    ax1.axvline(4000, color="gray", ls=":", label="Design Speed (4000 rpm)")
    ax1.set_xlabel("Compressor Speed N (rpm)")
    ax1.set_ylabel("Isentropic Efficiency (-)")
    ax1.set_title("Stage Isentropic Efficiency vs. Speed")
    ax1.legend()

    xis = np.linspace(0.0, 0.7, 50)
    for pr_tot, lbl in [(3.5, "PR_tot = 3.5"), (4.17, "PR_tot = 4.17 (Design)"), (5.2, "PR_tot = 5.2 (-20 C)")]:
        etav_curve = [(ASSUME["EVO"] - ASSUME["EV1"] * pr_tot) * (1.0 - cvi.COMP_MAP["k_leak_vi"] * x) for x in xis]
        ax2.plot(xis, etav_curve, lw=2, label=lbl)
    ax2.set_xlabel("Injection Mass Ratio xi = m_inj / m_suc (-)")
    ax2.set_ylabel("Effective Volumetric Efficiency eta_v (-)")
    ax2.set_title("Volumetric Efficiency with VI Back-Leakage")
    ax2.legend()
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_1_compressor_map.png")
    plt.close()

    # Fig 2: Cold-Weather Performance Comparison (Baseline vs FT-VI)
    Tamb_arr = [r["T_amb_C"] for r in cold_rows]
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    axs[0, 0].plot(Tamb_arr, [r["Base_Q_h_kW"] for r in cold_rows], "o--", label="Baseline Single-Stage")
    axs[0, 0].plot(Tamb_arr, [r["FTVI_Q_h_kW"] for r in cold_rows], "s-", label="FT-VI (phi=50%, P_FT=4.5 MPa)")
    axs[0, 0].axhline(BRIEF["Q_load"], color="r", ls=":", label="Cabin Heating Load (5.0 kW)")
    axs[0, 0].set_ylabel("Heating Capacity Q_h (kW)")
    axs[0, 0].set_title("Useful Heating Capacity vs. Ambient Temp")
    axs[0, 0].legend()

    axs[0, 1].plot(Tamb_arr, [r["Base_COP_h"] for r in cold_rows], "o--", label="Baseline Single-Stage")
    axs[0, 1].plot(Tamb_arr, [r["FTVI_COP_h"] for r in cold_rows], "s-", label="FT-VI (phi=50%, P_FT=4.5 MPa)")
    axs[0, 1].set_ylabel("Heating COP (-)")
    axs[0, 1].set_title("Heating COP vs. Ambient Temp")
    axs[0, 1].legend()

    axs[1, 0].plot(Tamb_arr, [r["Base_T_dis_C"] for r in cold_rows], "o--", label="Baseline Single-Stage")
    axs[1, 0].plot(Tamb_arr, [r["FTVI_T_dis_C"] for r in cold_rows], "s-", label="FT-VI (phi=50%, P_FT=4.5 MPa)")
    axs[1, 0].axhline(BRIEF["T_dis_max"], color="r", ls=":", label="Max Discharge Temp (130 C)")
    axs[1, 0].set_xlabel("Ambient Temperature T_amb (C)")
    axs[1, 0].set_ylabel("Discharge Temperature T_dis (C)")
    axs[1, 0].set_title("Compressor Discharge Temp vs. Ambient Temp")
    axs[1, 0].legend()

    axs[1, 1].plot(Tamb_arr, [r["Base_W_kW"] for r in cold_rows], "o--", label="Baseline Single-Stage")
    axs[1, 1].plot(Tamb_arr, [r["FTVI_W_kW"] for r in cold_rows], "s-", label="FT-VI (phi=50%, P_FT=4.5 MPa)")
    axs[1, 1].set_xlabel("Ambient Temperature T_amb (C)")
    axs[1, 1].set_ylabel("Compressor Power W (kW)")
    axs[1, 1].set_title("Total Compressor Power vs. Ambient Temp")
    axs[1, 1].legend()
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_2_cold_weather_compare.png")
    plt.close()

    # Fig 3: Stage 1 vs Stage 2 Work Breakdown across EEV Opening
    phis = np.linspace(0.0, 1.0, 21)
    w1s, w2s, wtots, cops = [], [], [], []
    for ph in phis:
        r = cvi.evaluate_ftvi_compressor(phi=float(ph))
        w1s.append(r["W1"])
        w2s.append(r["W2"])
        wtots.append(r["W"])
        cops.append(r["COP_h"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    ax1.plot(phis * 100, w1s, label="Stage 1 Power W1 (Suction -> Port)", lw=2)
    ax1.plot(phis * 100, w2s, label="Stage 2 Power W2 (Port -> Discharge)", lw=2)
    ax1.plot(phis * 100, wtots, "k--", label="Total Power W = W1 + W2", lw=2)
    ax1.axvline(50, color="gray", ls=":", label="Design Opening (50%)")
    ax1.set_xlabel("Injection EEV Opening phi (%)")
    ax1.set_ylabel("Compressor Power (kW)")
    ax1.set_title("Stage-by-Stage Compressor Power vs. EEV Opening")
    ax1.legend()

    ax2.plot(phis * 100, cops, "g-", lw=2, label="Realistic Compressor Map (Task 4)")
    cops_t3 = [cvi.evaluate_ftvi_compressor(phi=float(ph), use_realistic_map=False)["COP_h"] for ph in phis]
    ax2.plot(phis * 100, cops_t3, "b--", lw=1.8, label="Constant eta_is=0.70 (Task 3)")
    ax2.axvline(50, color="gray", ls=":")
    ax2.set_xlabel("Injection EEV Opening phi (%)")
    ax2.set_ylabel("Heating COP (-)")
    ax2.set_title("Heating COP Comparison (Task 3 vs. Task 4)")
    ax2.legend()
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_3_stage_work_breakdown.png")
    plt.close()

    # Fig 4: Compressor Speed Sweep (-10 C vs -20 C)
    s_m10 = [r for r in speed_rows if r["T_amb_C"] == -10.0]
    s_m20 = [r for r in speed_rows if r["T_amb_C"] == -20.0]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    ax1.plot([r["N_rpm"] for r in s_m10], [r["FTVI50_Q_h_kW"] for r in s_m10], "b-", lw=2, label="FT-VI 50% (T_amb=-10 C)")
    ax1.plot([r["N_rpm"] for r in s_m20], [r["FTVI50_Q_h_kW"] for r in s_m20], "r-", lw=2, label="FT-VI 50% (T_amb=-20 C)")
    ax1.plot([r["N_rpm"] for r in s_m20], [r["FTVI80_Q_h_kW"] for r in s_m20], "r--", lw=1.8, label="FT-VI 80% (T_amb=-20 C)")
    ax1.plot([r["N_rpm"] for r in s_m20], [r["Base_Q_h_kW"] for r in s_m20], "k:", lw=1.8, label="Baseline (T_amb=-20 C)")
    ax1.axhline(5.0, color="gray", ls="--", label="5.0 kW Load Target")
    ax1.set_xlabel("Compressor Speed N (rpm)")
    ax1.set_ylabel("Heating Capacity Q_h (kW)")
    ax1.set_title("Speed Modulation to Meet 5 kW Load in Extreme Cold")
    ax1.legend()

    ax2.plot([r["N_rpm"] for r in s_m10], [r["FTVI50_COP_h"] for r in s_m10], "b-", lw=2, label="FT-VI 50% (T_amb=-10 C)")
    ax2.plot([r["N_rpm"] for r in s_m20], [r["FTVI50_COP_h"] for r in s_m20], "r-", lw=2, label="FT-VI 50% (T_amb=-20 C)")
    ax2.plot([r["N_rpm"] for r in s_m20], [r["Base_COP_h"] for r in s_m20], "k:", lw=1.8, label="Baseline (T_amb=-20 C)")
    ax2.set_xlabel("Compressor Speed N (rpm)")
    ax2.set_ylabel("Heating COP (-)")
    ax2.set_title("Heating COP Across Compressor Speed Range")
    ax2.legend()
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_4_speed_performance.png")
    plt.close()

    # Fig 5: Discharge Pressure Sweep (COP Optimization vs P_max and T_dis_max)
    pds = [r["P_dis_MPa"] for r in pdis_rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    ax1.plot(pds, [r["Base_COP_h"] for r in pdis_rows], "o--", label="Baseline COP_h")
    ax1.plot(pds, [r["FTVI_COP_h"] for r in pdis_rows], "s-", label="FT-VI COP_h (phi=50%)")
    ax1.axvline(BRIEF["P_max"], color="r", ls=":", label="P_max = 12.0 MPa")
    ax1.set_xlabel("Discharge Pressure P_dis (MPa)")
    ax1.set_ylabel("Heating COP (-)")
    ax1.set_title("Transcritical COP Curve vs. Discharge Pressure")
    ax1.legend()

    ax2.plot(pds, [r["Base_T_dis_C"] for r in pdis_rows], "o--", label="Baseline T_dis")
    ax2.plot(pds, [r["FTVI_T_dis_C"] for r in pdis_rows], "s-", label="FT-VI T_dis (phi=50%)")
    ax2.axhline(BRIEF["T_dis_max"], color="r", ls=":", label="T_dis_max = 130 C")
    ax2.axvline(BRIEF["P_max"], color="m", ls="--", label="P_max = 12.0 MPa")
    ax2.set_xlabel("Discharge Pressure P_dis (MPa)")
    ax2.set_ylabel("Discharge Temperature T_dis (C)")
    ax2.set_title("Thermal & Pressure Operating Limits")
    ax2.legend()
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_5_discharge_pressure.png")
    plt.close()

    # Fig 6: 2D Operating Envelope Heatmap (T_amb vs Compressor Speed N)
    Tamb_map = np.linspace(-25.0, 0.0, 26)
    N_map = np.linspace(2500.0, 8000.0, 23)
    Q_grid = np.zeros((len(N_map), len(Tamb_map)))
    T_grid = np.zeros((len(N_map), len(Tamb_map)))
    for i, n_val in enumerate(N_map):
        for j, t_val in enumerate(Tamb_map):
            r = cvi.evaluate_ftvi_compressor(T_amb=float(t_val), P_FT=4.5, phi=0.50, N=float(n_val), V_disp=V_disp)
            Q_grid[i, j] = r["Q_h"]
            T_grid[i, j] = r["T_dis"]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    cf = ax.contourf(Tamb_map, N_map, Q_grid, levels=15, cmap="viridis")
    plt.colorbar(cf, ax=ax, label="Heating Capacity Q_h (kW)")
    cs_q = ax.contour(Tamb_map, N_map, Q_grid, levels=[5.0], colors="white", linewidths=2.2)
    ax.clabel(cs_q, fmt="Q_h = 5.0 kW min", inline=True)
    cs_t = ax.contour(Tamb_map, N_map, T_grid, levels=[130.0], colors="red", linewidths=2.2, linestyles="--")
    ax.clabel(cs_t, fmt="T_dis = 130 C max", inline=True)
    ax.plot([-10.0], [4000.0], "r*", markersize=12, label="Design Point (-10 C, 4000 rpm)")
    ax.set_xlabel("Ambient Temperature T_amb (C)")
    ax.set_ylabel("Compressor Speed N (rpm)")
    ax.set_title("FT-VI Feasible Operating Envelope (phi=50%, P_FT=4.5 MPa)")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig("figures_task4/fig_T4_6_operating_envelope.png")
    plt.close()

    # 6. Summary & Handover JSONs for Student 5
    summary = {
        "backend": cvi.props.name,
        "design_point_task4": {k: v for k, v in t4_des.items() if isinstance(v, (int, float, str, bool))},
        "design_point_baseline": {k: v for k, v in base_des.items() if isinstance(v, (int, float, str, bool))},
        "cold_weather_summary": cold_rows,
    }
    with open("results_task4/T4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    handover = {
        "module": "compressor_vi.py",
        "callable": "compressor_vi.evaluate_ftvi_compressor(T_amb, P_FT, phi, P_dis, T_gc_out, N)",
        "swappable_compressor_fn": "compressor_vi.compressor_realistic",
        "constraints": {
            "T_dis_max_C": BRIEF["T_dis_max"],
            "P_dis_max_MPa": BRIEF["P_max"],
            "N_min_rpm": BRIEF["N_min"],
            "N_max_rpm": BRIEF["N_max"],
            "Q_load_min_kW": BRIEF["Q_load"],
        },
        "comp_map_params": cvi.COMP_MAP,
    }
    with open("results_task4/T4_handover_student5.json", "w") as f:
        json.dump(handover, f, indent=2)

    print("Task 4 complete! Saved CSVs/JSONs to results_task4/ and 6 plots to figures_task4/.")


if __name__ == "__main__":
    main()