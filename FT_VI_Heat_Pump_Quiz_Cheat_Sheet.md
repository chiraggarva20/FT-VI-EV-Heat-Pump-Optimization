# ME 316 S2: Project Quiz Cheat Sheet
## Transcritical $\text{CO}_2$ Heat Pump Optimization with Flash-Tank Vapor Injection (FT-VI)

---

## 1. Quick Identity & Boundary Conditions Card

| Parameter | Symbol | Value | Unit | Significance in EV Application |
| :--- | :--- | :--- | :--- | :--- |
| **Working Fluid** | R744 | $\text{CO}_2$ | &mdash; | Natural refrigerant: $\text{ODP}=0$, $\text{GWP}=1$, non-toxic, non-flammable (A1). |
| **Critical Temperature** | $T_c$ | **$30.98$** | $^\circ\text{C}$ | Below cabin heating target ($40\text{--}45^\circ\text{C}$) $\rightarrow$ forces **transcritical** operation. |
| **Critical Pressure** | $P_c$ | **$7.38$** | $\text{MPa}$ | Gas cooler must operate supercritical ($P_{\text{dis}} > P_c$). |
| **Ambient Temperature** | $T_{\text{amb}}$ | **$-10.0$** | $^\circ\text{C}$ | Design winter condition (tested across $-5^\circ\text{C}, -10^\circ\text{C}, -15^\circ\text{C}$). |
| **Cabin Comfort Target** | $T_{\text{cab}}$ | **$20.0$** | $^\circ\text{C}$ | Constant indoor passenger setpoint. |
| **Cabin Heating Demand** | $\dot{Q}_{\text{load}}$ | **$5.00$** | $\text{kW}$ | Steady winter cruising heating load requirement. |
| **Discharge Pressure** | $P_{\text{dis}}$ | **$9.50$** | $\text{MPa}$ | Supercritical design operating pressure (safety limit $\le 12.0\text{ MPa}$). |
| **Gas Cooler Exit Temp** | $T_{\text{gc,out}}$ | **$35.0$** | $^\circ\text{C}$ | Approach to cabin airflow; fluid enters dense supercritical liquid-like state. |
| **Evaporator Pressure** | $P_{\text{evap}}$ | **$2.291$** | $\text{MPa}$ | Saturation pressure corresponding to $T_{\text{evap}} = -15^\circ\text{C}$ ($5\text{ K}$ approach). |
| **Suction Superheat** | $\Delta T_{\text{sh}}$ | **$5.0$** | $\text{K}$ | $T_1 = -10.0^\circ\text{C}$; ensures dry vapor enters compressor. |
| **Max Discharge Temp** | $T_{\text{dis,max}}$ | **$130.0$** | $^\circ\text{C}$ | **Hard thermal limit**: PAG lubricant oil degrades thermally above $130^\circ\text{C}$. |
| **Compressor Speed** | $N$ | **$4000$** | $\text{rpm}$ | Nominal speed (operating envelope: $2500\text{--}8000\text{ rpm}$). |
| **Calibrated Displacement**| $V_{\text{disp}}$ | **$8.878$** | $\text{cm}^3$ | Sized so Baseline Case A delivers exactly $5.00\text{ kW}$ at $4000\text{ rpm}, -10^\circ\text{C}$. |

---

## 2. Core Architecture Comparison (Case A vs. Case B vs. Case C)

```
Case A (Baseline):       Evaporator [1] -> Compressor [2] -> Gas Cooler [3] -> EEV [4] -> Evap
Case B (FT-VI):          Evap [1] -> C1 [2] + Inj [7a] -> Mix [3] -> C2 [4] -> GC [5] -> EEV1 [6] -> FT
                                  FT Vapor [7] -> EEVinj [7a] -> Mix [3]
                                  FT Liquid [8] -> EEV2 [9] -> Evap [1]
Case C (Intercooled):    Evap [1] -> C1 [2] -> Intercooler (Q_IC) [3] -> C2 [4] -> GC [5] -> EEV [6] -> Evap
```

