# ME 316 S2: Theory & Concepts Quiz Cheat Sheet
## Transcritical $\text{CO}_2$ Heat Pump with Flash-Tank Vapor Injection (FT-VI)

> **Quick Orientation:** This cheat sheet summarizes all core **theories, physical mechanisms, component working principles, and conceptual trade-offs** of the project in concise, bulleted format for rapid revision before a theory-based quiz.

---

## 1. Thermodynamic Problem in Electric Vehicles (EVs)

### Why EV Cabin Heating is Difficult
- **Internal Combustion Engine (ICE) vs. Battery Electric Vehicle (BEV):**
  - ICE cars harvest "free" high-grade waste heat from the engine cooling jacket (~$20\text{--}30\text{ kW}$ thermal) without penalizing fuel economy.
  - BEVs have powertrain efficiencies of $90\%\text{--}95\%$, producing virtually no waste heat during steady cruising ($\le 1\text{--}2\text{ kW}$).
- **Resistive (PTC) Heaters Penalty:**
  - Positive Temperature Coefficient (PTC) heaters operate on Joule heating ($\text{COP} = 1.0$).
  - Supplying a standard $5.0\text{ kW}$ cabin load draws $5.0\text{ kW}$ of continuous electrical power directly from the traction battery.
  - Over a 1-hour winter drive, extracting $5.0\text{ kWh}$ slashes driving range by **$30\%\text{--}45\%$**.
- **Heat Pump Solution:**
  - A heat pump pumps low-grade heat from cold outdoor air into the cabin with $\text{COP}_h = 2.5\text{--}3.0$, cutting battery drain by **$50\%\text{--}65\%$**.

### The Cold-Weather Thermodynamic Bottleneck (Why Baseline Fails at Sub-Zero)
1. **Suction Vapor Density Collapse:**
   - Outdoor air at $-10^\circ\text{C}$ to $-15^\circ\text{C}$ forces evaporation pressure down ($P_{\text{evap}} = 2.29\text{ MPa}$ to $1.97\text{ MPa}$).
   - Suction vapor density collapses from normal levels down to $\rho_{\text{suc}} \approx 60.1\text{ kg/m}^3$ (at $-10^\circ\text{C}$) and $47.6\text{ kg/m}^3$ (at $-15^\circ\text{C}$).
2. **Volumetric Efficiency ($\eta_v$) Degradation:**
   - The compressor must still lift refrigerant from low pressure ($2.29\text{ MPa}$) up to cabin heating pressure ($9.5\text{ MPa}$).
   - Overall pressure ratio surges: $\text{PR} = P_{\text{dis}} / P_{\text{suc}} > 4.15$ (surges to $4.84$ at $-15^\circ\text{C}$).
   - Residual vapor trapped in clearance volume re-expands during suction, preventing intake of fresh vapor ($\eta_v = 0.97 - 0.03 \cdot \text{PR}$).
   - Mass flow collapses $\rightarrow$ Heating capacity falls below the required $5.0\text{ kW}$ ($4.39\text{ kW}$ at $-15^\circ\text{C}$).
3. **Discharge Temperature Runaway:**
   - Steep single-stage isentropic pressure lift drives compressor discharge temperature above the **$130.0^\circ\text{C}$ hard thermal limit**.
   - Beyond $130^\circ\text{C}$, polyalkylene glycol (PAG) lubricant oil thermally decomposes, lubricity fails, and the compressor faces seizure.

---

## 2. R744 ($\text{CO}_2$) & The Transcritical Cycle

### Natural Refrigerant Fundamentals
- **Environmental Benefits:** Zero Ozone Depletion Potential ($\text{ODP} = 0$), Global Warming Potential ($\text{GWP} = 1$), non-toxic, non-flammable (ASHRAE Safety Group A1).

