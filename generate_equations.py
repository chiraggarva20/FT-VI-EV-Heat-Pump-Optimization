"""Generate crisp vector SVG equations for IEEE report using Matplotlib MathText."""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('eq_svg', exist_ok=True)

# STIX or Computer Modern fonts give publication-grade math rendering
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'serif'

equations = {
    'eq1': r"$\dot{Q}_e = \dot{m} (h_1 - h_4) = \dot{m} (h_1 - h_3)$",
    'eq2': r"$\dot{Q}_h = \dot{m} (h_2 - h_3)$",
    'eq3': r"$\dot{W}_c = \dot{m} (h_2 - h_1) = \dot{m} \frac{h_{2s} - h_1}{\eta_{is}}$",
    'eq4': r"$\mathrm{COP}_h = \frac{\dot{Q}_h}{\dot{W}_c} = \frac{h_2 - h_3}{h_2 - h_1}$",
    'eq5': r"$\eta_v = \mathrm{EV}_0 - \mathrm{EV}_1 \left(\frac{P_{dis}}{P_{evap}}\right)$",
    'eq6': r"$\dot{m} = \frac{V_{disp} \cdot N}{60} \cdot \rho_{suc} \cdot \eta_v$",
    'eq7': r"$\eta_{is}(n, PR) = \eta_d - a_{low}(1-n)^2 [n < 1] - a_{high}(n-1)^2 [n > 1] - k_{PR} \ln^2 \left(\frac{PR}{PR_{ref}}\right)$",
    'eq8': r"$P_{port} = r_{port} \cdot P_{evap} \quad (r_{port} = 1.50)$",
    'eq9': r"$x_{FT} = \frac{h_5 - h_f(P_{FT})}{h_g(P_{FT}) - h_f(P_{FT})}$",
    'eq10': r"$r_{crit} = \left(\frac{2}{k+1}\right)^{\frac{k}{k-1}} \approx 0.546 \quad (k = 1.30)$",
    'eq11': r"$\dot{m}_{valve} = \phi \cdot C_d A_{max} \cdot Y \cdot \sqrt{2 \rho_g(P_{FT}) \Delta P_{eff}}$",
    'eq12': r"$Y = 1 - 0.41 \frac{\Delta P_{eff}}{k P_{FT}}, \quad \Delta P_{eff} = \min(P_{FT} - P_{port}, (1 - r_{crit})P_{FT})$",
    'eq13': r"$\dot{m}_{inj} = \min(\dot{m}_{valve}, \dot{m}_{inj,max}), \quad \dot{m}_{inj,max} = \frac{x_{FT}}{1 - x_{FT}} \dot{m}_{suc}$",
    'eq14': r"$\dot{Q}_{ic} = \dot{m}_{suc} (h_2 - h_3)$",
    'eq15': r"$T_{mix} = \frac{\dot{m}_{vent} T_{amb} + (\dot{m}_{air} - \dot{m}_{vent}) T_{cabin}}{\dot{m}_{air}}$",
    'eq16': r"$\dot{Q}_h = \dot{Q}_e + \dot{W}_{comp} \quad \Longleftrightarrow \quad |\dot{Q}_h - (\dot{Q}_e + \dot{W}_{comp})| < \epsilon$",
    'eq17': r"$C_i = \frac{S_i^-}{S_i^* + S_i^-}, \quad 0 \leq C_i \leq 1$",
    'eq18': r"$h_{mix} = \frac{\dot{m}_{suc} h_{2a} + \dot{m}_{inj} h_7}{\dot{m}_{tot}} = \frac{h_{2a} + \mu h_7}{1 + \mu}$",
    'eq19': r"$\dot{W}_{comp} = \dot{m}_{suc} (h_{2a} - h_1) + \dot{m}_{tot} (h_2 - h_{mix})$",
    'eq20': r"$P_{i,geom} = \sqrt{P_{evap} \cdot P_{dis}}$"
}

for eq_name, latex_code in equations.items():
    fig = plt.figure(figsize=(5, 0.45), dpi=300)
    # Render text cleanly centered
    fig.text(0.5, 0.5, latex_code, fontsize=10.5, ha='center', va='center', color='#0f172a')
    out_path = os.path.join('eq_svg', f'{eq_name}.svg')
    fig.savefig(out_path, format='svg', bbox_inches='tight', pad_inches=0.03, transparent=True)
    plt.close(fig)
    print(f"Rendered {out_path}: {latex_code}")

print("All 20 equations generated successfully.")