| Architecture | Compressor Setup | Valves | States | $\dot{m}_{\text{gc}}$ | $\dot{Q}_h$ ($-10^\circ\text{C}$) | $\text{COP}_h$ ($-10^\circ\text{C}$) | $T_{\text{dis}}$ ($-10^\circ\text{C}$) | $-15^\circ\text{C}$ Feasibility | Cruising Speed ($5\text{ kW}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case A: Baseline** | 1-stage | 1 EEV | 4 | $20.22\text{ g/s}$ | $5.00\text{ kW}$ | $2.595$ | $120.4^\circ\text{C}$ | **FAILS** ($T_{\text{dis}}=130.4^\circ\text{C}$, $\dot{Q}_h=4.39\text{ kW}$) | $4000\text{ rpm}$ |
| **Case B: FT-VI (Nominal)**| 2-stage economized | 3 EEVs | 10 | $26.8\text{ g/s}$ | $6.20\text{ kW}$ | $2.671$ | $111.6^\circ\text{C}$ | **PASSES** ($T_{\text{dis}}=117.6^\circ\text{C}$) | $3032\text{ rpm}$ |
| **Case B: FT-VI (Optimized)**| 2-stage economized | 3 EEVs | 10 | **$31.26\text{ g/s}$** | **$7.05\text{ kW}$** (+41%)| **$2.742$** (+5.7%)| **$107.5^\circ\text{C}$** ($-12.9\text{ K}$)| **PASSES** ($T_{\text{dis}}=116.8^\circ\text{C}$, safe) | **$2800\text{ rpm}$** ($-30\%$ speed, $-3.8\%$ power) |
| **Case C: Intercooled (Reject)**| 2-stage split | 1 EEV | 6 | $20.22\text{ g/s}$ | $4.05\text{ kW}$ | $2.294$ | $98.2^\circ\text{C}$ | **FAILS** capacity ($3.8\text{ kW}$) | $4950\text{ rpm}$ |
| **Case C: Intercooled (Recover)**| 2-stage split | 1 EEV | 6 | $20.22\text{ g/s}$ | $4.76\text{ kW}$ | **$2.824$** | $68.7^\circ\text{C}$ | **PASSES** COP, but fails capacity | $4203\text{ rpm}$ (+33% speed, dual radiators) |

---

## 3. The Two Core Thermodynamic Mechanisms of FT-VI Superiority

Why does Flash-Tank Vapor Injection deliver **$+41.0\%$ heating capacity** and **lower discharge temperature**? Memorize these two physical mechanisms:

```
Mechanism 1: Mass Flow Augmentation (In Gas Cooler)
  m_tot = m_suc + m_inj = 20.22 + 11.04 = 31.26 g/s (+54.6% mass flow!)
  ==> Q_h = m_tot * (h_4 - h_5) surges by +41.0%

Mechanism 2: Liquid Subcooling (In Evaporator)
  Flashing to saturated liquid at P_FT = 4.25 MPa drops inlet enthalpy h_9 = h_8 = 221.5 kJ/kg
  versus Case A's h_4 = 293.5 kJ/kg.
  ==> Inlet vapor quality drops from x=0.322 (Case A) to x=0.207 (Case B).
  ==> Specific refrigerating effect (h_1 - h_9) expands by +48.0 kJ/kg (+27.6% latent lift)!
```

### Discharge Temperature Suppression Mechanism
- Stage 1 discharge gas exits at $T_2 = 45.1^\circ\text{C}$ ($P_{\text{port}} = 3.44\text{ MPa}$).
- Injected vapor enters at $T_{7a} \approx -0.5^\circ\text{C}$ from flash tank vapor dome ($P_{\text{FT}} = 4.25\text{ MPa}$).
- **Adiabatic mixing in plenum:**
  $$h_3 = \frac{\dot{m}_{\text{suc}} h_2 + \dot{m}_{\text{inj}} h_{7a}}{\dot{m}_{\text{tot}}} \implies T_3 = 12.6^\circ\text{C}$$
- This provides **$32.5\text{ K}$ of desuperheating** before Stage 2 compression.
- Consequently, Stage 2 final discharge reaches only $T_4 = 107.5^\circ\text{C}$ (a $12.9\text{ K}$ reduction compared to Case A's $120.4^\circ\text{C}$, well below the $130^\circ\text{C}$ oil limit).

---

## 4. Must-Know Governing Equations Sheet

### A. General Vapor Compression & Heat Exchanger Balances
1. **Evaporator Heat Absorption:**
   $$\dot{Q}_{\text{evap}} = \dot{m}_{\text{suc}} (h_1 - h_{\text{in,evap}})$$
2. **Gas Cooler Heat Rejection (Cabin Heating Duty):**
   $$\dot{Q}_h = \dot{m}_{\text{tot}} (h_{\text{dis}} - h_{\text{gc,out}})$$
3. **Total Compressor Electrical Work:**
   $$\dot{W}_{\text{comp}} = \dot{W}_{\text{stage1}} + \dot{W}_{\text{stage2}} = \dot{m}_{\text{suc}}(h_2 - h_1) + \dot{m}_{\text{tot}}(h_4 - h_3)$$
4. **Heating Coefficient of Performance ($\text{COP}_h$):**
   $$\text{COP}_h = \frac{\dot{Q}_h}{\dot{W}_{\text{comp}}}$$
5. **Air-Side Heat Balance (Gas Cooler Conductance):**
   $$\dot{Q}_h = \dot{m}_{\text{air}} c_{p,\text{air}} (T_{\text{air,out}} - T_{\text{air,in}}) = UA \cdot \Delta T_{\text{LMTD}}$$
   *Standard parameters:* $UA = 125\text{ W/K}$, $\dot{m}_{\text{vent}} = 0.04\text{ kg/s}$, $\dot{m}_{\text{gc,air}} = 0.15\text{ kg/s}$, $T_{\text{air,in}} = 20^\circ\text{C}$.

---

### B. Realistic Compressor Correlations (Off-Design Map)
6. **Volumetric Efficiency ($\eta_v$):**
   $$\eta_v = \text{EV}_0 - \text{EV}_1 \cdot \text{PR} = 0.97 - 0.03 \left(\frac{P_{\text{dis}}}{P_{\text{suc}}}\right)$$
   *Physical meaning:* High pressure ratio causes clearance pocket gas to re-expand during the suction stroke, starving intake vapor volume.
7. **Suction Mass Flow Swallowed:**
   $$\dot{m}_{\text{suc}} = \eta_v \cdot \rho_{\text{suc}} \cdot V_{\text{disp}} \cdot \left(\frac{N}{60}\right)$$
   *Cold-weather bottleneck:* At $-10^\circ\text{C}$, $\rho_{\text{suc}} = 60.1\text{ kg/m}^3$; at $-15^\circ\text{C}$, $\rho_{\text{suc}}$ collapses to $47.6\text{ kg/m}^3$.
8. **Isentropic Efficiency ($\eta_{\text{is}}$):**
   $$\eta_{\text{is}} = 0.815 - 0.022 \cdot \text{PR} - 0.0015 \cdot \text{PR}^2 - 1.2 \times 10^{-5} (N - 4000)$$
   *Physical meaning:* Compression irreversibilities (friction, valve throttling, turbulent eddies) grow quadratically with pressure ratio and linearly with shaft rotational speed.

---

### C. Flash Tank & Injection EEV Correlations
9. **Intermediate Port Pressure Coupling:**
   $$P_{\text{port}} = 1.50 \cdot P_{\text{evap}} = 1.50 \times 2.291\text{ MPa} = 3.436\text{ MPa}$$
10. **Flash Tank Vapor Quality ($x_{\text{FT}}$ from First Law):**
    $$x_{\text{FT}} = \frac{h_6 - h_f(P_{\text{FT}})}{h_g(P_{\text{FT}}) - h_f(P_{\text{FT}})} = \frac{293.46 - 221.53}{425.18 - 221.53} = 0.360$$
11. **Injection Ratio ($\mu$) & Flash Mass Balance:**
    $$\mu = \frac{\dot{m}_{\text{inj}}}{\dot{m}_{\text{suc}}} \le \mu_{\text{max}} = \frac{x_{\text{FT}}}{1 - x_{\text{FT}}} = \frac{0.360}{0.640} = 0.562$$
    *Continuous operation constraint:* You cannot inject vapor faster than the flash tank evaporates it, otherwise the tank fills with liquid or dries out!
12. **Sonic Choking Pressure Ratio ($r_{\text{crit}}$):**
    $$r_{\text{crit}} = \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma}{\gamma - 1}} \approx 0.546 \quad (\text{for R744 vapor, } \gamma \approx 1.29)$$