### The Critical Point Constraint ($T_c = 30.98^\circ\text{C}, P_c = 7.38\text{ MPa}$)
- **Why Transcritical?**
  - Automotive passenger cabin heating requires hot air delivery at **$40^\circ\text{C}\text{--}45^\circ\text{C}$**.
  - Because $40^\circ\text{C}\text{--}45^\circ\text{C}$ is **above** the critical temperature ($T_c = 30.98^\circ\text{C}$), constant-temperature subcritical condensation is physically impossible.
  - Heat rejection must occur **supercritically** ($P_{\text{dis}} = 9.5\text{ MPa} > P_c$) in a continuous single-phase **Gas Cooler** (sensible cooling along a temperature glide, no phase boundary).
  - Heat absorption occurs **subcritically** ($P_{\text{evap}} = 2.29\text{ MPa} < P_c$) inside the saturation dome via latent heat boiling.
  - A cycle operating across the critical pressure boundary is termed **Transcritical**.

### Temperature Glide & Exergy Advantage
- In standard subcritical condensers, condensation occurs at constant temperature, creating large temperature differences and high irreversibility (exergy destruction) against warming air.
- In supercritical gas cooling, $\text{CO}_2$ exhibits a **temperature glide** that matches the warming air temperature profile, reducing heat transfer exergy destruction.

---

## 3. Component-by-Component Governing Principles

| Component | Thermodynamic Process | Governing Equation / Principle | Physical Mechanism |
| :--- | :--- | :--- | :--- |
| **Compressor** | Non-isentropic compression | $\dot{W} = \dot{m}(h_{\text{out}} - h_{\text{in}})$, $\eta_{\text{is}} = \frac{h_{\text{is}} - h_{\text{in}}}{h_{\text{act}} - h_{\text{in}}}$ | Real compression deviates from isentropic due to internal friction, fluid shear, and valve throttling. $\eta_{\text{is}}$ drops quadratically with $\text{PR}$ and linearly with speed $N$. |
| **Gas Cooler** | Isobaric sensible cooling | $\dot{Q}_h = \dot{m}(h_{\text{in}} - h_{\text{out}}) = UA \cdot \Delta T_{\text{LMTD}}$ | Rejects heat to cabin air without condensation; dense fluid exits at $35^\circ\text{C}$ into dense liquid-like supercritical state. |
| **Expansion Valves** | Adiabatic, isenthalpic throttling | $h_{\text{out}} = h_{\text{in}}$ ($\Delta h = 0$) | Highly irreversible constant-enthalpy pressure drop; fluid partially flashes into vapor. |
| **Flash Tank** | Isobaric phase separation | $x_{\text{FT}} = \frac{h_{\text{in}} - h_f}{h_g - h_f}$, $\dot{m}_{\text{vap}} = x \dot{m}_{\text{tot}}$ | Gravity separates two-phase mixture into saturated vapor ($x=1$) at top dome and saturated liquid ($x=0$) at bottom sump. |
| **Injection EEV** | Compressible orifice expansion | $\dot{m} = f(C_d, A, \phi, \rho, P_{\text{up}}, P_{\text{down}})$ | Throttles vapor from $P_{\text{FT}}$ to $P_{\text{port}}$. Experiences sonic choking when pressure ratio drops below $r_{\text{crit}} \approx 0.546$. |
| **Mixing Plenum** | Isobaric adiabatic mixing | $h_3 = \frac{\dot{m}_{\text{suc}} h_2 + \dot{m}_{\text{inj}} h_{7a}}{\dot{m}_{\text{tot}}}$ | Merges Stage-1 warm discharge with cold throttled flash vapor, producing significant **desuperheating** ($-32.5\text{ K}$) before Stage 2. |
| **Evaporator** | Isobaric latent boiling | $\dot{Q}_{\text{evap}} = \dot{m}_{\text{suc}}(h_1 - h_{\text{in}})$ | Absorbs low-grade environmental heat from outdoor air; exits with $5\text{ K}$ superheat to protect compressor from liquid droplets. |

---

## 4. The Two Fundamental Mechanisms of FT-VI Superiority

Flash-Tank Vapor Injection boosts heating capacity by **$+41.0\%$** and suppresses discharge temperature by **$12.9\text{ K}$** through two distinct thermodynamic effects:

