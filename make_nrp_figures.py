"""Reproduce publication figures from validated aggregate results or plotted CSV.

Source mode audits OPS 1-613 case counts against original Excel workbooks.
CSV mode redraws figures without redistributing source workbooks.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys

_local_plot_dependencies = Path(__file__).resolve().parent/'.plot_deps'
if _local_plot_dependencies.is_dir():
    sys.path.insert(0,str(_local_plot_dependencies))
_plot_config = Path(__file__).resolve().parent/'tmp'/'matplotlib_config'
_plot_config.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(_plot_config))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter
import openpyxl

ROOT = Path(__file__).resolve().parent
Z = 1.959963984540054
BLUE = '#005A8D'
INK = '#222222'
GREY = '#555555'
WIDTH = 174/25.4
FIELDS = ['cohort','figure','panel','analysis','series','label','estimate','ci_lower','ci_upper',
          'unit','n_total','n_dys','n_no_dys','events','denominator','drgs','dys_coverage',
          'source_file','source_key','ci_method']


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(events,n):
    p=events/n; d=1+Z*Z/n
    centre=(p+Z*Z/(2*n))/d
    half=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/d
    return centre-half,centre+half


def row(**values):
    return {k:values.get(k,'') for k in FIELDS}


def audit_fees(cohort,analysis,raw_dir):
    observed={};sources={}
    for group in ['all','dys']:
        path=raw_dir/f'{cohort}_{group}_2025.xlsx'
        actual_sha=sha(path)
        if actual_sha != analysis['sources'][group]['sha256']:
            raise ValueError('Original workbook hash differs: '+path.name)
        wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
        try:
            n=wb['Info']['B8'].value
            matches=[r for r in wb['Prozeduren'].values if str(r[0])=='1-613']
        finally:
            wb.close()
        if len(matches)!=1:
            raise ValueError('Expected one exact OPS 1-613 case row')
        record=matches[0]; count=record[2]
        if not float(n).is_integer() or not float(count).is_integer():
            raise ValueError('Non-integer source case count')
        n,count=int(n),int(count)
        if n != analysis['n_'+group] or count != analysis['single_code_outcomes']['1-613'][group+'_events']:
            raise ValueError('FEES Excel/analysis discrepancy')
        if not math.isclose(record[4],count/n,rel_tol=1e-12):
            raise ValueError('FEES percentage does not use case denominator')
        observed[group]={'events':count,'denominator':n,'rate':count/n,'wilson_95_ci':wilson(count,n)}
        sources[group]={'file':path.name,'sha256':actual_sha,'sheet':'Prozeduren','exact_code':'1-613',
                        'count_column':'Fälle','case_denominator_cell':'Info!B8'}
    observed['no_dys']={'events':observed['all']['events']-observed['dys']['events'],
                        'denominator':observed['all']['denominator']-observed['dys']['denominator']}
    q=observed['no_dys'];q['rate']=q['events']/q['denominator'];q['wilson_95_ci']=wilson(q['events'],q['denominator'])
    fees=analysis['single_code_outcomes']['1-613']
    if q['events'] != fees['no_dys_events'] or q['denominator'] != fees['no_dys_n']:
        raise ValueError('Complement FEES count mismatch')
    for group in ['dys','no_dys']:
        if not all(math.isclose(a,b,rel_tol=1e-12) for a,b in zip(observed[group]['wilson_95_ci'],fees[group+'_rate_ci'])):
            raise ValueError('Wilson interval differs from validated analysis')
    return {'status':'PASS','code':'1-613','measure':'Hospital episodes with at least one coded FEES, not procedure mentions',
            'sources':sources,'groups':observed,
            'interpretation':'Recorded FEES frequency does not establish clinical need, unmet need, underuse, undercoding, or the frequency of all instrumental swallowing assessments including VFSS.'}


def source_rows(cohort,results_dir,raw_dir):
    base_path=results_dir/f'{cohort}_reanalysis.json'
    base=read_json(base_path)
    two_path=results_dir/f'{cohort}_joint_twofactor.json'
    three_path=results_dir/f'{cohort}_joint_standardization.json'
    two,three=read_json(two_path),read_json(three_path)
    fees=audit_fees(cohort,base,raw_dir)
    rows=[]
    models=[('age_sex','Age + sex',two['analyses']['age_sex'],two_path),
            ('age_sex_principal_diagnosis','Age + principal diagnosis\n+ sex',three['age_sex_principal_diagnosis'],three_path),
            ('age_pccl','Age + PCCL',two['analyses']['age_pccl'],two_path),
            ('age_principal_diagnosis_pccl_sensitivity','Age + principal diagnosis\n+ PCCL',three['age_principal_diagnosis_pccl_sensitivity'],three_path)]
    for name,label,result,path in models:
        counts=result['common_support']
        for series,key in [('matched_crude','crude_same_common_support_population'),('standardized','standardized')]:
            est=result[key]
            rows.append(row(cohort=cohort,figure=1,panel='',analysis=name,series=series,label=label,
                            estimate=est['rr'],ci_lower=est['rr_ci'][0],ci_upper=est['rr_ci'][1],unit='risk ratio',
                            n_total=counts['all_n'],n_dys=counts['dys_n'],n_no_dys=counts['no_dys_n'],
                            source_file=path.name,source_key=('analyses/' if path==two_path else '')+name+'/'+key,
                            ci_method='log risk-ratio binomial approximation' if series=='matched_crude' else 'fixed pooled weights; independent-binomial log-RR delta'))
    los=base['los']
    rows.append(row(cohort=cohort,figure=2,panel='a',analysis='los_crude',series='mean_difference',
                    label='Unstratified',estimate=los['mean_difference'],ci_lower=los['mean_difference_ci'][0],
                    ci_upper=los['mean_difference_ci'][1],unit='days',n_total=base['n_all'],n_dys=base['n_dys'],n_no_dys=base['n_no_dys'],
                    source_file=base_path.name,source_key='los/mean_difference',ci_method='independent-episode normal approximation'))
    drg=base['drg_standardization']['analyses']
    selections=['all_comparable'] if cohort=='acute' else ['all_comparable','variance_estimable']
    for name in selections:
        a=drg[name];ci=a['model_ci']
        rows.append(row(cohort=cohort,figure=2,panel='a',analysis='los_drg_'+name,series='mean_difference',
                        label='Within DRG' if name=='all_comparable' else 'Within DRG\n(variance estimable)',
                        estimate=a['mean_difference'],ci_lower=ci[0] if ci else '',ci_upper=ci[1] if ci else '',unit='days',
                        n_dys=a['dys_covered'],drgs=a['drgs'],dys_coverage=a['dys_coverage'],
                        source_file=base_path.name,source_key='drg_standardization/analyses/'+name,
                        ci_method='conditional observed dysphagia DRG weights' if ci else 'not estimable; no CI drawn'))
    for group,label in [('all','All episodes'),('dys','Coded dysphagia'),('no_dys','No coded dysphagia')]:
        a=fees['groups'][group]
        rows.append(row(cohort=cohort,figure=2,panel='b',analysis='fees',series=group,label=label,
                        estimate=100*a['rate'],ci_lower=100*a['wilson_95_ci'][0],ci_upper=100*a['wilson_95_ci'][1],unit='percent',
                        events=a['events'],denominator=a['denominator'],n_total=a['denominator'],
                        source_file=base_path.name,source_key='single_code_outcomes/1-613',ci_method='Wilson 95% interval'))
    sources={p.name:sha(p) for p in [base_path,two_path,three_path]}
    return rows,fees,sources


def configure():
    font_path=font_manager.findfont('Arial',fallback_to_default=False)
    plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.labelsize':9,'xtick.labelsize':8,
                         'ytick.labelsize':9,'axes.linewidth':.7,'lines.linewidth':1.1,
                         'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
                         'savefig.facecolor':'white','figure.facecolor':'white'})
    return font_path


def clean_axis(ax):
    for name in ['top','left','right']:
        ax.spines[name].set_visible(False)
    ax.tick_params(axis='y',length=0,labelleft=False)
    ax.tick_params(axis='x',width=.7,length=3,color=INK)
    ax.spines['bottom'].set_color(INK)


def point(ax,value,lo,hi,y,color,marker,filled=True):
    if lo!='' and hi!='':
        ax.errorbar(value,y,xerr=[[value-lo],[hi-value]],fmt='none',ecolor=color,capsize=2,elinewidth=1.1,capthick=1.0)
    ax.plot(value,y,marker=marker,markersize=5.2,markerfacecolor=color if filled else 'white',
            markeredgecolor=color,markeredgewidth=1.1,linestyle='none')


def export(fig,cohort,number,out):
    folder=out/cohort;folder.mkdir(parents=True,exist_ok=True)
    stem=folder/f'Fig{number}'
    for extension in ['png','tiff','pdf','eps','svg']:
        options={'dpi':600}
        if extension=='tiff':options['pil_kwargs']={'compression':'tiff_lzw'}
        if extension=='pdf':options['metadata']={'CreationDate':None,'ModDate':None,'Creator':'Matplotlib '+matplotlib.__version__}
        fig.savefig(stem.with_suffix('.'+extension),**options)
        if extension=='tiff':
            from PIL import Image
            with Image.open(stem.with_suffix('.tiff')) as source_image:
                rgb=source_image.convert('RGB')
            rgb.save(stem.with_suffix('.tiff'),compression='tiff_lzw',dpi=(600,600))
    # Stable descriptive filenames for Word insertion and local preview.
    import shutil
    for extension in ['png','pdf','svg']:
        shutil.copyfile(stem.with_suffix('.'+extension),out/f'{cohort}_figure{number}.{extension}')
    plt.close(fig)


def forest(cohort,rows,out):
    selected=[r for r in rows if r['figure']==1]
    names=list(dict.fromkeys(r['analysis'] for r in selected))
    fig=plt.figure(figsize=(WIDTH,116/25.4))
    grid=fig.add_gridspec(1,3,left=.025,right=.99,bottom=.14,top=.86,width_ratios=[2.25,2.3,1.8],wspace=.035)
    labels,ax,values=[fig.add_subplot(grid[0,k]) for k in range(3)]
    for t in [labels,values]:t.set_xlim(0,1);t.set_ylim(-.7,6.7);t.axis('off')
    ax.set_ylim(-.7,6.7);ax.set_xscale('log')
    ax.set_xlim(.9,6.0 if cohort=='acute' else 3.1)
    ticks=[1,2,3,4,5] if cohort=='acute' else [1,1.5,2,2.5,3]
    ax.set_xticks(ticks);ax.xaxis.set_major_formatter(ScalarFormatter());ax.minorticks_off()
    ax.axvline(1,color=INK,linewidth=.8,linestyle=(0,(3,3)))
    clean_axis(ax);ax.set_xlabel('Risk ratio (log scale)',labelpad=7)
    labels.text(0,1.07,'Model / adult episodes',transform=labels.transAxes,fontsize=8.5,fontweight='bold')
    values.text(.03,1.07,'RR (95% CI)',transform=values.transAxes,fontsize=9,fontweight='bold')
    for i,name in enumerate(names):
        y=6-2*i
        pair=[r for r in selected if r['analysis']==name]
        label=pair[0]['label'];n=int(pair[0]['n_total'])
        labels.text(0,y+.18,label,va='center',fontsize=9,linespacing=1.1)
        labels.text(0,y-.52,f'N = {n:,}',va='center',fontsize=8,color=GREY)
        for r in pair:
            standard=r['series']=='standardized';dy=-.22 if standard else .22
            color=BLUE if standard else GREY
            point(ax,r['estimate'],r['ci_lower'],r['ci_upper'],y+dy,color,'o' if standard else 's',standard)
            values.text(.03,y+dy,f"{r['estimate']:.2f} ({r['ci_lower']:.2f}–{r['ci_upper']:.2f})",fontsize=8.5,va='center',color=color)
    handles=[Line2D([0],[0],marker='s',markerfacecolor='white',markeredgecolor=GREY,color=GREY,linestyle='none',markersize=5),
             Line2D([0],[0],marker='o',markerfacecolor=BLUE,markeredgecolor=BLUE,color=BLUE,linestyle='none',markersize=5)]
    fig.legend(handles,['Crude, same episodes','Standardized'],loc='upper center',bbox_to_anchor=(.55,1.0),
               ncol=2,frameon=False,fontsize=8.5,handletextpad=.5,columnspacing=1.5)
    export(fig,cohort,1,out)


def burden(cohort,rows,out):
    fig=plt.figure(figsize=(WIDTH,157/25.4))
    grids=[fig.add_gridspec(1,3,left=.025,right=.99,bottom=.57,top=.94,width_ratios=[2.25,2.2,1.9],wspace=.035),
           fig.add_gridspec(1,3,left=.025,right=.99,bottom=.12,top=.43,width_ratios=[2.25,2.2,1.9],wspace=.035)]
    fig.text(.025,.975,'a',fontweight='bold',fontsize=12)
    fig.text(.025,.475,'b',fontweight='bold',fontsize=12)
    for panel,grid in zip(['a','b'],grids):
        labels,ax,values=[fig.add_subplot(grid[0,k]) for k in range(3)]
        subset=[r for r in rows if r['figure']==2 and r['panel']==panel]
        for t in [labels,values]:t.set_xlim(0,1);t.set_ylim(-.65,len(subset)-.35);t.axis('off')
        ax.set_ylim(-.65,len(subset)-.35);clean_axis(ax)
        if panel=='a':
            ax.set_xlim(0,10 if cohort=='acute' else 18)
            ax.set_xticks([0,5,10] if cohort=='acute' else [0,5,10,15])
            ax.set_xlabel('Hospital-stay difference (days)',fontsize=9,labelpad=7)
            values.text(.02,1.03,'Difference (95% CI)',transform=values.transAxes,fontsize=8.5,fontweight='bold')
        else:
            ax.set_xlim(0,25 if cohort=='acute' else 45)
            ax.set_xticks([0,10,20] if cohort=='acute' else [0,20,40])
            ax.set_xlabel('Episodes with coded FEES (%)',fontsize=9,labelpad=7)
            values.text(.02,1.06,'Proportion; episodes',transform=values.transAxes,fontsize=8.5,fontweight='bold')
        for i,r in enumerate(subset):
            y=len(subset)-1-i
            if panel=='a':
                no_ci=r['ci_lower']==''
                color=INK if i==0 else BLUE
                point(ax,r['estimate'],r['ci_lower'],r['ci_upper'],y,color,'D' if no_ci else ('o' if i==0 else 's'),not no_ci)
                labels.text(0,y+.13,r['label'],va='center',fontsize=9,linespacing=1.05)
                detail=f"N = {int(r['n_total']):,}" if i==0 else f"{int(r['drgs'])} DRGs; {100*r['dys_coverage']:.1f}% of D"
                labels.text(0,y-.28,detail,va='center',fontsize=8,color=GREY)
                text=f"{r['estimate']:.2f} (CI unavailable)" if no_ci else f"{r['estimate']:.2f} ({r['ci_lower']:.2f}–{r['ci_upper']:.2f})"
                values.text(.02,y,text,va='center',fontsize=8.5,color=color)
            else:
                color=BLUE if r['series']=='dys' else INK
                marker={'all':'D','dys':'s','no_dys':'^'}[r['series']]
                point(ax,r['estimate'],r['ci_lower'],r['ci_upper'],y,color,marker,r['series']!='no_dys')
                labels.text(0,y,r['label'],va='center',fontsize=9)
                values.text(.02,y+.10,f"{r['estimate']:.2f}%",va='center',fontsize=9,color=color)
                values.text(.02,y-.22,f"{int(r['events']):,}/{int(r['denominator']):,}",va='center',fontsize=8,color=GREY)
    export(fig,cohort,2,out)


def legend(cohort):
    cohort_label='OPS-defined acute stroke-care' if cohort=='acute' else 'neurological early-rehabilitation'
    precision_caution=('In the age–diagnosis–PCCL model, boundary-risk strata contribute zero plug-in variance and may make intervals too optimistic; see Online Resource 1, Table S3' if cohort=='acute' else
                       'Approximate intervals do not account for hospital clustering, repeated admissions or coding uncertainty')
    los_extra=('The within-DRG estimate includes 171 comparable DRGs and 98.3% of coded-dysphagia episodes' if cohort=='acute' else
               'The main within-DRG estimate includes 93 comparable DRGs and 99.2% of coded-dysphagia episodes; its confidence interval is unavailable because seven comparator strata have only one episode. The separate variance-estimable sensitivity includes 86 DRGs and 99.0% of coded-dysphagia episodes. The open diamond denotes the estimate without a confidence interval')
    return (f'**Fig. 1** Mortality associations under separate simultaneous standardizations in the {cohort_label} cohort\n\n'
            'Adults aged 18 years or older. Filled circles show directly standardized risk ratios comparing episodes with a secondary R13.0, R13.1 or R13.9 code with episodes without these codes. Open squares show the crude risk ratio recalculated on exactly the same common-support population as its paired standardized estimate; the displayed N is the total number of retained episodes. Whiskers are approximate 95% confidence intervals. Each model uses fixed pooled weights within its retained strata. Age comprises 18–74 and 75+ years; principal diagnosis comprises I63, I61 and all other principal diagnoses. Models containing sex and models containing PCCL are separate; no simultaneous sex-by-PCCL adjustment is implied. PCCL models are descriptive sensitivities and do not establish adjustment for baseline neurological severity. Different models can retain different episodes and reference distributions; differences between their estimates are not causal effects or causal mediation estimates. '+precision_caution+'\n\n'
            f'**Fig. 2** Hospital stay and coded FEES in the {cohort_label} cohort\n\n'
            f'(a) Mean difference in whole-hospital length of stay, coded dysphagia minus no coded dysphagia, in all-age episodes. Unstratified and within-DRG estimates are shown on the same days scale, with approximate 95% confidence intervals where estimable. Within-DRG estimates use the observed dysphagia-group DRG distribution as weights; the percentage of dysphagia episodes covered is shown. {los_extra}. These are descriptive case-mix comparisons, not causal attributable hospital days. '
            '(b) Percentage of all-age episodes with at least one recorded FEES procedure (OPS 1-613), shown for the full cohort and its two dysphagia-code subgroups. Numerators count episodes, not repeated procedure mentions; whiskers are 95% Wilson intervals, which can be narrower than the plotting symbols. The full-cohort point includes both subgroups and is not an independent comparator. Recorded FEES frequency does not measure clinical need, unmet need, coding completeness or all instrumental swallowing examinations, including videofluoroscopy. D, coded dysphagia; DRG, diagnosis-related group; FEES, flexible endoscopic evaluation of swallowing; PCCL, patient clinical complexity level\n')


def write_csv(rows,path):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)


def load_plot_csv(path):
    numeric=set(FIELDS)-{'cohort','panel','analysis','series','label','unit','source_file','source_key','ci_method'}
    with path.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    for r in rows:
        for key in numeric:
            if r[key]!='':r[key]=float(r[key])
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort',choices=['acute','rehab','both'],default='both')
    p.add_argument('--results-dir',type=Path,default=ROOT/'results')
    p.add_argument('--raw-dir',type=Path,default=ROOT/'raw')
    p.add_argument('--out-dir',type=Path,default=ROOT/'figures'/'nrp')
    p.add_argument('--plot-data',type=Path,help='Redraw exclusively from a previously audited aggregate CSV')
    a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    font=configure();all_rows=[];audits={};sources={}
    cohorts=['acute','rehab'] if a.cohort=='both' else [a.cohort]
    if a.plot_data:all_rows=load_plot_csv(a.plot_data)
    for cohort in cohorts:
        if a.plot_data:rows=[r for r in all_rows if r['cohort']==cohort]
        else:
            rows,audits[cohort],sources[cohort]=source_rows(cohort,a.results_dir,a.raw_dir);all_rows.extend(rows)
        if len([r for r in rows if r['figure']==1])!=8 or len([r for r in rows if r['panel']=='b'])!=3:
            raise ValueError('Incomplete figure data: '+cohort)
        forest(cohort,rows,a.out_dir);burden(cohort,rows,a.out_dir)
        write_csv(rows,a.out_dir/f'{cohort}_plotted_data.csv')
        (a.out_dir/f'{cohort}_figure_legends.md').write_text(legend(cohort),encoding='utf-8')
    write_csv(all_rows,a.out_dir/'plotted_data.csv')
    report={'status':'created_pending_visual_QA','software':{'python':platform.python_version(),'matplotlib':matplotlib.__version__},
            'font':{'family':'Arial','resolved_font_file':font,'minimum_point_size':8},
            'dimensions_mm':{'figure1':[174,116],'figure2':[174,157]},
            'formats':['EPS with embedded TrueType fonts','RGB TIFF 600 dpi','PNG 600 dpi','PDF vector','SVG vector'],
            'data_source_hashes':sources,'fees_workbook_audits':audits,
            'plot_data_sha256':sha(a.out_dir/'plotted_data.csv'),
            'interpretation':'No NIHSS-independent or causal dysphagia effect is shown. Figure 1 adults; Figure 2 all-age episodes. FEES is coded frequency, not unmet need.'}
    (a.out_dir/'figure_build_manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'cohorts':cohorts,'figures':2*len(cohorts),'data_rows':len(all_rows),'out_dir':str(a.out_dir)}))


if __name__=='__main__':main()
