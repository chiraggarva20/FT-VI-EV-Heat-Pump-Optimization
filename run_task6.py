"""Run Student 6 case C sensitivity, tables, and figures from repo root."""
import csv, math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from two_stage_intercooled import case_c
from baseline_cycle import baseline,calibrate_displacement
from config import BRIEF

OUT=Path('RESULTS')/'student6'; OUT.mkdir(parents=True,exist_ok=True)
V=calibrate_displacement()
rows=[]
for amb in (-5.,-10.,-15.):
    for p in np.linspace(3.5,6.0,51):
        for delta in (2.,5.,10.,15.,20.,25.):
            # Sweep outlet superheat above intermediate saturation temperature.
            from two_stage_intercooled import props
            try: ts=props.Tsat(float(p))
            except Exception: continue
            tic=ts+delta
            for recover in (False,True):
                try:
                    r=case_c(amb,float(p),tic,V_disp=V,recover_intercooler=recover)
                    r['ic_superheat']=delta
                    rows.append(r)
                except (ValueError,ArithmeticError,OverflowError): pass
if not rows: raise RuntimeError('No valid thermodynamic states. Check property backend and conditions.')
with (OUT/'case_c_sweep.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/'case_c_optima.csv').open('w',newline='') as f:
    keys=['T_amb','recover_intercooler','P_i','T_ic','COP_h','Q_h','W','Q_ic','T_dis','feasible','pressure_geomean']
    w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
    for amb in (-5.,-10.,-15.):
        for recover in (False,True):
            group=[r for r in rows if r['T_amb']==amb and r['recover_intercooler']==recover and r['feasible']]
            if group:
                best=max(group,key=lambda r:r['COP_h']);w.writerow({k:best[k] for k in keys})
            else: print('No feasible 5-kW point:',amb,'recovery:',recover)
for amb in (-5.,-10.,-15.):
    for recover in (False,True):
        subset=[r for r in rows if r['T_amb']==amb and r['recover_intercooler']==recover and r['ic_superheat']==10.]
        if not subset: continue
        subset.sort(key=lambda r:r['P_i'])
        fig,axs=plt.subplots(3,1,figsize=(7,10),sharex=True)
        for ax,key,unit in zip(axs,['COP_h','Q_h','T_dis'],['','kW','deg C']):
            ax.plot([r['P_i'] for r in subset],[r[key] for r in subset]);ax.set_ylabel(key+' '+unit);ax.grid(alpha=.3)
        axs[-1].set_xlabel('Intermediate pressure (MPa)')
        fig.suptitle(f'Case C: ambient {amb:g} C, recovery={recover}, IC superheat=10 K')
        fig.tight_layout();fig.savefig(OUT/f'sweep_{amb:g}_{int(recover)}.png',dpi=160);plt.close(fig)
print('Student 6 outputs saved to',OUT)
print('Compare case A at -10 C:',{k:baseline(V_disp=V)[k] for k in ('Q_h','W','COP_h','T_dis')})
