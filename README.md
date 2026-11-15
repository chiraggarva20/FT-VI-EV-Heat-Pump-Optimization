# Vapor-Injection-Heat-Pump-Optimization-for-Electric-Vehicle-Cold-Weather-Performance
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![CoolProp](https://img.shields.io/badge/CoolProp-6.4.3-green.svg)](http://www.coolprop.org/)
 
## Project Overview
This repository contains a steady-state thermodynamic model evaluating a transcritical CO₂ (R744) heat pump designed for Electric Vehicle (EV) cabin heating in cold weather (design ambient -10 °C, with -5 °C and -15 °C sensitivity cases).
 
The project evaluates and compares three system architectures:
1. **Case A (Baseline):** A conventional single-stage vapor-compression heat pump cycle.
2. **Case B (FT-VI):** A Flash-Tank Vapor Injection system that injects intermediate-pressure vapor into a two-stage compressor to improve heating capacity and COP while cooling the compressor discharge.
3. **Case C (Two-Stage Intercooled):** A two-stage compression cycle with intermediate intercooling as an alternative architecture (Student 6).
### Objectives & Optimization Framework
- **Decision Variables:** Intermediate flash-tank pressure (`P_FT` / `P_inj`), injection EEV opening (`phi`), high-side discharge pressure (`P_dis`), and compressor speed (`N`).
- **Objectives:** Maximize Heating COP (`COP_h`), maximize useful heating capacity (`Q_h`), and minimize compressor discharge temperature (`T_dis`).
- **Constraints:** Maintain compressor discharge temperature `T_dis <= 130 °C`, discharge pressure `P_dis <= 12.0 MPa`, compressor speed `2500 <= N <= 8000 rpm`, `P_evap < P_inj < P_dis`, and ensure cabin heating capacity meets the `5.0 kW` target.
### Design Brief (`config.py`)
| Parameter | Value |
| :--- | :--- |
| Working fluid | R744 (CO₂), transcritical |
| Design ambient / evaporating temperature | -10 °C / -15 °C (5 K approach, 5 K superheat) |
| Cabin target / heating load | 20 °C / 5.0 kW |
| Gas-cooler outlet / discharge pressure | 35 °C / 9.5 MPa (hard limit 12.0 MPa) |
| Intermediate (injection) pressure | 4.5 MPa (sweep 3.5–6.0 MPa), baseline EEV opening 50 % |
| Compressor | 4000 rpm design (2500–8000 rpm), eta_is = 0.70, T_dis <= 130 °C |
 
---
 
## Team Contributions
 
The repository is built sequentially: each one of us reuse the shared property backend (co2_props.py) and design brief (config.py) and call the earlier modules without modifying them.
 
| Task | Author | Core files | Engineering scope |
| :--- | :--- | :--- | :--- |
| **1 Baseline cycle** | Kartik Gupta | `config.py`, `co2_props.py`, `baseline_cycle.py`, `run_all.py` | Shared constants, dual-backend property wrapper, Case A cycle, compressor displacement calibration |
| **2 Ideal FT-VI** | Durgesh Nimse | `flash_tank_vi.py`, `run_all.py` | Case B flash-tank cycle, mass/energy balances, P_inj sweeps, separator sizing |
| **3 Injection EEV** | Disha Jain | `eev.py`, `ftvi_eev.py`, `run_task3.py` | Compressible orifice EEV, choking, valve sizing, coupled FT-VI + EEV cycle |
| **4 Compressor & heating performance** | Garva Chirag | `compressor_vi.py`, `run_task4.py` | Off-design two-stage compressor map, stage work, heating capacity/COP, limit checker, cold-weather comparison |
| **5 Integration & optimization** | Anmol | `optimization_vi.py`, `run_task5.py` | Complete system integration, mass/energy balance verification, 3D Pareto frontier optimization, TOPSIS MCDM point selection, and cross-architecture benchmarking |
| **6 Two-stage intercooled cycle** | Tarang Gupta | `two_stage_intercooled.py`, `run_task6.py` | Case C two-stage cycle with intermediate intercooling, ambient rejection vs. cabin heat recovery, and P_i sensitivity |
 
---
 
## Thermodynamic Methodology
 
### Phase 1: Baseline Model (Case A — Kartik Gupta)
The conventional cycle models four main state points:
- **1 to 2:** Isentropic compression (adjusted by eta_is = 0.70) and compressor displacement calibration so that Case A delivers Q_load = 5.0 kW at -10 °C ambient.
- **2 to 3:** Isobaric heat rejection in the gas cooler.
- **3 to 4:** Isenthalpic expansion via an Electronic Expansion Valve (EEV).
- **4 to 1:** Isobaric heat absorption in the evaporator.
- *Heating Capacity:* Q_h = m_dot * (h_2 - h_3)
- *Compressor Work:* W = m_dot * (h_2 - h_1)
- *Volumetric efficiency:* eta_v = 0.97 - 0.03 * (P_dis / P_suc)
> **Backend note.** The calibrated displacement is V_disp = 6.27 cm³/rev with the CoolProp backend (used for all numbers in this README) and 6.49 cm³/rev with the built-in Peng–Robinson fallback (CO2_BACKEND=PR). Absolute results differ slightly between the two backends; trends and rankings do not.
 
### Phase 2: Ideal FT-VI Model (Case B — Durgesh Nimse)
The FT-VI system utilizes two expansion stages and a flash tank to separate saturated liquid and vapor at an intermediate pressure (P_inj = 3.5–6.0 MPa):
- **Mass Balance:** The vapor quality at the flash tank inlet dictates the maximum available injection ratio: x = (h_6 - h_f) / (h_g - h_f).
- **Injection Ratio:** xi = m_inj / m_suc
- **Two-Stage Compression:** Suction gas is compressed to P_inj, mixed adiabatically with the injected saturated vapor, and compressed to P_dis, lowering final discharge temperature and boosting total mass flow through the gas cooler.
### Phase 3: Injection EEV & Flow Control (Disha Jain)
Replaces the ideal intermediate-pressure assumption with a physical injection electronic expansion valve sitting on the vapor line between the flash tank (P_FT) and a fixed compressor injection port (P_port = r_port * P_evap, r_port = 1.5):
- **Compressible Orifice Flow (Choke-Limited):**
  m_valve = Cd * phi * A_max * Y * sqrt(2 * rho_v * dP)
  where Y = 1 - 0.41 * dP / (k * P_FT) (Cd = 0.70, k = 1.30) and dP = min(P_FT - P_port, (1 - r_crit) * P_FT) with sonic choking limit r_crit ≈ 0.546.
- **Flash-Tank Vapor Cap:** m_inj = min(m_valve, (x / (1 - x)) * m_suc) ensures no liquid is drawn into the injection port.
- **Un-injected Vapor Routing:** Vapor blocked by a partially closed EEV exits the tank bottom with the liquid into EEV-2: h_8 = h_5 + xi * (h_5 - h_7).
- **Valve Sizing & Design Baseline:** Sized so phi = 1.0 passes 1.20x available vapor at the design point (Cd * A_max = 0.823 mm², d_eq ≈ 1.22 mm). At the 50% EEV baseline (-10 °C, 4.5 MPa, 4000 rpm), the system delivers Q_h = 6.25 kW (+25% over Case A), COP_h = 2.670 (+2.9%), and T_dis = 111.7 °C.
- **Hand-over:** eev.m_inj(phi, P_FT, P_port, m_suc, x, CdA_max) and the coupled cycle ftvi_eev.ftvi_eev(...) with a swappable compressor() stub (constant eta_is), which Chirag will replace.
### Phase 4: Compressor & Heating Performance (Garva Chirag)
Evaluates realistic two-stage compressor operation, stage-by-stage work, useful heating performance, and operating limits across cold-weather conditions using the integrated framework from Kartik, Durgesh and Disha. Chirag adds one new module (`compressor_vi.py`) and one study runner (`run_task4.py`); Previous modules are untouched.
 
- **Off-Design Stage Isentropic Efficiency Map:** stage_efficiency(N, PR_stage, PR_ref)
  eta_is = 0.70 - a_low (1-n)² [n<1]  - a_high (n-1)² [n>1]  - k_PR ln²(PR/PR_ref), with n = N/4000, a_low = 0.20 (low-speed internal leakage), a_high = 0.06 (high-speed port/valve throttling), k_PR = 0.06. Anchored to eta_is = 0.70 at the 4000 rpm design point; clipped to 0.45–0.80. Stage 1 and stage 2 use their own design pressure ratios (1.50 and 2.77); Case A uses the overall ratio (4.15) so that the baseline is compared with the **same** map.
- **Injection Back-Leakage Derating:** eta_v = (0.97 - 0.03 * PR_tot) * f_N(N) * (1 - k_leak * xi) with k_leak = 0.03 and a small low-speed leakage factor f_N. Because m_suc depends on xi and the vapor cap x/(1-x) * m_suc depends on m_suc, the two are solved by fixed-point iteration inside ftvi_real().
- **Stage Work & Heating Performance:** Stage-1 power W1 = m_suc * (h_2 - h_1), stage-2 power W2 = m_tot * (h_4 - h_3), total power W = W1 + W2, useful heating capacity Q_h = m_tot * (h_4 - h_5), and COP_h = Q_h / W.
- **Operating Constraint Verification:** check_limits() explicitly verifies T_dis <= 130.0 °C, P_dis <= 12.0 MPa, 2500 <= N <= 8000 rpm, Q_h >= 5.0 kW and P_evap < P_port, P_FT < P_dis, and returns margins plus a list of violated limits.
- **Load Matching:** required_speed() finds the lowest speed that delivers 5.0 kW for any cycle function, so the two architectures are also compared at equal useful output.
- **Validation:** with the map switched off (realistic=False) ftvi_real() reproduces ftvi_eev.ftvi_eev() and baseline_real() reproduces baseline_cycle.baseline() to machine precision (max relative difference = 0, results_task4/T4_validation_vs_student3.csv).
#### Key results (CoolProp backend)
 
| Design point, `-10 °C`, `4000 rpm`, `9.5 MPa`, `P_FT = 4.5 MPa`, `phi = 50 %` | `Q_h` [kW] | `W` [kW] | `COP_h` | `T_dis` [°C] | `xi` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Case A (baseline, calibrated) | 5.000 | 1.926 | 2.595 | 120.4 | – |
| Case B, Task 3 (constant `eta_is`) | 6.251 | 2.341 | 2.670 | 111.7 | 0.314 |
| Case B, Task 4 (compressor map) | 6.203 | 2.322 | 2.671 | 111.6 | 0.317 |
 
The realistic compressor changes the design-point answer by under 1 %, because the map is anchored there; its effect appears away from the design point.
 
| Ambient | Case A at 4000 rpm | Case B at 4000 rpm, `phi = 50 %` | Speed for 5.0 kW: A / B |
| :---: | :--- | :--- | :--- |
| `-10 °C` | `Q_h = 5.00`, `COP = 2.60`, `T_dis = 120` — feasible | `Q_h = 6.20`, `COP = 2.67`, `T_dis = 112` — feasible | 4000 / 3030 rpm |
| `-15 °C` | `Q_h = 4.39`, `T_dis = 130.3` — **fails** `Q_h` and `T_dis` | `Q_h = 5.84`, `COP = 2.50`, `T_dis = 130.3` — feasible | 4555 (`T_dis` at limit) / 3280 rpm |
 
- **FT-VI rescues feasibility in extreme cold:** at 4000 rpm Case A stays feasible down to `-10 °C`, Case B down to `-20 °C`. At `-25 °C` neither does with `P_dis = 9.5 MPa`; `P_dis` and `N` must be co-optimized (Student 5).
- **At equal 5 kW output, Case B needs 24–28 % less speed** between `-10 °C` and `-20 °C`, runs 13–16 K cooler at `-15 °C` and `-20 °C`, and has `COP_h` 3–4 % higher.
- **COP peaks near 9.0 MPa** for both architectures at `-10 °C` and `-15 °C` (`P_dis` sweep); higher `P_dis` raises `T_dis` faster than it raises `Q_h`.
- **Best point on the `P_FT × phi` grid** (`-10 °C`, `4000 rpm`): `P_FT = 4.25 MPa`, `phi = 100 %`, `COP_h = 2.742`, `Q_h = 7.05 kW`, `T_dis = 107 °C`.
- **Feasible share of the `(T_amb, N)` envelope** (`-25…0 °C`, `2500…8000 rpm`): 40 % for Case A versus 63 % for Case B.
- **Model limit:** at `0 °C` the fixed port pressure (`1.5 * P_evap = 4.5 MPa`) reaches `P_FT`, so injection stops and Case B no longer helps; this is expected for a warm-weather condition and not a cold-weather target.
> The efficiency-map coefficients are a documented parametric surrogate, not measured compressor data. If a manufacturer map becomes available, only `stage_efficiency()` and `vol_eff_real()` need replacing.
 
### Phase 5: System Integration & Multi-Objective Optimization (Student 5 — Anmol)
Student 5 integrates the physics, thermodynamic states, and off-design models developed across Tasks 1–4 into an integrated steady-state simulation model, performs rigorous conservation-law checks, conducts multi-objective optimization across the 3D decision variable space, applies multi-criteria decision making (TOPSIS and Knee-Point), and benchmarks the four system architectures. Core scripts added: optimization_vi.py and 
un_task5.py.

#### 1. System Integration & Conservation Law Verification
- **Unified Function:** optimization_vi.evaluate_system(phi, P_FT, N, T_amb, P_dis, ...) encapsulates the complete coupled cycle, fixed-point suction/injection mass balance iteration, off-design stage efficiencies, and constraint evaluation.
- **Thermodynamic Balance Closures:** Evaluated across 165 operating points ({FT} \in [3.5, 6.0]$ MPa, $\phi \in [0.1, 1.0]$,  \in [3000, 6000]$ rpm):
  - Overall Mass Conservation: $|m_{tot} - (m_{suc} + m_{inj})| = 0.00\text{ kg/s}$ (machine zero)
  - Adiabatic Flash-Tank Energy Balance: $|m_{tot} h_6 - (m_{inj} h_7 + m_{suc} h_8)| < 2\times 10^{-15}\text{ kW}$
  - First-Law Cycle Energy Closure: $|Q_h - (Q_e + W)| < 6\times 10^{-15}\text{ kW}$
  - Compressor Power Closure: $|W - (W_1 + W_2)| = 0.00\text{ kW}$

#### 2. Optimization Framework
- **Decision Variables:**
  - Flash-tank intermediate pressure: {FT} \in [3.5, 6.0]$ MPa
  - Injection EEV opening: $\phi \in [0.05, 1.00]$ (5 % to 100 %)
  - Compressor rotational speed:  \in [2500, 8000]$ rpm
- **Objectives:**
  1. $\max COP_h = Q_h / W$ (maximize electrical driving efficiency and EV range)
  2. $\max Q_h = m_{tot}(h_4 - h_5)$ (maximize heating capacity for rapid cabin warm-up)
  3. $\min T_{dis} = T_4$ (minimize compressor discharge temperature for component reliability)
- **Hard Constraints:**
  - {dis} \le 130.0\ ^\circ\text{C}$ (compressor thermal limit)
  - {dis} \le 12.0\text{ MPa}$ (system mechanical pressure limit; nominal 9.5 MPa)
  -  \ge 5.0\text{ kW}$ (cabin thermal comfort requirement at $-10\ ^\circ\text{C}$)
  -  \le N \le 8000\text{ rpm}$
  - Pressure consistency: {evap} < P_{port} < P_{dis}$ and {evap} < P_{FT} < P_{dis}$

#### 3. Pareto Frontier & Trade-Offs (CoolProp Backend at $-10\ ^\circ\text{C}$, .5\text{ MPa}$)
From 7,056 sampled evaluations across the 3D space, 5,905 states (83.7 %) satisfy all hard constraints. Fast non-dominated sorting extracted 45 non-dominated Pareto-optimal solutions (
esults_task5/T5_pareto_front.csv):

| Pareto Anchor Point | $ | $ [kW] | {dis}$ [°C] | {FT}$ [MPa] | $\phi$ [%] | $ [rpm] | Engineering Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Max $ Point** | **2.745** | 6.88 | 107.2 | 4.25 | 100 % | 3875 | Maximum steady-state efficiency |
| **Max $ Point** | 2.540 | **13.51** | 113.2 | 5.12 | 100 % | 8000 | Maximum pull-down / extreme heating |
| **Min {dis}$ Point** | 2.705 | 6.85 | **107.0** | 5.00 | 62 % | 4150 | Maximum thermal protection |

#### 4. Multi-Criteria Decision Making (MCDM) & Recommended Design Point
Applying TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) and Euclidean Utopia Knee-Point analysis across the Pareto set:
- **TOPSIS Balanced Weights** ( = [1/3, 1/3, 1/3]$):  = 2.687$,  = 9.88\text{ kW}$, {dis} = 108.1\ ^\circ\text{C}$ ({FT} = 4.75\text{ MPa}$, $\phi = 1.0$,  = 5800\text{ rpm}$).
- **TOPSIS Efficiency-First** ( = [0.50, 0.20, 0.30]$):  = 2.728$,  = 8.16\text{ kW}$, {dis} = 107.3\ ^\circ\text{C}$ ({FT} = 4.50\text{ MPa}$, $\phi = 1.0$,  = 4700\text{ rpm}$).
- **Selected Recommended Design Point:**
  - **Operating Parameters:** Intermediate pressure {FT} = 4.25\text{ MPa}$, EEV opening $\phi = 100\,\%$, nominal speed  = 4000\text{ rpm}$.
  - **Performance at Design Ambient ($-10\ ^\circ\text{C}$):**
    - Useful Heating Capacity:  = 7.049\text{ kW}$ (**+41.0 %** over Case A baseline 5.0 kW)
    - Heating COP:  = 2.742$ (**+5.7 %** improvement over Case A .595$)
    - Compressor Discharge Temperature: {dis} = 107.5\ ^\circ\text{C}$ (**12.9 K lower** than Case A .4\ ^\circ\text{C}$, safely below 130 °C)
    - Total Power:  = 2.571\text{ kW}$ ( = 0.482\text{ kW}$,  = 2.089\text{ kW}$)
    - Injection Ratio: $\xi = 0.546$, Flash Vapor Quality:  = 0.360$
  - **Load-Matched Cruising (delivering exactly {load} = 5.00\text{ kW}$):**
    - Compressor speed throttles down from 4000 rpm to **2800 rpm (-30.0 % speed reduction)**.
    - Power consumption drops to **1.854 kW (-3.8 % power savings)** with  = 2.697$ and {dis} = 108.9\ ^\circ\text{C}$.