13. **Compressible Orifice Flow Model ($\text{EEV}_{\text{inj}}$):**
    - If $\frac{P_{\text{port}}}{P_{\text{FT}}} \le r_{\text{crit}}$ (**Choked / Sonic Flow**):
      $$\dot{m}_{\text{valve}} = C_d A_{\text{max}} \phi \sqrt{\gamma \rho_{\text{up}} P_{\text{up}} \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma+1}{\gamma-1}}}$$
    - If $\frac{P_{\text{port}}}{P_{\text{FT}}} > r_{\text{crit}}$ (**Subcritical Flow**):
      $$\dot{m}_{\text{valve}} = C_d A_{\text{max}} \phi \sqrt{2 \rho_{\text{up}} P_{\text{up}} \left(\frac{\gamma}{\gamma-1}\right) \left[\left(\frac{P_{\text{down}}}{P_{\text{up}}}\right)^{\frac{2}{\gamma}} - \left(\frac{P_{\text{down}}}{P_{\text{up}}}\right)^{\frac{\gamma+1}{\gamma}}\right]}$$
14. **Valve Saturation Phenomenon ($\phi_{\text{sat}}$):**
    $$\dot{m}_{\text{inj}} = \min(\dot{m}_{\text{valve}}(\phi), \dot{m}_{\text{inj,max}})$$
    At $P_{\text{FT}} = 4.5\text{ MPa}$, for valve opening $\phi > 83.3\%$, valve flow capacity exceeds flash vapor generation. The cycle transitions smoothly from the **valve-throttled regime** to the **tank vapor generation limit**.

