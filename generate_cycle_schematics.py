"""
generate_cycle_schematics.py
============================
Generates publication-quality scientific schematic diagrams for:
- Case A: Baseline Single-Stage Heat Pump
- Case B: Flash-Tank Vapor Injection (FT-VI) Heat Pump
- Case C: Two-Stage Intercooled Heat Pump
And a unified comparative 3-panel schematic (Case A, B, C).

Directly inspired by handwritten notebook schematics, adhering to IEEE publication standards:
- State numbers ①, ②, ③, ④, ⑤, ⑥, ⑦, ⑦a, ⑧, ⑨ in circular badges
- Precise thermodynamic boundary conditions and scientific notations
- Distinct color-coded pressure regimes:
    High pressure / supercritical: Crimson (#b03a2e)
    Intermediate pressure: Amber / Orange (#d35400, #e67e22)
    Low pressure / evaporating: Deep Blue (#1b4f72)
    Injection line: Purple (#8e44ad)
- Professional engineering component symbols:
    Compressors (trapezoids), Heat exchangers (tubed serpentines),
    Expansion valves (bowties), Flash tank (vertical separator vessel).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon, Circle
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common styling constants
FONT_FAMILY = "DejaVu Sans"
COLOR_HP = "#b03a2e"   # High pressure (supercritical)
COLOR_IP = "#d35400"   # Intermediate pressure
COLOR_LP = "#1b4f72"   # Low pressure (evaporating)
COLOR_INJ = "#7d3c98"  # Injection line
COLOR_BG_BOX = "#fdfefe"
COLOR_BORDER = "#2c3e50"

def draw_state_badge(ax, x, y, num_str, color="#2c3e50", bg="#ffffff", radius=0.28, fontsize=8.5):
    """Draws a clean circular state badge with a bold number inside."""
    circle = Circle((x, y), radius, facecolor=bg, edgecolor=color, linewidth=1.6, zorder=10)
    ax.add_patch(circle)
    ax.text(x, y, num_str, color=color, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', zorder=11, fontfamily=FONT_FAMILY)

def draw_valve(ax, x, y, width=0.45, height=0.5, horizontal=False, color="#2c3e50", label=""):
    """Draws a standard bowtie expansion valve symbol."""
    if horizontal:
        poly1 = Polygon([[x - width/2, y - height/2], [x, y], [x - width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.4, zorder=6)
        poly2 = Polygon([[x + width/2, y - height/2], [x, y], [x + width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.4, zorder=6)
    else:
        poly1 = Polygon([[x - width/2, y - height/2], [x, y], [x + width/2, y - height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.4, zorder=6)
        poly2 = Polygon([[x - width/2, y + height/2], [x, y], [x + width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.4, zorder=6)
    ax.add_patch(poly1)
    ax.add_patch(poly2)
    # Valve actuator/stem
    if horizontal:
        ax.plot([x, x], [y, y + height*0.75], color=color, lw=1.3, zorder=5)
        ax.plot([x - width*0.25, x + width*0.25], [y + height*0.75, y + height*0.75], color=color, lw=1.6, zorder=5)
    else:
        ax.plot([x, x + width*0.75], [y, y], color=color, lw=1.3, zorder=5)
        ax.plot([x + width*0.75, x + width*0.75], [y - height*0.25, y + height*0.25], color=color, lw=1.6, zorder=5)
    if label:
        ax.text(x - 0.52 if not horizontal else x, y - 0.40 if horizontal else y + 0.48,
                label, fontsize=7.8, fontweight='bold', ha='center', va='center', color=color)

def draw_compressor(ax, x, y, width=0.95, height=0.9, label="Compressor", color="#2c3e50", sublabel=""):
    """Draws an engineering trapezoid compressor narrowing in flow direction (upwards)."""
    pts = [
        [x - width*0.55, y - height*0.5],
        [x + width*0.55, y - height*0.5],
        [x + width*0.32, y + height*0.5],
        [x - width*0.32, y + height*0.5]
    ]
    poly = Polygon(pts, closed=True, facecolor="#eaf2f8", edgecolor=color, linewidth=1.6, zorder=6)
    ax.add_patch(poly)
    ax.text(x, y - (0.08 if sublabel else 0), label, fontsize=8.2, fontweight='bold',
            ha='center', va='center', color=color, zorder=7)
    if sublabel:
        ax.text(x, y - 0.28, sublabel, fontsize=6.8, ha='center', va='center', color="#444", zorder=7)

def draw_heat_exchanger(ax, x, y, width=2.6, height=0.78, label="Gas Cooler", sublabel="", color="#c0392b", coil_color="#c0392b"):
    """Draws a heat exchanger box with an internal serpentine coil."""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.03,rounding_size=0.08",
                         facecolor="#fdfefe", edgecolor=color, linewidth=1.5, zorder=5)
    ax.add_patch(box)
    
    n_coils = 4
    dx = (width * 0.72) / n_coils
    x0 = x - width * 0.36
    for i in range(n_coils):
        cx = x0 + i * dx + dx/2
        arc = patches.Arc((cx, y), dx*0.9, height*0.55, angle=0, theta1=0, theta2=180 if i%2==0 else 360,
                          color=coil_color, lw=1.3, zorder=6, alpha=0.55)
        ax.add_patch(arc)
        
    ax.text(x, y + 0.16, label, fontsize=8.6, fontweight='bold', ha='center', va='center', color=color, zorder=7)
    if sublabel:
        ax.text(x, y - 0.18, sublabel, fontsize=7.0, ha='center', va='center', color="#444", zorder=7)

def draw_flash_tank(ax, x, y, width=1.1, height=1.65, color="#d35400"):
    """Draws a vertical cylindrical pressure vessel with vapor dome and liquid sump."""
    tank = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.05,rounding_size=0.25",
                          facecolor="#fef9e7", edgecolor=color, linewidth=1.6, zorder=5)
    ax.add_patch(tank)
    
    liq_h = height * 0.42
    liq_box = FancyBboxPatch((x - width/2 + 0.05, y - height/2 + 0.05), width - 0.1, liq_h,
                            boxstyle="round,pad=0.02,rounding_size=0.15",
                            facecolor="#d4efdf", edgecolor="none", zorder=6, alpha=0.85)
    ax.add_patch(liq_box)
    
    ax.plot([x - width/2 + 0.08, x + width/2 - 0.08], [y - height/2 + liq_h, y - height/2 + liq_h],
            color="#27ae60", lw=1.3, ls="--", zorder=7)
    
    ax.text(x, y + height*0.22, "Vapor ($x=1$)", fontsize=7.0, fontweight='bold',
            ha='center', va='center', color="#b7950b", zorder=8)
    ax.text(x, y - height*0.24, "Liquid ($x=0$)", fontsize=7.0, fontweight='bold',
            ha='center', va='center', color="#196f3d", zorder=8)
    ax.text(x, y + 0.02, "Flash Tank\n$P_{FT}$", fontsize=7.6, fontweight='bold',
            ha='center', va='center', color=color, zorder=8)

# ==============================================================================
# CASE A: BASELINE SINGLE-STAGE HEAT PUMP
# ==============================================================================
def create_case_a_schematic():
    fig, ax = plt.subplots(figsize=(7.4, 5.4), dpi=300)
    ax.set_xlim(-1.6, 9.6)
    ax.set_ylim(-0.6, 6.4)
    ax.axis('off')
    
    gc_x, gc_y = 3.8, 5.2
    evap_x, evap_y = 3.8, 0.6
    eev_x, eev_y = 1.0, 2.9
    comp_x, comp_y = 6.6, 2.9
    
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.8, height=0.75,
                        label="Gas Cooler (Condenser)", sublabel="Rejects heat to cabin",
                        color=COLOR_HP, coil_color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.8, height=0.75,
                        label="Evaporator", sublabel="Absorbs heat from ambient",
                        color=COLOR_LP, coil_color=COLOR_LP)
    draw_compressor(ax, comp_x, comp_y, width=1.1, height=1.1,
                    label="Compressor", sublabel="$N=4000\\,\\mathrm{rpm}$\n$\\eta_{is}=0.70$",
                    color="#2c3e50")
    draw_valve(ax, eev_x, eev_y, width=0.45, height=0.55, horizontal=False,
               color="#2c3e50", label="Expansion\nValve (EEV)")
    
    lw = 2.0
    # 1 -> Compressor Suction
    ax.plot([gc_x + 1.4, comp_x, comp_x], [evap_y, evap_y, comp_y - 0.55], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(comp_x, comp_y - 0.55), xytext=(comp_x, comp_y - 0.75),
                arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax.annotate("", xy=(comp_x - 0.7, evap_y), xytext=(comp_x - 0.9, evap_y),
                arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> Compressor Discharge to Gas Cooler
    ax.plot([comp_x, comp_x, gc_x + 1.4], [comp_y + 0.55, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.4, gc_y), xytext=(gc_x + 1.7, gc_y),
                arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax.annotate("", xy=(comp_x, comp_y + 1.3), xytext=(comp_x, comp_y + 1.1),
                arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 3 -> Gas Cooler exit to EEV inlet
    ax.plot([gc_x - 1.4, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.35], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev_x, eev_y + 0.35), xytext=(eev_x, eev_y + 0.55),
                arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax.annotate("", xy=(gc_x - 2.0, gc_y), xytext=(gc_x - 1.8, gc_y),
                arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 4 -> EEV exit to Evaporator inlet
    ax.plot([eev_x, eev_x, gc_x - 1.4], [eev_y - 0.35, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.4, evap_y), xytext=(gc_x - 1.7, evap_y),
                arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax.annotate("", xy=(eev_x, eev_y - 1.3), xytext=(eev_x, eev_y - 1.1),
                arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # State Badges
    draw_state_badge(ax, 6.6, 1.2, "1", color=COLOR_LP)
    draw_state_badge(ax, 6.6, 4.6, "2", color=COLOR_HP)
    draw_state_badge(ax, 1.0, 4.6, "3", color=COLOR_HP)
    draw_state_badge(ax, 1.0, 1.2, "4", color=COLOR_LP)
    
    # Compressor Specifications box (placed right of compressor)
    comp_info = (
        "Compressor Specifications:\n"
        "• Speed: $N = 4000\\,\\mathrm{rpm}$ (max $8000$)\n"
        "• Adiabatic assumed, $\\eta_{is} = 0.70$\n"
        "• Displacement: $V_{disp} = 8.878\\,\\mathrm{cm^3}$\n"
        "• Mass flow: $\\dot{m} = 20.22\\,\\mathrm{g/s}$\n"
        "• Power input: $W_{comp} = 1.926\\,\\mathrm{kW}$"
    )
    ax.text(comp_x + 0.65, comp_y, comp_info, fontsize=7.2, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.35", fc="#f8f9fa", ec="#bdc3c7", lw=0.8))
    
    st1_info = "State 1 (Suction):\n$P_{evap} = 2.29\\,\\mathrm{MPa}$\n$T_1 = -10.0\\,^\\circ\\mathrm{C}$ ($5\\,\\mathrm{K}$ SH)\n$h_1 = 437.2\\,\\mathrm{kJ/kg}$"
    ax.text(comp_x - 0.25, 1.2, st1_info, fontsize=6.8, ha='right', va='center', color=COLOR_LP)
    
    st2_info = "State 2 (Discharge):\n$P_{dis} = 9.50\\,\\mathrm{MPa}$ (Max $12.0$)\n$T_{dis} = 120.4\\,^\\circ\\mathrm{C}$ (Limit $\\leq 130\\,^\\circ\\mathrm{C}$)\n$h_2 = 532.5\\,\\mathrm{kJ/kg}$"
    ax.text(comp_x - 0.25, 4.6, st2_info, fontsize=6.8, ha='right', va='center', color=COLOR_HP)
    
    gc_info = (
        "Cabin Heat Delivery & Air Conditions:\n"
        "• Cabin Temp ($CT$): $20.0\\,^\\circ\\mathrm{C}$, Cabin Load ($CL$): $5.0\\,\\mathrm{kW}$\n"
        "• Heat Exchanger Conductance: $UA = 125\\,\\mathrm{W/K}$\n"
        "• Ventilation Air: $\\dot{m}_{vent} = 0.04\\,\\mathrm{kg/s}$, Blower: $\\dot{m}_{gc,air} = 0.15\\,\\mathrm{kg/s}$\n"
        "• Heating Coefficient of Performance: $\\mathrm{COP}_h = 2.596$"
    )
    ax.text(gc_x, gc_y + 0.65, gc_info, fontsize=7.2, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.35", fc="#fdedec", ec=COLOR_HP, lw=0.8))
    
    st3_info = "State 3 (GC Exit):\n$P_3 = 9.50\\,\\mathrm{MPa}$\n$T_3 = 35.0\\,^\\circ\\mathrm{C}$\n$h_3 = 285.2\\,\\mathrm{kJ/kg}$"
    ax.text(eev_x + 0.35, 4.6, st3_info, fontsize=6.8, ha='left', va='center', color=COLOR_HP)
    
    # EEV text placed on the left with safe coordinate
    ax.text(eev_x - 0.55, eev_y, "Isenthalpic\nExpansion\n$h_4 = h_3$", fontsize=6.8, ha='center', va='center', color="#555")
    
    st4_info = "State 4 (Evap Inlet):\n$P_{evap} = 2.29\\,\\mathrm{MPa}$\n$x_4 = 0.322$\n$h_4 = 285.2\\,\\mathrm{kJ/kg}$"
    ax.text(eev_x + 0.35, 1.2, st4_info, fontsize=6.8, ha='left', va='center', color=COLOR_LP)
    
    evap_info = (
        "Ambient Air & Evaporator Conditions:\n"
        "• Ambient Temp: $T_{amb} = -10.0\\,^\\circ\\mathrm{C}$, Air $c_p = 1.006\\,\\mathrm{kJ/(kg\\cdot K)}$\n"
        "• Evaporating Temp: $T_{evap} = -15.0\\,^\\circ\\mathrm{C}$ ($P_{evap} = 2.276-2.29\\,\\mathrm{MPa}$)\n"
        "• Evaporator Heat Duty Absorbed: $\\dot{Q}_{evap} = 3.074\\,\\mathrm{kW}$"
    )
    ax.text(evap_x, evap_y - 0.45, evap_info, fontsize=7.2, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.35", fc="#ebf5fb", ec=COLOR_LP, lw=0.8))
    
    ax.set_title("Case A: Baseline Single-Stage Transcritical $\\mathrm{CO}_2$ Heat Pump Cycle",
                 fontsize=10.5, fontweight='bold', pad=12, color="#1a252f")
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_a.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# CASE B: FLASH-TANK VAPOR INJECTION (FT-VI)
# ==============================================================================
def create_case_b_schematic():
    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)
    ax.set_xlim(-2.9, 12.0)
    ax.set_ylim(-0.6, 6.8)
    ax.axis('off')
    
    gc_x, gc_y = 4.3, 5.8
    evap_x, evap_y = 4.3, 0.6
    
    c1_x, c1_y = 7.4, 1.8
    c2_x, c2_y = 7.4, 4.4
    mix_x, mix_y = 7.4, 3.1
    
    ft_x, ft_y = 2.0, 3.1
    eev1_x, eev1_y = 2.0, 4.8
    eev2_x, eev2_y = 2.0, 1.4
    eev_inj_x, eev_inj_y = 4.6, 3.65
    
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.8, height=0.75,
                        label="Gas Cooler (Condenser)", sublabel="Delivers $\\dot{Q}_h = 7.05\\,\\mathrm{kW}$ to cabin",
                        color=COLOR_HP, coil_color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.8, height=0.75,
                        label="Evaporator", sublabel="Absorbs $\\dot{Q}_{evap} = 4.41\\,\\mathrm{kW}$ from ambient",
                        color=COLOR_LP, coil_color=COLOR_LP)
    
    draw_compressor(ax, c1_x, c1_y, width=1.0, height=0.85, label="Compressor\nStage 1", color="#2c3e50")
    draw_compressor(ax, c2_x, c2_y, width=1.0, height=0.85, label="Compressor\nStage 2", color="#2c3e50")
    
    mix_circle = Circle((mix_x, mix_y), 0.16, facecolor="#f39c12", edgecolor="#b9770e", lw=1.5, zorder=8)
    ax.add_patch(mix_circle)
    ax.text(mix_x + 0.28, mix_y, "Mixing\nPlenum", fontsize=7.2, fontweight='bold', va='center', color="#b9770e")
    
    draw_flash_tank(ax, ft_x, ft_y, width=1.1, height=1.65, color=COLOR_IP)
    
    draw_valve(ax, eev1_x, eev1_y, width=0.45, height=0.5, horizontal=False, color="#2c3e50", label="EEV-1")
    draw_valve(ax, eev2_x, eev2_y, width=0.45, height=0.5, horizontal=False, color="#2c3e50", label="EEV-2 (Main)")
    draw_valve(ax, eev_inj_x, eev_inj_y, width=0.5, height=0.4, horizontal=True, color=COLOR_INJ, label="EEV-inj")
    
    lw = 2.0
    # 1 -> Suction into Stage 1
    ax.plot([gc_x + 1.4, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.43], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(c1_x, c1_y - 0.43), xytext=(c1_x, c1_y - 0.65), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> Stage 1 discharge to mixing plenum
    ax.plot([c1_x, c1_x], [c1_y + 0.43, mix_y - 0.16], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c1_x, mix_y - 0.16), xytext=(c1_x, mix_y - 0.35), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 3 -> Mixing plenum to Stage 2 suction
    ax.plot([c2_x, c2_x], [mix_y + 0.16, c2_y - 0.43], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c2_x, c2_y - 0.43), xytext=(c2_x, c2_y - 0.65), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 4 -> Stage 2 discharge to Gas Cooler inlet
    ax.plot([c2_x, c2_x, gc_x + 1.4], [c2_y + 0.43, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.4, gc_y), xytext=(gc_x + 1.7, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 5 -> Gas Cooler outlet to EEV1 inlet
    ax.plot([gc_x - 1.4, eev1_x, eev1_x], [gc_y, gc_y, eev1_y + 0.25], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev1_x, eev1_y + 0.25), xytext=(eev1_x, eev1_y + 0.45), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 6 -> EEV1 outlet to Flash Tank inlet
    ax.plot([eev1_x, ft_x], [eev1_y - 0.25, ft_y + 0.8], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(ft_x, ft_y + 0.8), xytext=(ft_x, ft_y + 1.0), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 7 -> Vapor extraction from top dome to EEV_inj
    ax.plot([ft_x + 0.55, eev_inj_x - 0.25], [ft_y + 0.55, eev_inj_y], color=COLOR_INJ, lw=lw)
    ax.annotate("", xy=(eev_inj_x - 0.25, eev_inj_y), xytext=(eev_inj_x - 0.45, eev_inj_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    
    # 7a -> EEV_inj outlet into Mixing Plenum
    ax.plot([eev_inj_x + 0.25, mix_x - 0.6, mix_x - 0.6, mix_x - 0.16],
            [eev_inj_y, eev_inj_y, mix_y, mix_y], color=COLOR_INJ, lw=lw)
    ax.annotate("", xy=(mix_x - 0.16, mix_y), xytext=(mix_x - 0.35, mix_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    
    # 8 -> Saturated liquid from Flash Tank bottom to EEV2 inlet
    ax.plot([ft_x, eev2_x], [ft_y - 0.8, eev2_y + 0.25], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(eev2_x, eev2_y + 0.25), xytext=(eev2_x, eev2_y + 0.45), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 9 -> EEV2 outlet to Evaporator inlet
    ax.plot([eev2_x, eev2_x, gc_x - 1.4], [eev2_y - 0.25, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.4, evap_y), xytext=(gc_x - 1.7, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # State Badges
    draw_state_badge(ax, 7.4, 0.9, "1", color=COLOR_LP)
    draw_state_badge(ax, 7.8, 2.5, "2", color=COLOR_IP)
    draw_state_badge(ax, 7.8, 3.8, "3", color=COLOR_IP)
    draw_state_badge(ax, 7.4, 5.2, "4", color=COLOR_HP)
    draw_state_badge(ax, 2.0, 5.5, "5", color=COLOR_HP)
    draw_state_badge(ax, 1.4, 4.1, "6", color=COLOR_IP)
    draw_state_badge(ax, 2.8, 3.9, "7", color=COLOR_INJ)
    draw_state_badge(ax, 6.2, 3.4, "7a", color=COLOR_INJ)
    draw_state_badge(ax, 1.4, 2.1, "8", color=COLOR_IP)
    draw_state_badge(ax, 2.0, 0.7, "9", color=COLOR_LP)
    
    # Text Callouts
    st_info_c = (
        "Two-Stage Compression & Injection:\n"
        "• State 1: Suction $P_1 = 2.29\\,\\mathrm{MPa}$, $\\dot{m}_{suc} = 20.22\\,\\mathrm{g/s}$\n"
        "• State 2: Stage-1 Disch. $P_{port} = 3.44\\,\\mathrm{MPa}$, $T_2 = 45.1\\,^\\circ\\mathrm{C}$\n"
        "• State 7a: Injected Vapor $\\dot{m}_{inj} = 11.04\\,\\mathrm{g/s}$ ($\\mu = 0.546$)\n"
        "• State 3: Mixed Flow $T_3 = 12.6\\,^\\circ\\mathrm{C}$ (Desuperheated $-32.5\\,\\mathrm{K}$!)\n"
        "• State 4: Discharge $P_{dis} = 9.5\\,\\mathrm{MPa}$, $T_{dis} = 107.5\\,^\\circ\\mathrm{C}$\n"
        "  ($-12.9\\,\\mathrm{K}$ cooler than Baseline, safe below $130\\,^\\circ\\mathrm{C}$)\n"
        "• Total Work: $W_{comp} = 2.571\\,\\mathrm{kW}$"
    )
    ax.text(c2_x + 0.65, 3.1, st_info_c, fontsize=6.8, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.35", fc="#fdfefe", ec="#bdc3c7", lw=0.8))
    
    ft_info = (
        "Flash Tank Phase Separation:\n"
        "• Intermediate $P_{FT} = 4.25\\,\\mathrm{MPa}$ ($T_{sat} = 7.8\\,^\\circ\\mathrm{C}$)\n"
        "• State 6: Flash inlet ($x_6 = 0.353$)\n"
        "• State 7: Saturated vapor ($x_7 = 1.0$)\n"
        "• State 8: Saturated liquid ($x_8 = 0.0$)\n"
        "• State 9: Evap inlet ($x_9 = 0.208$, vs $0.32$ Case A!)\n"
        "  Increases evaporator specific latent heat lift!"
    )
    ax.text(ft_x - 0.75, 3.1, ft_info, fontsize=6.8, va='center', ha='right',
            bbox=dict(boxstyle="round,pad=0.35", fc="#fef9e7", ec=COLOR_IP, lw=0.8))
    
    perf_info = (
        "FT-VI Performance Gains (Nominal $4000\\,\\mathrm{rpm}$):\n"
        "• Heating Capacity: $\\dot{Q}_h = 7.049\\,\\mathrm{kW}$ (+41.0% vs Case A)\n"
        "• Heating $\\mathrm{COP}_h = 2.742$ (+5.7% vs Case A)\n"
        "• Matched $5.0\\,\\mathrm{kW}$ Cruising: $N=2800\\,\\mathrm{rpm}$ (-30% speed, -3.8% power)"
    )
    ax.text(gc_x, gc_y + 0.58, perf_info, fontsize=7.2, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.35", fc="#eafaf1", ec="#27ae60", lw=0.8))
    
    ax.set_title("Case B: Flash-Tank Vapor Injection (FT-VI) Transcritical $\\mathrm{CO}_2$ Heat Pump Cycle",
                 fontsize=10.5, fontweight='bold', pad=12, color="#1a252f")
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_b.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# CASE C: TWO-STAGE INTERCOOLED CYCLE
# ==============================================================================
def create_case_c_schematic():
    fig, ax = plt.subplots(figsize=(7.6, 5.4), dpi=300)
    ax.set_xlim(-1.8, 9.8)
    ax.set_ylim(-0.6, 6.6)
    ax.axis('off')
    
    gc_x, gc_y = 3.9, 5.4
    evap_x, evap_y = 3.9, 0.6
    eev_x, eev_y = 1.0, 3.0
    
    c1_x, c1_y = 6.8, 1.5
    ic_x, ic_y = 6.8, 3.0
    c2_x, c2_y = 6.8, 4.5
    
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.8, height=0.75,
                        label="Gas Cooler (Condenser)", sublabel="Rejects heat to cabin",
                        color=COLOR_HP, coil_color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.8, height=0.75,
                        label="Evaporator", sublabel="Absorbs heat from ambient",
                        color=COLOR_LP, coil_color=COLOR_LP)
    draw_compressor(ax, c1_x, c1_y, width=1.0, height=0.85, label="Compressor C1\n(Low-Stage)", color="#2c3e50")
    draw_heat_exchanger(ax, ic_x, ic_y, width=1.4, height=0.75, label="Intercooler (IC)", sublabel="Rejects $\\dot{Q}_{IC}$", color=COLOR_IP, coil_color=COLOR_IP)
    draw_compressor(ax, c2_x, c2_y, width=1.0, height=0.85, label="Compressor C2\n(High-Stage)", color="#2c3e50")
    draw_valve(ax, eev_x, eev_y, width=0.45, height=0.55, horizontal=False, color="#2c3e50", label="Expansion\nValve (EEV)")
    
    lw = 2.0
    # 1 -> C1 Suction
    ax.plot([gc_x + 1.4, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.43], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(c1_x, c1_y - 0.43), xytext=(c1_x, c1_y - 0.65), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> C1 discharge to IC inlet
    ax.plot([c1_x, c1_x], [c1_y + 0.43, ic_y - 0.38], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c1_x, ic_y - 0.38), xytext=(c1_x, ic_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 3 -> IC outlet to C2 suction
    ax.plot([c2_x, c2_x], [ic_y + 0.38, c2_y - 0.43], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c2_x, c2_y - 0.43), xytext=(c2_x, c2_y - 0.65), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 4 -> C2 discharge to Gas Cooler inlet
    ax.plot([c2_x, c2_x, gc_x + 1.4], [c2_y + 0.43, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.4, gc_y), xytext=(gc_x + 1.7, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 5 -> Gas Cooler outlet to EEV inlet
    ax.plot([gc_x - 1.4, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.35], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev_x, eev_y + 0.35), xytext=(eev_x, eev_y + 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 6 -> EEV outlet to Evaporator inlet
    ax.plot([eev_x, eev_x, gc_x - 1.4], [eev_y - 0.35, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.4, evap_y), xytext=(gc_x - 1.7, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # Intercooler Heat Rejection Arrow
    ax.annotate("$\\dot{Q}_{IC} = 0.812\\,\\mathrm{kW}$\n(Ambient Reject or\nCabin Recovery)",
                xy=(ic_x - 0.7, ic_y), xytext=(ic_x - 1.9, ic_y),
                arrowprops=dict(arrowstyle="<-", color=COLOR_IP, lw=1.5),
                fontsize=6.8, ha='center', va='center', color=COLOR_IP,
                bbox=dict(boxstyle="round,pad=0.25", fc="#fef9e7", ec=COLOR_IP, lw=0.6))
    
    draw_state_badge(ax, 6.8, 0.8, "1", color=COLOR_LP)
    draw_state_badge(ax, 7.4, 2.2, "2", color=COLOR_IP)
    draw_state_badge(ax, 7.4, 3.8, "3", color=COLOR_IP)
    draw_state_badge(ax, 6.8, 5.0, "4", color=COLOR_HP)
    draw_state_badge(ax, 1.0, 4.8, "5", color=COLOR_HP)
    draw_state_badge(ax, 1.0, 1.2, "6", color=COLOR_LP)
    
    c_info = (
        "Two-Stage Compression & Intercooling:\n"
        "• Intermediate: $P_i = \\sqrt{P_{evap}\\cdot P_{dis}} = 4.67\\,\\mathrm{MPa}$\n"
        "  (Optimum $P_i = 4.50\\,\\mathrm{MPa}$)\n"
        "• State 1: $P_1 = 2.29\\,\\mathrm{MPa}$, $T_1 = -10.0\\,^\\circ\\mathrm{C}$\n"
        "• State 2: $T_2 = 59.8\\,^\\circ\\mathrm{C}$, $P_i = 4.50\\,\\mathrm{MPa}$\n"
        "• State 3: $T_3 = 35.0\\,^\\circ\\mathrm{C}$, $P_i = 4.50\\,\\mathrm{MPa}$\n"
        "• State 4: $P_{dis} = 9.50\\,\\mathrm{MPa}$, $T_{dis} = 98.2\\,^\\circ\\mathrm{C}$\n"
        "• Total Compression Work: $W_{comp} = 1.765\\,\\mathrm{kW}$"
    )
    ax.text(c1_x + 0.65, 3.0, c_info, fontsize=6.8, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.35", fc="#fdfefe", ec="#bdc3c7", lw=0.8))
    
    ic_comp_info = (
        "Case C Architecture Insights:\n"
        "• Two operational modes evaluated:\n"
        "  1) Reject: $\\dot{Q}_{IC}$ lost to ambient ($\\mathrm{COP}_h = 2.294$)\n"
        "  2) Recover: Preheats cabin air ($\\mathrm{COP}_h = 2.824$)\n"
        "• Note: No mass flow augmentation ($\\dot{m}_{high} = \\dot{m}_{low} = 20.22\\,\\mathrm{g/s}$)\n"
        "• Requires 33% higher speed ($N=4203\\,\\mathrm{rpm}$) to match $5.0\\,\\mathrm{kW}$ load,\n"
        "  plus significant packaging complexity (dual radiators)."
    )
    ax.text(eev_x - 0.35, 4.7, ic_comp_info, fontsize=6.8, ha='left', va='bottom',
            bbox=dict(boxstyle="round,pad=0.35", fc="#f4ecf7", ec="#8e44ad", lw=0.8))
    
    ax.set_title("Case C: Two-Stage Intercooled Transcritical $\\mathrm{CO}_2$ Heat Pump Cycle",
                 fontsize=10.5, fontweight='bold', pad=12, color="#1a252f")
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_c.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# COMBINED 3-PANEL COMPARATIVE SCHEMATIC
# ==============================================================================
def create_combined_schematic():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 5.0), dpi=300)
    
    # Panel 1: Case A
    ax1.set_xlim(-0.2, 7.8)
    ax1.set_ylim(-0.4, 6.2)
    ax1.axis('off')
    gc_x, gc_y = 3.8, 5.2
    evap_x, evap_y = 3.8, 0.6
    eev_x, eev_y = 1.0, 2.9
    comp_x, comp_y = 6.6, 2.9
    
    draw_heat_exchanger(ax1, gc_x, gc_y, width=2.6, height=0.7, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax1, evap_x, evap_y, width=2.6, height=0.7, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax1, comp_x, comp_y, width=1.0, height=1.0, label="Compressor", color="#2c3e50")
    draw_valve(ax1, eev_x, eev_y, width=0.4, height=0.5, horizontal=False, color="#2c3e50", label="EEV")
    
    lw = 1.8
    ax1.plot([gc_x + 1.3, comp_x, comp_x], [evap_y, evap_y, comp_y - 0.5], color=COLOR_LP, lw=lw)
    ax1.annotate("", xy=(comp_x, comp_y - 0.5), xytext=(comp_x, comp_y - 0.7), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax1.plot([comp_x, comp_x, gc_x + 1.3], [comp_y + 0.5, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax1.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.5, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax1.plot([gc_x - 1.3, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.3], color=COLOR_HP, lw=lw)
    ax1.annotate("", xy=(eev_x, eev_y + 0.3), xytext=(eev_x, eev_y + 0.5), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax1.plot([eev_x, eev_x, gc_x - 1.3], [eev_y - 0.3, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax1.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.5, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax1, 6.6, 1.2, "1", color=COLOR_LP)
    draw_state_badge(ax1, 6.6, 4.6, "2", color=COLOR_HP)
    draw_state_badge(ax1, 1.0, 4.6, "3", color=COLOR_HP)
    draw_state_badge(ax1, 1.0, 1.2, "4", color=COLOR_LP)
    
    ax1.text(3.8, 3.2,
             "Case A: Baseline Single-Stage\n"
             "• 1 Compressor, 1 EEV, 4 States\n"
             "• $\\dot{Q}_h = 5.00\\,\\mathrm{kW}$, $\\mathrm{COP}_h = 2.596$\n"
             "• $T_{dis} = 120.4\\,^\\circ\\mathrm{C}$, $W = 1.926\\,\\mathrm{kW}$\n"
             "• At $-15\\,^\\circ\\mathrm{C}$: Fails $130\\,^\\circ\\mathrm{C}$ limit!",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9fa", ec="#bdc3c7", lw=0.8))
    ax1.set_title("(a) Case A: Baseline Single-Stage", fontsize=9.5, fontweight='bold', color="#2c3e50")

    # Panel 2: Case B (FT-VI)
    ax2.set_xlim(-0.2, 8.8)
    ax2.set_ylim(-0.4, 6.2)
    ax2.axis('off')
    gc_x, gc_y = 4.3, 5.2
    evap_x, evap_y = 4.3, 0.6
    c1_x, c1_y = 7.4, 1.6
    c2_x, c2_y = 7.4, 4.2
    mix_x, mix_y = 7.4, 2.9
    ft_x, ft_y = 2.0, 2.9
    eev1_x, eev1_y = 2.0, 4.5
    eev2_x, eev2_y = 2.0, 1.3
    eev_inj_x, eev_inj_y = 4.6, 3.4
    
    draw_heat_exchanger(ax2, gc_x, gc_y, width=2.6, height=0.7, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax2, evap_x, evap_y, width=2.6, height=0.7, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax2, c1_x, c1_y, width=0.9, height=0.8, label="C1", color="#2c3e50")
    draw_compressor(ax2, c2_x, c2_y, width=0.9, height=0.8, label="C2", color="#2c3e50")
    draw_flash_tank(ax2, ft_x, ft_y, width=1.0, height=1.5, color=COLOR_IP)
    draw_valve(ax2, eev1_x, eev1_y, width=0.38, height=0.45, horizontal=False, color="#2c3e50", label="EEV1")
    draw_valve(ax2, eev2_x, eev2_y, width=0.38, height=0.45, horizontal=False, color="#2c3e50", label="EEV2")
    draw_valve(ax2, eev_inj_x, eev_inj_y, width=0.45, height=0.35, horizontal=True, color=COLOR_INJ, label="EEVinj")
    
    mix_circle = Circle((mix_x, mix_y), 0.14, facecolor="#f39c12", edgecolor="#b9770e", lw=1.2, zorder=8)
    ax2.add_patch(mix_circle)
    
    ax2.plot([gc_x + 1.3, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.4], color=COLOR_LP, lw=lw)
    ax2.annotate("", xy=(c1_x, c1_y - 0.4), xytext=(c1_x, c1_y - 0.6), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax2.plot([c1_x, c1_x], [c1_y + 0.4, mix_y - 0.14], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(c1_x, mix_y - 0.14), xytext=(c1_x, mix_y - 0.3), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([c2_x, c2_x], [mix_y + 0.14, c2_y - 0.4], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(c2_x, c2_y - 0.4), xytext=(c2_x, mix_y + 0.14), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([c2_x, c2_x, gc_x + 1.3], [c2_y + 0.4, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax2.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.5, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax2.plot([gc_x - 1.3, eev1_x, eev1_x], [gc_y, gc_y, eev1_y + 0.22], color=COLOR_HP, lw=lw)
    ax2.annotate("", xy=(eev1_x, eev1_y + 0.22), xytext=(eev1_x, eev1_y + 0.4), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax2.plot([eev1_x, ft_x], [eev1_y - 0.22, ft_y + 0.75], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(ft_x, ft_y + 0.75), xytext=(ft_x, ft_y + 0.95), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([ft_x + 0.5, eev_inj_x - 0.22], [ft_y + 0.5, eev_inj_y], color=COLOR_INJ, lw=lw)
    ax2.annotate("", xy=(eev_inj_x - 0.22, eev_inj_y), xytext=(ft_x + 0.5, eev_inj_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    ax2.plot([eev_inj_x + 0.22, mix_x - 0.5, mix_x - 0.5, mix_x - 0.14],
             [eev_inj_y, eev_inj_y, mix_y, mix_y], color=COLOR_INJ, lw=lw)
    ax2.annotate("", xy=(mix_x - 0.14, mix_y), xytext=(mix_x - 0.3, mix_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    ax2.plot([ft_x, eev2_x], [ft_y - 0.75, eev2_y + 0.22], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(eev2_x, eev2_y + 0.22), xytext=(eev2_x, eev2_y + 0.4), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([eev2_x, eev2_x, gc_x - 1.3], [eev2_y - 0.22, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax2.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.5, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax2, 7.4, 0.8, "1", color=COLOR_LP)
    draw_state_badge(ax2, 7.8, 2.3, "2", color=COLOR_IP)
    draw_state_badge(ax2, 7.8, 3.5, "3", color=COLOR_IP)
    draw_state_badge(ax2, 7.4, 4.8, "4", color=COLOR_HP)
    draw_state_badge(ax2, 2.0, 5.1, "5", color=COLOR_HP)
    draw_state_badge(ax2, 1.4, 3.8, "6", color=COLOR_IP)
    draw_state_badge(ax2, 2.7, 3.6, "7", color=COLOR_INJ)
    draw_state_badge(ax2, 6.2, 3.2, "7a", color=COLOR_INJ)
    draw_state_badge(ax2, 1.4, 1.9, "8", color=COLOR_IP)
    draw_state_badge(ax2, 2.0, 0.7, "9", color=COLOR_LP)
    
    ax2.text(4.4, 2.1,
             "Case B: Flash-Tank Vapor Injection\n"
             "• Flash Tank, 3 Valves, 10 States\n"
             "• $\\dot{Q}_h = 7.049\\,\\mathrm{kW}$ (+41.0% vs A)\n"
             "• $\\mathrm{COP}_h = 2.742$ (+5.7% vs A)\n"
             "• $T_{dis} = 107.5\\,^\\circ\\mathrm{C}$ ($-12.9\\,\\mathrm{K}$ cooler)\n"
             "• Subcools liquid: $x_9=0.21$ vs $0.32$",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#eafaf1", ec="#27ae60", lw=0.8))
    ax2.set_title("(b) Case B: Flash-Tank Vapor Injection (FT-VI)", fontsize=9.5, fontweight='bold', color="#27ae60")

    # Panel 3: Case C (Intercooled)
    ax3.set_xlim(-0.2, 8.0)
    ax3.set_ylim(-0.4, 6.2)
    ax3.axis('off')
    gc_x, gc_y = 3.9, 5.2
    evap_x, evap_y = 3.9, 0.6
    eev_x, eev_y = 1.0, 2.9
    c1_x, c1_y = 6.8, 1.5
    ic_x, ic_y = 6.8, 2.9
    c2_x, c2_y = 6.8, 4.3
    
    draw_heat_exchanger(ax3, gc_x, gc_y, width=2.6, height=0.7, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax3, evap_x, evap_y, width=2.6, height=0.7, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax3, c1_x, c1_y, width=0.9, height=0.8, label="C1", color="#2c3e50")
    draw_heat_exchanger(ax3, ic_x, ic_y, width=1.2, height=0.65, label="Intercooler", sublabel="$\\dot{Q}_{IC}$", color=COLOR_IP)
    draw_compressor(ax3, c2_x, c2_y, width=0.9, height=0.8, label="C2", color="#2c3e50")
    draw_valve(ax3, eev_x, eev_y, width=0.4, height=0.5, horizontal=False, color="#2c3e50", label="EEV")
    
    ax3.plot([gc_x + 1.3, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.4], color=COLOR_LP, lw=lw)
    ax3.annotate("", xy=(c1_x, c1_y - 0.4), xytext=(c1_x, c1_y - 0.6), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax3.plot([c1_x, c1_x], [c1_y + 0.4, ic_y - 0.33], color=COLOR_IP, lw=lw)
    ax3.annotate("", xy=(c1_x, ic_y - 0.33), xytext=(c1_x, ic_y - 0.5), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax3.plot([c2_x, c2_x], [ic_y + 0.33, c2_y - 0.4], color=COLOR_IP, lw=lw)
    ax3.annotate("", xy=(c2_x, c2_y - 0.4), xytext=(c2_x, c2_y - 0.6), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax3.plot([c2_x, c2_x, gc_x + 1.3], [c2_y + 0.4, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax3.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.5, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax3.plot([gc_x - 1.3, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.3], color=COLOR_HP, lw=lw)
    ax3.annotate("", xy=(eev_x, eev_y + 0.3), xytext=(eev_x, eev_y + 0.5), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax3.plot([eev_x, eev_x, gc_x - 1.3], [eev_y - 0.3, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax3.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.5, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax3, 6.8, 0.8, "1", color=COLOR_LP)
    draw_state_badge(ax3, 7.3, 2.1, "2", color=COLOR_IP)
    draw_state_badge(ax3, 7.3, 3.6, "3", color=COLOR_IP)
    draw_state_badge(ax3, 6.8, 4.8, "4", color=COLOR_HP)
    draw_state_badge(ax3, 1.0, 4.6, "5", color=COLOR_HP)
    draw_state_badge(ax3, 1.0, 1.2, "6", color=COLOR_LP)
    
    ax3.text(3.9, 2.9,
             "Case C: Two-Stage Intercooled\n"
             "• 2 Compressors, 1 IC, 6 States\n"
             "• $P_i = 4.50\\,\\mathrm{MPa}$, $\\dot{Q}_{IC} = 0.812\\,\\mathrm{kW}$\n"
             "• Mode 1 (Reject): $\\mathrm{COP}_h = 2.294$\n"
             "• Mode 2 (Recover): $\\mathrm{COP}_h = 2.824$\n"
             "• Requires +33% Speed ($4203\\,\\mathrm{rpm}$)\n"
             "• Heavy dual-radiator penalty",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="#f4ecf7", ec="#8e44ad", lw=0.8))
    ax3.set_title("(c) Case C: Two-Stage Intercooled", fontsize=9.5, fontweight='bold', color="#8e44ad")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematics_cases_abc_comparison.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    print("Generating cycle schematics...")
    create_case_a_schematic()
    create_case_b_schematic()
    create_case_c_schematic()
    create_combined_schematic()
    print("All schematics generated successfully!")
