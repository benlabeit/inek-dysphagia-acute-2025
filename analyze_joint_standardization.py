"""Joint demographic/diagnosis mortality standardization from NEW InEK exports.

No new results exist until every required workbook for the selected cohort(s)
has been supplied and validated. Use --status-only to report missing inputs.
The 24-file design per cohort is age x all-HD/I63/I61 x T/D/T-death/D-death.
Input workbooks are read-only; no marginal distributions are assumed independent.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import math
import re

import openpyxl

ROOT = Path(__file__).resolve().parent
Z = 1.959963984540054
DELIVERY = 'Unterjährige Datenlieferung DRG Januar bis Dezember 2025'
SEX_LABELS = ['männlich', 'weiblich', 'divers', 'unbekannt']
HD = ['allhd', 'i63', 'i61']
KINDS = ['all', 'dys', 'all_death', 'dys_death']
QUERY_AGES = {
    'age18_74': ['18-29 Jahre', '30-39 Jahre', '40-49 Jahre', '50-54 Jahre', '55-59 Jahre', '60-64 Jahre', '65-74 Jahre'],
    'age75plus': ['75-79 Jahre', '80+ Jahre'],
}
MINOR_AGES = ['< 28 Tage', '28 Tage - 1. Jahr', '1-2 Jahre', '3-5 Jahre', '6-9 Jahre', '10-15 Jahre', '16-17 Jahre']
HD_CODES = {name: [name.upper()+'.'+str(k) for k in [0,1,2,3,4,5,6,8,9]] for name in ['i63', 'i61']}
OPS = {
    'acute': [prefix+'.'+str(k) for prefix in ['8-981', '8-98b'] for k in [20,21,22,23,30,31,32,33]],
    'rehab': ['8-552.'+str(k) for k in [0,5,6,7,8,9]],
}


def save(value, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def filename(cohort, age, hd, kind):
    return f'{cohort}_joint_{age}_{hd}_{kind}_2025.xlsx'


def expected_files(cohort):
    return [filename(cohort, age, hd, kind) for age in QUERY_AGES for hd in HD for kind in KINDS]


def reference_files(cohort):
    return [f'{cohort}_{kind}_2025.xlsx' for kind in KINDS]


def read_info(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb['Info'].values)
    finally:
        wb.close()
    def cell(row, column):
        return rows[row-1][column-1]
    if cell(8,1) != 'Fallzahl':
        raise ValueError(path.name+': unrecognized Info layout')
    raw_n = cell(8,2)
    if (isinstance(raw_n, bool) or not isinstance(raw_n, (int, float))
            or not math.isfinite(raw_n) or not float(raw_n).is_integer()):
        raise ValueError(path.name+': non-integer source population')
    n = int(raw_n)
    if n <= 0:
        raise ValueError(path.name+': no positive source population')
    distributions = {}
    for name, indices, lc, vc in [('sex', range(11,15), 1, 2),
                                  ('pccl', range(8,15), 7, 8),
                                  ('age', range(8,len(rows)+1), 10, 11)]:
        counts = {}
        for row in indices:
            label, fraction = cell(row,lc), cell(row,vc)
            if label is None and fraction is None:
                continue
            if label is None or fraction is None:
                raise ValueError(path.name+': incomplete '+name+' row')
            value = float(fraction)*n
            recovered = round(value)
            if abs(value-recovered) >= 1e-6 or recovered < 0:
                raise ValueError(path.name+': nonrecoverable '+name+' count')
            label = str(int(label)) if isinstance(label,(float,int)) and float(label).is_integer() else str(label)
            if label in counts:
                raise ValueError(path.name+': repeated '+name+' category')
            counts[label] = recovered
        if sum(counts.values()) != n:
            raise ValueError(path.name+': '+name+' does not partition N')
        distributions[name] = counts
    expected_age = set(MINOR_AGES + sum(QUERY_AGES.values(), []))
    if set(distributions['age']) != expected_age or set(distributions['pccl']) != {str(k) for k in range(7)}:
        raise ValueError(path.name+': unexpected age/PCCL categories')
    if set(distributions['sex']) != set(SEX_LABELS):
        raise ValueError(path.name+': unexpected sex categories')
    return {'n': n, 'selection': str(cell(2,1)), 'delivery': cell(5,1),
            'distributions': distributions,
            'source': {'path': 'raw/'+path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'size_bytes': path.stat().st_size}}


def selection_fields(text):
    fields = {}
    for name, values in re.findall(r'([^();]+)\(([^()]*)\)', text):
        name = name.strip()
        if name in fields:
            raise ValueError('Repeated selection field: '+name)
        fields[name] = {v.strip().rstrip('!*') for v in values.split(',') if v.strip()}
    return fields


def validate_export(export, cohort, age, hd, kind):
    if export['delivery'] != DELIVERY:
        raise ValueError('Different delivery: '+export['source']['path'])
    fields = selection_fields(export['selection'])
    allowed = {'Prozeduren','Nebendiagnosen','Hauptdiagnosen','Hauptdiagnose',
               'Altersklasse','Altersklassen','Altersgruppe','Entlassungsgrund'}
    if set(fields)-allowed:
        raise ValueError('Unexpected population filters: '+str(sorted(set(fields)-allowed)))
    if fields.get('Prozeduren') != set(OPS[cohort]):
        raise ValueError('OPS selection differs from protocol: '+export['source']['path'])
    expected_nd = {'R13.0','R13.1','R13.9'} if kind.startswith('dys') else set()
    if fields.get('Nebendiagnosen',set()) != expected_nd:
        raise ValueError('R13 secondary-diagnosis selection differs: '+export['source']['path'])
    hdcodes = fields.get('Hauptdiagnosen',fields.get('Hauptdiagnose',set()))
    if hdcodes != (set() if hd=='allhd' else set(HD_CODES[hd])):
        raise ValueError('Principal diagnosis must use the full explicit endcode set: '+export['source']['path'])
    death = fields.get('Entlassungsgrund',set())
    if kind.endswith('death'):
        if len(death)!=1 or not next(iter(death)).startswith('07'):
            raise ValueError('Discharge reason 07 required: '+export['source']['path'])
    elif death:
        raise ValueError('Unexpected discharge filter: '+export['source']['path'])
    age_fields=[name for name in ['Altersklasse','Altersklassen','Altersgruppe'] if name in fields]
    if len(age_fields)!=1:
        raise ValueError('Exactly one recognized age selection field required: '+export['source']['path'])
    ages = fields[age_fields[0]]
    if ages != set(QUERY_AGES[age]):
        raise ValueError('Age filter differs from protocol: '+export['source']['path'])
    age_counts=export['distributions']['age']
    if sum(age_counts[label] for label in QUERY_AGES[age]) != export['n']:
        raise ValueError('Export contains cases outside its selected adult age band: '+export['source']['path'])


def validate_reference(reference, cohort, kind):
    """Validate the unrestricted original cohort, not merely its total size."""
    if reference['delivery'] != DELIVERY:
        raise ValueError('Original reference delivery differs')
    fields = selection_fields(reference['selection'])
    allowed = {'Prozeduren', 'Nebendiagnosen', 'Entlassungsgrund'}
    if set(fields) - allowed:
        raise ValueError('Unexpected original reference filters: '+str(set(fields)-allowed))
    if fields.get('Prozeduren') != set(OPS[cohort]):
        raise ValueError('Original reference OPS differs')
    expected_nd = {'R13.0', 'R13.1', 'R13.9'} if kind.startswith('dys') else set()
    if fields.get('Nebendiagnosen', set()) != expected_nd:
        raise ValueError('Original reference R13 definition differs')
    death = fields.get('Entlassungsgrund', set())
    if kind.endswith('death'):
        if len(death) != 1 or not next(iter(death)).startswith('07'):
            raise ValueError('Original reference requires discharge 07')
    elif death:
        raise ValueError('Unexpected original reference death filter')


def contrast(a, n, b, m):
    if n<=0 or m<=0 or not(0<=a<=n and 0<=b<=m):
        raise ValueError('Invalid two-group contrast')
    p,q = a/n,b/m
    variance = p*(1-p)/n+q*(1-q)/m
    rr = p/q if q>0 else None
    interval = None
    if a>0 and b>0:
        se = math.sqrt(1/a-1/n+1/b-1/m)
        interval = [rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    return {'dys_events': a,'dys_n': n,'no_dys_events': b,'no_dys_n': m,
            'dys_rate': p,'no_dys_rate': q,'rr': rr,'rr_ci': interval,
            'risk_difference': p-q,
            'risk_difference_ci': [p-q-Z*math.sqrt(variance),p-q+Z*math.sqrt(variance)]}


def standardize(cells):
    """Fixed pooled weights, denominator-based common support, matched crude."""
    included, excluded = [], []
    for cell in cells:
        t,d,et,ed = [cell[k] for k in ['all_n','dys_n','all_events','dys_events']]
        c,ec = t-d,et-ed
        if min(t,d,c,et,ed,ec)<0 or ed>d or ec>c:
            raise ValueError('Invalid reconstructed cell: '+str(cell))
        item = dict(cell, no_dys_n=c, no_dys_events=ec)
        if d==0 or c==0:
            item['reason'] = 'No dysphagia cases' if d==0 else 'No comparator cases'
            excluded.append(item)
        else:
            included.append(item)
    if not included:
        return {'status':'not_estimable','reason':'No common-support cells','excluded_cells':excluded}
    full_t = sum(c['all_n'] for c in cells)
    full_d = sum(c['dys_n'] for c in cells)
    nt = sum(c['all_n'] for c in included)
    nd = sum(c['dys_n'] for c in included)
    nc = nt-nd
    ed = sum(c['dys_events'] for c in included)
    ec = sum(c['no_dys_events'] for c in included)
    pd=pc=vd=vc=0.0
    for cell in included:
        w = cell['all_n']/nt
        p = cell['dys_events']/cell['dys_n']
        q = cell['no_dys_events']/cell['no_dys_n']
        pd += w*p; pc += w*q
        vd += w*w*p*(1-p)/cell['dys_n']
        vc += w*w*q*(1-q)/cell['no_dys_n']
        cell.update(reference_weight=w, dys_rate=p, no_dys_rate=q,
                    sparse_event_cell=min(cell['dys_events'],cell['no_dys_events'],
                                          cell['dys_n']-cell['dys_events'],
                                          cell['no_dys_n']-cell['no_dys_events'])<5,
                    boundary_probability=p in [0,1] or q in [0,1])
    rr = pd/pc if pc>0 else None
    ci = None
    if pd>0 and pc>0:
        se = math.sqrt(vd/pd**2+vc/pc**2)
        ci = [rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    se_rd = math.sqrt(vd+vc)
    return {'status':'estimated','strata':included,'excluded_cells':excluded,
            'selected_population_before_common_support':{'all_n':full_t,'dys_n':full_d,'no_dys_n':full_t-full_d},
            'common_support':{'included_cells':len(included),'excluded_cells':len(excluded),
                              'all_n':nt,'dys_n':nd,'no_dys_n':nc,
                              'all_coverage':nt/full_t if full_t else None,
                              'dys_coverage':nd/full_d if full_d else None,
                              'no_dys_coverage':nc/(full_t-full_d) if full_t>full_d else None},
            'crude_same_common_support_population':contrast(ed,nd,ec,nc),
            'standardized':{'dys_rate':pd,'no_dys_rate':pc,'rr':rr,'rr_ci':ci,
                            'rr_ci_status':'available' if ci is not None else 'undefined because a standardized event risk is zero',
                            'dys_rate_ci':[pd-Z*math.sqrt(vd),pd+Z*math.sqrt(vd)],
                            'no_dys_rate_ci':[pc-Z*math.sqrt(vc),pc+Z*math.sqrt(vc)],
                            'risk_difference':pd-pc,
                            'risk_difference_ci':[pd-pc-Z*se_rd,pd-pc+Z*se_rd]},
            'method':'Direct standardization to pooled common-support population; fixed observed weights; independent-binomial delta intervals. Zero-event cells retained; unsupported cells excluded using denominators only.'}


def build_cells(exports, distribution):
    cells=[]
    labels = SEX_LABELS if distribution=='sex' else [str(k) for k in range(7)]
    for age in QUERY_AGES:
        for label in labels:
            values = {hd:{kind:exports[age,hd,kind]['distributions'][distribution][label]
                         for kind in KINDS} for hd in HD}
            values['otherhd'] = {kind:values['allhd'][kind]-values['i63'][kind]-values['i61'][kind] for kind in KINDS}
            if any(v<0 for v in values['otherhd'].values()):
                raise ValueError('I63/I61 are not nested disjoint principal-diagnosis groups')
            for hd in ['i63','i61','otherhd']:
                v=values[hd]
                cells.append({'age_band':'18-74' if age=='age18_74' else '75+',
                              'principal_diagnosis':hd,distribution:label,
                              'all_n':v['all'],'dys_n':v['dys'],
                              'all_events':v['all_death'],'dys_events':v['dys_death']})
    return cells


def analyze(cohort, raw_dir):
    exports={}
    for age in QUERY_AGES:
        for hd in HD:
            for kind in KINDS:
                e=read_info(raw_dir/filename(cohort,age,hd,kind))
                validate_export(e,cohort,age,hd,kind)
                exports[age,hd,kind]=e
    references={kind:read_info(raw_dir/f'{cohort}_{kind}_2025.xlsx') for kind in KINDS}
    reference_checks={}
    for kind,reference in references.items():
        validate_reference(reference, cohort, kind)
        adult_expected=sum(reference['distributions']['age'][label] for label in sum(QUERY_AGES.values(),[]))
        adult_observed=sum(exports[age,'allhd',kind]['n'] for age in QUERY_AGES)
        if adult_expected!=adult_observed:
            raise ValueError(f'{cohort}/{kind}: new adult total differs from original export')
        for age,labels in QUERY_AGES.items():
            new=exports[age,'allhd',kind]
            for label in labels:
                if new['distributions']['age'][label]!=reference['distributions']['age'][label]:
                    raise ValueError(f'{cohort}/{kind}: native age counts differ from original reference')
        reference_checks[kind]={'original_source':reference['source'],
                                'original_n':reference['n'],'expected_adult_n':adult_expected,
                                'new_adult_n':adult_observed,'native_age_counts_match':True}
    # Validate all source/subgroup count identities before restricting age.
    for distribution in ['sex','pccl']:
        checked=build_cells(exports,distribution)
        for cell in checked:
            t,d,et,ed=[cell[k] for k in ['all_n','dys_n','all_events','dys_events']]
            if min(t,d,t-d,et,ed,et-ed)<0 or ed>d or et-ed>t-d:
                raise ValueError('Invalid nested source counts')
    age_result=standardize(build_cells(exports,'sex'))
    pccl_result=standardize(build_cells(exports,'pccl'))
    pccl_result['population_scope'] = 'Adults aged 18+, all recorded sex categories; sex is not a joint PCCL covariate'
    return {'cohort':cohort,'outcome':'In-hospital death, discharge reason 07',
            'delivery':DELIVERY,'population':'Adults aged 18+, all four recorded sex categories; unsupported joint cells reported separately',
            'inputs':{filename(cohort,*key):{'source':e['source'],'selection':e['selection'],'n':e['n']} for key,e in exports.items()},
            'original_reference_checks':reference_checks,
            'age_sex_principal_diagnosis':age_result,
            'age_principal_diagnosis_pccl_sensitivity':pccl_result,
            'diagnosis_partition':{'i63':HD_CODES['i63'],'i61':HD_CODES['i61'],
                                   'otherhd':'All principal diagnoses minus full directly selected I63 and I61, separately within each age/sex or age/PCCL and event/exposure group'},
            'limitations':['No NIHSS or validated admission neurological severity is available.',
                           'Mortality analyses only; pneumonia has not been jointly standardized by this query design.',
                           'Age/sex/diagnosis and age/diagnosis/PCCL standardizations are separate; no joint sex-by-PCCL table is available.',
                           'Two broad age groups (18-74 and 75+) leave within-band age differences; the existing finer age-only analysis remains a separate sensitivity.',
                           'PCCL can reflect dysphagia-related or outcome-related diagnoses and is a descriptive sensitivity, not pure baseline adjustment.',
                           'Principal diagnosis and functional prognosis can still differ within broad diagnosis groups; no causal dysphagia effect is identified.',
                           'Fixed-weight model CIs omit hospital clustering, repeated admissions, coding uncertainty and selection bias.',
                           'Sparse or boundary-event strata are flagged; normal/delta intervals can be less reliable there.',
                           'No absent workbook or suppressed query is treated as zero; all queries must be explicitly available.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort',required=True,choices=['acute','rehab','both'])
    parser.add_argument('--raw-dir',type=Path,default=ROOT/'raw')
    parser.add_argument('--out-dir',type=Path,default=ROOT/'results')
    parser.add_argument('--status-only',action='store_true',help='Write availability status only; never calculate effect estimates.')
    args=parser.parse_args()
    cohorts=['acute','rehab'] if args.cohort=='both' else [args.cohort]
    status={'checked_utc':datetime.now(timezone.utc).isoformat(),'status':'available','cohorts':{},
            'effects_computed':False,'note':'Availability is not scientific validation. Missing files remain unknown. Existing result files are not refreshed by status-only or pending runs.'}
    for cohort in cohorts:
        names=expected_files(cohort)
        missing=[name for name in names if not(args.raw_dir/name).is_file()]
        originals=reference_files(cohort)
        missing_originals=[name for name in originals if not(args.raw_dir/name).is_file()]
        status['cohorts'][cohort]={'expected_files':names,'missing_files':missing,'available':len(names)-len(missing),'required':len(names),
                                  'original_reference_files':originals,'missing_original_reference_files':missing_originals}
        if missing or missing_originals:status['status']='pending'
    save(status,args.out_dir/'joint_standardization_status.json')
    print(json.dumps(status,ensure_ascii=False,indent=2))
    if args.status_only:return
    if status['status']=='pending':
        raise SystemExit(2)
    # Validate and compute every requested cohort before writing any estimates.
    results={cohort:analyze(cohort,args.raw_dir) for cohort in cohorts}
    for cohort,result in results.items():
        save(result,args.out_dir/(cohort+'_joint_standardization.json'))
        rows=[]
        for name in ['age_sex_principal_diagnosis','age_principal_diagnosis_pccl_sensitivity']:
            r=result[name]
            if r['status']!='estimated':continue
            ci=r['standardized']['rr_ci'] or [None,None]
            rows.append({'analysis':name,'population_scope':r.get('population_scope','Adults, all four sex categories'),
                         'rr':r['standardized']['rr'],'rr_ci_lower':ci[0],'rr_ci_upper':ci[1],
                         'risk_difference':r['standardized']['risk_difference'],
                         'crude_rr_same_common_support':r['crude_same_common_support_population']['rr'],
                         **r['common_support']})
        if rows:
            with (args.out_dir/(cohort+'_joint_standardization.csv')).open('w',encoding='utf-8',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    status.update(status='computed',effects_computed=True)
    save(status,args.out_dir/'joint_standardization_status.json')


if __name__=='__main__':main()