---

### D. Case C (Two-Stage Intercooled) & Intermediate Pressure Theory
15. **Ideal Gas Intermediate Pressure (Geometric Mean):**
    $$P_{i,\text{ideal}} = \sqrt{P_{\text{evap}} \cdot P_{\text{dis}}} = \sqrt{2.291 \times 9.500} = 4.665\text{ MPa}$$
16. **Why Real Gas Optimum Shifts:**
    - For **Case C (Intercooled)**: Real optimum shifts *upward* to **$5.10\text{ MPa}$** because higher $P_i$ elevates $T_2$, increasing intercooler temperature difference and capturing higher $\dot{Q}_{\text{IC}}$ recovery into cabin air.
    - For **Case B (FT-VI)**: Real optimum shifts *downward* to **$4.25\text{ MPa}$** ($9\%$ below geometric mean) because R744 has supercritical specific heat peaks near the pseudo-critical line; lowering $P_{\text{FT}}$ produces a colder saturated liquid stream ($h_8$), maximizing evaporator latent enthalpy lift.
17. **Cabin Air Preheating in Recover Mode:**
    $$T_{\text{air,mix}} = T_{\text{air,in}} + \frac{\dot{Q}_{\text{IC}}}{\dot{m}_{\text{vent}} c_{p,\text{air}}} = 20.0^\circ\text{C} + \frac{0.812\text{ kW}}{0.04 \times 1.006} = 24.5^\circ\text{C}$$

---

### E. Multi-Objective Optimization & TOPSIS Formulations
18. **3 Optimization Objectives:**
    $$\max \text{COP}_h, \quad \max \dot{Q}_h, \quad \min T_{\text{dis}}$$
19. **Hard Engineering Constraints:**
    $$\dot{Q}_h \ge 5.00\text{ kW}, \quad T_{\text{dis}} \le 130.0^\circ\text{C}, \quad P_{\text{dis}} \le 12.0\text{ MPa}, \quad 2500 \le N \le 8000\text{ rpm}$$
20. **TOPSIS Closeness Coefficient ($C_i^*$):**
    $$C_i^* = \frac{S_i^-}{S_i^* + S_i^-} \in [0, 1]$$
    where $S_i^*$ is Euclidean distance to the Positive Ideal Solution ($A^*$) and $S_i^-$ is distance to Negative Ideal ($A^-$). Selected weights: $w_{\text{COP}} = 0.40, w_Q = 0.40, w_T = 0.20$.
21. **Knee-Point Criterion:**
    Identifies the solution on the Pareto frontier with minimum normalized Euclidean distance to the unattainable Utopia point: $(1, 1, 0)$ in normalized $[\text{COP}_h, \dot{Q}_h, T_{\text{dis}}]$ space.

---

## 5. Master 10-State Refrigerant Table (Recommended FT-VI Point)