---

### Phase 6: Two-Stage Compression with Intercooling (Student 6 — Tarang Gupta)
Student 6 models an alternative two-stage transcritical CO₂ cycle (	wo_stage_intercooled.py, 
un_task6.py) comprising low-stage compression from {evap}$ to intermediate pressure $, isobaric intercooling to {ic}$, high-stage compression to {dis}$, and gas-cooling.

- **Intermediate Pressure & Intercooler Duty:**
  - Intermediate pressure investigated between 3.5 and 6.0 MPa (geometric mean $\sqrt{P_{evap} P_{dis}} \approx 4.66\text{ MPa}$).
  - Intercooler heat rejection duty: {ic} = \dot{m}(h_2 - h_3)$.
- **Intercooler Heat Management Architectures:**
  1. *Option 1 (No Recovery):* Rejects {ic}$ to ambient air; useful heating is gas cooler only:  = Q_{gc} = \dot{m}(h_4 - h_5)$.
  2. *Option 2 (Heat Recovery):* Uses {ic}$ to preheat fresh cabin ventilation air:  = Q_{gc} + Q_{ic}$.
- **Key Findings:**
  - Intercooling delivers the lowest compressor discharge temperatures of all systems ({dis} = 87.2\ ^\circ\text{C}$, 33.2 K below Case A).
  - Without heat recovery (Option 1), COP severely degrades ( = 2.275$, -12.3 % vs Case A) and capacity drops to 4.01 kW (fails 5.0 kW target at 4000 rpm).
  - With heat recovery (Option 2), COP reaches .745$ (+5.8 % vs Case A), but requires an additional cabin-air heat exchanger loop. At extreme cold ($-15\ ^\circ\text{C}$), it requires higher compressor speed ( = 4750\text{ rpm}$) to satisfy 5.0 kW.

