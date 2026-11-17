"""Independent E43 joint standardization QA from the 24 original XLSX files.

No imports from the production joint pipeline. Detailed output is private audit.
"""
from pathlib import Path
from decimal import Decimal, getcontext
import hashlib
import argparse
import csv
import json
import re
import openpyxl

getcontext().prec = 60
D=Decimal
Z=D('1.959963984540054')
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data-root',type=Path,required=True,help='Directory of separately obtained native workbooks')
parser.add_argument('--aggregate-csv',type=Path,default=ROOT/'outcomes_severe_malnutrition_joint_aggregate.csv')
parser.add_argument('--previous-binary-audit',type=Path,help='Optional private earlier single-code QA JSON for six additional regression checks')
parser.add_argument('--summary-output',type=Path,help='Optional model-level validation summary; no source hashes or strata')
parser.add_argument('--private-audit',type=Path,help='Optional detailed local audit; keep this file private')
args=parser.parse_args()
RAW=args.data_root
AGES=['age18_74','age75plus']
HDS=['allhd','i63','i61']
OPS={f'{p}.{s}' for p in ['8-981','8-98b'] for s in ['20','21','22','23','30','31','32','33']}
CHECKS=[]

def check(label,truth):
    CHECKS.append({'check':label,'passed':bool(truth)})
    if not truth: raise AssertionError(label)

def compare(label,a,b):
    check(label,abs(D(str(a))-D(str(b)))<D('1e-10'))

def integer(v,label):
    check(label+': numeric and observed',isinstance(v,(float,int)))
    x=D(str(v)); n=int(x.to_integral())
    check(label+': nonnegative exact integer',n>=0 and abs(x-n)<D('1e-8'))
    return n

