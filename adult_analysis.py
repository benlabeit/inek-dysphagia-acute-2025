"""Adult acute-stroke-care cohort. Read independently obtained InEK workbooks locally."""
import argparse
import csv
import json
import tempfile
from itertools import product
from pathlib import Path
import openpyxl
from adult_export_audit import audit
from outcomes_analyze_joint import build_cells, derive_pneumonia_complement
from outcomes_analyze_los_age_diagnosis import Moments, read_source, run as analyze_stay, summarize, sum_moments
from outcomes_standardization_core import QUERY_AGES, SEX_LABELS, read_info, contrast, standardize
from outcomes_within_drg import (PROCEDURES, source, filename, observed, eligible, residual_cells,
                                code_margins, write_table)

HERE = Path(__file__).resolve().parent
AGES = list(QUERY_AGES)
HDS = ['allhd','i63','i61']
POPS = ['all','dys']
def read_csv(name):
    with (HERE/name).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
def bundle(cells):
    result = standardize(cells)
    if result['status'] != 'estimated':
        return None
    s = result['standardized']
    c = result['crude_same_common_support_population']
    strata = result['strata']
    low, high = s['rr_ci'] or (None, None)
    return dict(dys_n=c['dys_n'], comparator_n=c['no_dys_n'],
                dys_events=c['dys_events'], comparator_events=c['no_dys_events'],
                dys_risk=s['dys_rate'], comparator_risk=s['no_dys_rate'],
                rr=s['rr'], rr_low=low, rr_high=high, rd=s['risk_difference'],
                rd_low=s['risk_difference_ci'][0], rd_high=s['risk_difference_ci'][1],
                strata=len(strata), matched_crude_rr=c['rr'],
                sparse_weight=sum(g['reference_weight'] for g in strata if g['sparse_event_cell']),
                boundary_weight=sum(g['reference_weight'] for g in strata if g['boundary_probability']))


def event(raw, age, hd, pop, key):
    record = source(raw, age, hd, pop, key)
    if record is None:
        return None
    info = record[1]
    if 'distributions' not in info:  # Exact younger pneumonia complement, with zero paediatric events.
        return derive_pneumonia_complement(raw, age, pop)
    return info


def diagnosis_parts(age, fine=False):
    if age == 'age18_74' and not fine:
        return [('i63', ()), ('allhd', ('i63',))]
    return [('i63', ()), ('i61', ()), ('allhd', ('i63', 'i61'))]


def counts(den, ev, age, hd, dimension, level=None):
    def extract(info):
        return info['n'] if dimension == 'total' else info['distributions'][dimension][level]
    return {field: extract(records[age,hd,pop])
            for field,records,pop in [('all_n',den,'all'), ('dys_n',den,'dys'),
                                      ('all_events',ev,'all'), ('dys_events',ev,'dys')]}


def common_cells(den, ev, dimension):
    cells = []
    levels = {'total': [None], 'sex': SEX_LABELS, 'pccl': [str(i) for i in range(7)]}[dimension]
    for age in AGES:
        for level in levels:
            for hd, subtract in diagnosis_parts(age):
                base = counts(den, ev, age, hd, dimension, level)
                for other in subtract:
                    part = counts(den, ev, age, other, dimension, level)
                    base = {k: n - part[k] for k,n in base.items()}
                cells.append(base)
    return cells


def drg_bundle(values):
    return bundle([dict(all_n=d+c, dys_n=d, all_events=a+b, dys_events=a) for d,c,a,b in values])


def b70d_models(raw):
    # The extension audit has verified each restricted workbook's complete filter set.
    den, ev = {}, {}
    for age, pop, endpoint in product(AGES, POPS, (None, 'mortality')):
        name = filename(age, 'allhd', pop, endpoint).replace('_2025.xlsx', '_B70D_2025.xlsx')
        info = read_info(raw / name)
        if info['n'] != source(raw,age,'allhd',pop,endpoint)[0]['B70D']:
            raise ValueError(f'{name}: restricted cohort differs from named B70D row')
        (den if endpoint is None else ev)[age,'allhd',pop] = info
    age_cells = [counts(den,ev,a,'allhd','total') for a in AGES]
    return {'B70D_crude': bundle([{k:sum(g[k] for g in age_cells) for k in age_cells[0]}]),
            'B70D_age': bundle(age_cells),
            'M4_B70D': bundle([counts(den,ev,a,'allhd','sex',s) for a,s in product(AGES,SEX_LABELS)])}