---

### Comprehensive Architecture Benchmarking Across Cold Ambients

#### 1. Nominal Speed Comparison ( = 4000\text{ rpm}$, {dis} = 9.5\text{ MPa}$)

| Ambient | Metric | Case A (Baseline) | Case B (FT-VI Nominal) | Case B (FT-VI Optimized) | Case C (Intercooled, Recov) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$-5\ ^\circ\text{C}$** | $ [kW] | 5.66 | 6.51 (+15.1 %) | **6.87 (+21.4 %)** | 5.51 (-2.6 %) |
| | $ [-] | 2.81 | 2.86 (+1.7 %) | 2.90 (+3.1 %) | **2.96 (+5.2 %)** |
| | {dis}$ [°C] | 111.5 | 106.5 (-5.0 K) | 104.7 (-6.7 K) | **87.2 (-24.3 K)** |
| | Feasible? | **Yes** | **Yes** | **Yes** | **Yes** |
| **$-10\ ^\circ\text{C}$** | $ [kW] | 5.00 | 6.20 (+24.1 %) | **7.05 (+41.0 %)** | 4.84 (-3.3 %) |
| *(Design)* | $ [-] | 2.595 | 2.671 (+2.9 %) | 2.742 (+5.7 %) | **2.745 (+5.8 %)** |
| | {dis}$ [°C] | 120.4 | 111.6 (-8.8 K) | 107.5 (-12.9 K) | **87.2 (-33.2 K)** |
| | Feasible? | **Yes** | **Yes** | **Yes** | Fails {load}$ at 4000 rpm |
| **$-15\ ^\circ\text{C}$** | $ [kW] | 4.39 (fails) | 5.84 (+33.2 %) | **6.24 (+42.2 %)** | 4.21 (fails) |
| *(Extreme)* | $ [-] | 2.407 | 2.496 (+3.7 %) | 2.524 (+4.9 %) | **2.559 (+6.3 %)** |
| | {dis}$ [°C] | 130.2 (violates) | 117.6 (-12.6 K) | 115.9 (-14.3 K) | **87.2 (-43.0 K)** |
| | Feasible? | **No** (fails $ & {dis}$) | **Yes** | **Yes** | Fails {load}$ at 4000 rpm |

