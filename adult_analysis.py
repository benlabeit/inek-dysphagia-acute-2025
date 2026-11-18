"""Adult acute-stroke-care cohort. Read independently obtained InEK workbooks locally."""
import argparse
import csv
import json
import math
import tempfile
from itertools import product
from pathlib import Path
import openpyxl
from outcomes_analyze_joint import build_cells, derive_pneumonia_complement
from outcomes_analyze_los_age_diagnosis import Moments, read_source, run as analyze_stay, summarize, sum_moments
from outcomes_standardization_core import QUERY_AGES, contrast, standardize
from outcomes_within_drg import (PROCEDURES, source, filename, observed, eligible, residual_cells,
                                code_margins, margin_block, bounds_row, write_table)

HERE = Path(__file__).resolve().parent
AGES = list(QUERY_AGES)
HDS = ['allhd','i63','i61']
POPS = ['all','dys']
def read_csv(name):
    with (HERE/name).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
def bundle(cells):
    r=standardize(cells)
    s=r['standardized']; c=r['crude_same_common_support_population']
    return dict(dys_n=c['dys_n'],comparator_n=c['no_dys_n'],dys_events=c['dys_events'],comparator_events=c['no_dys_events'],
                dys_risk=s['dys_rate'],comparator_risk=s['no_dys_rate'],rr=s['rr'],rr_low=s['rr_ci'][0],rr_high=s['rr_ci'][1],
                rd=s['risk_difference'],rd_low=s['risk_difference_ci'][0],rd_high=s['risk_difference_ci'][1],
                strata=r['common_support']['included_cells'],matched_crude_rr=c['rr'])
def event(raw,age,hd,pop,key):
    record=source(raw,age,hd,pop,key)
    if record:
        info=record[1]
        if 'distributions' not in info:
            return derive_pneumonia_complement(raw,age,pop)
        return info
    tab='Prozeduren' if key in PROCEDURES else 'Nebendiagnosen'
    n=code_margins(raw,age,hd,pop,tab).get(key)
    return {'n':n} if n is not None else None

def compare_drg(vals):
    return bundle([dict(all_n=d+c,dys_n=d,all_events=a+b,dys_events=a) for d,c,a,b in vals])

def binary(raw,out):
    summaries=read_csv('outcomes_harmonized_binary_summary.csv')
    endpoints={r['outcome']:r['label'] for r in summaries}
    grid=list(product(AGES,HDS,POPS))
    den={k:source(raw,*k,None)[1] for k in grid}
    rows=[]; limits=[]
    def add(model, result=None, note=''):
        rows.append(dict(outcome=key,label=label,model=model,status='estimated' if result else 'unavailable',
                         note=note,**(result or {})))
    for key,label in endpoints.items():
        ev={k:event(raw,*k,key) for k in grid}
        ages=[]
        for a in AGES:
            ages.append(dict(all_n=den[a,'allhd','all']['n'],dys_n=den[a,'allhd','dys']['n'],
                             all_events=ev[a,'allhd','all']['n'],dys_events=ev[a,'allhd','dys']['n']))
        add('M1',bundle([{k:sum(g[k] for g in ages) for k in ages[0]}]))
        add('age',bundle(ages))
        for model,dim in [('age_hd','total'),('M2','sex'),('M3','pccl')]:
            if all(v is not None and (dim=='total' or 'distributions' in v) for v in ev.values()):
                add(model,bundle(build_cells(den,ev,dim)))
            elif key=='E43' and model in ('M2','M3'):
                typ={'M2':'age_sex_principal_diagnosis','M3':'age_principal_diagnosis_pccl_sensitivity'}[model]
                r=next(r for r in summaries if r['outcome']==key and r['analysis']==typ)
                fields={'dys_n':'dys_n','comparator_n':'no_dys_n','dys_risk':'dys_rate','comparator_risk':'no_dys_rate',
                        'rr':'rr','rr_low':'rr_ci_lower','rr_high':'rr_ci_upper','rd':'risk_difference',
                        'rd_low':'risk_difference_ci_lower','rd_high':'risk_difference_ci_upper','strata':'included_strata',
                        'matched_crude_rr':'crude_rr_same_supported_adult_population'}
                add(model,{k:float(r[v]) if r[v] else None for k,v in fields.items()},'Previously validated adult aggregate; original event workbooks unavailable in this release.')
            else:
                add(model,note='Incomplete event strata for the requested factors.')
        add('M4',note='Sex within age and DRG is unavailable in the source extracts.')
        age_cells={}; joint={}
        for age in AGES:
            by_hd={h:observed(raw,age,h,key) for h in HDS}
            age_cells.update({(age,k):v for k,v in eligible(by_hd['allhd']).items()})
            by_hd['other']=residual_cells(by_hd['allhd'],by_hd['i63'],by_hd['i61'])
            for h in ('i63','i61','other'):
                joint.update({(age,h,k):v for k,v in eligible(by_hd[h]).items()})
        for model, cells in [('age_drg',age_cells),('age_hd_drg',joint)]:
            add(model,compare_drg(cells.values()) if cells else None,'Named, jointly observable DRGs only; pooled weights.')
        if not age_cells:
            # Historical identification bounds use dysphagia-coded weights, explicitly separate from pooled point estimates.
            result=bounds_row(key,'age_drg_dys_weights',[margin_block(raw,a,'allhd',key) for a in AGES])
            if result: limits.append(result)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'adult_binary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    if limits: write_table(out/'adult_drg_bounds.csv',limits)
    return den

