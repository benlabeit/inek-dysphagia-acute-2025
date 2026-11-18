"""Adult acute-stroke-care episode disposition from local aggregate workbooks."""
import argparse
import csv
from functools import lru_cache
from hashlib import sha256
from itertools import product
from pathlib import Path

import openpyxl

from adult_analysis import AGES, HDS, POPS, bundle, common_cells, counts, diagnosis_parts, drg_bundle
from outcomes_analyze_joint import DELIVERY, HD_CODES, OPS, R13, build_cells, selection_fields
from outcomes_standardization_core import QUERY_AGES, SEX_LABELS, read_info
from outcomes_within_drg import difference, eligible, filename, residual_cells, source, write_table


ROOT = Path(__file__).resolve().parent
CATEGORIES = {'rehabilitation':('09',), 'nursing_facility':('10',), 'hospice':('11',),
              'external_hospital_transfer':('06','08','13')}
LABELS = {'rehabilitation':'Rehabilitationseinrichtung', 'nursing_facility':'Pflegeeinrichtung',
          'hospice':'Hospiz', 'external_hospital_transfer':'Externe Krankenhausverlegung'}
FIELDS = ('outcome','model','population','status','reason','all_n','dys_n','comparator_n',
          'all_events','dys_events','comparator_events','all_observed_risk','dys_risk','comparator_risk',
          'rr','rr_low','rr_high','rd','rd_low','rd_high','strata','matched_crude_rr',
          'sparse_weight','boundary_weight','dys_coverage','comparator_coverage')


def outcome_file(key,age,hd,pop,drg=''):
    suffix = '_'+drg if drg else ''
    return f'acute_discharge_{key}_{age}_{hd}_{pop}{suffix}_2025.xlsx'


def query_plan():
    stages = [
        ('1 Kern: Rohvergleich und Alter × DRG',[(a,'allhd',p,'') for a,p in product(AGES,POPS)]),
        ('2 Kern: Alter, Hauptdiagnose und Geschlecht bzw. PCCL',
         [(a,h,p,'') for a,h,p in product(AGES,('i63','i61'),POPS) if (a,h)!=('age18_74','i61')]),
        ('3 Optional: feinere Diagnosegruppen', [('age18_74','i61',p,'') for p in POPS]),
        ('4 Optional: B70D-Pilot mit Geschlecht', [(a,'allhd',p,'B70D') for a,p in product(AGES,POPS)])]
    rows = []
    for stage,grid in stages:
        for key,codes in CATEGORIES.items():
            for age,hd,pop,drg in grid:
                rows.append({'Nr':len(rows)+1,'Stufe':stage,'Entlassungskategorie':LABELS[key],
                             'Lieferung':DELIVERY,'Alter':', '.join(QUERY_AGES[age]),
                             'Hauptdiagnosen':', '.join(HD_CODES.get(hd,[])), 'Prozeduren':', '.join(OPS),
                             'Nebendiagnosen':', '.join(R13) if pop=='dys' else '',
                             'Entlassungsgrund':', '.join(codes),'DRG':drg,
                             'Dateiname':outcome_file(key,age,hd,pop,drg)})
    return rows


@lru_cache(None)
def read_filtered(path,age,hd,pop,codes,drg):
    """Check every selector; within the discharge selector the numeric key defines the reason."""
    info = read_info(path)
    fields = {k:v for k,v in selection_fields(info['selection']).items() if v}
    for alias,canonical in [('Altersklassen','Altersgruppe'),('Altersklasse','Altersgruppe'),
                            ('Hauptdiagnosen','Hauptdiagnose')]:
        if alias in fields:
            if canonical in fields:
                raise ValueError(f'{path.name}: duplicate filter')
            fields[canonical]=fields.pop(alias)
    reasons = {v.split()[0] for v in fields.pop('Entlassungsgrund',set())}
    expected = {'Prozeduren':set(OPS),'Altersgruppe':set(QUERY_AGES[age])}
    if hd!='allhd':
        expected['Hauptdiagnose']=set(HD_CODES[hd])
    if pop=='dys':
        expected['Nebendiagnosen']=set(R13)
    if drg:
        expected['DRG']={drg}
    if fields!=expected or reasons!=set(codes) or info['delivery']!=DELIVERY:
        raise ValueError(f'{path.name}: unexpected selection or delivery')
    if sum(info['distributions']['age'][s] for s in QUERY_AGES[age])!=info['n']:
        raise ValueError(f'{path.name}: patients outside age band')
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    try:
        data=iter(w['DRG-Verteilung'].values)
        if next(data)[:3]!=('DRG','Bezeichnung','Fälle'):
            raise ValueError(f'{path.name}: DRG header')
        named={}; total=0
        for code,label,n,*_ in data:
            if code is None and n is None:continue
            if not isinstance(n,(int,float)) or n<0 or not float(n).is_integer():
                raise ValueError(f'{path.name}: invalid DRG count')
            total+=int(n)
            if code=='---' and str(label).startswith('Rest'):continue
            if code in named or (drg and code!=drg):raise ValueError(f'{path.name}: unexpected DRG row')
            named[code]=int(n)
        if total!=info['n']:raise ValueError(f'{path.name}: DRG rows do not sum to N')
    finally:
        w.close()
    return named,info