def read_file(age,hd,pop,event):
    name=(f'acute_outcome_severe_malnutrition_{age}_{hd}_{pop}_2025.xlsx' if event else f'acute_joint_{age}_{hd}_{pop}_2025.xlsx')
    path=RAW/name
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    s=w['Info']; query=s['A2'].value
    selections={}
    for segment in query.split(';'):
        if not segment.strip():continue
        m=re.fullmatch(r'([^()]+)\(([^()]*)\)',segment.strip())
        check(name+': parse query',m is not None)
        key=m.group(1).strip()
        check(name+': query key unique '+key,key not in selections)
        selections[key]=set(x.strip() for x in m.group(2).split(',') if x.strip())
    check(name+': exact OPS',selections['Prozeduren']==OPS)
    check(name+': exact exposure',selections.get('Nebendiagnosen',set())==({'R13.0','R13.1','R13.9'} if pop=='dys' else set()))
    check(name+': exact additional diagnosis',selections.get('weitere Nebendiagnosen',set())==({'E43'} if event else set()))
    hd_expected={f'{hd.upper()}.{i}' for i in ['0','1','2','3','4','5','6','8','9']} if hd!='allhd' else set()
    check(name+': exact HD',selections.get('Hauptdiagnose',set())==hd_expected)
    age_expected={'18-29 Jahre','30-39 Jahre','40-49 Jahre','50-54 Jahre','55-59 Jahre','60-64 Jahre','65-74 Jahre'} if age=='age18_74' else {'75-79 Jahre','80+ Jahre'}
    check(name+': exact age',selections['Altersgruppe']==age_expected)
    allowed={'Prozeduren','Nebendiagnosen','weitere Nebendiagnosen','Hauptdiagnose','Altersgruppe','Entlassungsgrund'}
    check(name+': no unwanted filter',not(set(selections)-allowed) and not selections.get('Entlassungsgrund'))
    check(name+': same exact 2025 delivery',s['A5'].value=='Unterj\u00e4hrige Datenlieferung DRG Januar bis Dezember 2025')
    n=integer(s['B8'].value,name+': total N')
    result={'n':n,'sex':{},'pccl':{},'age':{},'name':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    for model,rows,keycol,valcol in [('sex',range(11,15),'A','B'),('pccl',range(8,15),'G','H'),('age',range(8,24),'J','K')]:
        for r in rows:
            key=str(s[f'{keycol}{r}'].value)
            prop=s[f'{valcol}{r}'].value
            check(f'{name}:{model}/{key}: observed proportion',isinstance(prop,(int,float)) and 0<=prop<=1)
            value=D(str(prop))*n
            count=int(value.to_integral())
            check(f'{name}:{model}/{key}: integer reconstruction',abs(value-count)<D('1e-8'))
            check(f'{name}:{model}/{key}: unique category',key not in result[model])
            result[model][key]=count
        check(name+': '+model+' exhaustive',sum(result[model].values())==n)
    check(name+': ages obey filter',all(value==0 or key in age_expected for key,value in result['age'].items()))
    if not event:
        e43=[row[2] for row in w['Nebendiagnosen'].iter_rows(min_row=2,values_only=True) if row[0]=='E43']
        check(name+': E43 exact row observed',len(e43)==1)
        result['table_e43_n']=integer(e43[0],name+': E43 row N')
    w.close()
    return result

src={(a,h,p,e):read_file(a,h,p,e) for a in AGES for h in HDS for p in ['all','dys'] for e in [False,True]}
for a in AGES:
    for h in HDS:
        for p in ['all','dys']:
            den=src[a,h,p,False]; ev=src[a,h,p,True]
            check(f'{a}/{h}/{p}: new query matches previous E43',ev['n']==den['table_e43_n'])
            for mode in ['sex','pccl']:
                check(f'{a}/{h}/{p}/{mode}: matching categories',set(den[mode])==set(ev[mode]))
                check(f'{a}/{h}/{p}/{mode}: raw event nesting',all(ev[mode][k]<=den[mode][k] for k in den[mode]))

def value(a,h,p,e,mode,key):
    if h=='otherhd':return value(a,'allhd',p,e,mode,key)-value(a,'i63',p,e,mode,key)-value(a,'i61',p,e,mode,key)
    s=src[a,h,p,e]
    return s['n'] if mode=='total' else s[mode][key]

def estimate(cells):
    total=sum(c['all_n'] for c in cells)
    risk=[]; variance=[]
    for p in ['dys','no_dys']:
        ps=[D(c[p+'_events'])/c[p+'_n'] for c in cells]
        ws=[D(c['all_n'])/total for c in cells]
        risk.append(sum(w*prop for w,prop in zip(ws,ps)))
        variance.append(sum(w*w*prop*(1-prop)/c[p+'_n'] for c,w,prop in zip(cells,ws,ps)))
    rr=risk[0]/risk[1]; rd=risk[0]-risk[1]
    logse=(variance[0]/risk[0]**2+variance[1]/risk[1]**2).sqrt(); rdse=sum(variance).sqrt()
    crude=(D(sum(c['dys_events'] for c in cells))/sum(c['dys_n'] for c in cells))/(D(sum(c['no_dys_events'] for c in cells))/sum(c['no_dys_n'] for c in cells))
    return {'dys_standardized_risk':risk[0],'no_dys_standardized_risk':risk[1],
            'rr':rr,'rr_ci_lower':(rr.ln()-Z*logse).exp(),'rr_ci_upper':(rr.ln()+Z*logse).exp(),
            'risk_difference':rd,'risk_difference_ci_lower':rd-Z*rdse,'risk_difference_ci_upper':rd+Z*rdse,
            'crude_rr_same_population':crude}

with args.aggregate_csv.open(encoding='utf-8-sig',newline='') as stream:
    main=list(csv.DictReader(stream))
models={}
for mode,name in [('total','age_principal_diagnosis'),('sex','age_sex_principal_diagnosis'),('pccl','age_principal_diagnosis_pccl_sensitivity')]:
    keys=['total'] if mode=='total' else list(src[AGES[0],'allhd','all',False][mode])
    included=[];excluded=[]
    for age in AGES:
        for hd in ['i63','i61','otherhd']:
            for key in keys:
                c={'age':age,'hd':hd,'factor':key}
                for p in ['all','dys']:
                    c[p+'_n']=value(age,hd,p,False,mode,key)
                    c[p+'_events']=value(age,hd,p,True,mode,key)
                c['no_dys_n']=c['all_n']-c['dys_n']; c['no_dys_events']=c['all_events']-c['dys_events']
                for p in ['all','dys','no_dys']:
                    check(f'{name}/{age}/{hd}/{key}/{p}: nonnegative disjoint valid cell',0<=c[p+'_events']<=c[p+'_n'])
                if c['dys_n']>0 and c['no_dys_n']>0:
                    c['sparse']=min(c['dys_events'],c['dys_n']-c['dys_events'],c['no_dys_events'],c['no_dys_n']-c['no_dys_events'])<5
                    c['boundary']=any(c[p+'_events'] in (0,c[p+'_n']) for p in ['dys','no_dys'])
                    included.append(c)
                else:excluded.append(c)
    totals={k:sum(c[k] for c in included) for k in ['all_n','dys_n','no_dys_n','all_events','dys_events','no_dys_events']}
    result=estimate(included)
    for kind in ['sparse','boundary']:
        result[kind+'_strata']=sum(c[kind] for c in included)
        result[kind+'_reference_weight']=D(sum(c['all_n'] for c in included if c[kind]))/totals['all_n']
    result.update({k:totals[k] for k in ['all_n','dys_n','no_dys_n']})
    result.update(included_cells=len(included),excluded_cells=len(excluded))
    target=next(r for r in main if r['analysis']==name)
    for k,v in result.items():
        if k in target:compare(name+': '+k,v,target[k])
    if mode=='total' and args.previous_binary_audit is not None:
        old=json.loads(args.previous_binary_audit.read_text(encoding='utf-8'))['outcomes']['E43']['standardized']
        for k1,k2 in [('rr','rr'),('risk_difference','risk_difference'),('dys_standardized_risk','dys_rate'),('no_dys_standardized_risk','no_dys_rate')]:compare('original single-code match '+k1,result[k1],old[k2])
        compare('original single-code match RRlower',result['rr_ci_lower'],old['rr_ci95'][0]);compare('original single-code match RRupper',result['rr_ci_upper'],old['rr_ci95'][1])
    models[name]={'estimates':result,'event_totals':totals,'included_private':included,'excluded_private':excluded}
    if mode=='pccl':
        # Influence checks only: excluding outcome-defined cells changes target.
        diagnostics={}
        for condition in ['boundary','sparse']:
            subset=[c for c in included if not c[condition]]
            diagnostics['excluding_'+condition]={'n':sum(c['all_n'] for c in subset),'strata':len(subset),'estimates':estimate(subset)}
        models[name]['posthoc_influence_only']=diagnostics

# Prespecified only at QA stage after observing native sparsity: post hoc
# coarsening sensitivity, not a replacement or claim of calibrated coverage.
native=models['age_principal_diagnosis_pccl_sensitivity']
all_native=native['included_private']+native['excluded_private']
coarse=[]
for a in AGES:
    for h in ['i63','i61','otherhd']:
        for label,members in [('0',{'0'}),('1-2',{'1','2'}),('3-6',{'3','4','5','6'})]:
            cells=[c for c in all_native if c['age']==a and c['hd']==h and c['factor'] in members]
            check(f'coarse/{a}/{h}/{label}: exact native membership',len(cells)==len(members))
            c={'age':a,'hd':h,'factor':label}
            for key in ['all_n','dys_n','no_dys_n','all_events','dys_events','no_dys_events']:
                c[key]=sum(cell[key] for cell in cells)
            for p in ['all','dys','no_dys']:
                check(f'coarse/{a}/{h}/{label}/{p}: valid counts',0<=c[p+'_events']<=c[p+'_n'])
            c['sparse']=min(c['dys_events'],c['dys_n']-c['dys_events'],c['no_dys_events'],c['no_dys_n']-c['no_dys_events'])<5
            c['boundary']=any(c[p+'_events'] in (0,c[p+'_n']) for p in ['dys','no_dys'])
            coarse.append(c)
supported=[c for c in coarse if c['dys_n']>0 and c['no_dys_n']>0]
coarse_totals={key:sum(c[key] for c in supported) for key in ['all_n','dys_n','no_dys_n','all_events','dys_events','no_dys_events']}
check('coarse total N retained',coarse_totals['all_n']==279255)
check('coarse E43 retained',coarse_totals['dys_events']==216 and coarse_totals['no_dys_events']==318)
coarse_result=estimate(supported)
coarse_result.update({key:coarse_totals[key] for key in ['all_n','dys_n','no_dys_n']})
coarse_result.update(included_cells=len(supported),excluded_cells=len(coarse)-len(supported))
for kind in ['sparse','boundary']:
    coarse_result[kind+'_strata']=sum(c[kind] for c in supported)
    coarse_result[kind+'_reference_weight']=D(sum(c['all_n'] for c in supported if c[kind]))/coarse_totals['all_n']
target=next(r for r in main if r['analysis']=='age_principal_diagnosis_coarsened_pccl_posthoc')
for k,v in coarse_result.items():
    if k in target:compare('coarsened PCCL aggregate: '+k,v,target[k])
models['age_principal_diagnosis_coarsened_pccl_posthoc']={
    'estimates':coarse_result,'event_totals':coarse_totals,'strata_private':coarse,
    'definition':'PCCL 0 / 1-2 / 3-6, crossed with two age bands and three principal diagnosis groups.',
    'warning':'Post hoc QA sensitivity chosen after inspecting native PCCL sparsity. Uses common support after aggregating native PCCL categories. Coarsening leaves residual complexity differences and does not by itself establish interval calibration.'}

result={'status':'PASS','checks_passed':len(CHECKS),'checks':CHECKS,
        'source_hashes':{s['name']:s['sha256'] for s in src.values()},'models':models,
        'source_zero_handling':'All sex/PCCL percentages explicitly observed, including zeros; integer reconstruction and exhaustive sums verified; no absent/suppressed cells imputed.',
        'limitations':['E43 identifies unspecified severe protein-energy malnutrition, not a unique broad malnutrition union.',
                       'Three-factor models separately include sex or PCCL; they do not jointly control sex plus PCCL.',
                       'Approximate nominal fixed-weight binomial delta CIs. Sparse strata affect 11.86% of sex-model weights; PCCL has 52.85% sparse weights and 16.64% boundary weights.',
                       'At a boundary the plug-in binomial variance for the affected group is zero; PCCL interval calibration is not established.',
                       'PCCL can incorporate malnutrition/complications and is not baseline neurological severity; overadjustment or selection bias remains possible.',
                       'No admission NIHSS, onset ordering, hospital clustering, repeat-admission linkage or multiplicity correction.']}
if args.private_audit:
    args.private_audit.parent.mkdir(parents=True,exist_ok=True)
    args.private_audit.write_text(json.dumps(result,indent=2,default=lambda x:float(x) if isinstance(x,D) else str(x))+'\n',encoding='utf-8')
public_keys={'all_n','dys_n','no_dys_n','dys_standardized_risk','no_dys_standardized_risk','rr','rr_ci_lower','rr_ci_upper','risk_difference','risk_difference_ci_lower','risk_difference_ci_upper','crude_rr_same_population'}
summary={'status':'PASS','checks_passed':len(CHECKS),'models':{k:{f:v for f,v in model['estimates'].items() if f in public_keys} for k,model in models.items()},
    'notes':['Four model-level results recalculated independently using Decimal arithmetic. No source hashes or stratum tables in this summary.',
             'The coarsened PCCL model is a post hoc QA sensitivity; sparse/boundary strata remain and interval calibration is not established.',
             'The portable check count depends on whether the optional earlier single-code audit is supplied; it differs from the original development audit.']}
text=json.dumps(summary,indent=2,default=lambda x:float(x))+'\n'
if args.summary_output:
    args.summary_output.parent.mkdir(parents=True,exist_ok=True)
    args.summary_output.write_text(text,encoding='utf-8')
print(text)