### Mechanism 1: Mass Flow Augmentation (In Gas Cooler)
- In single-stage baseline (Case A), only suction flow $\dot{m}_{\text{suc}} = 20.22\text{ g/s}$ passes through the compressor and gas cooler.
- In FT-VI (Case B), the flash tank extracts vapor and injects $\dot{m}_{\text{inj}} = 11.04\text{ g/s}$ into Stage 2.
- Total refrigerant mass flow circulating through the cabin gas cooler surges by **$+54.6\%$**:
  $$\dot{m}_{\text{tot}} = \dot{m}_{\text{suc}} + \dot{m}_{\text{inj}} = 20.22 + 11.04 = 31.26\text{ g/s}$$
- Because heating capacity $\dot{Q}_h = \dot{m}_{\text{tot}}(h_4 - h_5)$, boosting mass flow directly expands cabin heat output from $5.00\text{ kW}$ to $7.05\text{ kW}$.

### Mechanism 2: Liquid Subcooling (In Evaporator)
- In Case A, fluid throttles directly from the gas cooler exit ($h_3 = 285.2\text{ kJ/kg}$) to evaporator pressure, entering with high vapor quality ($x_4 = 0.322$).
- In FT-VI, expanded fluid is separated in the flash tank, and **only pure saturated liquid** ($x_8 = 0.0$, $h_8 = 219.0\text{ kJ/kg}$) is fed to the main expansion valve (EEV-2).
- Evaporator inlet vapor quality drops from **$0.322$ down to $0.207$**.
- This subcooling expands the specific latent heat absorption capacity $(h_1 - h_{\text{in}})$ by **$+42.6\text{ kJ/kg}$ ($+27.6\%$)**, enabling the outdoor evaporator to extract $4.41\text{ kW}$ of heat from $-10^\circ\text{C}$ air despite low suction density.

### Thermal Safety Mechanism: Intermediate Desuperheating
- Stage 1 compresses gas to intermediate port pressure ($3.44\text{ MPa}$), reaching $T_2 = 45.1^\circ\text{C}$.
- Cold injected vapor enters at $T_{7a} \approx -0.5^\circ\text{C}$.
- Mixing drops Stage 2 inlet temperature to **$T_3 = 12.6^\circ\text{C}$ (a $32.5\text{ K}$ desuperheating drop)**.
- Stage 2 starts compression from a much colder base, limiting final discharge to **$107.5^\circ\text{C}$** ($12.9\text{ K}$ cooler than Case A).
- At $-15^\circ\text{C}$, FT-VI operates safely at $116.8^\circ\text{C}$ while Case A violates the $130^\circ\text{C}$ oil breakdown limit ($130.4^\circ\text{C}$).

---

## 5. Architectural Comparison: Case A vs. Case B vs. Case C

```
   Case A (Baseline)             Case B (FT-VI Economized)         Case C (Two-Stage Intercooled)
  ┌─────────────────┐             ┌─────────────────────┐              ┌────────────────────┐
  │  1 Compressor   │             │ 2 Compression Stages│              │2 Compression Stages│
  │  1 EEV          │             │ 3 EEVs + Flash Tank │              │1 EEV + Intercooler │
  │  4 States       │             │ 10 States           │              │6 States            │
  └─────────────────┘             └─────────────────────┘              └────────────────────┘
  Single mass flow.               Augmented mass flow.                 Single mass flow.
  Steep pressure lift.            Inter-stage vapor injection.         Sensible heat rejected midway.
  Fails at -15 °C.                Cruises at -30% speed.               Packaging penalty (dual radiators).
```

### State-by-State Mapping (Directly Matching Handwritten Diagrams)