def combine_info(records, signs):
    n=sum(sign*r['n'] for sign,r in zip(signs,records))
    result={}
    for dimension,levels in records[0]['distributions'].items():
        values={k:sum(sign*r['distributions'][dimension][k] for sign,r in zip(signs,records)) for k in levels}
        if min(values.values())<0 or sum(values.values())!=n:raise ValueError('Invalid disjoint margin')
        result[dimension]=values
    return {'n':n,'distributions':result}


def event_export(raw,key,age,hd,pop,drg=''):
    codes=CATEGORIES[key]
    path=raw/outcome_file(key,age,hd,pop,drg)
    if path.is_file():
        return read_filtered(path,age,hd,pop,codes,drg)
    if len(codes)==1:return None
    # If a release cannot select several reasons together, accept the three
    # distinct single-code queries. Every contributing source must be observed.
    paths=[raw/outcome_file(key+'_'+c,age,hd,pop,drg) for c in codes]
    if not all(p.is_file() for p in paths):return None
    parts=[read_filtered(p,age,hd,pop,(c,),drg) for c,p in zip(codes,paths)]
    shared=set.intersection(*(set(p[0]) for p in parts))
    return {k:sum(p[0][k] for p in parts) for k in shared},combine_info([p[1] for p in parts],[1]*len(parts))


def audit_exports(raw, out, protocol):
    """Match every planned filter to its workbook and, if given, to the private retrieval log."""
    plan = query_plan()
    log = {}
    if protocol:
        wb = openpyxl.load_workbook(protocol, read_only=True, data_only=True)
        try:
            for sheet in ('Kernabfragen', 'Ergänzungen'):
                for row in list(wb[sheet].values)[3:]:
                    if row[0] is None:
                        continue
                    number, name = int(row[0]), row[10]
                    if name in log or number < 1 or number > len(plan) or plan[number-1]['Dateiname'] != name:
                        raise ValueError(f'{sheet}: inconsistent query number or repeated filename')
                    log[name] = (row[7], row[8], row[9] or '')
        finally:
            wb.close()
        if set(log)!={r['Dateiname'] for r in plan}:
            raise ValueError('The retrieval log does not cover the complete query plan')
    result = []
    for row in plan:
        name = row['Dateiname']
        key = next(k for k,v in LABELS.items() if v == row['Entlassungskategorie'])
        age = next(a for a in AGES if ', '.join(QUERY_AGES[a]) == row['Alter'])
        hd = next((h for h in HDS if h != 'allhd' and ', '.join(HD_CODES[h]) == row['Hauptdiagnosen']), 'allhd')
        pop = 'dys' if row['Nebendiagnosen'] else 'all'
        rec = event_export(raw,key,age,hd,pop,row['DRG'])
        path = raw/name
        status = 'verified' if rec is not None else 'unavailable'
        if log:
            state, n, message = log[name]
            if state == 'exportiert':
                if rec is None or n != rec[1]['n']:
                    raise ValueError(f'{name}: file or case count differs from retrieval log')
            elif state == 'unterdrückt':
                if rec is not None or n is not None or 'zu wenige' not in message.lower():
                    raise ValueError(f'{name}: inconsistent suppression record')
                status = 'suppressed'
            elif rec is not None:
                raise ValueError(f'{name}: log does not mark the observed export as complete')
        # A grouped hospital-transfer query may be reconstructed from three single-code
        # exports. The public hash describes the exact planned file only when it exists.
        digest = sha256(path.read_bytes()).hexdigest() if path.is_file() else ''
        result.append(dict(query=row['Nr'],outcome=key,age_band=age,diagnosis=hd,
                           source_group=pop,drg=row['DRG'],filename=name,status=status,sha256=digest))
    write_table(out/'adult_discharge_export_audit.csv',result)
    return {r['filename'] for r in result if r['status']=='suppressed'}