> **Design Point:** $P_{\text{FT}} = 4.25\text{ MPa}$, $\phi = 100\%$, $N = 4000\text{ rpm}$, $T_{\text{amb}} = -10.0^\circ\text{C}$, $P_{\text{dis}} = 9.50\text{ MPa}$.

| State | Location in Flow Circuit | $P$ [MPa] | $T$ [$^\circ\text{C}$] | $h$ [kJ/kg] | $s$ [kJ/kg$\cdot$K] | Quality $x$ | $\dot{m}$ [g/s] | Physical State Description |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | Evaporator outlet / Stage-1 suction | **$2.291$** | **$-10.00$** | $443.46$ | $1.928$ | Superheated | $20.22$ | Saturated vapor $+5\text{ K}$ superheat |
| **2** | Stage-1 compressor discharge | **$3.436$** | **$23.63$** | $466.81$ | $1.974$ | Superheated | $20.22$ | Discharged at $P_{\text{port}} = 1.5 \times P_{\text{evap}}$ |
| **7** | Flash tank vapor dome outlet | **$4.250$** | **$7.69$** | $425.18$ | $1.800$ | **$1.000$** | $11.04$ | Saturated vapor extracted from top of tank |
| **7a**| After injection EEV throttling | **$3.436$** | **$-0.53$** | $425.18$ | $1.826$ | Superheated | $11.04$ | Isenthalpic throttling to port pressure |
| **3** | Mixing plenum / Stage-2 suction | **$3.436$** | **$12.64$** | $452.11$ | $1.923$ | Superheated | **$31.26$** | Desuperheated mixture ($-32.5\text{ K}$ drop) |
| **4** | Stage-2 compressor discharge | **$9.500$** | **$107.47$** | $518.93$ | $1.977$ | Supercritical | **$31.26$** | Supercritical fluid entering gas cooler |
| **5** | Gas cooler outlet | **$9.500$** | **$35.00$** | $293.46$ | $1.296$ | Supercritical | **$31.26$** | Dense liquid-like supercritical state |
| **6** | EEV-1 outlet / Flash tank inlet | **$4.250$** | **$7.69$** | $293.46$ | $1.331$ | **$0.360$** | **$31.26$** | Two-phase mixture after 1st throttling |
| **8** | Flash tank liquid sump drain | **$4.250$** | **$7.69$** | $221.53$ | $1.067$ | **$0.000$** | $20.22$ | Saturated liquid drained to EEV-2 |
| **9** | EEV-2 outlet / Evaporator inlet | **$2.291$** | **$-15.00$** | $221.53$ | $1.092$ | **$0.207$** | $20.22$ | Low-quality two-phase fluid ($h_9 = h_8$) |

---

## 6. Key Numerical "Magic Numbers" to Memorize

- **$5.00\text{ kW}$**: Required cabin heating load at $20^\circ\text{C}$ cabin setpoint.
- **$130.0^\circ\text{C}$**: PAG lubricant oil thermal degradation ceiling.
- **$30.98^\circ\text{C}$ & $7.38\text{ MPa}$**: R744 critical point ($T_c, P_c$).
- **$8.878\text{ cm}^3$**: Calibrated compressor displacement.
- **$41.0\%$**: Heating capacity increase of optimized FT-VI over baseline ($7.049\text{ kW}$ vs $5.000\text{ kW}$).
- **$5.7\%$**: $\text{COP}_h$ improvement of optimized FT-VI over baseline ($2.742$ vs $2.595$).
- **$12.9\text{ K}$**: Discharge temperature reduction of FT-VI at nominal speed ($107.5^\circ\text{C}$ vs $120.4^\circ\text{C}$).
- **$2800\text{ rpm}$**: FT-VI operating speed to deliver matched $5.0\text{ kW}$ load ($-30\%$ speed reduction, $-3.8\%$ electrical power: $1.854\text{ kW}$ vs $1.926\text{ kW}$).
- **$4.25\text{ MPa}$**: Optimal flash-tank pressure.
- **$100\%$**: Optimal injection EEV opening ($\phi = 1.0$).
- **$0.546$**: Optimal injection ratio $\mu = \dot{m}_{\text{inj}} / \dot{m}_{\text{suc}}$.
- **$83.3\%$**: Valve saturation point ($\phi_{\text{sat}}$) at $4.5\text{ MPa}$.
- **$130.4^\circ\text{C}$**: Baseline Case A discharge temperature at $-15^\circ\text{C}$ ambient (violates $130^\circ\text{C}$ limit $\rightarrow$ system failure).
- **$116.8^\circ\text{C}$**: FT-VI discharge temperature at $-15^\circ\text{C}$ ambient (safe, continuous operation).
- **$7,056 \rightarrow 5,905 \rightarrow 45$**: Optimization sweep: $7056$ grid evaluations, $5905$ feasible designs, $45$ non-dominated Pareto solutions.
- **$< 6 \times 10^{-15}\text{ kW}$**: Solver mass and energy balance closure to machine precision.

