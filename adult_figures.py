"""Draw the adult-cohort figures directly from the published analysis tables."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
LABEL={'mortality':'In-hospital death','J69.0':'Aspiration-related pneumonitis (J69.0)',
       'PNEUMONIA_UNION':'Pneumonia (J12–J18)','PULMONARY_UNION':'Pneumonia or aspiration-related pneumonitis',
       'J96.00':'Hypoxemic respiratory failure','U69.01':'Pneumonia after 48 hours','U69.04':'Pneumonia by 48 hours',
       'MALNUT_UNION':'Protein-energy malnutrition (any)','E43':'Severe malnutrition (E43)','E44.0':'Moderate malnutrition (E44.0)',
       'E44.1':'Mild malnutrition (E44.1)','E46':'Unspecified malnutrition (E46)','E86':'Volume depletion',
       '8-701':'Simple endotracheal intubation','5-431.22':'PEG, thread-pull technique','1-613':'FEES'}
def plot():
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    x=pd.read_csv(ROOT/'adult_binary.csv').set_index(['outcome','model'])
    def base(h):
        f,a=plt.subplots(figsize=(9.2,h));f.subplots_adjust(left=.42,right=.975,bottom=.13,top=.91);return f,a
    def labels(a):
        a.set_yticks(range(len(LABEL)),list(LABEL.values()));a.set_ylim(len(LABEL)-.45,-.6)
        a.grid(axis='x',color='#dce1e5',zorder=0);a.tick_params(axis='y',length=0,pad=7);a.spines['left'].set_visible(False)
    def save(f,i):
        for ext in ['png','pdf']:
            f.savefig(ROOT/f'adult_figure_{i}.{ext}',dpi=260,facecolor='white')
        plt.close(f)
    f,a=base(6.4);labels(a)
    for i,k in enumerate(LABEL):
        r=x.loc[k,'M1'];d,c=r.dys_risk*100,r.comparator_risk*100
        a.plot([c,d],[i,i],color='#aab8c1');a.plot(c,i,'s',color='#aa4f2d',ms=5);a.plot(d,i,'o',color='#15657b',ms=5)
    a.legend([Line2D([],[],ls='',marker='o',color='#15657b'),Line2D([],[],ls='',marker='s',color='#aa4f2d')],['Dysphagia code','No dysphagia code'],loc='lower center',bbox_to_anchor=(.48,1.02),ncol=2,frameon=False)
    a.set_xlabel('Episodes with the outcome (%)');save(f,1)
    f,a=base(8.1);labels(a);f.subplots_adjust(bottom=.23,top=.975)
    cases=[('M1','Crude','o','#4a535b'),('age','Age','+','#996a19'),('age_hd','Age + principal diagnosis','s','#777b23'),('M2','Age + principal diagnosis + sex','^','#0876a0'),('M3','Age + principal diagnosis + PCCL','v','#793e8f'),('age_drg','Age + DRG','D','#bc502f'),('age_hd_drg','Age + principal diagnosis + DRG','x','#34358f')]
    for offset,(model,lab,marker,col) in zip(np.linspace(-.35,.35,len(cases)),cases):
        for i,k in enumerate(LABEL):
            r=x.loc[k,model]
            if pd.isna(r.rr): continue
            a.plot([r.rr_low,r.rr_high],[i+offset]*2,color=col,lw=.9)
            a.plot(r.rr,i+offset,ls='',marker=marker,color=col,ms=4)
    a.set_xscale('log');a.set_xticks([1,2,5,10,20,50,100]);a.xaxis.set_major_formatter(ScalarFormatter())
    a.axvline(1,color='#727b80',lw=.9);a.set_xlabel('Risk ratio (95% CI, logarithmic scale)')
    a.legend([Line2D([],[],marker=m,color=c,lw=1) for _,_,m,c in cases],[z[1] for z in cases],loc='upper center',bbox_to_anchor=(.06,-.10),ncol=2,frameon=False)
    save(f,2)
    t=pd.read_csv(ROOT/'adult_los.csv').set_index('model')
    labs={'M1':'Crude','age_hd':'Age + principal diagnosis','age_drg':'Age + DRG','age_drg_n2':'Age + DRG, ≥2 per group and stratum','age_hd_survivors':'Age + principal diagnosis, discharged alive'}
    f,a=base(3.9);f.subplots_adjust(left=.45,top=.95,bottom=.22);a.set_yticks(range(len(labs)),list(labs.values()));a.invert_yaxis()
    for i,k in enumerate(labs):
        r=t.loc[k]
        if pd.notna(r.ci_low):a.plot([r.ci_low,r.ci_high],[i,i],color='#15657b',lw=1.8)
        a.plot(r.difference,i,marker='o',color='#15657b',mfc='white' if pd.isna(r.ci_low) else '#15657b')
    a.grid(axis='x',color='#dce1e5');a.set_xlim(0,11.3);a.set_xlabel('Difference in mean hospital stay (days)');save(f,3)
if __name__=='__main__':plot()