#### 2. Load-Matched Speed Comparison (Exact  = 5.00\text{ kW}$ Delivery)

| Ambient | Metric | Case A (Baseline) | Case B (FT-VI Nominal) | Case B (FT-VI Optimized) | Case C (Intercooled, Recov) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$-10\ ^\circ\text{C}$** | Speed $ [rpm] | 4000 | 3032 (-24.2 %) | **2800 (-30.0 %)** | 4140 (+3.5 %) |
| *(Design)* | Work $ [kW] | 1.926 | 1.871 (-2.9 %) | **1.854 (-3.8 %)** | 1.823 (-5.4 %) |
| | $ [-] | 2.595 | 2.673 | 2.697 | **2.745** |
| | {dis}$ [°C] | 120.4 | 110.3 (-10.1 K) | 108.9 (-11.5 K) | **87.2 (-33.2 K)** |
| **$-15\ ^\circ\text{C}$** | Speed $ [rpm] | 4555 (violates {dis}$) | 3276 (-28.1 %) | **3197 (-29.8 %)** | 4750 (+4.3 %) |
| *(Extreme)* | Work $ [kW] | 2.079 | 2.001 (-3.8 %) | **1.996 (-4.0 %)** | 1.954 (-6.0 %) |
| | $ [-] | 2.405 | 2.499 | 2.505 | **2.559** |
| | {dis}$ [°C] | 130.4 (exceeds 130 °C) | 116.5 (-13.9 K) | 116.8 (-13.6 K) | **87.2 (-43.2 K)** |