---

## 7. Student Division of Work & Technical Ownership

| Student | Name & Roll No | Assigned Module | Key Formulation / Contribution | Key Finding / Result |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Kartik Gupta**<br>(24B2152) | Baseline Single-Stage Cycle | 4-state transcritical model; displacement calibration ($8.878\text{ cm}^3$); approach temperature heat balances. | Baseline delivers $5.00\text{ kW}$ at $-10^\circ\text{C}$, but fails at $-15^\circ\text{C}$ ($T_{\text{dis}} = 130.4^\circ\text{C} > 130^\circ\text{C}$, capacity collapses to $4.39\text{ kW}$). |
| **2** | **Durgesh Nimse**<br>(24B2226) | Flash-Tank Phase Separation | Flash tank mass & First-Law balances; flash quality $x_{\text{FT}}$; max injection limit $\mu_{\text{max}} = x/(1-x)$. | Swept $P_{\text{FT}} \in [3.5, 6.0]\text{ MPa}$; found optimum at $4.25\text{--}4.50\text{ MPa}$ balancing subcooling gain vs desuperheating. |
| **3** | **Disha Jain**<br>(24B2125) | Injection EEV Orifice Flow | Compressible gas orifice model; sonic choking criteria ($r_{\text{crit}} = 0.546$); effective area $C_d A_{\text{max}} \phi$. | Discovered valve saturation ($\phi_{\text{sat}} \approx 83.3\%$ at $4.5\text{ MPa}$); full opening $\phi=100\%$ gives maximum desuperheating. |
| **4** | **Garva Chirag**<br>(24B2269) | Off-Design Compressor Map | Empirical quadratic $\eta_{\text{is}}(\text{PR}, N)$ and volumetric $\eta_v(\text{PR})$ maps; feasible envelope filtering. | FT-VI expands operating envelope by $+44.7\%$ (87.0% vs 60.1% feasibility); load matching at $-10^\circ\text{C}$ drops speed to $2800\text{ rpm}$. |
| **5** | **Anmol Raj**<br>(24B2260) | System Integration & Optimization | Conservation-closed solver ($<6\times 10^{-15}\text{ kW}$); 7,056-point 3D grid sweep; Pareto front extraction; TOPSIS & Knee point. | Identified recommended design point ($P_{\text{FT}} = 4.25\text{ MPa}, \phi=100\%, N=4000\text{ rpm}$); $+41\%$ heating capacity, $+5.7\%$ COP, $-12.9\text{ K}$ $T_{\text{dis}}$. |
| **6** | **Tarang Gupta**<br>(24B2230) | Two-Stage Intercooled Cycle | C1/C2 compressor splitting; counter-flow intercooler; Reject vs Recover modes; $P_i$ optimization. | Recover mode achieves $\text{COP}=2.824$, but requires $+33\%$ speed ($4203\text{ rpm}$) to deliver $5\text{ kW}$ and adds heavy dual-radiator penalty. |

---

## 8. High-Probability Quiz Questions & Instant Answers

#### Q1: Why must an automotive $\text{CO}_2$ heat pump operate transcritically instead of subcritically?
> **Answer:** The critical temperature of $\text{CO}_2$ is only $30.98^\circ\text{C}$ ($P_c = 7.38\text{ MPa}$). Passenger cabin comfort heating requires warm air delivery at $40\text{--}45^\circ\text{C}$, well above $30.98^\circ\text{C}$. Constant-temperature subcritical condensation is physically impossible above $T_c$. Therefore, the system must operate above $P_c$ in a continuous single-phase **Gas Cooler**, rejecting sensible heat along a gliding temperature profile.

