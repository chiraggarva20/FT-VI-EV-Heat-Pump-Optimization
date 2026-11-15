# Vapor-Injection-Heat-Pump-Optimization-for-Electric-Vehicle-Cold-Weather-Performance
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![CoolProp](https://img.shields.io/badge/CoolProp-6.4.3-green.svg)](http://www.coolprop.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 
## Project Overview
This repository contains a steady-state thermodynamic model evaluating a transcritical CO₂ (R744) heat pump designed for Electric Vehicle (EV) cabin heating in cold weather (down to -15 °C and -20 °C).
 
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
| **5 Integration & optimization** | Anmol | *(to be added)* | Pareto optimization |
| **6 Two-stage intercooled cycle** | Tarang Gupta | *(to be added)* | Case C |
 
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
| `-15 °C` | `Q_h = 4.39`, `T_dis = 130.3` — **fails** `Q_h` and `T_dis` | `Q_h = 5.84`, `COP = 2.50`, `T_dis = 118` — feasible | 4555 (`T_dis` at limit) / 3280 rpm |
| `-20 °C` | `Q_h = 3.82`, `T_dis = 141` — **fails** | `Q_h = 5.31`, `COP = 2.33`, `T_dis = 126` — feasible | 5220 (`T_dis = 142`) / 3770 rpm |
| `-25 °C` | `Q_h = 3.29`, `T_dis = 153` — **fails** | `Q_h = 4.58`, `T_dis = 137` — **fails** | not feasible / 4370 rpm (`T_dis = 137`) |
 
- **FT-VI rescues feasibility in extreme cold:** at 4000 rpm Case A stays feasible down to `-10 °C`, Case B down to `-20 °C`. At `-25 °C` neither does with `P_dis = 9.5 MPa`; `P_dis` and `N` must be co-optimized (Student 5).
- **At equal 5 kW output, Case B needs 24–28 % less speed** between `-10 °C` and `-20 °C`, runs 13–16 K cooler at `-15 °C` and `-20 °C`, and has `COP_h` 3–4 % higher.
- **COP peaks near 9.0 MPa** for both architectures at `-10 °C` and `-15 °C` (`P_dis` sweep); higher `P_dis` raises `T_dis` faster than it raises `Q_h`.
- **Best point on the `P_FT × phi` grid** (`-10 °C`, `4000 rpm`): `P_FT = 4.25 MPa`, `phi = 100 %`, `COP_h = 2.742`, `Q_h = 7.05 kW`, `T_dis = 107 °C`.
- **Feasible share of the `(T_amb, N)` envelope** (`-25…0 °C`, `2500…8000 rpm`): 40 % for Case A versus 63 % for Case B.
- **Model limit:** at `0 °C` the fixed port pressure (`1.5 * P_evap = 4.5 MPa`) reaches `P_FT`, so injection stops and Case B no longer helps; this is expected for a warm-weather condition and not a cold-weather target.
> The efficiency-map coefficients are a documented parametric surrogate, not measured compressor data. If a manufacturer map becomes available, only `stage_efficiency()` and `vol_eff_real()` need replacing.
 
### Phase 5: System Integration & Multi-Objective Optimization (Student 5)
*(To be filled by Student 5)*
Student 5 can call `compressor_vi.ftvi_real(phi, P_FT, T_evap, N, P_dis)` directly: it returns `Q_h`, `W`, `COP_h`, `T_dis`, `xi` and the constraint flags (`feasible`, `violations`, margins). The interface, constants, decision-variable ranges and ten test cases are in `results_task4/T4_handover_student5.json`.
 
### Phase 6: Two-Stage Compression with Intercooling (Student 6)
*(To be filled by Student 6)*
 
---
 
## Project Structure
 
The repository is modularly designed with the following file structure:
 
```text
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
├── README.md                # Unified project documentation
│
├── /results/                # Task 1 & 2 output CSV files and JSON handoff data
├── /figures/                # Task 1 & 2 P-h diagrams, T-s diagrams, maps, and schematics
├── /results_task3/          # Task 3 EEV sweep CSVs, state table, validation, and JSON handover
├── /figures_task3/          # Task 3 EEV flow, opening, ambient, speed, sensitivity, and P-h plots
├── /results_task4/          # Task 4 CSVs (design point, cold weather, load-matched speed, sweeps, envelopes,
│                            #   state table, validation) + T4_summary.json + T4_handover_student5.json
└── /figures_task4/          # Task 4 compressor map, cold-weather, stage work, speed, pressure, envelope,
                             #   load-matched speed, and P-h plots
```
 
## How to Run
 
```bash
pip install numpy scipy matplotlib CoolProp       # CoolProp is optional: a Peng-Robinson fallback is built in
python run_all.py       # Tasks 1 & 2  -> results/, figures/
python run_task3.py     # Task 3       -> results_task3/, figures_task3/
python run_task4.py     # Task 4       -> results_task4/, figures_task4/   (about 15 s)
```
Set `CO2_BACKEND=PR` to force the built-in Peng–Robinson backend (small offsets in absolute numbers; see the backend note in Phase 1).
 
### Task 4 output files
| File | Content |
| :--- | :--- |
| `T4_design_point_comparison.csv` | Case A / B, constant-eta vs compressor map |
| `T4_validation_vs_student3.csv` | Regression check: map off reproduces Task 3 |
| `T4_cold_weather.csv` | -15…0 °C at 4000 rpm: A, B 50 %, B 100 % |
| `T4_load_matched_speed.csv` | Lowest speed delivering 5.0 kW, with power, COP, T_dis, limit flags |
| `T4_stage_work.csv` | W1, W2, COP_h, T_dis vs P_FT and phi |
| `T4_speed_sweep.csv`, `T4_pdis_sweep.csv` | Speed (2500–8000 rpm) and discharge-pressure (7.5–12.5 MPa) sweeps |
| `T4_envelope_Tamb_N.csv`, `T4_envelope_PFT_Pdis.csv` | Feasibility maps with all constraint flags |
| `T4_map_eta_is.csv`, `T4_map_eta_v.csv` | Compressor map grids |
| `T4_state_table_design.csv` | State points 1–9 of Case B at the design point |
| `T4_summary.json`, `T4_handover_student5.json`, `T4_handover_testcases.csv` | Report numbers and hand-over to Anmol|
