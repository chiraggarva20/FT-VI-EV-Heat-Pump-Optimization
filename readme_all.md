# Vapor Injection Heat Pump Optimization for Electric Vehicle Cold-Weather Performance ($\text{CO}_2$ / R744)

A modular thermodynamic modeling, component-level simulation, and performance evaluation framework for a transcritical $\text{CO}_2$ (R744) flash-tank vapor-injection (FT-VI) heat pump designed for electric vehicle (EV) cabin heating in cold climates.

---

## Project Architecture & Team Contributions

The repository is structured sequentially so each student builds cleanly on the preceding modules using a shared thermodynamic property backend (`co2_props.py`) and design brief (`config.py`):

| Task / Module | Author | Core Files | Engineering Scope |
| :--- | :--- | :--- | :--- |
| **Task 1: Baseline Cycle** | Student 1 | `config.py`, `co2_props.py`, `baseline_cycle.py`, `run_all.py` | Shared project constants, dual-backend $\text{CO}_2$ property wrapper (`CoolProp` with `Peng–Robinson` fallback), Case A single-stage transcritical cycle, and compressor displacement sizing ($V_{\text{disp}} = 6.49\text{ cm}^3/\text{rev}$ for $Q_{\text{load}} = 5.0\text{ kW}$ at $-10^\circ\text{C}$). |
| **Task 2: Ideal FT-VI Cycle** | Student 2 | `flash_tank_vi.py`, `run_all.py` | Case B two-stage flash-tank vapor-injection cycle with intermediate pressure sweeps ($P_{\text{inj}} = 3.5\text{--}6.0\text{ MPa}$), flash-tank mass/energy balance, and separator sizing ($D_{\text{tank}}$, liquid hold-up volume, Souders–Brown vapor velocity). |
| **Task 3: Injection EEV Control** | Student 3 | `eev.py`, `ftvi_eev.py`, `run_task3.py` | Compressible orifice model for the injection electronic expansion valve ($C_d = 0.70$, expansion factor $Y$, sonic choking $r_{\text{crit}} \approx 0.546$), fixed compressor injection-port pressure ($P_{\text{port}} = 1.5\,P_{\text{evap}}$), valve sizing ($C_d A_{\max} = 0.823\text{ mm}^2$), and $50\%$ EEV opening baseline evaluation. |
| **Task 4: Compressor & Heating Performance** | Student 4 | `compressor_vi.py`, `run_task4.py` | Off-design stage isentropic efficiency maps $\eta_{\text{is}}(N, \text{PR})$, injection back-leakage volumetric derating, stage-by-stage work ($W_1, W_2$), useful heating capacity ($Q_h$), heating COP ($\text{COP}_h$), operating constraint checks ($T_{\text{dis}}, P_{\text{dis}}, N, Q_h$), and cold-weather baseline vs. FT-VI comparisons. |

---

## Design Brief & Operating Constraints (`config.py`)

* **Working Fluid:** $\text{CO}_2$ (R744), transcritical operation
* **Design Ambient / Evaporating Temperature:** $T_{\text{amb}} = -10.0^\circ\text{C}$ ($\Delta T_{\text{approach}} = 5.0\text{ K} \Rightarrow T_{\text{evap}} = -15.0^\circ\text{C}$, superheat $= 5.0\text{ K}$)
* **Cabin Target & Load:** $T_{\text{cabin}} = 20.0^\circ\text{C}$, $Q_{\text{load}} = 5.0\text{ kW}$
* **High-Side Conditions:** $P_{\text{dis}} = 9.5\text{ MPa}$ ($P_{\max} = 12.0\text{ MPa}$), $T_{\text{gc,out}} = 35.0^\circ\text{C}$
* **Intermediate / Injection Conditions:** $P_{\text{inj}} = 4.5\text{ MPa}$ (sweep range $3.5\text{--}6.0\text{ MPa}$), baseline EEV opening $\phi = 50.0\%$
* **Compressor Parameters:** $N_{\text{design}} = 4000\text{ rpm}$ ($2500\text{--}8000\text{ rpm}$), design $\eta_{\text{is}} = 0.70$, volumetric efficiency $\eta_v = 0.97 - 0.03\,\text{PR}$, max discharge temperature $T_{\text{dis,max}} = 130.0^\circ\text{C}$

---

## Repository File Structure

```text
├── config.py                # Design brief parameters & modeling assumptions (Student 1)
├── co2_props.py             # R744 thermodynamic properties: CoolProp + PR fallback (Student 1)
├── baseline_cycle.py        # Case A single-stage baseline cycle & displacement sizing (Student 1)
├── flash_tank_vi.py         # Case B ideal flash-tank VI cycle & separator sizing (Student 2)
├── run_all.py               # Tasks 1 & 2 runner -> results/ & figures/ (Students 1 & 2)
├── eev.py                   # Compressible orifice EEV & choking physics (Student 3)
├── ftvi_eev.py              # Coupled FT-VI + EEV cycle with swappable compressor() (Student 3)
├── run_task3.py             # Task 3 sweeps & validation -> results_task3/ & figures_task3/ (Student 3)
├── compressor_vi.py         # Off-design two-stage compressor map & limit checker (Student 4)
├── run_task4.py             # Task 4 cold-weather & compressor studies -> results_task4/ & figures_task4/ (Student 4)
└── README.md                # Unified project documentation