def drg_moments(raw,age,pop):
    path=raw/filename(age,'allhd',pop,None)
    overall=read_source(path,age,'allhd',pop)[0]
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    try:
        rows=iter(w['DRG-Verteilung'].values)
        assert next(rows)==('DRG','Bezeichnung','Fälle','Prozent','Mitt.VWD','Stdabw.VWD')
        moments={}; residual_n=0
        for code,_,n,__,mean,sd in rows:
            if n is None: continue
            if code=='---':
                residual_n=int(n)
                continue
            s=n*mean; q=n*(mean**2+sd**2)
            if max(abs(s-round(s)),abs(q-round(q)))>1e-4: raise ValueError(f'LOS moment reconstruction: {path.name}, {code}')
            m=Moments(int(n),round(s),round(q)).validate()
            moments[code]=m
        total=sum_moments(moments.values())
        remainder=overall-total
        if remainder.n!=residual_n: raise ValueError(f'DRG counts do not partition cohort: {path.name}')
        return moments
    finally: w.close()

def los(raw,out):
    with tempfile.TemporaryDirectory() as t:
        analyze_stay(raw,Path(t))
        source_data=json.loads((Path(t)/'los_age_diagnosis_results.json').read_text())
    rows=[]
    def add(name,r,crude=False):
        x=r['crude_same_population'] if crude else r['standardized']
        ci=x['ci95'] or [None,None]
        rows.append(dict(model=name,dys_n=r['common_support']['dys_n'],comparator_n=r['common_support']['no_dys_n'],
                         strata=1 if crude else r['common_support']['included_strata'],
                         dys_mean=x['dys']['mean_days'] if crude else x['dys_mean_days'],
                         comparator_mean=x['no_dys']['mean_days'] if crude else x['no_dys_mean_days'],
                         difference=x['mean_difference_days'],ci_low=ci[0],ci_high=ci[1],
                         matched_crude_difference=r['crude_same_population']['mean_difference_days']))
    add('M1',source_data['primary'],True); add('age_hd',source_data['primary'])
    add('age_hd_survivors',source_data['survivor_sensitivity'])
    groups=[]
    for a in AGES:
        t,d=(drg_moments(raw,a,p) for p in POPS)
        for drg in sorted(t.keys() & d.keys()):
            c=t[drg]-d[drg]
            if min(d[drg].n,c.n)>0:
                groups.append(dict(age=a,hd=drg,total=t[drg],dys=d[drg]))
    add('age_drg',summarize(groups,'age_drg'))
    if any(min(g['dys'].n,(g['total']-g['dys']).n)<2 for g in groups):
        add('age_drg_n2',summarize([g for g in groups if min(g['dys'].n,(g['total']-g['dys']).n)>=2],'age_drg_n2'))
    write_table(out/'adult_los.csv',rows)

def cohort(raw,out,den):
    info=[]
    for p in POPS:
        bands=[den[a,'allhd',p] for a in AGES]
        vals={'All':sum(b['n'] for b in bands),'18–74 years':bands[0]['n'],'≥75 years':bands[1]['n']}
        for s in ('männlich','weiblich'):
            vals[s]=sum(b['distributions']['sex'][s] for b in bands)
        for h in ('i63','i61'): vals[h]=sum(den[a,h,p]['n'] for a in AGES)
        vals['8-836.80']=sum(code_margins(raw,a,'allhd',p,'Prozeduren')['8-836.80'] for a in AGES)
        info.append(vals)
    write_table(out/'adult_cohort.csv',[dict(characteristic=k,dys_n=info[1][k],comparator_n=v-info[1][k]) for k,v in info[0].items()])

def functional(raw,out):
    from outcomes_standardization_core import MINOR_AGES
    baseline=read_csv('functional_sensitivity.csv')
    codes={r['code']:(r['instrument'],r['score_band']) for r in baseline}
    result=[]
    for endpoint in ('mortality','PNEUMONIA_UNION'):
        parts=[]
        for pop in POPS:
            info=source(raw,'allages','allhd',pop,endpoint)[1]
            if any(info['distributions']['age'][a] for a in MINOR_AGES):
                raise ValueError('All-age event workbook contains pediatric episodes')
            with open((raw/filename('allages','allhd',pop,endpoint)),'rb') as f:
                w=openpyxl.load_workbook(f,read_only=True,data_only=True)
                rows=iter(w['Nebendiagnosen'].values)
                assert next(rows)[2]=='Fälle'
                margins={r[0]:int(r[2]) for r in rows if r[0] in codes}
                w.close()
            parts.append(margins)
        for code,(instrument,band) in codes.items():
            row=dict(outcome=endpoint,code=code,instrument=instrument,band=band,status='source row unavailable',
                     dys_n=None,comparator_n=None,rr=None,rr_low=None,rr_high=None)
            counts=[code_margins(raw,a,'allhd',p,'Nebendiagnosen').get(code) for p in POPS for a in AGES]
            if all(v is not None for v in counts) and all(code in m for m in parts):
                n,d=sum(counts[:2]),sum(counts[2:])
                a,b=parts[1][code],parts[0][code]-parts[1][code]
                if min(a,b,d-a,n-d-b)>=5:
                    x=contrast(a,d,b,n-d)
                    row.update(status='estimated',dys_n=d,comparator_n=n-d,rr=x['rr'],rr_low=x['rr_ci'][0],rr_high=x['rr_ci'][1])
                else: row['status']='small cell'
            result.append(row)
    write_table(out/'adult_functional.csv',result)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--raw',required=True,type=Path);ap.add_argument('--out',type=Path,default=HERE)
    args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    den=binary(args.raw,args.out);cohort(args.raw,args.out,den);los(args.raw,args.out);functional(args.raw,args.out)