#### Q2: What causes conventional single-stage heat pumps (Case A) to fail in extreme cold ($-15^\circ\text{C}$)?
> **Answer:** Two simultaneous thermodynamic bottlenecks:
> 1. **Vapor density collapse:** Evaporator pressure drops to $1.97\text{ MPa}$, collapsing suction density to $47.6\text{ kg/m}^3$. Combined with high pressure ratio ($\text{PR} = 4.84$) which destroys volumetric efficiency ($\eta_v$), mass flow collapses, causing heating capacity to fall short ($4.39\text{ kW} < 5.0\text{ kW}$).
> 2. **Thermal runaway:** Steep isentropic pressure lift drives compressor discharge temperature to $130.4^\circ\text{C}$, exceeding the $130.0^\circ\text{C}$ PAG oil degradation threshold.

#### Q3: How does vapor injection increase heating capacity by 41% if the evaporator suction flow ($\dot{m}_{\text{suc}}$) doesn't change?
> **Answer:** Through two mechanisms:
> 1. **Mass flow augmentation:** The injection valve feeds an additional $\dot{m}_{\text{inj}} = 11.04\text{ g/s}$ directly into the Stage 2 compressor. The gas cooler circulates the *total* mass flow ($\dot{m}_{\text{tot}} = 31.26\text{ g/s}$), which is $+54.6\%$ higher than baseline!
> 2. **Evaporator subcooling:** The flash tank drains saturated liquid ($x_8 = 0.0$) at $P_{\text{FT}} = 4.25\text{ MPa}$ ($h_8 = 221.5\text{ kJ/kg}$) instead of liquid from the gas cooler exit ($h_5 = 293.5\text{ kJ/kg}$). This drops evaporator inlet quality to $0.207$ (vs $0.322$), increasing specific enthalpy absorption by $+42.6\text{ kJ/kg}$ ($+27.6\%$).

#### Q4: Why is the optimal flash-tank pressure ($4.25\text{ MPa}$) lower than the classic geometric mean ($\sqrt{P_{\text{evap}} P_{\text{dis}}} = 4.67\text{ MPa}$)?
> **Answer:** The geometric mean formula $\sqrt{P_{\text{evap}} P_{\text{dis}}}$ is derived for ideal gases with constant specific heats. In transcritical R744, fluid near the gas cooler exit is in the dense supercritical region with strong non-ideal property variations and high specific heat peaks near the pseudo-critical line. Flashing to a lower pressure ($4.25\text{ MPa}$) produces lower liquid enthalpy ($h_8$), boosting evaporator latent heat absorption, which shifts the real-fluid thermodynamic optimum below the ideal gas estimate.

#### Q5: What is the valve saturation phenomenon ($\phi_{\text{sat}}$)?
> **Answer:** It is the boundary where injection valve flow capacity equals the maximum vapor generation rate of the flash tank ($\dot{m}_{\text{valve}} = \dot{m}_{\text{inj,max}}$). For openings below $\phi_{\text{sat}}$, the injection rate is throttled by the valve orifice. Above $\phi_{\text{sat}}$ (e.g., $>83.3\%$ at $4.5\text{ MPa}$), opening the valve further cannot increase injection flow because it is physically constrained by the rate at which two-phase refrigerant flashes into vapor inside the tank.

#### Q6: Why doesn't Case C (Two-Stage Intercooled) augment refrigerant mass flow?
> **Answer:** Case C is a closed single-loop circuit without an economizer or separator. The entire mass flow ($\dot{m} = 20.22\text{ g/s}$) flows through C1, passes through the intercooler, and continues through C2. There is no intermediate fluid addition ($\dot{m}_{\text{high}} = \dot{m}_{\text{low}}$). Consequently, it does not achieve the mass flow augmentation boost of FT-VI.

#### Q7: If Case C (Recover mode) achieves a higher paper COP ($2.824$ vs $2.742$), why is FT-VI preferred for EVs?
> **Answer:** Because of **packaging, speed, and real-world implementation penalties**:
> 1. To match the $5.00\text{ kW}$ heating load at $-10^\circ\text{C}$, Case C must spin at **$4203\text{ rpm}$** ($+33\%$ faster than FT-VI at $2800\text{ rpm}$), causing higher mechanical wear and cabin NVH (noise, vibration, harshness).
> 2. Case C requires plumbing two separate heat exchangers into the vehicle HVAC duct (the intercooler pre-heater and the gas cooler), requiring bulky dual-radiator routing in cramped EV front-ends.