---

## Project Structure

The repository is modularly designed with the following file structure:

`	ext
Vapor-Injection-Heat-Pump-Optimization-for-Electric-Vehicle-Cold-Weather-Performance/
│
├── config.py                # Global configuration: Project brief data, parameters, and assumptions (Kartik Gupta)
├── co2_props.py             # Fluid property backend: Wraps CoolProp & built-in Peng-Robinson fallback (Kartik Gupta)
├── baseline_cycle.py        # Conventional cycle & compressor displacement calibration (Kartik Gupta)
├── flash_tank_vi.py         # Ideal FT-VI cycle, mass/energy balances, P_inj sweeps (Durgesh Nimse)
├── run_all.py               # Tasks 1 & 2 orchestration script: runs sweeps, saves data, plots figures (Kartik Gupta, Durgesh Nimse)
│
├── eev.py                   # Compressible orifice EEV & choking physics (Disha Jain)
├── ftvi_eev.py              # Coupled FT-VI + EEV cycle with swappable compressor() (Disha Jain)
├── run_task3.py             # Task 3 sweeps, validation vs. Student 2, and plots (Disha Jain)
│
├── compressor_vi.py         # Off-design two-stage compressor map, realistic FT-VI / baseline cycles, 
│                            #   operating-limit checker, load-matching solver (Garva Chirag)
├── run_task4.py             # Task 4 cold-weather, load-matching, stage-work, speed, pressure & envelope studies (Garva Chirag)
│
├── optimization_vi.py       # Student 5: Integrated system model, conservation laws, 3D Pareto frontier,
│                            #   TOPSIS MCDM ranking, Knee-point selection, and cross-architecture benchmarking (Anmol)
├── run_task5.py             # Student 5: Complete study runner, Pareto optimization, state tables, and figures (Anmol)
│
├── two_stage_intercooled.py # Student 6: Case C two-stage cycle with intermediate intercooling (Tarang Gupta)
├── run_task6.py             # Student 6: Case C parametric studies and intermediate pressure optimization (Tarang Gupta)
│
├── README.md                # Unified project documentation
│
├── /results/                # Task 1 & 2 output CSV files and JSON handoff data
├── /figures/                # Task 1 & 2 P-h diagrams, T-s diagrams, maps, and schematics
├── /results_task3/          # Task 3 EEV sweep CSVs, state table, validation, and JSON handover
├── /figures_task3/          # Task 3 EEV flow, opening, ambient, speed, sensitivity, and P-h plots
├── /results_task4/          # Task 4 CSVs (design point, cold weather, load-matched speed, sweeps, envelopes,
│                            #   state table, validation) + T4_summary.json + T4_handover_student5.json
├── /figures_task4/          # Task 4 compressor map, cold-weather, stage work, speed, pressure, envelope,
│                            #   load-matched speed, and P-h plots
├── /results_task5/          # Task 5 CSVs (mass/energy residuals, sweeps, 3D Pareto front, all evaluations,
│                            #   recommended state table, architecture comparisons, load-matched benchmarks) + T5_optima_summary.json
├── /figures_task5/          # Task 5 publication figures (3D Pareto surface, 2D trade-offs, parametric effects,
│                            #   P-h cycle overlay, architecture comparison bars, TOPSIS decision landscape, residuals)
└── /RESULTS/student6/       # Task 6 Case C sweep data, optima tables, and figures
`