| State | Case A (Baseline) | Case B (Flash-Tank VI) | Case C (Intercooled) |
| :---: | :--- | :--- | :--- |
| **①** | Evaporator exit $\rightarrow$ Comp suction | Evaporator exit $\rightarrow$ Stage 1 suction | Evaporator exit $\rightarrow$ C1 suction |
| **②** | Comp discharge $\rightarrow$ Gas Cooler inlet | Stage 1 discharge $\rightarrow$ Mixing plenum | C1 discharge $\rightarrow$ Intercooler (IC) inlet |
| **③** | Gas Cooler exit ($35^\circ\text{C}$) $\rightarrow$ EEV inlet | Mixing plenum $\rightarrow$ Stage 2 suction | Intercooler exit $\rightarrow$ C2 suction |
| **④** | EEV exit $\rightarrow$ Evaporator inlet ($h_4=h_3$) | Stage 2 discharge $\rightarrow$ Gas Cooler inlet | C2 discharge $\rightarrow$ Condenser/GC inlet |
| **⑤** | — | Gas Cooler exit ($35^\circ\text{C}$) $\rightarrow$ EEV-1 inlet | Condenser/GC exit $\rightarrow$ EEV inlet |
| **⑥** | — | EEV-1 exit $\rightarrow$ Flash Tank inlet ($h_6=h_5$) | EEV exit $\rightarrow$ Evaporator inlet ($h_6=h_5$) |
| **⑦** | — | Flash Tank saturated vapor ($x_7=1$) $\rightarrow$ EEV-inj | — |
| **⑦a**| — | EEV-inj exit $\rightarrow$ Mixing plenum ($h_{7a}=h_7$) | — |
| **⑧** | — | Flash Tank saturated liquid ($x_8=0$) $\rightarrow$ EEV-2 | — |
| **⑨** | — | EEV-2 exit $\rightarrow$ Evaporator inlet ($h_9=h_8$) | — |

### Baseline Operating Parameters (From Handwritten Baseline Note)
- **Ambient & Cabin Targets:** $T_{\text{amb}} = -10^\circ\text{C}$, $CT = 20^\circ\text{C}$ (Cabin Temp), Cabin Heating Load $CL = 5.0\text{ kW}$.
- **Gas Cooler / Cabin Loop:** $UA = 125\text{ W/K}$, $\dot{m}_{\text{vent}} = 0.04\text{ kg/s}$, $\dot{m}_{\text{gc}} = 0.15\text{ kg/s}$, $T_{\text{gc,air}} = 20^\circ\text{C}$, Gas cooler refrigerant exit $T_{\text{exit}} = 35^\circ\text{C}$.
- **Evaporator Conditions:** $T_{\text{evap}} = -15^\circ\text{C}$ (5 K approach to ambient), $P_{\text{evap}} = 2.276\text{--}2.29\text{ MPa}$ (from sat. tables), Air $C_p = 1.006\text{ kJ/(kg}\cdot\text{K)}$.
- **Compressor Ratings:** Nominal speed $N = 4000\text{ rpm}$, Maximum speed $N_{\max} = 8000\text{ rpm}$, Nominal discharge $P_{\text{dis}} = 9.5\text{ MPa}$, Maximum pressure $P_{\max} = 12.0\text{ MPa}$, Maximum allowable discharge temperature $T_{\text{dis},\max} = 130^\circ\text{C}$, Isentropic efficiency $\eta_i = 0.70$, Adiabatic casing assumed.

### Why Case C (Intercooling) is Inferior to FT-VI for Automotive EVs:
1. **No Mass Flow Augmentation:**
   - The same mass flow passes through C1, the intercooler, and C2 ($\dot{m}_{\text{high}} = \dot{m}_{\text{low}} = 20.22\text{ g/s}$).
   - It cannot match the heating capacity of FT-VI ($4.76\text{ kW}$ vs. $7.05\text{ kW}$ at $4000\text{ rpm}$).
2. **Speed & NVH Penalty:**
   - To match a $5.00\text{ kW}$ heating load, Case C must run at **$4203\text{ rpm}$** ($+33\%$ faster than FT-VI at $2800\text{ rpm}$), increasing friction, wear, and cabin acoustic noise.
3. **Packaging Complexity:**
   - In Recover mode, two heat exchangers (the intercooler air preheater + main gas cooler) must be plumbed in series into the cabin air duct, which is impractical in compact vehicle front-ends.

