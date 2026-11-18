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
    colors = ['#475467','#087e9b','#8a4182','#bb5725','#41653d']
    cases = [('M1','Crude','o'),('M2','Age + diagnosis + sex','^'),
             ('M3','Age + diagnosis + PCCL','s'),('age_drg','Age + DRG','D'),
             ('age_hd_drg','Age + diagnosis + DRG','x')]
    f = plt.figure(figsize=(9.2,9.6))
    grid = f.add_gridspec(2,1,height_ratios=[8,1.25],left=.405,right=.965,top=.955,bottom=.089,hspace=.32)
    a = f.add_subplot(grid[0]); pilot = f.add_subplot(grid[1],sharex=a)
    labels(a)
    def point(ax,row,y,marker,color):
        ax.plot([row.rr_low,row.rr_high],[y,y],color=color,lw=.95,zorder=2)
        ax.plot(row.rr,y,ls='',marker=marker,color=color,ms=4.4,zorder=3)
    for off,(model,title,marker),color in zip(np.linspace(-.31,.31,len(cases)),cases,colors):
        for i,k in enumerate(LABEL):
            point(a,x.loc[k,model],i+off,marker,color)
    a.set_title('A   Adult cohort',loc='left',fontsize=11,weight='bold')
    pilot.set_title('B   In-hospital death within B70D only',loc='left',fontsize=11,weight='bold')
    pilot.set_yticks([0,1,2],['Crude','Age','Age + sex (model 4)'])
    pilot.set_ylim(2.55,-.65);pilot.tick_params(axis='y',length=0,pad=7)
    for i,(model,marker,col) in enumerate([('B70D_crude','o',colors[0]),('B70D_age','v','#9c7441'),('M4_B70D','^',colors[1])]):
        point(pilot,x.loc['mortality',model],i,marker,col)
    for ax in [a,pilot]:
        ax.set_xscale('log');ax.set_xlim(.86,95);ax.set_xticks([1,2,5,10,20,50])
        ax.xaxis.set_major_formatter(ScalarFormatter());ax.minorticks_off()
        ax.axvline(1,color='#8a9197',lw=.85);ax.grid(axis='x',color='#e2e6e8',zorder=0)
        ax.spines['left'].set_visible(False)
    a.legend([Line2D([],[],marker=m,color=c,lw=1) for (_,_,m),c in zip(cases,colors)],
             [title for _,title,_ in cases],loc='upper center',bbox_to_anchor=(.35,-.044),
             ncol=3,frameon=False,fontsize=8.0,columnspacing=1.1,handlelength=1.1)
    pilot.set_xlabel('Risk ratio (95% CI, logarithmic scale)',labelpad=6)
    save(f,2)
    t=pd.read_csv(ROOT/'adult_los.csv').set_index('model')
    labs={'M1':'Crude','age':'Age','age_hd':'Age + diagnosis, common grouping',
          'age_hd_fine':'Age + diagnosis, finer grouping',
          'age_drg':'Age + DRG','age_drg_n2':'Age + DRG, ≥2 per group and stratum',
          'age_hd_drg':'Age + diagnosis + DRG',
          'age_hd_drg_n2':'Age + diagnosis + DRG, ≥2 per group and stratum',
          'age_hd_survivors':'Discharged alive, age + diagnosis',
          'B70D_age':'B70D only, age'}
    f,a=base(5.4);f.subplots_adjust(left=.47,right=.97,top=.95,bottom=.14)
    a.set_yticks(range(len(labs)),list(labs.values()));a.invert_yaxis()
    for i,k in enumerate(labs):
        r=t.loc[k]
        if pd.notna(r.ci_low):a.plot([r.ci_low,r.ci_high],[i,i],color='#15657b',lw=1.8)
        a.plot(r.difference,i,marker='o',color='#15657b',mfc='white' if pd.isna(r.ci_low) else '#15657b')
    for y in (3.5,7.5):a.axhline(y,lw=.6,color='#dce1e5')
    a.tick_params(axis='y',length=0,pad=7);a.spines['left'].set_visible(False)
    a.grid(axis='x',color='#dce1e5');a.set_xlim(0,11.3);a.set_xlabel('Difference in mean hospital stay (days)');save(f,3)
    f,(ax1,ax2)=plt.subplots(1,2,figsize=(12.2,8.3),sharey=True)
    f.subplots_adjust(left=.32,right=.99,top=.925,bottom=.19,wspace=.12)
    panels=[(ax1,'Age and principal diagnosis',[('M1','Crude','o','#475467'),('age','Age alone','+','#996a19'),('age_hd','Age + diagnosis (5 groups)','s','#38734b'),('age_hd_fine','Age + diagnosis (6 groups)','x','#964b2c')]),
            (ax2,'Sex and PCCL models',[('M2','Sex (5 groups)','^','#167e99'),('M2_fine','Sex (6 groups)','v','#367db3'),('M3','PCCL (5 groups)','s','#843875'),('M3_fine','PCCL (6 groups)','D','#b87299')])]
    for ax,title,models in panels:
        ax.set_title(title,loc='left',weight='bold',fontsize=11)
        for off,(m,label,marker,col) in zip(np.linspace(-.3,.3,len(models)),models):
            for i,k in enumerate(LABEL):
                row=x.loc[k,m]
                if pd.notna(row.rr):
                    point(ax,row,i+off,marker,col)
        ax.axvline(1,color='#8a9197',lw=.85);ax.set_xscale('log');ax.set_xlim(.82,95)
        ax.set_xticks([1,2,5,10,20,50]);ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.minorticks_off();ax.grid(axis='x',color='#e2e6e8',zorder=0);ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y',length=0,pad=5);ax.set_xlabel('Risk ratio (95% CI)')
        ax.legend([Line2D([],[],marker=m,color=c,lw=1) for _,_,m,c in models],
                  [label for _,label,_,_ in models],loc='upper center',bbox_to_anchor=(.5,-.095),
                  ncol=1,frameon=False,fontsize=8.5)
    ax1.set_yticks(range(len(LABEL)),list(LABEL.values()));ax1.set_ylim(len(LABEL)-.48,-.55)
    save(f,'s1')
if __name__=='__main__':plot()