## How to Run

`ash
pip install numpy scipy matplotlib CoolProp       # CoolProp is recommended for report numbers
python run_all.py       # Tasks 1 & 2  -> results/, figures/
python run_task3.py     # Task 3       -> results_task3/, figures_task3/
python run_task4.py     # Task 4       -> results_task4/, figures_task4/
python run_task5.py     # Task 5       -> results_task5/, figures_task5/
python run_task6.py     # Task 6       -> RESULTS/student6/
`
Set CO2_BACKEND=PR to force the built-in Peng–Robinson backend (small offsets in absolute numbers; see the backend note in Phase 1).

### Task 5 output files (Student 5 — Anmol)
| File | Content |
| :--- | :--- |
| T5_validation_vs_student4.csv | Regression check against 10 test cases from Task 4 (max abs diff = 1.16e-07) |
| T5_mass_energy_balance_verification.csv | Rigorous check of conservation of mass, First-Law closure, and adiabatic flash tank energy balances across 165 states |
| T5_parametric_sweeps.csv | Parametric sweeps of decision variables ({FT}$, $\phi$, $) |
| T5_all_evaluations.csv | 7,056 sampled evaluations across 3D decision variable space with feasibility and constraint flags |
| T5_pareto_front.csv | 45 non-dominated Pareto-optimal solutions across the 3 objectives (, Q_h, T_{dis}$) |
| T5_optima_summary.json | Single-objective anchors, TOPSIS rankings (balanced, efficiency, capacity), Knee-point, and recommended operating point |
| T5_recommended_state_table.csv | Complete thermodynamic state table (States 1–9, 7a) at the recommended design point ({FT} = 4.25$ MPa, $\phi = 100\%$,  = 4000$ rpm) |
| T5_case_comparison.csv | Cross-architecture comparison (Case A, Case B nominal, Case B optimized, Case C) at $-5, -10, -15\ ^\circ\text{C}$ |
| T5_load_matched_comparison.csv | Cross-architecture comparison at exact .0\text{ kW}$ heating delivery, showing required speed and power savings |