---

## 6. Advanced Phenomenological Concepts (High-Probability Quiz Topics)

### A. Sonic Choking in the Injection EEV
- **Definition:** Occurs when the downstream-to-upstream pressure ratio across an orifice drops below the critical pressure ratio:
  $$r_{\text{crit}} = \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma}{\gamma - 1}} \approx 0.546 \quad (\gamma \approx 1.29 \text{ for R744})$$
- **Physics:** Flow velocity in the valve throat reaches the local speed of sound ($Ma = 1$). Downstream pressure waves can no longer propagate upstream.
- **Consequence:** Mass flow rate becomes **independent of downstream port pressure** ($P_{\text{port}}$) and depends solely on upstream flash-tank pressure ($P_{\text{FT}}$), temperature, and orifice opening $\phi$.

### B. Valve Saturation Phenomenon ($\phi_{\text{sat}}$)
- **Concept:** Continuous injection requires that the valve flow cannot exceed the tank's vapor generation rate:
  $$\dot{m}_{\text{inj}} = \min(\dot{m}_{\text{valve}}(\phi), \dot{m}_{\text{inj,max}})$$
- **Behavior:**
  - For small openings ($\phi < \phi_{\text{sat}} \approx 83.3\%$ at $4.5\text{ MPa}$), flow is throttled by the valve orifice.
  - For large openings ($\phi \ge \phi_{\text{sat}}$), the valve flow capacity exceeds the rate at which vapor is generated by flashing. The system saturates: opening the valve to $100\%$ does not cause liquid floodback, but ensures maximum vapor extraction.

### C. Why Real Optimal Intermediate Pressure Shifts Away from Geometric Mean
- **Ideal Gas Theory:** For ideal gases with constant specific heat, minimum total compression work occurs at the geometric mean:
  $$P_{i,\text{ideal}} = \sqrt{P_{\text{evap}} \cdot P_{\text{dis}}} = \sqrt{2.291 \times 9.500} = 4.665\text{ MPa}$$
- **Real R744 Thermodynamic Shifts:**
  - **Case C (Intercooling) shifts HIGHER ($5.10\text{ MPa}$):** Higher intermediate pressure elevates Stage-1 discharge temperature $T_2$, creating a larger temperature difference in the intercooler to recover more heat into cabin air.
  - **Case B (FT-VI) shifts LOWER ($4.25\text{ MPa}$, $-9\%$ shift):** In transcritical $\text{CO}_2$, fluid near the gas cooler exit operates in the dense supercritical region where specific heat ($c_p$) peaks sharply near the pseudo-critical line. Flashing to a lower intermediate pressure ($4.25\text{ MPa}$) lowers saturated liquid enthalpy ($h_8$), creating a much larger evaporator latent cooling/heating boost that outweighs compression work savings.

### D. Multi-Objective Trade-offs & Pareto Frontier
- **The Optimization Conflict:**
  - Maximum $\text{COP}_h$ occurs at lower speeds ($N \approx 3875\text{ rpm}$) where isentropic efficiency is high.
  - Maximum heating capacity $\dot{Q}_h$ occurs at maximum speed ($N = 8000\text{ rpm}$) and high pressure ($5.13\text{ MPa}$).
  - Minimum discharge temperature $T_{\text{dis}}$ occurs at high flash pressure and throttled speed.
- **Pareto Optimality:** A point is Pareto-optimal if no objective can be improved without degrading at least one other objective.
- **TOPSIS Selection:** Ranks the 45 Pareto points by Euclidean closeness to the Ideal Solution ($A^*$) and distance from Negative-Ideal ($A^-$).
- **Knee Point:** The point on the Pareto frontier that achieves the sharpest mathematical compromise (minimum distance to the Utopia point).

---

## 7. Limitations & Modeling Assumptions

