"""Student 6: Case C, two-stage intercooled transcritical R744 heat pump.
Drop this file next to config.py, co2_props.py, and baseline_cycle.py.
Uses the same thermodynamic backend, kJ/kg, MPa, Celsius and kg/s conventions.
"""
import math
from config import BRIEF, ASSUME
from co2_props import get_props
from baseline_cycle import baseline, calibrate_displacement, vol_eff, evap_temperature

props = get_props()

def case_c(T_amb=-10.0, P_i=4.5, T_ic=20.0, N=None, V_disp=None,
           recover_intercooler=False, eta_is=None):
    N = BRIEF['N'] if N is None else N
    eta_is = BRIEF['eta_is'] if eta_is is None else eta_is
    V_disp = calibrate_displacement() if V_disp is None else V_disp
    T_e = evap_temperature(T_amb)
    P_e = props.Psat(T_e)
    P_d = BRIEF['P_dis']
    if not (P_e < P_i < P_d):
        raise ValueError('Intermediate pressure must be between suction and discharge pressures')
    T1 = T_e + ASSUME['superheat']
    h1, s1, rho1 = props.h(P_e,T1),props.s(P_e,T1),props.rho(P_e,T1)
    eta_v = vol_eff(P_d,P_e) # same suction-flow calibration as Cases A and B
    m = rho1 * V_disp * (N/60) * eta_v
    h2s = props.h_ps(P_i,s1)
    h2 = h1 + (h2s-h1)/eta_is
    T2 = props.T_ph(P_i,h2)
    T_sat = props.Tsat(P_i)
    if T_ic <= T_sat + 0.1:
        raise ValueError(f'Intercooler outlet must remain vapor: T_ic > Tsat={T_sat:.2f} C')
    if T_ic >= T2:
        raise ValueError('Intercooler outlet must be cooler than stage-one discharge')
    h3, s3 = props.h(P_i,T_ic),props.s(P_i,T_ic)
    h4s = props.h_ps(P_d,s3)
    h4 = h3 + (h4s-h3)/eta_is
    T4 = props.T_ph(P_d,h4)
    T_gc = BRIEF['T_gc_out']
    h5 = props.h(P_d,T_gc)
    h6 = h5
    W1 = m*(h2-h1); W2=m*(h4-h3)
    Qic = m*(h2-h3); Qgc=m*(h4-h5)
    Quse = Qgc + (Qic if recover_intercooler else 0)
    W=W1+W2
    Qev=m*(h1-h6)
    # Energy identity for refrigerant cycle: Qgc + Qic = Qev + W
    err=Qgc+Qic-Qev-W
    feasible = (T4 <= BRIEF['T_dis_max'] and P_d <= BRIEF['P_max'] and Quse >= BRIEF['Q_load'])
    return dict(case='C',T_amb=T_amb,T_evap=T_e,P_evap=P_e,P_i=P_i,P_dis=P_d,
        T_ic=T_ic,T_sat_i=T_sat,N=N,m_dot=m,eta_v=eta_v,
        T1=T1,h1=h1,s1=s1,T2=T2,h2=h2,h2s=h2s,T3=T_ic,h3=h3,s3=s3,
        T4=T4,h4=h4,h4s=h4s,T5=T_gc,h5=h5,h6=h6,
        W1=W1,W2=W2,W=W,Q_ic=Qic,Q_gc=Qgc,Q_h=Quse,Q_e=Qev,
        COP_h=Quse/W,T_dis=T4,energy_balance_err=err,
        recover_intercooler=recover_intercooler,feasible=feasible,
        pressure_geomean=math.sqrt(P_e*P_d))