#### Q8: What happens if the flash-tank pressure ($P_{\text{FT}}$) is set too high ($> 5.5\text{ MPa}$)?
> **Answer:** Flash quality drops sharply ($x_{\text{FT}} \propto h_6 - h_f$). At $6.0\text{ MPa}$, flash vapor quality drops to $0.18$ and maximum injection ratio collapses to $\mu = 0.22$. With negligible vapor injected, Stage-2 desuperheating disappears, discharge temperatures escalate, and the cycle degenerates back into baseline single-stage performance.

#### Q9: What happens if the flash-tank pressure ($P_{\text{FT}}$) is set too low ($< 3.5\text{ MPa}$)?
> **Answer:** Flash tank pressure approaches port pressure ($P_{\text{port}} = 3.44\text{ MPa}$). The pressure differential driving vapor through the injection valve collapses ($\Delta P \rightarrow 0$), causing sonic choking to fail and choking the injection valve flow rate. Furthermore, the liquid subcooling benefit diminishes.

#### Q10: How was compressor displacement ($V_{\text{disp}} = 8.878\text{ cm}^3$) calibrated?
> **Answer:** Student 1 calibrated $V_{\text{disp}}$ using the single-stage Baseline Case A model such that at nominal cruising speed ($N = 4000\text{ rpm}$), design ambient ($T_{\text{amb}} = -10.0^\circ\text{C}$), and gas cooler pressure ($P_{\text{dis}} = 9.50\text{ MPa}$), the baseline heat pump delivers *exactly* the required cabin heating load of $\dot{Q}_h = 5.000\text{ kW}$.

#### Q11: What is the Knee Point on the Pareto frontier?
> **Answer:** The Knee Point is the solution on the multi-objective Pareto frontier that achieves the best compromise among competing objectives (maximum $\text{COP}_h$, maximum $\dot{Q}_h$, minimum $T_{\text{dis}}$) by minimizing the normalized Euclidean distance to the unattainable Utopia point $(1, 1, 0)$. Moving away from the knee point incurs a disproportionate sacrifice in one objective for negligible gains in the others.

#### Q12: Why does increasing compressor speed ($N$) from $2500$ to $8000\text{ rpm}$ decrease $\text{COP}_h$?
> **Answer:** Although mass flow and heating capacity scale almost linearly with speed, higher rotational speed incurs severe frictional losses, valve throttling irreversibilities, and fluid shear, which degrades compressor isentropic efficiency ($\Delta \eta_{\text{is}} \propto -1.2 \times 10^{-5} \Delta N$). Compression work increases faster than heating capacity, lowering $\text{COP}_h$.

#### Q13: How does the FT-VI system behave during continuous highway cruising delivering 5.0 kW?
> **Answer:** Because the optimized FT-VI system delivers $7.049\text{ kW}$ at $4000\text{ rpm}$ (+41% overcapacity), the variable-speed inverter throttles the compressor down to **$2800\text{ rpm}$** ($-30.0\%$ speed reduction). This reduces compressor power consumption to **$1.854\text{ kW}$** (a $3.8\%$ electrical energy saving compared to Case A's $1.926\text{ kW}$), extending EV driving range while drastically cutting cabin acoustic noise.

#### Q14: What equation of state was used in the model backend, and what is the reference state?
> **Answer:** The high-accuracy **CoolProp Span-Wagner Equation of State (EOS)** for carbon dioxide, with an analytical Peng-Robinson cubic EOS fallback. The reference state is the **IIR standard** ($h = 200.0\text{ kJ/kg}$ and $s = 1.000\text{ kJ/(kg}\cdot\text{K)}$ at $0.0^\circ\text{C}$ saturated liquid).

#### Q15: What was the mass and energy balance closure precision of the integrated solver?
> **Answer:** Residual mass and First-Law energy balances across every component (evaporator, compressors, gas cooler, flash tank, mixing plenum, and EEVs) closed to **machine precision** ($< 6 \times 10^{-15}\text{ kW}$), proving absolute thermodynamic conservation rigor.
