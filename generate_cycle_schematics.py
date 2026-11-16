"""
generate_cycle_schematics.py
============================
Clean, clutter-free, publication-quality scientific schematic diagrams:
- Case A: Baseline Single-Stage Heat Pump
- Case B: Flash-Tank Vapor Injection (FT-VI) Heat Pump
- Case C: Two-Stage Intercooled Heat Pump
- Unified 3-Panel Comparative Schematic

Engineered with generous margins, ZERO text-line overlaps, NO internal heading
collision (captions are handled in HTML/IEEE format), and precise thermodynamic annotations.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon, Circle

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Styling constants
FONT_FAMILY = "DejaVu Sans"
COLOR_HP = "#b03a2e"   # High pressure / supercritical (Crimson)
COLOR_IP = "#d35400"   # Intermediate pressure (Amber)
COLOR_LP = "#1b4f72"   # Low pressure (Deep Blue)
COLOR_INJ = "#6c3483"  # Injection line (Purple)
COLOR_COMP = "#2c3e50" # Compressor border

def draw_state_badge(ax, x, y, num_str, color="#2c3e50", bg="#ffffff", radius=0.24, fontsize=8):
    """Draws a clean circular state badge with a bold number inside."""
    circle = Circle((x, y), radius, facecolor=bg, edgecolor=color, linewidth=1.5, zorder=10)
    ax.add_patch(circle)
    ax.text(x, y, num_str, color=color, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', zorder=11, fontfamily=FONT_FAMILY)

def draw_valve(ax, x, y, width=0.45, height=0.45, horizontal=False, color="#2c3e50", label=""):
    """Draws a clean bowtie expansion valve symbol."""
    if horizontal:
        poly1 = Polygon([[x - width/2, y - height/2], [x, y], [x - width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.3, zorder=6)
        poly2 = Polygon([[x + width/2, y - height/2], [x, y], [x + width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.3, zorder=6)
    else:
        poly1 = Polygon([[x - width/2, y - height/2], [x, y], [x + width/2, y - height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.3, zorder=6)
        poly2 = Polygon([[x - width/2, y + height/2], [x, y], [x + width/2, y + height/2]],
                        closed=True, facecolor="#ecf0f1", edgecolor=color, linewidth=1.3, zorder=6)
    ax.add_patch(poly1)
    ax.add_patch(poly2)
    # Valve actuator stem
    if horizontal:
        ax.plot([x, x], [y, y + height*0.65], color=color, lw=1.2, zorder=5)
        ax.plot([x - width*0.25, x + width*0.25], [y + height*0.65, y + height*0.65], color=color, lw=1.5, zorder=5)
    else:
        ax.plot([x, x + width*0.65], [y, y], color=color, lw=1.2, zorder=5)
        ax.plot([x + width*0.65, x + width*0.65], [y - height*0.25, y + height*0.25], color=color, lw=1.5, zorder=5)
    if label:
        ax.text(x - 0.50 if not horizontal else x, y - 0.35 if horizontal else y + 0.40,
                label, fontsize=7.5, fontweight='bold', ha='center', va='center', color=color)

def draw_compressor(ax, x, y, width=0.9, height=0.85, label="Compressor", color="#2c3e50", sublabel=""):
    """Draws a clean trapezoid compressor narrowing in flow direction."""
    pts = [
        [x - width*0.52, y - height*0.5],
        [x + width*0.52, y - height*0.5],
        [x + width*0.30, y + height*0.5],
        [x - width*0.30, y + height*0.5]
    ]
    poly = Polygon(pts, closed=True, facecolor="#eaf2f8", edgecolor=color, linewidth=1.5, zorder=6)
    ax.add_patch(poly)
    ax.text(x, y - (0.07 if sublabel else 0), label, fontsize=8.0, fontweight='bold',
            ha='center', va='center', color=color, zorder=7)
    if sublabel:
        ax.text(x, y - 0.25, sublabel, fontsize=6.8, ha='center', va='center', color="#444", zorder=7)

def draw_heat_exchanger(ax, x, y, width=2.6, height=0.72, label="Gas Cooler", sublabel="", color="#c0392b"):
    """Draws a heat exchanger box with an internal serpentine coil."""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.03,rounding_size=0.08",
                         facecolor="#fdfefe", edgecolor=color, linewidth=1.4, zorder=5)
    ax.add_patch(box)
    
    n_coils = 4
    dx = (width * 0.70) / n_coils
    x0 = x - width * 0.35
    for i in range(n_coils):
        cx = x0 + i * dx + dx/2
        arc = patches.Arc((cx, y), dx*0.88, height*0.50, angle=0, theta1=0, theta2=180 if i%2==0 else 360,
                          color=color, lw=1.2, zorder=6, alpha=0.55)
        ax.add_patch(arc)
        
    ax.text(x, y + 0.14, label, fontsize=8.2, fontweight='bold', ha='center', va='center', color=color, zorder=7)
    if sublabel:
        ax.text(x, y - 0.16, sublabel, fontsize=6.8, ha='center', va='center', color="#555", zorder=7)

def draw_flash_tank(ax, x, y, width=1.1, height=1.65, color="#d35400"):
    """Draws a vertical cylindrical pressure vessel with vapor dome and liquid sump."""
    tank = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.04,rounding_size=0.22",
                          facecolor="#fef9e7", edgecolor=color, linewidth=1.5, zorder=5)
    ax.add_patch(tank)
    
    liq_h = height * 0.42
    liq_box = FancyBboxPatch((x - width/2 + 0.04, y - height/2 + 0.04), width - 0.08, liq_h,
                            boxstyle="round,pad=0.02,rounding_size=0.12",
                            facecolor="#d4efdf", edgecolor="none", zorder=6, alpha=0.85)
    ax.add_patch(liq_box)
    
    ax.plot([x - width/2 + 0.08, x + width/2 - 0.08], [y - height/2 + liq_h, y - height/2 + liq_h],
            color="#27ae60", lw=1.2, ls="--", zorder=7)
    
    ax.text(x, y + height*0.22, "Vapor (x=1)", fontsize=6.8, fontweight='bold',
            ha='center', va='center', color="#b7950b", zorder=8)
    ax.text(x, y - height*0.24, "Liquid (x=0)", fontsize=6.8, fontweight='bold',
            ha='center', va='center', color="#196f3d", zorder=8)
    ax.text(x, y + 0.02, "Flash Tank\n$P_{FT}$", fontsize=7.5, fontweight='bold',
            ha='center', va='center', color=color, zorder=8)


# ==============================================================================
# CASE A: BASELINE SINGLE-STAGE HEAT PUMP (Clutter-Free)
# ==============================================================================
def create_case_a_schematic():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=300)
    ax.set_xlim(-0.5, 9.8)
    ax.set_ylim(-0.8, 5.6)
    ax.axis('off')
    
    gc_x, gc_y = 3.8, 4.6
    evap_x, evap_y = 3.8, 0.4
    eev_x, eev_y = 0.8, 2.5
    comp_x, comp_y = 6.8, 2.5
    
    # Components
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.6, height=0.70,
                        label="Gas Cooler (Condenser)", sublabel="Rejects heat to cabin",
                        color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.6, height=0.70,
                        label="Evaporator", sublabel="Absorbs heat from ambient",
                        color=COLOR_LP)
    draw_compressor(ax, comp_x, comp_y, width=1.0, height=0.95,
                    label="Compressor", sublabel="$N=4000\\,\\mathrm{rpm}$\n$\\eta_{is}=0.70$",
                    color=COLOR_COMP)
    draw_valve(ax, eev_x, eev_y, width=0.45, height=0.50, horizontal=False,
               color=COLOR_COMP, label="EEV\n($h_4=h_3$)")
    
    lw = 1.8
    # Piping: 1 -> Suction
    ax.plot([gc_x + 1.3, comp_x, comp_x], [evap_y, evap_y, comp_y - 0.48], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(comp_x, comp_y - 0.48), xytext=(comp_x, comp_y - 0.68), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> Discharge to Gas Cooler
    ax.plot([comp_x, comp_x, gc_x + 1.3], [comp_y + 0.48, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.6, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 3 -> Gas Cooler to EEV
    ax.plot([gc_x - 1.3, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.32], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev_x, eev_y + 0.32), xytext=(eev_x, eev_y + 0.52), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 4 -> EEV to Evaporator
    ax.plot([eev_x, eev_x, gc_x - 1.3], [eev_y - 0.32, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.6, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # State Badges
    draw_state_badge(ax, 6.8, 1.2, "1", color=COLOR_LP)
    draw_state_badge(ax, 6.8, 3.8, "2", color=COLOR_HP)
    draw_state_badge(ax, 0.8, 3.8, "3", color=COLOR_HP)
    draw_state_badge(ax, 0.8, 1.2, "4", color=COLOR_LP)
    
    # State Data Labels directly placed neatly near pipes
    ax.text(6.8 - 0.22, 1.2, "State 1 (Suction):\n$2.29\\,\\mathrm{MPa},\\,-10\\,^\\circ\\mathrm{C}$\n($5\\,\\mathrm{K}$ superheat)",
            fontsize=6.8, ha='right', va='center', color=COLOR_LP)
    
    ax.text(6.8 - 0.22, 3.8, "State 2 (Discharge):\n$9.50\\,\\mathrm{MPa},\\,120.4\\,^\\circ\\mathrm{C}$\n(limit $\\leq 130\\,^\\circ\\mathrm{C}$)",
            fontsize=6.8, ha='right', va='center', color=COLOR_HP)
    
    ax.text(0.8 + 0.30, 3.8, "State 3 (GC Exit):\n$9.50\\,\\mathrm{MPa},\\,35.0\\,^\\circ\\mathrm{C}$",
            fontsize=6.8, ha='left', va='center', color=COLOR_HP)
    
    ax.text(0.8 + 0.30, 1.2, "State 4 (Evap In):\n$2.29\\,\\mathrm{MPa},\\,x_4=0.32$",
            fontsize=6.8, ha='left', va='center', color=COLOR_LP)
    
    # External Conditions (top & bottom boxes)
    gc_note = "Cabin Air Rejection: $CT = 20\\,^\\circ\\mathrm{C}$, $\\dot{Q}_h = 5.0\\,\\mathrm{kW}$, $UA = 125\\,\\mathrm{W/K}$, $\\mathrm{COP}_h = 2.596$"
    ax.text(gc_x, gc_y + 0.55, gc_note, fontsize=7.2, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.25", fc="#fdedec", ec=COLOR_HP, lw=0.7))
    
    evap_note = "Ambient Evaporation: $T_{amb} = -10\\,^\\circ\\mathrm{C}$, $T_{evap} = -15\\,^\\circ\\mathrm{C}$, $\\dot{Q}_{evap} = 3.07\\,\\mathrm{kW}$"
    ax.text(evap_x, evap_y - 0.40, evap_note, fontsize=7.2, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.25", fc="#ebf5fb", ec=COLOR_LP, lw=0.7))
    
    # Compressor Specifications Box (placed on right side with ample margin)
    comp_box = (
        "Compressor Specs:\n"
        "• Speed: $4000\\,\\mathrm{rpm}$\n"
        "• Isentropic: $\\eta_{is}=0.70$\n"
        "• Displacement: $8.88\\,\\mathrm{cm^3}$\n"
        "• Mass flow: $20.22\\,\\mathrm{g/s}$\n"
        "• Power input: $1.926\\,\\mathrm{kW}$"
    )
    ax.text(comp_x + 0.65, comp_y, comp_box, fontsize=6.8, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.30", fc="#f8f9fa", ec="#bdc3c7", lw=0.7))
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_a.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


# ==============================================================================
# CASE B: FLASH-TANK VAPOR INJECTION (Clutter-Free)
# ==============================================================================
def create_case_b_schematic():
    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=300)
    ax.set_xlim(-1.2, 10.6)
    ax.set_ylim(-0.8, 5.8)
    ax.axis('off')
    
    gc_x, gc_y = 4.4, 4.8
    evap_x, evap_y = 4.4, 0.4
    
    c1_x, c1_y = 7.6, 1.4
    c2_x, c2_y = 7.6, 3.7
    mix_x, mix_y = 7.6, 2.55
    
    ft_x, ft_y = 1.6, 2.55
    eev1_x, eev1_y = 1.6, 4.15
    eev2_x, eev2_y = 1.6, 1.05
    eev_inj_x, eev_inj_y = 4.5, 3.25
    
    # Components
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.6, height=0.70,
                        label="Gas Cooler (Condenser)", sublabel="Delivers heat to cabin",
                        color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.6, height=0.70,
                        label="Evaporator", sublabel="Absorbs ambient heat",
                        color=COLOR_LP)
    
    draw_compressor(ax, c1_x, c1_y, width=0.95, height=0.80, label="Stage 1", color=COLOR_COMP)
    draw_compressor(ax, c2_x, c2_y, width=0.95, height=0.80, label="Stage 2", color=COLOR_COMP)
    
    mix_circle = Circle((mix_x, mix_y), 0.14, facecolor="#f39c12", edgecolor="#b9770e", lw=1.4, zorder=8)
    ax.add_patch(mix_circle)
    ax.text(mix_x + 0.25, mix_y, "Mixing\nPlenum", fontsize=6.8, fontweight='bold', va='center', color="#b9770e")
    
    draw_flash_tank(ax, ft_x, ft_y, width=1.1, height=1.65, color=COLOR_IP)
    
    draw_valve(ax, eev1_x, eev1_y, width=0.40, height=0.45, horizontal=False, color=COLOR_COMP, label="EEV-1")
    draw_valve(ax, eev2_x, eev2_y, width=0.40, height=0.45, horizontal=False, color=COLOR_COMP, label="EEV-2")
    draw_valve(ax, eev_inj_x, eev_inj_y, width=0.45, height=0.35, horizontal=True, color=COLOR_INJ, label="EEV-inj")
    
    lw = 1.8
    # 1 -> Stage 1 Suction
    ax.plot([gc_x + 1.3, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.40], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(c1_x, c1_y - 0.40), xytext=(c1_x, c1_y - 0.60), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> Stage 1 Discharge to Mix
    ax.plot([c1_x, c1_x], [c1_y + 0.40, mix_y - 0.14], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c1_x, mix_y - 0.14), xytext=(c1_x, mix_y - 0.32), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 3 -> Mix to Stage 2 Suction
    ax.plot([c2_x, c2_x], [mix_y + 0.14, c2_y - 0.40], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c2_x, c2_y - 0.40), xytext=(c2_x, c2_y - 0.58), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 4 -> Stage 2 Discharge to Gas Cooler
    ax.plot([c2_x, c2_x, gc_x + 1.3], [c2_y + 0.40, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.6, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 5 -> Gas Cooler to EEV1
    ax.plot([gc_x - 1.3, eev1_x, eev1_x], [gc_y, gc_y, eev1_y + 0.23], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev1_x, eev1_y + 0.23), xytext=(eev1_x, eev1_y + 0.42), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 6 -> EEV1 to Flash Tank
    ax.plot([eev1_x, ft_x], [eev1_y - 0.23, ft_y + 0.82], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(ft_x, ft_y + 0.82), xytext=(ft_x, ft_y + 1.0), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 7 -> Vapor extraction to EEV_inj
    ax.plot([ft_x + 0.55, eev_inj_x - 0.23], [ft_y + 0.55, eev_inj_y], color=COLOR_INJ, lw=lw)
    ax.annotate("", xy=(eev_inj_x - 0.23, eev_inj_y), xytext=(eev_inj_x - 0.42, eev_inj_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    
    # 7a -> EEV_inj outlet into Mix
    ax.plot([eev_inj_x + 0.23, mix_x - 0.55, mix_x - 0.55, mix_x - 0.14],
            [eev_inj_y, eev_inj_y, mix_y, mix_y], color=COLOR_INJ, lw=lw)
    ax.annotate("", xy=(mix_x - 0.14, mix_y), xytext=(mix_x - 0.32, mix_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    
    # 8 -> Flash Tank liquid to EEV2
    ax.plot([ft_x, eev2_x], [ft_y - 0.82, eev2_y + 0.23], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(eev2_x, eev2_y + 0.23), xytext=(eev2_x, eev2_y + 0.42), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 9 -> EEV2 to Evaporator
    ax.plot([eev2_x, eev2_x, gc_x - 1.3], [eev2_y - 0.23, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.6, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # State Badges
    draw_state_badge(ax, 7.6, 0.7, "1", color=COLOR_LP)
    draw_state_badge(ax, 7.6, 2.0, "2", color=COLOR_IP)
    draw_state_badge(ax, 7.6, 3.1, "3", color=COLOR_IP)
    draw_state_badge(ax, 7.6, 4.4, "4", color=COLOR_HP)
    draw_state_badge(ax, 1.6, 4.7, "5", color=COLOR_HP)
    draw_state_badge(ax, 1.1, 3.5, "6", color=COLOR_IP)
    draw_state_badge(ax, 2.4, 3.5, "7", color=COLOR_INJ)
    draw_state_badge(ax, 6.4, 2.85, "7a", color=COLOR_INJ)
    draw_state_badge(ax, 1.1, 1.7, "8", color=COLOR_IP)
    draw_state_badge(ax, 1.6, 0.5, "9", color=COLOR_LP)
    
    # Side summary boxes with generous padding
    comp_summary = (
        "Compression & Injection:\n"
        "• State 1: $2.29\\,\\mathrm{MPa},\\,\\dot{m}=20.2\\,\\mathrm{g/s}$\n"
        "• State 2: $3.44\\,\\mathrm{MPa},\\,45.1\\,^\\circ\\mathrm{C}$\n"
        "• State 7a: $\\dot{m}_{inj}=11.0\\,\\mathrm{g/s}\\,(\\mu=0.55)$\n"
        "• State 3: $12.6\\,^\\circ\\mathrm{C}\\,(-32.5\\,\\mathrm{K}\\,\\mathrm{desup.})$\n"
        "• State 4: $9.50\\,\\mathrm{MPa},\\,107.5\\,^\\circ\\mathrm{C}$\n"
        "  ($-12.9\\,\\mathrm{K}$ vs Base, safe $\\leq 130\\,^\\circ\\mathrm{C}$)\n"
        "• Power input: $2.571\\,\\mathrm{kW}$"
    )
    ax.text(c2_x + 0.65, 2.55, comp_summary, fontsize=6.8, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.30", fc="#f8f9fa", ec="#bdc3c7", lw=0.7))
    
    ft_summary = (
        "Flash Tank Specs:\n"
        "• Intermediate: $P_{FT} = 4.25\\,\\mathrm{MPa}$\n"
        "• Sat. temp: $T_{sat} = 7.8\\,^\\circ\\mathrm{C}$\n"
        "• State 6: Flash inlet ($x_6=0.35$)\n"
        "• State 7: Sat. vapor ($x_7=1.0$)\n"
        "• State 8: Sat. liquid ($x_8=0.0$)\n"
        "• State 9: Evap inlet ($x_9=0.21$)\n"
        "  Subcooling adds $+42.6\\,\\mathrm{kJ/kg}$ lift!"
    )
    ax.text(ft_x - 0.70, 2.55, ft_summary, fontsize=6.8, va='center', ha='right',
            bbox=dict(boxstyle="round,pad=0.30", fc="#fef9e7", ec=COLOR_IP, lw=0.7))
    
    # Top & Bottom performance banners
    gc_banner = "FT-VI Heat Delivery: $\\dot{Q}_h = 7.049\\,\\mathrm{kW}$ (+41.0% vs Base), $\\mathrm{COP}_h = 2.742$ (+5.7% vs Base)"
    ax.text(gc_x, gc_y + 0.55, gc_banner, fontsize=7.2, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.25", fc="#eafaf1", ec="#27ae60", lw=0.7))
    
    evap_banner = "Ambient Evaporation: $T_{amb} = -10\\,^\\circ\\mathrm{C}$, $\\dot{Q}_{evap} = 4.41\\,\\mathrm{kW}$, $\\dot{m}_{suc} = 20.22\\,\\mathrm{g/s}$"
    ax.text(evap_x, evap_y - 0.40, evap_banner, fontsize=7.2, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.25", fc="#ebf5fb", ec=COLOR_LP, lw=0.7))
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_b.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


# ==============================================================================
# CASE C: TWO-STAGE INTERCOOLED CYCLE (Clutter-Free)
# ==============================================================================
def create_case_c_schematic():
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    ax.set_xlim(-0.6, 9.8)
    ax.set_ylim(-0.8, 5.6)
    ax.axis('off')
    
    gc_x, gc_y = 3.8, 4.6
    evap_x, evap_y = 3.8, 0.4
    eev_x, eev_y = 0.8, 2.5
    
    c1_x, c1_y = 6.8, 1.3
    ic_x, ic_y = 6.8, 2.5
    c2_x, c2_y = 6.8, 3.7
    
    # Components
    draw_heat_exchanger(ax, gc_x, gc_y, width=2.6, height=0.70,
                        label="Gas Cooler (Condenser)", sublabel="Rejects heat to cabin",
                        color=COLOR_HP)
    draw_heat_exchanger(ax, evap_x, evap_y, width=2.6, height=0.70,
                        label="Evaporator", sublabel="Absorbs heat from ambient",
                        color=COLOR_LP)
    draw_compressor(ax, c1_x, c1_y, width=0.95, height=0.75, label="Compressor C1", color=COLOR_COMP)
    draw_heat_exchanger(ax, ic_x, ic_y, width=1.3, height=0.65, label="Intercooler", sublabel="$\\dot{Q}_{IC}$", color=COLOR_IP)
    draw_compressor(ax, c2_x, c2_y, width=0.95, height=0.75, label="Compressor C2", color=COLOR_COMP)
    draw_valve(ax, eev_x, eev_y, width=0.45, height=0.50, horizontal=False, color=COLOR_COMP, label="EEV\n($h_6=h_5$)")
    
    lw = 1.8
    # 1 -> C1 Suction
    ax.plot([gc_x + 1.3, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.38], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(c1_x, c1_y - 0.38), xytext=(c1_x, c1_y - 0.58), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # 2 -> C1 discharge to IC
    ax.plot([c1_x, c1_x], [c1_y + 0.38, ic_y - 0.33], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c1_x, ic_y - 0.33), xytext=(c1_x, ic_y - 0.50), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 3 -> IC to C2 suction
    ax.plot([c2_x, c2_x], [ic_y + 0.33, c2_y - 0.38], color=COLOR_IP, lw=lw)
    ax.annotate("", xy=(c2_x, c2_y - 0.38), xytext=(c2_x, c2_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    
    # 4 -> C2 discharge to Gas Cooler
    ax.plot([c2_x, c2_x, gc_x + 1.3], [c2_y + 0.38, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(gc_x + 1.3, gc_y), xytext=(gc_x + 1.6, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 5 -> Gas Cooler to EEV
    ax.plot([gc_x - 1.3, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.32], color=COLOR_HP, lw=lw)
    ax.annotate("", xy=(eev_x, eev_y + 0.32), xytext=(eev_x, eev_y + 0.52), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    
    # 6 -> EEV to Evaporator
    ax.plot([eev_x, eev_x, gc_x - 1.3], [eev_y - 0.32, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax.annotate("", xy=(gc_x - 1.3, evap_y), xytext=(gc_x - 1.6, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    # State Badges
    draw_state_badge(ax, 6.8, 0.65, "1", color=COLOR_LP)
    draw_state_badge(ax, 7.3, 1.9, "2", color=COLOR_IP)
    draw_state_badge(ax, 7.3, 3.1, "3", color=COLOR_IP)
    draw_state_badge(ax, 6.8, 4.25, "4", color=COLOR_HP)
    draw_state_badge(ax, 0.8, 3.8, "5", color=COLOR_HP)
    draw_state_badge(ax, 0.8, 1.2, "6", color=COLOR_LP)
    
    # State callout labels
    ax.text(6.8 - 0.25, 0.65, "State 1: $2.29\\,\\mathrm{MPa},\\,-10\\,^\\circ\\mathrm{C}$", fontsize=6.8, ha='right', va='center', color=COLOR_LP)
    ax.text(6.8 - 0.85, 2.5, "$\\dot{Q}_{IC} = 0.812\\,\\mathrm{kW}$\n(Ambient Reject or\nCabin Recovery)",
            fontsize=6.8, ha='right', va='center', color=COLOR_IP,
            bbox=dict(boxstyle="round,pad=0.20", fc="#fef9e7", ec=COLOR_IP, lw=0.6))
    
    ax.text(0.8 + 0.30, 3.8, "State 5: $9.50\\,\\mathrm{MPa},\\,35.0\\,^\\circ\\mathrm{C}$", fontsize=6.8, ha='left', va='center', color=COLOR_HP)
    ax.text(0.8 + 0.30, 1.2, "State 6: $2.29\\,\\mathrm{MPa},\\,x=0.32$", fontsize=6.8, ha='left', va='center', color=COLOR_LP)
    
    # Intercooled Specs box on right
    ic_box = (
        "Two-Stage Intercooled:\n"
        "• Intermediate: $P_i = 4.50\\,\\mathrm{MPa}$\n"
        "• State 2: $T_2 = 59.8\\,^\\circ\\mathrm{C}$\n"
        "• State 3: $T_3 = 35.0\\,^\\circ\\mathrm{C}$\n"
        "• State 4: $T_{dis} = 98.2\\,^\\circ\\mathrm{C}$\n"
        "• Power input: $1.765\\,\\mathrm{kW}$\n"
        "• Speed: $4203\\,\\mathrm{rpm}$ (+33%)\n"
        "• Dual radiators required"
    )
    ax.text(c1_x + 0.65, 2.5, ic_box, fontsize=6.8, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.30", fc="#f4ecf7", ec="#8e44ad", lw=0.7))
    
    # Top & bottom banners
    gc_banner = "Case C Heat Rejection: $\\mathrm{COP}_h = 2.294$ (Reject Mode), $\\mathrm{COP}_h = 2.824$ (Recover Mode)"
    ax.text(gc_x, gc_y + 0.55, gc_banner, fontsize=7.2, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.25", fc="#fdedec", ec=COLOR_HP, lw=0.7))
    
    evap_banner = "Ambient Evaporator: $T_{amb} = -10\\,^\\circ\\mathrm{C}$, $\\dot{Q}_{evap} = 3.07\\,\\mathrm{kW}$, $\\dot{m} = 20.22\\,\\mathrm{g/s}$"
    ax.text(evap_x, evap_y - 0.40, evap_banner, fontsize=7.2, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.25", fc="#ebf5fb", ec=COLOR_LP, lw=0.7))
    
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematic_case_c.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


# ==============================================================================
# COMBINED 3-PANEL COMPARATIVE SCHEMATIC (Clutter-Free)
# ==============================================================================
def create_combined_schematic():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 4.6), dpi=300)
    
    # Panel 1: Case A
    ax1.set_xlim(-0.2, 7.8)
    ax1.set_ylim(-0.6, 5.6)
    ax1.axis('off')
    gc_x, gc_y = 3.8, 4.6
    evap_x, evap_y = 3.8, 0.4
    eev_x, eev_y = 0.8, 2.5
    comp_x, comp_y = 6.8, 2.5
    
    draw_heat_exchanger(ax1, gc_x, gc_y, width=2.4, height=0.65, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax1, evap_x, evap_y, width=2.4, height=0.65, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax1, comp_x, comp_y, width=0.9, height=0.9, label="Compressor", color=COLOR_COMP)
    draw_valve(ax1, eev_x, eev_y, width=0.4, height=0.45, horizontal=False, color=COLOR_COMP, label="EEV")
    
    lw = 1.6
    ax1.plot([gc_x + 1.2, comp_x, comp_x], [evap_y, evap_y, comp_y - 0.45], color=COLOR_LP, lw=lw)
    ax1.annotate("", xy=(comp_x, comp_y - 0.45), xytext=(comp_x, comp_y - 0.65), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax1.plot([comp_x, comp_x, gc_x + 1.2], [comp_y + 0.45, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax1.annotate("", xy=(gc_x + 1.2, gc_y), xytext=(gc_x + 1.45, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax1.plot([gc_x - 1.2, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.28], color=COLOR_HP, lw=lw)
    ax1.annotate("", xy=(eev_x, eev_y + 0.28), xytext=(eev_x, eev_y + 0.48), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax1.plot([eev_x, eev_x, gc_x - 1.2], [eev_y - 0.28, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax1.annotate("", xy=(gc_x - 1.2, evap_y), xytext=(gc_x - 1.45, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax1, 6.8, 1.1, "1", color=COLOR_LP)
    draw_state_badge(ax1, 6.8, 3.9, "2", color=COLOR_HP)
    draw_state_badge(ax1, 0.8, 3.9, "3", color=COLOR_HP)
    draw_state_badge(ax1, 0.8, 1.1, "4", color=COLOR_LP)
    
    ax1.text(3.8, 2.5,
             "Case A: Baseline Single-Stage\n"
             "• 1 Compressor, 1 EEV, 4 States\n"
             "• $\\dot{Q}_h = 5.00\\,\\mathrm{kW}$, $\\mathrm{COP}_h = 2.596$\n"
             "• $T_{dis} = 120.4\\,^\\circ\\mathrm{C}$, $W = 1.926\\,\\mathrm{kW}$\n"
             "• At $-15\\,^\\circ\\mathrm{C}$: Fails $130\\,^\\circ\\mathrm{C}$ limit!",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.25", fc="#f8f9fa", ec="#bdc3c7", lw=0.7))
    ax1.text(3.8, 5.3, "(a) Case A: Baseline Single-Stage", fontsize=9.0, fontweight='bold', ha='center', color=COLOR_COMP)

    # Panel 2: Case B (FT-VI)
    ax2.set_xlim(-0.2, 8.8)
    ax2.set_ylim(-0.6, 5.6)
    ax2.axis('off')
    gc_x, gc_y = 4.3, 4.6
    evap_x, evap_y = 4.3, 0.4
    c1_x, c1_y = 7.4, 1.3
    c2_x, c2_y = 7.4, 3.7
    mix_x, mix_y = 7.4, 2.5
    ft_x, ft_y = 2.0, 2.5
    eev1_x, eev1_y = 2.0, 4.0
    eev2_x, eev2_y = 2.0, 1.0
    eev_inj_x, eev_inj_y = 4.6, 3.1
    
    draw_heat_exchanger(ax2, gc_x, gc_y, width=2.4, height=0.65, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax2, evap_x, evap_y, width=2.4, height=0.65, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax2, c1_x, c1_y, width=0.85, height=0.75, label="C1", color=COLOR_COMP)
    draw_compressor(ax2, c2_x, c2_y, width=0.85, height=0.75, label="C2", color=COLOR_COMP)
    draw_flash_tank(ax2, ft_x, ft_y, width=1.0, height=1.45, color=COLOR_IP)
    draw_valve(ax2, eev1_x, eev1_y, width=0.35, height=0.40, horizontal=False, color=COLOR_COMP, label="EEV1")
    draw_valve(ax2, eev2_x, eev2_y, width=0.35, height=0.40, horizontal=False, color=COLOR_COMP, label="EEV2")
    draw_valve(ax2, eev_inj_x, eev_inj_y, width=0.42, height=0.32, horizontal=True, color=COLOR_INJ, label="EEVinj")
    
    mix_circle = Circle((mix_x, mix_y), 0.12, facecolor="#f39c12", edgecolor="#b9770e", lw=1.2, zorder=8)
    ax2.add_patch(mix_circle)
    
    ax2.plot([gc_x + 1.2, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.38], color=COLOR_LP, lw=lw)
    ax2.annotate("", xy=(c1_x, c1_y - 0.38), xytext=(c1_x, c1_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax2.plot([c1_x, c1_x], [c1_y + 0.38, mix_y - 0.12], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(c1_x, mix_y - 0.12), xytext=(c1_x, mix_y - 0.28), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([c2_x, c2_x], [mix_y + 0.12, c2_y - 0.38], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(c2_x, c2_y - 0.38), xytext=(c2_x, c2_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([c2_x, c2_x, gc_x + 1.2], [c2_y + 0.38, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax2.annotate("", xy=(gc_x + 1.2, gc_y), xytext=(gc_x + 1.45, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax2.plot([gc_x - 1.2, eev1_x, eev1_x], [gc_y, gc_y, eev1_y + 0.20], color=COLOR_HP, lw=lw)
    ax2.annotate("", xy=(eev1_x, eev1_y + 0.20), xytext=(eev1_x, eev1_y + 0.38), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax2.plot([eev1_x, ft_x], [eev1_y - 0.20, ft_y + 0.72], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(ft_x, ft_y + 0.72), xytext=(ft_x, ft_y + 0.90), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([ft_x + 0.5, eev_inj_x - 0.21], [ft_y + 0.48, eev_inj_y], color=COLOR_INJ, lw=lw)
    ax2.annotate("", xy=(eev_inj_x - 0.21, eev_inj_y), xytext=(eev_inj_x - 0.38, eev_inj_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    ax2.plot([eev_inj_x + 0.21, mix_x - 0.45, mix_x - 0.45, mix_x - 0.12],
             [eev_inj_y, eev_inj_y, mix_y, mix_y], color=COLOR_INJ, lw=lw)
    ax2.annotate("", xy=(mix_x - 0.12, mix_y), xytext=(mix_x - 0.28, mix_y), arrowprops=dict(arrowstyle="->", color=COLOR_INJ, lw=lw))
    ax2.plot([ft_x, eev2_x], [ft_y - 0.72, eev2_y + 0.20], color=COLOR_IP, lw=lw)
    ax2.annotate("", xy=(eev2_x, eev2_y + 0.20), xytext=(eev2_x, eev2_y + 0.38), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax2.plot([eev2_x, eev2_x, gc_x - 1.2], [eev2_y - 0.20, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax2.annotate("", xy=(gc_x - 1.2, evap_y), xytext=(gc_x - 1.45, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax2, 7.4, 0.7, "1", color=COLOR_LP)
    draw_state_badge(ax2, 7.8, 1.9, "2", color=COLOR_IP)
    draw_state_badge(ax2, 7.8, 3.1, "3", color=COLOR_IP)
    draw_state_badge(ax2, 7.4, 4.3, "4", color=COLOR_HP)
    draw_state_badge(ax2, 2.0, 4.6, "5", color=COLOR_HP)
    draw_state_badge(ax2, 1.4, 3.3, "6", color=COLOR_IP)
    draw_state_badge(ax2, 2.7, 3.2, "7", color=COLOR_INJ)
    draw_state_badge(ax2, 6.4, 2.8, "7a", color=COLOR_INJ)
    draw_state_badge(ax2, 1.4, 1.7, "8", color=COLOR_IP)
    draw_state_badge(ax2, 2.0, 0.6, "9", color=COLOR_LP)
    
    ax2.text(4.4, 1.8,
             "Case B: Flash-Tank Vapor Injection\n"
             "• Flash Tank, 3 Valves, 10 States\n"
             "• $\\dot{Q}_h = 7.049\\,\\mathrm{kW}$ (+41.0% vs A)\n"
             "• $\\mathrm{COP}_h = 2.742$ (+5.7% vs A)\n"
             "• $T_{dis} = 107.5\\,^\\circ\\mathrm{C}$ ($-12.9\\,\\mathrm{K}$ cooler)\n"
             "• Subcools liquid: $x_9=0.21$ vs $0.32$",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.25", fc="#eafaf1", ec="#27ae60", lw=0.7))
    ax2.text(4.3, 5.3, "(b) Case B: Flash-Tank Vapor Injection (FT-VI)", fontsize=9.0, fontweight='bold', ha='center', color="#27ae60")

    # Panel 3: Case C (Intercooled)
    ax3.set_xlim(-0.2, 8.0)
    ax3.set_ylim(-0.6, 5.6)
    ax3.axis('off')
    gc_x, gc_y = 3.9, 4.6
    evap_x, evap_y = 3.9, 0.4
    eev_x, eev_y = 0.8, 2.5
    c1_x, c1_y = 6.8, 1.3
    ic_x, ic_y = 6.8, 2.5
    c2_x, c2_y = 6.8, 3.7
    
    draw_heat_exchanger(ax3, gc_x, gc_y, width=2.4, height=0.65, label="Gas Cooler", sublabel="To cabin air", color=COLOR_HP)
    draw_heat_exchanger(ax3, evap_x, evap_y, width=2.4, height=0.65, label="Evaporator", sublabel="From ambient air", color=COLOR_LP)
    draw_compressor(ax3, c1_x, c1_y, width=0.85, height=0.75, label="C1", color=COLOR_COMP)
    draw_heat_exchanger(ax3, ic_x, ic_y, width=1.1, height=0.55, label="Intercooler", sublabel="$\\dot{Q}_{IC}$", color=COLOR_IP)
    draw_compressor(ax3, c2_x, c2_y, width=0.85, height=0.75, label="C2", color=COLOR_COMP)
    draw_valve(ax3, eev_x, eev_y, width=0.38, height=0.45, horizontal=False, color=COLOR_COMP, label="EEV")
    
    ax3.plot([gc_x + 1.2, c1_x, c1_x], [evap_y, evap_y, c1_y - 0.38], color=COLOR_LP, lw=lw)
    ax3.annotate("", xy=(c1_x, c1_y - 0.38), xytext=(c1_x, c1_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    ax3.plot([c1_x, c1_x], [c1_y + 0.38, ic_y - 0.28], color=COLOR_IP, lw=lw)
    ax3.annotate("", xy=(c1_x, ic_y - 0.28), xytext=(c1_x, ic_y - 0.45), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax3.plot([c2_x, c2_x], [ic_y + 0.28, c2_y - 0.38], color=COLOR_IP, lw=lw)
    ax3.annotate("", xy=(c2_x, c2_y - 0.38), xytext=(c2_x, c2_y - 0.55), arrowprops=dict(arrowstyle="->", color=COLOR_IP, lw=lw))
    ax3.plot([c2_x, c2_x, gc_x + 1.2], [c2_y + 0.38, gc_y, gc_y], color=COLOR_HP, lw=lw)
    ax3.annotate("", xy=(gc_x + 1.2, gc_y), xytext=(gc_x + 1.45, gc_y), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax3.plot([gc_x - 1.2, eev_x, eev_x], [gc_y, gc_y, eev_y + 0.25], color=COLOR_HP, lw=lw)
    ax3.annotate("", xy=(eev_x, eev_y + 0.25), xytext=(eev_x, eev_y + 0.45), arrowprops=dict(arrowstyle="->", color=COLOR_HP, lw=lw))
    ax3.plot([eev_x, eev_x, gc_x - 1.2], [eev_y - 0.25, evap_y, evap_y], color=COLOR_LP, lw=lw)
    ax3.annotate("", xy=(gc_x - 1.2, evap_y), xytext=(gc_x - 1.45, evap_y), arrowprops=dict(arrowstyle="->", color=COLOR_LP, lw=lw))
    
    draw_state_badge(ax3, 6.8, 0.7, "1", color=COLOR_LP)
    draw_state_badge(ax3, 7.3, 1.8, "2", color=COLOR_IP)
    draw_state_badge(ax3, 7.3, 3.2, "3", color=COLOR_IP)
    draw_state_badge(ax3, 6.8, 4.3, "4", color=COLOR_HP)
    draw_state_badge(ax3, 0.8, 3.9, "5", color=COLOR_HP)
    draw_state_badge(ax3, 0.8, 1.1, "6", color=COLOR_LP)
    
    ax3.text(3.9, 2.5,
             "Case C: Two-Stage Intercooled\n"
             "• 2 Compressors, 1 IC, 6 States\n"
             "• $P_i = 4.50\\,\\mathrm{MPa}$, $\\dot{Q}_{IC} = 0.812\\,\\mathrm{kW}$\n"
             "• Mode 1 (Reject): $\\mathrm{COP}_h = 2.294$\n"
             "• Mode 2 (Recover): $\\mathrm{COP}_h = 2.824$\n"
             "• Requires +33% Speed ($4203\\,\\mathrm{rpm}$)\n"
             "• Heavy dual-radiator penalty",
             fontsize=7.2, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.25", fc="#f4ecf7", ec="#8e44ad", lw=0.7))
    ax3.text(3.9, 5.3, "(c) Case C: Two-Stage Intercooled", fontsize=9.0, fontweight='bold', ha='center', color="#8e44ad")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "schematics_cases_abc_comparison.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    print("Generating clean, clutter-free cycle schematics...")
    create_case_a_schematic()
    create_case_b_schematic()
    create_case_c_schematic()
    create_combined_schematic()
    print("All schematics generated successfully!")