def analyze(raw,out,suppressed=()):
    grid=list(product(AGES,HDS,POPS))
    baseline={k:source(raw,*k,None) for k in grid}
    deaths={k:source(raw,*k,'mortality') for k in grid}
    den={k:combine_info([baseline[k][1],deaths[k][1]],[1,-1]) for k in grid}
    live_drgs={k:difference(baseline[k][0],deaths[k][0]) for k in grid}
    def sums(records, index=None):
        total,d=(sum((records[a,'allhd',p][index] if index is not None else records[a,'allhd',p])['n']
                     for a in AGES) for p in POPS)
        return total,d,total-d
    all_n,all_d,all_c=sums(baseline,1)
    live_n,live_d,live_c=sums(den)
    rows=[]
    for outcome,events in [('discharged_alive',(live_n,live_d,live_c)),('in_hospital_death',sums(deaths,1))]:
        t,d,c=events
        res=bundle([dict(all_n=all_n,dys_n=all_d,all_events=t,dys_events=d)])
        rows.append(dict(outcome=outcome,model='crude',population='all adult episodes',status='estimated',
                         reason='',all_n=all_n,all_events=t,all_observed_risk=t/all_n,**res,
                         dys_coverage=1,comparator_coverage=1))
    if live_n+rows[1]['all_events']!=all_n:raise ValueError('Discharge status does not partition adult episodes')
    # Live discharge is the complement of death within the same observed stratum.
    # Recompute risks and intervals on the live scale; the mortality RR cannot be inverted.
    base_info={k:v[1] for k,v in baseline.items()}
    def add_live(model,cells):
        r=bundle(cells)
        if r is None:return
        n=r['dys_n']+r['comparator_n']
        events=r['dys_events']+r['comparator_events']
        rows.append(dict(outcome='discharged_alive',model=model,
                         population='all adult episodes' if model!='B70D_age_sex' else 'adult B70D episodes',
                         status='estimated',reason='',all_n=n,all_events=events,all_observed_risk=events/n,
                         **r,dys_coverage=r['dys_n']/all_d,comparator_coverage=r['comparator_n']/all_c))
    for model,dimension in [('age_hd','total'),('M2','sex'),('M3','pccl')]:
        add_live(model,common_cells(base_info,den,dimension))
    by_drg=[]
    for age in AGES:
        total,coded=(baseline[age,'allhd',p][0] for p in POPS)
        live,live_coded=(live_drgs[age,'allhd',p] for p in POPS)
        for k in sorted(live.keys() & live_coded.keys()):
            by_drg.append(dict(all_n=total[k],dys_n=coded[k],all_events=live[k],dys_events=live_coded[k]))
    add_live('age_drg',by_drg)
    bden={};blive={}
    for a,pop in product(AGES,POPS):
        k=(a,'allhd',pop)
        part=[]
        for outcome,codes in [(None,()),('mortality',('07',))]:
            fn=filename(*k,outcome).replace('_2025.xlsx','_B70D_2025.xlsx')
            if not (raw/fn).is_file():
                break
            validated=read_filtered(raw/fn,a,'allhd',pop,codes,'B70D')[1]
            parent=(deaths if outcome else baseline)[k][0]
            if 'B70D' in parent and validated['n']!=parent['B70D']:
                raise ValueError(f'{fn}: count differs from matching parent DRG row')
            part.append(validated)
        if len(part)==2:
            bden[k]=part[0];blive[k]=combine_info(part,[1,-1])
    if len(blive)==len(AGES)*len(POPS):
        add_live('B70D_age_sex',[counts(bden,blive,a,'allhd','sex',level) for a,level in product(AGES,SEX_LABELS)])
    else:
        rows.append(dict(outcome='discharged_alive',model='B70D_age_sex',population='adult B70D episodes',
                         status='unavailable',reason='B70D denominator or death export unavailable.'))
    # Each destination is a mutually exclusive discharge reason. Subtract the
    # observed margins from the live discharges for each age, diagnosis and arm.
    remaining = dict(den)
    for key in CATEGORIES:
        records={k:event_export(raw,key,*k) for k in grid}
        events={k:r[1] for k,r in records.items() if r is not None}
        for k,event in events.items():
            remaining[k]=combine_info([remaining[k],event],[1,-1])
        for age,hd in product(AGES,HDS):
            all_key=(age,hd,'all')
            dys_key=(age,hd,'dys')
            if all_key in events and dys_key in events:
                combine_info([events[all_key],events[dys_key]],[1,-1])
        def add(model,result=None,reason='Matching event exports unavailable.',full=False):
            population='all adult episodes' if full else 'adult live discharges in B70D' if model.startswith('B70D_') else 'adult live discharges'
            d0,c0=(all_d,all_c) if full else (live_d,live_c)
            row=dict(outcome=key,model=model,population=population,status='unavailable',reason=reason)
            if result is not None:
                t=result['dys_n']+result['comparator_n']; et=result['dys_events']+result['comparator_events']
                row.update(result,status='estimated',reason='',all_n=t,all_events=et,all_observed_risk=et/t,
                           dys_coverage=result['dys_n']/d0,comparator_coverage=result['comparator_n']/c0)
            rows.append(row)
        have_age=all((a,'allhd',p) in events for a,p in product(AGES,POPS))
        live_info=den
        def crude(info):
            blocks=[counts(info,events,a,'allhd','total') for a in AGES]
            return bundle([{field:sum(b[field] for b in blocks) for field in blocks[0]}])
        add('crude_all_discharges',crude({k:v[1] for k,v in baseline.items()}) if have_age else None,full=True)
        add('M1',crude(live_info) if have_age else None)
        add('age',bundle([counts(live_info,events,a,'allhd','total') for a in AGES]) if have_age else None)
        common_keys={k for k in grid if k[:2]!=('age18_74','i61')}
        missing_files = {outcome_file(key,*k) for k in grid if k not in events}
        fine_reason = ('Fine diagnosis grid incomplete after source suppression.'
                       if missing_files.intersection(suppressed) else 'Fine diagnosis grid incomplete.')
        for m,dimension in [('age_hd','total'),('M2','sex'),('M3','pccl')]:
            add(m,bundle(common_cells(live_info,events,dimension)) if common_keys<=events.keys() else None)
            add(m+'_fine',bundle(build_cells(live_info,events,dimension)) if len(events)==len(grid) else None, fine_reason)
        drgs={}
        for a,h in product(AGES,HDS):
            if not all((a,h,p) in events for p in POPS):continue
            t,d=(live_drgs[a,h,p] for p in POPS)
            e,b=(records[a,h,p][0] for p in POPS)
            drgs[a,h]={k:(d[k],t[k]-d[k],b[k],e[k]-b[k]) for k in sorted(t.keys() & d.keys() & e.keys() & b.keys())}
        def billing(with_hd):
            needed=common_keys if with_hd else {(a,'allhd',p) for a,p in product(AGES,POPS)}
            if not needed<=events.keys():return None
            cells=[]
            for age in AGES:
                parts=diagnosis_parts(age) if with_hd else [('allhd',())]
                for hd,subtract in parts:
                    g=drgs[age,hd]
                    if subtract:g=residual_cells(g,*(drgs[age,h] for h in subtract))
                    cells.extend(eligible(g).values())
            return drg_bundle(cells) if cells else None
        add('age_drg',billing(False),'Event export or shared named survivor and event DRG rows unavailable.')
        add('age_hd_drg',billing(True),'Event export or shared named survivor and event DRG rows unavailable.')
        pilot={(a,'allhd',p):event_export(raw,key,a,'allhd',p,'B70D') for a,p in product(AGES,POPS)}
        add('M4',reason='Joint sex-specific event and denominator counts unavailable across multiple DRGs.')
        pilot_models = {}
        if all(pilot.values()) and set(pilot)<=blive.keys():
            pe={k:v[1] for k,v in pilot.items()}
            for k,info in pe.items():
                parent=records[k]
                if parent is not None and 'B70D' in parent[0] and info['n']!=parent[0]['B70D']:
                    raise ValueError(f'{key}, {k}: B70D event file disagrees with parent DRG row')
            age_counts=[counts(blive,pe,a,'allhd','total') for a in AGES]
            pilot_models['B70D_crude']=bundle([{k:sum(r[k] for r in age_counts) for k in age_counts[0]}])
            pilot_models['B70D_age']=bundle(age_counts)
            pilot_models['B70D_age_sex']=bundle([counts(blive,pe,a,'allhd','sex',level)
                                                   for a,level in product(AGES,SEX_LABELS)])
        for model in ('B70D_crude','B70D_age','B70D_age_sex'):
            add(model,pilot_models.get(model))
    # Audit mutual exclusivity and the residual only when every destination is observed.
    crude_rows=[r for r in rows if r['model']=='M1' and r['status']=='estimated']
    d=sum(r['dys_events'] for r in crude_rows);c=sum(r['comparator_events'] for r in crude_rows)
    if d>live_d or c>live_c:raise ValueError('Discharge destinations exceed the population discharged alive')
    if len(crude_rows)==len(CATEGORIES):
        res=bundle([dict(all_n=live_n,dys_n=live_d,all_events=live_n-d-c,dys_events=live_d-d)])
        rows.append(dict(outcome='other_or_unspecified_live_disposition',model='M1',population='adult live discharges',
                         status='estimated',reason='',all_n=live_n,all_events=live_n-d-c,all_observed_risk=(live_n-d-c)/live_n,
                         **res,dys_coverage=1,comparator_coverage=1))
    with (out/'adult_discharge.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,FIELDS,lineterminator='\n');writer.writeheader();writer.writerows(rows)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=ROOT)
    ap.add_argument('--protocol',type=Path,help='Optional private discharge retrieval log (.xlsx)')
    args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    plan=query_plan()
    with (args.out/'adult_discharge_queries.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,plan[0].keys(),delimiter=';',lineterminator='\n')
        writer.writeheader();writer.writerows(plan)
    suppressed=audit_exports(args.raw,args.out,args.protocol)
    analyze(args.raw,args.out,suppressed)
