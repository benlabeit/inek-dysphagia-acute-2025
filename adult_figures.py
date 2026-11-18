"""Publication figures from the adult cohort's released summary estimates."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
LABEL={'mortality':'In-hospital death','J69.0':'Aspiration-related pneumonitis (J69.0)',
       'PNEUMONIA_UNION':'Pneumonia (J12–J18)','PULMONARY_UNION':'Pneumonia or aspiration-related pneumonitis',
       'J96.00':'Hypoxemic respiratory failure','U69.01':'Pneumonia after 48 hours','U69.04':'Pneumonia by 48 hours',
       'MALNUT_UNION':'Protein-energy malnutrition (any)','E43':'Severe malnutrition (E43)','E44.0':'Moderate malnutrition (E44.0)',
       'E44.1':'Mild malnutrition (E44.1)','E46':'Unspecified malnutrition (E46)','E86':'Volume depletion',
       '8-701':'Simple endotracheal intubation','5-431.22':'PEG, thread-pull technique','1-613':'FEES'}

MAIN = ['mortality','PULMONARY_UNION','J96.00','MALNUT_UNION','E86','8-701','5-431.22','1-613']
DETAIL = ['J69.0','PNEUMONIA_UNION','U69.01','U69.04','E43','E44.0','E44.1','E46']
DISPLAY = {**LABEL,'PULMONARY_UNION':'Pneumonia or aspiration pneumonitis',
           'MALNUT_UNION':'Protein-energy malnutrition','J96.00':'Hypoxaemic respiratory failure',
           '8-701':'Endotracheal intubation','5-431.22':'Gastrostomy (thread-pull PEG)',
           '1-613':'Endoscopic swallowing evaluation (FEES)',
           'U69.01':'Pneumonia after 48 h','U69.04':'Pneumonia within 48 h'}
INK = '#17344B'
BLUE = '#116A82'
RUST = '#AA532A'
GRID = '#DCE3E7'


def save(fig, index):
    for ext in ('png','pdf'):
        meta={'CreationDate':None,'ModDate':None} if ext=='pdf' else None
        fig.savefig(ROOT/f'adult_figure_{index}.{ext}',dpi=300,facecolor='white',metadata=meta)
    plt.close(fig)


def categories(keys, split, headers):
    y=np.arange(len(keys),dtype=float)
    y[split:]+=.85
    headings=[(-.83,headers[0]),(y[split]-.82,headers[1])]
    return y,headings


def layout(widths, height=4.65):
    fig=plt.figure(figsize=(8.6,height))
    grid=fig.add_gridspec(1,len(widths),width_ratios=widths,left=.015,right=.985,top=.855,bottom=.16,wspace=.06)
    return fig,[fig.add_subplot(grid[0,i]) for i in range(len(widths))]


def row_labels(ax, keys, y, headings):
    ax.axis('off')
    for yi,label in headings:
        ax.text(0,yi,label,va='center',weight='bold',color=INK,fontsize=10.5)
    for yi,key in zip(y,keys):
        ax.text(.015,yi,DISPLAY[key],va='center',fontsize=9.4)


def prepare_axis(ax, y):
    ax.set_ylim(y[-1]+.6,-1.18)
    ax.set_yticks([])
    ax.spines[['left','top','right']].set_visible(False)
    ax.spines['bottom'].set_color('#84949C')
    ax.tick_params(axis='x',length=3,pad=4,labelsize=9)


def forest_axis(ax,xmax,ticks):
    ax.set_xscale('log');ax.set_xlim(.86,xmax)
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_locator(NullLocator())
    ax.grid(axis='x',color=GRID,lw=.7,zorder=0)
    ax.axvline(1,color='#85949D',lw=1,zorder=1)


def forest(data, keys, split, headings, index, xmax, ticks):
    y,groups=categories(keys,split,headings)
    fig,axes=layout([3.65,1.84,.52,1.84,.57])
    for ax in axes:prepare_axis(ax,y)
    row_labels(axes[0],keys,y,groups)
    styles=[('M2','Age, diagnosis and sex',BLUE,'o'),
            ('age_drg','Age within DRG',RUST,'s')]
    for i,(model,title,color,marker) in enumerate(styles):
        ax,value=axes[i*2+1:i*2+3]
        forest_axis(ax,xmax,ticks)
        ax.set_title(title,loc='left',fontsize=10.5,color=color,weight='bold',pad=8)
        value.axis('off')
        for yi,key in zip(y,keys):
            r=data.loc[(key,model)]
            ax.hlines(yi,r.rr_low,r.rr_high,color=color,lw=1.5,zorder=2)
            ax.plot(r.rr,yi,marker=marker,markersize=5,color=color,zorder=3,ls='')
            value.text(.95,yi,f'{r.rr:.2f}',va='center',ha='right',fontsize=9.5)
    fig.text(.69,.035,'Risk ratio (95% CI), logarithmic scale',ha='center',fontsize=9.5)
    save(fig,index)


def plot():
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','pdf.fonttype':42,
                         'axes.edgecolor':'#84949C','text.color':INK,'axes.labelcolor':INK,
                         'xtick.color':INK})
    data=pd.read_csv(ROOT/'adult_binary.csv').set_index(['outcome','model'])
    groupnames=['Clinical outcomes','Recorded procedures']
    y,groups=categories(MAIN,5,groupnames)
    fig,axes=layout([3.6,3.15,.87,.87])
    for ax in axes:prepare_axis(ax,y)
    labels,ax,with_code,without_code=axes
    row_labels(labels,MAIN,y,groups)
    for value,title,color in [(with_code,'With code',BLUE),(without_code,'Without code',RUST)]:
        value.axis('off');value.set_title(title,fontsize=9.6,color=color,weight='bold',pad=9)
    ax.set_xlim(-.7,35);ax.set_xticks([0,10,20,30]);ax.grid(axis='x',color=GRID,lw=.7)
    ax.set_xlabel('Episodes with the outcome (%)')
    for yi,key in zip(y,MAIN):
        r=data.loc[(key,'M1')];d,c=r.dys_risk*100,r.comparator_risk*100
        ax.hlines(yi,min(c,d),max(c,d),color='#A6B5BD',lw=1.2)
        ax.plot(d,yi,'o',color=BLUE,ms=5.5);ax.plot(c,yi,'s',color=RUST,ms=5)
        for value,n in [(with_code,d),(without_code,c)]:
            value.text(.5,yi,f'{n:.2f}%',ha='center',va='center',fontsize=9.4)
    fig.legend([Line2D([],[],ls='',marker='o',color=BLUE),Line2D([],[],ls='',marker='s',color=RUST)],
               ['With dysphagia coding','Without dysphagia coding'],frameon=False,ncol=2,
               loc='upper left',bbox_to_anchor=(.013,.992),fontsize=9.5,handlelength=1.0)
    save(fig,1)
    forest(data,MAIN,5,groupnames,2,85,[1,2,5,10,20,50])
    forest(data,DETAIL,4,['Pulmonary diagnoses','Malnutrition subtypes'],'s1',22,[1,2,5,10,20])

    los=pd.read_csv(ROOT/'adult_los.csv').set_index('model')
    fig,axes=layout([2.9,3.0,1.8],height=2.65)
    labels,ax,values=axes
    fig.subplots_adjust(top=.83,bottom=.30)
    for a in axes:prepare_axis(a,[0,1,2]);a.set_ylim(2.5,-.55)
    labels.axis('off');values.axis('off')
    values.set_title('Difference (95% CI)',fontsize=10,loc='center',pad=8,weight='bold')
    ax.set_xticks([0,2,4,6,8,10]);ax.set_xlim(-.2,11);ax.grid(axis='x',color=GRID,lw=.8)
    ax.set_xlabel('Difference in mean stay (days)')
    for i,(model,title,color) in enumerate([('M1','Crude',INK),('age_hd','Age and principal diagnosis',BLUE),
                                            ('age_drg_n2','Age within DRG (202 strata)',RUST)]):
        r=los.loc[model]
        labels.text(.005,i,title,va='center',fontsize=10)
        ax.hlines(i,r.ci_low,r.ci_high,color=color,lw=1.8)
        ax.plot(r.difference,i,'o',color=color,ms=6)
        values.text(.53,i,f'{r.difference:.2f} ({r.ci_low:.2f}–{r.ci_high:.2f})',ha='center',va='center',fontsize=10)
    save(fig,3)


if __name__=='__main__':
    plot()