def binary(raw, out):
    endpoints = {r['outcome']:r['label'] for r in read_csv('outcomes_harmonized_binary_summary.csv')}
    grid = list(product(AGES,HDS,POPS))
    den = {k:source(raw,*k,None)[1] for k in grid}
    pilot = b70d_models(raw)
    rows = []
    for key,label in endpoints.items():
        def add(model, result=None, note=''):
            row = dict(outcome=key, label=label, model=model,
                       status='estimated' if result else 'unavailable', note=note)
            if result:
                row.update(result)
                row['dys_coverage'] = result['dys_n'] / full['dys_n']
                row['comparator_coverage'] = result['comparator_n'] / full['comparator_n']
            rows.append(row)
        ev = {k:event(raw,*k,key) for k in grid}
        missing = {k for k,v in ev.items() if v is None}
        expected = {('age18_74','i61','dys')} if key in ('E44.0','E44.1') else set()
        if missing != expected:
            raise ValueError(f'{key}: unexpected missing queries {missing}')
        ages = [counts(den,ev,a,'allhd','total') for a in AGES]
        full = bundle([{k:sum(g[k] for g in ages) for k in ages[0]}])
        add('M1', full)
        add('age', bundle(ages))
        for model,dim in [('age_hd','total'),('M2','sex'),('M3','pccl')]:
            add(model, bundle(common_cells(den,ev,dim)), 'Five common age and diagnosis groups.')
            if missing:
                add(model+'_fine', note='Younger I61 dysphagia event query suppressed.')
            else:
                add(model+'_fine', bundle(build_cells(den,ev,dim)), 'Six planned age and diagnosis groups.')
        add('M4', note='Age by sex by DRG across multiple DRGs unavailable.')
        age_cells, joint = [], []
        for age in AGES:
            by_hd = {h:observed(raw,age,h,key) for h in HDS}
            age_cells.extend(eligible(by_hd['allhd']).values())
            for h,subtract in diagnosis_parts(age):
                group = residual_cells(by_hd[h], *(by_hd[k] for k in subtract)) if subtract else by_hd[h]
                joint.extend(eligible(group).values())
        add('age_drg', drg_bundle(age_cells), 'Named rows observed in both groups and event tables.')
        add('age_hd_drg', drg_bundle(joint), 'Five common age and diagnosis groups within observable DRGs.')
        if key == 'mortality':
            for model, result in pilot.items():
                add(model, result, 'Single DRG B70D; coverage is relative to the full adult cohort.')
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (out/'adult_binary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f,fields,lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    return den

def drg_moments(raw,age,pop,hd):
    path=raw/filename(age,hd,pop,None)
    overall=read_source(path,age,hd,pop)[0]
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

def los(raw, out):
    with tempfile.TemporaryDirectory() as tmp:
        analyze_stay(raw, Path(tmp))
        original = json.loads((Path(tmp)/'los_age_diagnosis_results.json').read_text())
    rows = []
    def add(name, result, crude=False):
        calc = result['crude_same_population'] if crude else result['standardized']
        ci = calc['ci95'] or [None,None]
        rows.append(dict(model=name, dys_n=result['common_support']['dys_n'],
                         comparator_n=result['common_support']['no_dys_n'],
                         strata=1 if crude else result['common_support']['included_strata'],
                         dys_mean=calc['dys']['mean_days'] if crude else calc['dys_mean_days'],
                         comparator_mean=calc['no_dys']['mean_days'] if crude else calc['no_dys_mean_days'],
                         difference=calc['mean_difference_days'], ci_low=ci[0], ci_high=ci[1],
                         matched_crude_difference=result['crude_same_population']['mean_difference_days']))
    add('M1', original['primary'], True)
    for key, suffix in [('primary',''),('survivor_sensitivity','_survivors')]:
        strata = original[key]['strata']
        def moments(arm):
            return Moments(arm['n'],arm['sum_days'],arm['sum_squared_days'])
        groups = []
        for row in strata:
            d, c = (moments(row[arm]) for arm in ('dys','no_dys'))
            age,hd = row['age_band'],row['principal_diagnosis']
            groups.append(dict(age=age,hd=hd,dys=d,total=d+c))
        merged = {}
        for g in groups:
            diag = 'non_i63' if g['age']=='age18_74' and g['hd']!='i63' else g['hd']
            group = merged.setdefault((g['age'],diag),dict(age=g['age'],hd=diag,dys=Moments(0,0,0),total=Moments(0,0,0)))
            group['dys'] += g['dys']
            group['total'] += g['total']
        add('age_hd'+suffix,summarize(list(merged.values()),'five groups'))
        add('age_hd_fine'+suffix,original[key])
        if key=='primary':
            age_groups = []
            for age in AGES:
                parts = [g for g in groups if g['age']==age]
                age_groups.append(dict(age=age,hd='all',dys=sum_moments(g['dys'] for g in parts),
                                       total=sum_moments(g['total'] for g in parts)))
            add('age',summarize(age_groups,'age'))
    age_drg, joint, b70d = [], [], []
    for age in AGES:
        maps = {(h,p):drg_moments(raw,age,p,h) for h,p in product(HDS,POPS)}
        def groups(h, subtract):
            codes = sorted(set.intersection(*(set(maps[k,p]) for k,p in product((h,*subtract),POPS))))
            for code in codes:
                t,d = (maps[h,p][code] - sum_moments(maps[k,p][code] for k in subtract) for p in POPS)
                c = t-d
                if min(d.n,c.n)>0:
                    yield dict(age=age,hd=code,total=t,dys=d)
        for g in groups('allhd', ()):
            age_drg.append(g)
            if g['hd']=='B70D':
                b70d.append(g)
        for h,subtract in diagnosis_parts(age):
            joint.extend(groups(h,subtract))
    for name,values in [('age_drg',age_drg),('age_hd_drg',joint)]:
        add(name,summarize(values,name))
        precision = [g for g in values if min(g['dys'].n,(g['total']-g['dys']).n)>=2]
        if len(precision)<len(values):
            add(name+'_n2',summarize(precision,name))
    add('B70D_age',summarize(b70d,'B70D, age'))
    write_table(out/'adult_los.csv',rows)

def cohort(raw, out, den):
    """Tabulate episode characteristics for the entire cohort and both disjoint groups."""
    profiles = {}
    for pop in POPS:
        bands = [den[a,'allhd',pop] for a in AGES]
        total = sum(b['n'] for b in bands)
        profile = {'All':total, '18–74 years':bands[0]['n'], '≥75 years':bands[1]['n']}
        for age in sum(QUERY_AGES.values(),[]):
            profile[age] = sum(b['distributions']['age'][age] for b in bands)
        for sex in ('männlich','weiblich'):
            profile[sex] = sum(b['distributions']['sex'][sex] for b in bands)
        profile['other_sex'] = total-profile['männlich']-profile['weiblich']
        for h in ('i63','i61'):
            profile[h] = sum(den[a,h,pop]['n'] for a in AGES)
        profile['other_hd'] = total-profile['i63']-profile['i61']
        for label,levels in [('PCCL 0',('0',)),('PCCL 1–2',('1','2')),('PCCL 3–6',('3','4','5','6'))]:
            profile[label] = sum(b['distributions']['pccl'][k] for b in bands for k in levels)
        profile['8-836.80'] = sum(code_margins(raw,a,'allhd',pop,'Prozeduren')['8-836.80'] for a in AGES)
        for partition in (sum(QUERY_AGES.values(),[]), ('männlich','weiblich','other_sex'),
                          ('i63','i61','other_hd'),('PCCL 0','PCCL 1–2','PCCL 3–6')):
            if sum(profile[k] for k in partition) != total:
                raise ValueError(f'{pop}: cohort partition does not sum to episode count')
        profiles[pop] = profile
    total,dys = profiles['all'],profiles['dys']
    comp_n = total['All']-dys['All']
    rows = []
    for key,n in total.items():
        d = dys[key]
        if not (0 <= d <= n and n-d <= comp_n):
            raise ValueError(f'Invalid nested counts for {key}')
        rows.append(dict(characteristic=key, dys_n=d, comparator_n=n-d, all_n=n,
                         dys_pct=100*d/dys['All'], comparator_pct=100*(n-d)/comp_n,
                         all_pct=100*n/total['All'], count_type='exact'))
    # Some G45 end codes are pooled into the unidentified remainder. The visible count
    # is a lower bound for all adults. Subtracting group-specific lower bounds is invalid.
    visible = sum(n for age in AGES for k,n in code_margins(raw,age,'allhd','all','Hauptdiagnosen').items()
                  if k.startswith('G45'))
    rows.append(dict(characteristic='G45 visible',dys_n=None,comparator_n=None,all_n=visible,
                     dys_pct=None,comparator_pct=None,all_pct=100*visible/total['All'],
                     count_type='lower bound from named principal-diagnosis rows; subset of other_hd'))
    write_table(out/'adult_cohort.csv',rows)


def functional(raw,out):
    from outcomes_standardization_core import MINOR_AGES
    from analyze_functional_sensitivity import INSTRUMENTS
    codes = {
        code: (instrument, band)
        for instrument, definition in INSTRUMENTS.items()
        for code, band in zip(definition['codes'], definition['score_bands'])
    }
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
    ap.add_argument('--protocol', type=Path, help='Optional private Exportprotokoll.csv with original checksums')
    args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    write_table(args.out/'adult_export_audit.csv', audit(args.raw,args.protocol))
    den=binary(args.raw,args.out);cohort(args.raw,args.out,den);los(args.raw,args.out);functional(args.raw,args.out)