1. **Lumped Steady-State Heat Exchangers:** Assumes fixed approach temperatures ($\Delta T_{\text{app}} = 5\text{ K}$) and effectiveness rather than distributed finite-volume discretization with local frost formation.
2. **Negligible Pressure Drops ($\Delta P = 0$):** Friction losses inside tubes, bends, manifolds, and the flash tank are neglected.
3. **Ideal Phase Separation:** Assumes 100% phase separation efficiency in the flash tank (zero liquid droplet carryover in the vapor line, zero vapor bubbling into the liquid drain).
4. **Adiabatic Compressor Shell:** Neglects external heat dissipation through the compressor casing to ambient air.
5. **Constant Valve Discharge Coefficient:** $C_d$ is treated as constant across varying Reynolds numbers and opening ratios.

---

## 8. Rapid-Fire Quiz Concept Questions & Answers

1. **Q: Why can't an automotive $\text{CO}_2$ heat pump condense refrigerant at constant temperature?**  
   *A:* Because cabin heating requires air at $40\text{--}45^\circ\text{C}$, which is above $\text{CO}_2$'s critical temperature ($30.98^\circ\text{C}$). Heat rejection must occur in the single-phase supercritical region (Gas Cooler).

2. **Q: What is the primary cause of baseline heat pump failure at $-15^\circ\text{C}$?**  
   *A:* Suction vapor density collapse ($47.6\text{ kg/m}^3$) and high pressure ratio ($4.84$) starve mass flow below the $5\text{ kW}$ heating target, while discharge temperature exceeds the $130^\circ\text{C}$ PAG oil breakdown limit ($130.4^\circ\text{C}$).

3. **Q: Does vapor injection increase the mass flow through the outdoor evaporator?**  
   *A:* No. The evaporator receives only the saturated liquid flow ($\dot{m}_{\text{suc}} = 20.22\text{ g/s}$). Vapor injection augments mass flow only in the Stage 2 compressor and cabin gas cooler ($\dot{m}_{\text{tot}} = 31.26\text{ g/s}$).

4. **Q: How does the flash tank improve evaporator performance?**  
   *A:* By feeding pure saturated liquid ($x=0$) at intermediate pressure ($4.25\text{ MPa}$) instead of hot gas cooler exit fluid, dropping evaporator inlet quality from $0.32$ to $0.21$ and expanding latent heat lift by $+27.6\%$.

5. **Q: What is the thermodynamic benefit of intermediate mixing before Stage 2?**  
   *A:* It provides $32.5\text{ K}$ of desuperheating, dropping Stage 2 inlet temperature to $12.6^\circ\text{C}$, which keeps final discharge temperature ($107.5^\circ\text{C}$) well below the $130^\circ\text{C}$ safety limit.

6. **Q: Why does compressor isentropic efficiency drop at higher speeds?**  
   *A:* Fluid shear, aerodynamic turbulence, and mechanical friction increase with shaft speed, creating internal irreversibilities ($\Delta \eta_{\text{is}} \propto -1.2 \times 10^{-5} \Delta N$).

7. **Q: Why does volumetric efficiency drop at higher pressure ratios?**  
   *A:* Trapped high-pressure vapor in the cylinder clearance pocket re-expands during the intake stroke, preventing the intake valve from opening until cylinder pressure falls below suction pressure, which starves intake volume.

8. **Q: What is sonic choking in an EEV?**  
   *A:* When the pressure ratio drops below $r_{\text{crit}} \approx 0.546$, throat velocity reaches the local speed of sound ($Ma = 1$), making mass flow independent of downstream pressure.

9. **Q: Why is Case C (Intercooled) unviable despite having a higher theoretical COP?**  
   *A:* It lacks mass flow augmentation, requiring $+33\%$ higher speed ($4203\text{ rpm}$) to deliver $5\text{ kW}$ and requiring complex, bulky dual radiators in the vehicle cabin HVAC unit.

10. **Q: How does FT-VI extend EV winter driving range during highway cruising?**  
    *A:* By producing surplus capacity at nominal speed, it allows the inverter to throttle the compressor from $4000\text{ rpm}$ down to $2800\text{ rpm}$ ($-30\%$ speed), saving $3.8\%$ electrical battery power while meeting the exact $5.0\text{ kW}$ load.
