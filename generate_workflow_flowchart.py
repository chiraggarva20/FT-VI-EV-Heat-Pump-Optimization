"""Generate a publication-grade group integration and contribution flowchart."""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig = plt.figure(figsize=(10, 5.2), dpi=300)
ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Background canvas styling
fig.patch.set_facecolor('#ffffff')

# Colors
c_s1 = '#e0f2fe'  # Light blue
b_s1 = '#0284c7'
c_s2 = '#e0e7ff'  # Indigo light
b_s2 = '#4f46e5'
c_s3 = '#fef3c7'  # Amber light
b_s3 = '#d97706'
c_s4 = '#dcfce7'  # Emerald light
b_s4 = '#059669'
c_s5 = '#fee2e2'  # Red light
b_s5 = '#dc2626'
c_s6 = '#f3e8ff'  # Purple light
b_s6 = '#7c3aed'
c_out = '#f8fafc' # Slate light
b_out = '#334155'

def draw_card(ax, x, y, w, h, bg, border, title, student, roll, bullets):
    # Card shadow/border
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=2.0",
                                  facecolor=bg, edgecolor=border, linewidth=1.8, zorder=2)
    ax.add_patch(rect)
    
    # Title bar
    ax.text(x + w/2, y + h - 4.5, title, fontsize=9.2, fontweight='bold', color=border,
            ha='center', va='center', zorder=3)
    ax.text(x + w/2, y + h - 9.0, f"{student} ({roll})", fontsize=7.8, fontweight='bold', color='#1e293b',
            ha='center', va='center', zorder=3)
    
    # Divider line
    ax.plot([x + 2, x + w - 2], [y + h - 12.0, y + h - 12.0], color=border, linewidth=0.8, alpha=0.6, zorder=3)
    
    # Bullet points
    curr_y = y + h - 16.5
    for b in bullets:
        ax.text(x + 2.5, curr_y, f"• {b}", fontsize=7.2, color='#334155', va='center', zorder=3)
        curr_y -= 4.2

# 1. Student 1 (Top Left)
draw_card(ax, 2, 54, 28, 42, c_s1, b_s1,
          "Task 1: Baseline EV Model", "Kartik Gupta", "Roll: 24B2152",
          ["Single-stage cycle (Case A)",
           "Displacement calibration",
           "V_disp = 8.878 cm³ (5.0 kW)",
           "Suction collapse at -10 °C",
           "Baseline state points (1-4)"])

# 2. Student 2 (Top Center)
draw_card(ax, 36, 54, 28, 42, c_s2, b_s2,
          "Task 2: Flash Tank Model", "Durgesh Nimse", "Roll: 24B2226",
          ["Adiabatic phase separation",
           "Flash vapor quality x_FT",
           "Mass & energy balance",
           "P_inj sweeps (3.5 - 6.0 MPa)",
           "Ideal FT-VI performance"])

# 3. Student 3 (Top Right)
draw_card(ax, 70, 54, 28, 42, c_s3, b_s3,
          "Task 3: Injection EEV", "Disha Jain", "Roll: 24B2125",
          ["Compressible orifice flow",
           "Sonic choking (r_crit = 0.546)",
           "Expansion factor Y(ΔP_eff)",
           "Valve sizing CdA_max = 1.18 mm²",
           "Valve opening sweeps (φ: 5-100%)"])

# 4. Student 4 (Bottom Left)
draw_card(ax, 2, 4, 28, 42, c_s4, b_s4,
          "Task 4: Compressor Map", "Garva Chirag", "Roll: 24B2269",
          ["Empirical η_is(n, PR) & η_v(PR)",
           "Off-design two-stage split",
           "T_dis limit check (≤ 130 °C)",
           "Discharge pressure P_dis sweep",
           "Cold-weather speed solver"])

# 5. Student 6 (Bottom Right)
draw_card(ax, 70, 4, 28, 42, c_s6, b_s6,
          "Task 6: Two-Stage Intercooled", "Tarang Gupta", "Roll: 24B2230",
          ["Alternative Case C cycle",
           "Dual compressor stages",
           "Intercooler duty Q_IC",
           "Reject vs Cabin Recover",
           "Optimum P_i vs √(P_e · P_dis)"])

# 6. Student 5 (Bottom Center - The Hub / Integration Lead)
draw_card(ax, 36, 4, 28, 42, c_s5, b_s5,
          "Task 5: System Integration & Opt.", "Anmol Raj", "Roll: 24B2260",
          ["First-Law closures (< 10⁻¹⁴ kW)",
           "3D Pareto optimization (7,056 pts)",
           "45 non-dominated solutions",
           "MCDM TOPSIS & Knee Point",
           "Cross-Architecture Benchmarking"])

# Draw interconnecting workflow arrows
arrow_props = dict(arrowstyle="-|>", color="#475569", lw=1.6, mutation_scale=14, zorder=1)

# Student 1 -> Student 2
ax.annotate("", xy=(36, 75), xytext=(30, 75), arrowprops=arrow_props)
ax.text(33, 77, "V_disp, States", fontsize=6.8, ha='center', color='#0284c7', fontweight='bold')

# Student 2 -> Student 3
ax.annotate("", xy=(70, 75), xytext=(64, 75), arrowprops=arrow_props)
ax.text(67, 77, "P_FT, m_flash", fontsize=6.8, ha='center', color='#4f46e5', fontweight='bold')

# Student 1 -> Student 4
ax.annotate("", xy=(16, 46), xytext=(16, 54), arrowprops=arrow_props)
ax.text(18.5, 50, "P_e, PR", fontsize=6.8, ha='left', color='#059669', fontweight='bold')

# Student 3 -> Student 4 (via diagonal or down)
ax.annotate("", xy=(64, 25), xytext=(70, 54),
            arrowprops=dict(arrowstyle="-|>", color="#d97706", lw=1.4, linestyle="--", mutation_scale=12, zorder=1))

# Student 4 -> Student 5
ax.annotate("", xy=(36, 25), xytext=(30, 25), arrowprops=arrow_props)
ax.text(33, 27, "η maps, Envelopes", fontsize=6.8, ha='center', color='#059669', fontweight='bold')

# Student 2 -> Student 5
ax.annotate("", xy=(50, 46), xytext=(50, 54), arrowprops=arrow_props)
ax.text(51.5, 50, "x_FT, μ_max", fontsize=6.8, ha='left', color='#4f46e5', fontweight='bold')

# Student 6 -> Student 5 (Handover)
ax.annotate("", xy=(64, 25), xytext=(70, 25), arrowprops=dict(arrowstyle="-|>", color="#7c3aed", lw=1.6, mutation_scale=14, zorder=1))
ax.text(67, 27, "Case C Data", fontsize=6.8, ha='center', color='#7c3aed', fontweight='bold')

# Header text
ax.text(50, 97.5, "ME306 Capstone Project: Inter-Student Thermodynamic Workflow & Integration Architecture",
        fontsize=11.0, fontweight='bold', color='#0f172a', ha='center', va='center')

plt.tight_layout()
os.makedirs('figures_task5', exist_ok=True)
out_path = 'figures_task5/fig_group_workflow_flowchart.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Workflow flowchart saved successfully at: {out_path}")
