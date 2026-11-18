"""Acute InEK single-code outcome comparisons from existing denominator exports.

Read-only input, exact filter/count validation, no missing-row zero substitution.
Standalone CLI requires Python >=3.10 and openpyxl. The default output contains
model-level estimates/statuses only. --private-audit explicitly enables detailed
local JSON, which must not be included in the public repository.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
import openpyxl

Z = 1.959963984540054
DELIVERY = 'Unterjährige Datenlieferung DRG Januar bis Dezember 2025'
AGES = {
    'age18_74': ['18-29 Jahre', '30-39 Jahre', '40-49 Jahre', '50-54 Jahre',
                 '55-59 Jahre', '60-64 Jahre', '65-74 Jahre'],
    'age75plus': ['75-79 Jahre', '80+ Jahre'],
}
MINOR = ['< 28 Tage', '28 Tage - 1. Jahr', '1-2 Jahre', '3-5 Jahre',
         '6-9 Jahre', '10-15 Jahre', '16-17 Jahre']
SEX = ['männlich', 'weiblich', 'divers', 'unbekannt']
HD = ['allhd', 'i63', 'i61']
KINDS = ['all', 'dys']
OPS = {f'{prefix}.{suffix}' for prefix in ['8-981', '8-98b']
       for suffix in [20, 21, 22, 23, 30, 31, 32, 33]}
R13 = {'R13.0', 'R13.1', 'R13.9'}
HD_CODES = {hd: {hd.upper()+'.'+str(k) for k in [0,1,2,3,4,5,6,8,9]}
            for hd in ['i63', 'i61']}
OUTCOMES = {
    'J96.00': ('Nebendiagnosen', 'Hypoxemic acute respiratory failure', 'clinical'),
    'U69.01': ('Nebendiagnosen', 'Pneumonia occurring more than 48 hours after admission, timing code', 'clinical_timing_marker'),
    'U69.04': ('Nebendiagnosen', 'Pneumonia present within 48 hours after admission, timing code', 'clinical_timing_marker'),
    'E43': ('Nebendiagnosen', 'Unspecified severe protein-energy malnutrition', 'clinical'),
    'E44.0': ('Nebendiagnosen', 'Moderate protein-energy malnutrition', 'clinical'),
    'E44.1': ('Nebendiagnosen', 'Mild protein-energy malnutrition', 'clinical'),
    'E46': ('Nebendiagnosen', 'Unspecified protein-energy malnutrition', 'clinical'),
    'E86': ('Nebendiagnosen', 'Volume depletion', 'clinical'),
    'J69.0': ('Nebendiagnosen', 'Pneumonitis due to food and vomit', 'clinical'),
    '8-701': ('Prozeduren', 'Simple endotracheal intubation', 'procedure'),
    '5-431.22': ('Prozeduren', 'Percutaneous-endoscopic gastrostomy with thread-pull technique; single code only', 'procedure'),
    '1-613': ('Prozeduren', 'FEES procedure coding', 'process_marker'),
}
UNION_CODES = ['E40', 'E41', 'E42', 'E43', 'E44.0', 'E44.1', 'E46']


def integer(value, label):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not float(value).is_integer()):
        raise ValueError(f'{label}: expected finite exact integer; got {value!r}')
    return int(value)


def count(value, label):
    value = integer(value, label)
    if value < 0:
        raise ValueError(label+': negative count')
    return value


def normalized_code(value):
    return str(value).strip().rstrip('!*')


def selection_fields(selection):
    fields = {}
    matches = list(re.finditer(r'([^();]+)\(([^()]*)\)', selection))
    for match in matches:
        name, values = match.groups(); name = name.strip()
        if name in fields:
            raise ValueError('Repeated selection field: '+name)
        fields[name] = {normalized_code(x) for x in values.split(',') if x.strip()}
    leftover = re.sub(r'([^();]+)\(([^()]*)\)', '', selection).strip(' ;\t\r\n')
    if leftover:
        raise ValueError('Unparsed selection syntax: '+leftover)
    return fields


def read_export(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb['Info'].values)
        cell = lambda row, col: rows[row-1][col-1]
        if cell(8,1) != 'Fallzahl':
            raise ValueError(path.name+': unrecognized Info layout')
        n = count(cell(8,2), path.name+' N')
        if not n:
            raise ValueError(path.name+': no positive source population')
        distributions = {}
        for name, indices, lc, vc in [
            ('sex', range(11,15), 1, 2), ('pccl', range(8,15), 7, 8),
            ('age', range(8,len(rows)+1), 10,11),
        ]:
            dist = {}
            for row in indices:
                label, fraction = cell(row,lc), cell(row,vc)
                if label is None and fraction is None:
                    continue
                if label is None or fraction is None or isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction):
                    raise ValueError(path.name+': incomplete/nonfinite '+name)
                value = fraction*n; recovered = round(value)
                if recovered < 0 or abs(value-recovered) >= 1e-6:
                    raise ValueError(path.name+': nonrecoverable '+name+' count')
                label = str(integer(label,'PCCL label')) if name == 'pccl' else str(label)
                if label in dist:
                    raise ValueError(path.name+': duplicated '+name+' label')
                dist[label] = recovered
            if sum(dist.values()) != n:
                raise ValueError(path.name+': '+name+' distribution does not partition N')
            distributions[name] = dist
        if set(distributions['age']) != set(MINOR+sum(AGES.values(),[])):
            raise ValueError(path.name+': age labels differ from design')
        if set(distributions['sex']) != set(SEX) or set(distributions['pccl']) != set(map(str,range(7))):
            raise ValueError(path.name+': sex/PCCL labels differ from design')
        tables = {}
        for sheet in ['Nebendiagnosen', 'Prozeduren']:
            vals = list(wb[sheet].values)
            if vals[0][:4] != ('Kode', 'Nebendiagnose' if sheet == 'Nebendiagnosen' else 'Prozedur', 'Fälle', 'Nennungen'):
                raise ValueError(path.name+': unexpected columns in '+sheet)
            table = {}
            for row, values in enumerate(vals[1:],2):
                if values[0] is None:
                    continue
                code = normalized_code(values[0])
                if code == '---' or code.startswith('Rest ('):
                    continue
                cases = count(values[2],f'{path.name}/{sheet}/{code}/cases')
                mentions = count(values[3],f'{path.name}/{sheet}/{code}/mentions')
                if cases > n or mentions < cases:
                    raise ValueError(path.name+': invalid case/mention count '+code)
                if code in table:
                    raise ValueError(path.name+': duplicate exact outcome code '+code)
                if (isinstance(values[4],bool) or not isinstance(values[4],(int,float))
                        or not math.isfinite(values[4]) or not 0<=values[4]<=1
                        or abs(values[4]*n-cases) >= 1e-6):
                    raise ValueError(path.name+': case proportion mismatch '+code)
                table[code] = {'cases': cases,'mentions': mentions,'label': values[1],'row': row}
            tables[sheet] = table
        return {'n': n,'selection': str(cell(2,1)), 'delivery': cell(5,1),
                'distributions': distributions,'tables': tables,
                'source': {'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                           'size_bytes':path.stat().st_size}}
    finally:
        wb.close()


def validate_filters(export, kind, age=None, hd=None):
    name = export['source']['filename']
    if export['delivery'] != DELIVERY:
        raise ValueError(name+': different delivery')
    fields = selection_fields(export['selection'])
    allowed = {'Prozeduren','Nebendiagnosen','Entlassungsgrund'}
    if age is not None:
        allowed |= {'Hauptdiagnosen','Hauptdiagnose','Altersklasse','Altersklassen','Altersgruppe'}
    if set(fields)-allowed:
        raise ValueError(name+': unexpected filters '+str(set(fields)-allowed))
    if fields.get('Prozeduren') != OPS:
        raise ValueError(name+': OPS cohort differs')
    if fields.get('Nebendiagnosen',set()) != (R13 if kind == 'dys' else set()):
        raise ValueError(name+': R13 secondary-diagnosis definition differs')
    if fields.get('Entlassungsgrund',set()):
        raise ValueError(name+': unexpected discharge-reason restriction')
    if age is None:
        return
    hdf = [f for f in ['Hauptdiagnose','Hauptdiagnosen'] if f in fields]
    if len(hdf)>1:
        raise ValueError(name+': multiple principal-diagnosis fields')
    actual_hd = fields[hdf[0]] if hdf else set()
    if actual_hd != (set() if hd == 'allhd' else HD_CODES[hd]):
        raise ValueError(name+': full explicit I63/I61 diagnosis selection required')
    af = [f for f in ['Altersklasse','Altersklassen','Altersgruppe'] if f in fields]
    if len(af)!=1 or fields[af[0]] != set(AGES[age]):
        raise ValueError(name+': adult age selection differs')
    if sum(export['distributions']['age'][x] for x in AGES[age]) != export['n']:
        raise ValueError(name+': age selection does not match case distribution')


def contrast(ed, nd, ec, nc):
    if nd <= 0 or nc <= 0 or not (0 <= ed <= nd and 0 <= ec <= nc):
        raise ValueError('Invalid binary contrast')
    pd, pc = ed/nd, ec/nc
    vard = pd*(1-pd)/nd; varc = pc*(1-pc)/nc
    rr = pd/pc if pc else None; ci = None
    if pd > 0 and pc > 0:
        se = math.sqrt(1/ed-1/nd+1/ec-1/nc)
        ci = [rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    se_rd = math.sqrt(vard+varc)
    return {'dys_events':ed,'dys_n':nd,'no_dys_events':ec,'no_dys_n':nc,
            'dys_rate':pd,'no_dys_rate':pc,'rr':rr,'rr_ci95':ci,
            'risk_difference':pd-pc,'risk_difference_ci95':[pd-pc-Z*se_rd,pd-pc+Z*se_rd],
            'boundary_probability':pd in [0,1] or pc in [0,1],
            'sparse_event_or_nonevent':min(ed,nd-ed,ec,nc-ec)<5}


def validate_and_cell(age, hd, nt, nd, et=None, ed=None):
    for value in [nt,nd]:
        count(value,'reconstructed denominator')
    nc=nt-nd
    if nc < 0:
        raise ValueError('Negative reconstructed comparator denominator')
    cell={'age_band':age,'principal_diagnosis':hd,'all_n':nt,'dys_n':nd,'no_dys_n':nc}
    if et is not None and ed is not None:
        ec=et-ed
        if min(et,ed,ec)<0 or et>nt or ed>nd or ec>nc:
            raise ValueError('Invalid reconstructed event cell: '+str(cell))
        cell.update(all_events=et,dys_events=ed,no_dys_events=ec)
    return cell


def make_cells(exports, sheet=None, code=None):
    result=[]
    for age in AGES:
        raw={}
        for hd in HD:
            t,d=exports[age,hd,'all'],exports[age,hd,'dys']
            if code is None:
                raw[hd]={'nt':t['n'],'nd':d['n']}
            else:
                if code not in t['tables'][sheet] or code not in d['tables'][sheet]:
                    raw[hd]=None;continue
                raw[hd]={'nt':t['n'],'nd':d['n'],'et':t['tables'][sheet][code]['cases'],
                         'ed':d['tables'][sheet][code]['cases']}
        if all(raw[x] is not None for x in HD):
            raw['otherhd']={k:raw['allhd'][k]-raw['i63'][k]-raw['i61'][k] for k in raw['allhd']}
        else:raw['otherhd']=None
        for hd in ['i63','i61','otherhd']:
            r=raw[hd]
            if r is not None:
                result.append(validate_and_cell(age,hd,**r))
    return result


def standardize(cells):
    if len(cells)!=6:
        raise ValueError('Complete six-cell event grid required')
    included=[dict(c) for c in cells if c['dys_n']>0 and c['no_dys_n']>0]
    excluded=[dict(c,reason='No denominator support in both exposure groups') for c in cells
              if c['dys_n']==0 or c['no_dys_n']==0]
    nt=sum(c['all_n'] for c in included);nd=sum(c['dys_n'] for c in included);nc=nt-nd
    full={k:sum(c[k] for c in cells) for k in ['all_n','dys_n','no_dys_n']}
    common={'included_strata':len(included),'excluded_strata':len(excluded),
            'all_n':nt,'dys_n':nd,'no_dys_n':nc,
            'all_coverage':nt/full['all_n'] if full['all_n'] else None,
            'dys_coverage':nd/full['dys_n'] if full['dys_n'] else None,
            'no_dys_coverage':nc/full['no_dys_n'] if full['no_dys_n'] else None}
    if not included:
        return {'status':'not_estimable_no_common_support','common_support':common,'excluded_strata':excluded}
    pd=pc=vd=vc=0.0
    for c in included:
        w=c['all_n']/nt;p=c['dys_events']/c['dys_n'];q=c['no_dys_events']/c['no_dys_n']
        pd+=w*p;pc+=w*q;vd+=w*w*p*(1-p)/c['dys_n'];vc+=w*w*q*(1-q)/c['no_dys_n']
        c.update(weight=w,dys_rate=p,no_dys_rate=q,boundary_probability=p in [0,1] or q in [0,1],
                 sparse_event_or_nonevent=min(c['dys_events'],c['dys_n']-c['dys_events'],
                                             c['no_dys_events'],c['no_dys_n']-c['no_dys_events'])<5)
    rr=pd/pc if pc else None;ci=None
    if pd>0 and pc>0:
        se=math.sqrt(vd/pd**2+vc/pc**2);ci=[rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    serd=math.sqrt(vd+vc)
    return {'status':'estimated','common_support':common,'selected_adult_population':full,
            'strata':included,'excluded_strata':excluded,
            'sparse_strata':sum(c['sparse_event_or_nonevent'] for c in included),
            'boundary_strata':sum(c['boundary_probability'] for c in included),
            'sparse_reference_weight':sum(c['weight'] for c in included if c['sparse_event_or_nonevent']),
            'boundary_reference_weight':sum(c['weight'] for c in included if c['boundary_probability']),
            'crude_same_supported_adult_population':contrast(sum(c['dys_events'] for c in included),nd,
                                                           sum(c['no_dys_events'] for c in included),nc),
            'standardized':{'dys_rate':pd,'no_dys_rate':pc,'rr':rr,'rr_ci95':ci,
                            'risk_difference':pd-pc,'risk_difference_ci95':[pd-pc-Z*serd,pd-pc+Z*serd],
                            'dys_rate_ci95':[pd-Z*math.sqrt(vd),pd+Z*math.sqrt(vd)],
                            'no_dys_rate_ci95':[pc-Z*math.sqrt(vc),pc+Z*math.sqrt(vc)]}}


def analyze(data_root):
    refs={kind:read_export(data_root/f'acute_{kind}_2025.xlsx') for kind in KINDS}
    for kind,e in refs.items():validate_filters(e,kind)
    if refs['all']['n']!=279277 or refs['dys']['n']!=33643:
        raise ValueError('Unrestricted reference cohort totals differ from locked design')
    exports={}
    for age in AGES:
        for hd in HD:
            for kind in KINDS:
                e=read_export(data_root/f'acute_joint_{age}_{hd}_{kind}_2025.xlsx')
                validate_filters(e,kind,age,hd);exports[age,hd,kind]=e
    checks={}
    for kind,reference in refs.items():
        adult_expected=sum(reference['distributions']['age'][a] for a in sum(AGES.values(),[]))
        actual=sum(exports[age,'allhd',kind]['n'] for age in AGES)
        if actual!=adult_expected:raise ValueError('Adult totals do not reproduce original reference')
        for age,labels in AGES.items():
            for label in labels:
                if exports[age,'allhd',kind]['distributions']['age'][label] != reference['distributions']['age'][label]:
                    raise ValueError('Native age counts do not reproduce original reference')
        checks[kind]={'original_n':reference['n'],'adult_expected':adult_expected,'adult_observed':actual,
                      'all_native_age_counts_verified':True}
    # Nested exposure and mutually exclusive I63/I61 populations must hold at
    # every exported demographic marginal, even though they are not adjustment
    # dimensions in this two-factor extension.
    for age in AGES:
        for distribution in ['age','sex','pccl']:
            labels=exports[age,'allhd','all']['distributions'][distribution]
            for label in labels:
                vals={hd:{kind:exports[age,hd,kind]['distributions'][distribution][label] for kind in KINDS} for hd in HD}
                vals['otherhd']={kind:vals['allhd'][kind]-vals['i63'][kind]-vals['i61'][kind] for kind in KINDS}
                for hd,v in vals.items():validate_and_cell(age,hd,v['all'],v['dys'])
    denom_cells=make_cells(exports)
    if len(denom_cells)!=6:raise ValueError('Incomplete denominator partition')
    results={}
    for code,(sheet,label,role) in OUTCOMES.items():
        item={'code':code,'label':label,'role':role,'sheet':sheet,
              'definition':'Hospital episode with this exact secondary-diagnosis/procedure code; not code mentions'}
        trow=refs['all']['tables'][sheet].get(code);drow=refs['dys']['tables'][sheet].get(code)
        if trow is not None and drow is not None:
            item['source_label']=trow['label']
            item['baseline_crude']={'status':'estimated','population':'Original unrestricted cohort, including 22 under-18 episodes',
                                     **contrast(drow['cases'],refs['dys']['n'],trow['cases']-drow['cases'],refs['all']['n']-refs['dys']['n'])}
        else:
            item['baseline_crude']={'status':'not_estimable_missing_row','missing_exports':[refs[k]['source']['filename'] for k in KINDS if code not in refs[k]['tables'][sheet]]}
        missing=[e['source']['filename'] for e in exports.values() if code not in e['tables'][sheet]]
        cells=make_cells(exports,sheet,code)
        known={(c['age_band'],c['principal_diagnosis']) for c in cells}
        known_nt=sum(c['all_n'] for c in denom_cells if (c['age_band'],c['principal_diagnosis']) in known)
        availability={'required_source_rows':12,'available_source_rows':12-len(missing),
                      'complete_event_strata':len(cells),'required_event_strata':6,
                      'all_case_coverage_of_known_strata':known_nt/sum(c['all_n'] for c in denom_cells),
                      'missing_exports':missing}
        # Do not select the analyzable subset by visibility of outcome rows.
        if missing or len(cells)!=6:
            item['age_principal_diagnosis']={'status':'not_estimable_incomplete_event_grid',
                                            'availability':availability,'estimate':None,
                                            'reason':'One or more source outcome rows are absent/suppressed; not assumed zero and no outcome-dependent complete-case standardization performed'}
        else:
            # Adult event totals must be nested in the unrestricted original.
            for kind,event_key in [('all','all_events'),('dys','dys_events')]:
                adult_events=sum(c[event_key] for c in cells)
                refrow=refs[kind]['tables'][sheet].get(code)
                if refrow is not None:
                    pediatric_events=refrow['cases']-adult_events
                    pediatric_n=refs[kind]['n']-checks[kind]['adult_observed']
                    if not 0<=pediatric_events<=pediatric_n:
                        raise ValueError(code+': adult events do not reconcile with original all-age reference')
            item['age_principal_diagnosis']={**standardize(cells),'availability':availability,
                                             'adjusted_factors':['age_band','principal_diagnosis'],
                                             'not_adjusted_for':['sex','PCCL','NIHSS']}
        results[code]=item
    results['MALNUT_UNION']={
        'role':'clinical','label':'Recorded protein-energy malnutrition, specified code union',
        'codes':UNION_CODES,'excluded_code':'E45 (developmental delay following protein-energy malnutrition)',
        'status':'requires_direct_union_exports','estimate':None,
        'reason':'Code rows are non-exclusive. Exact episode unions and event-specific sex/PCCL strata cannot be obtained by adding separate code counts.',
        'required_query':'OR union within further secondary diagnoses; AND with fixed cohort, adult age and selected principal diagnosis; retain separate R13 secondary-diagnosis filter for exposed queries',
    }
    return {'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'analysis':'Acute single-code outcomes: crude and age-by-principal-diagnosis direct standardization',
            'delivery':DELIVERY,'software':{'openpyxl':openpyxl.__version__},
            'reference_checks':checks,'sources':[{'selection':e['selection'],'delivery':e['delivery'],'n':e['n'],**e['source']} for e in list(refs.values())+list(exports.values())],
            'denominator_strata':denom_cells,'outcomes':results,
            'warnings':['Post hoc exploratory extension; no causal effect is identified.',
                        'All 95% confidence intervals are nominal and are not adjusted for multiple comparisons.',
                        'Recorded secondary diagnoses/procedures lack onset timing and do not establish a dysphagia complication.',
                        'Pooled adult common-support reference weights are fixed. Confidence intervals assume independent episodes; no hospital clustering or coding uncertainty is covered.',
                        'No simultaneous sex/PCCL adjustment. Missing and suppressed outcome rows remain unknown.',
                        '1-613 is a diagnostic process marker. 5-431.22 is a single PEG technique, not all PEG or enteral nutrition.',
                        'Detailed JSON strata are private audit data; disclosure review is needed before public release.']}


def summary_rows(result):
    rows=[]
    for code,item in result['outcomes'].items():
        if code=='MALNUT_UNION':
            rows.append({'outcome':code,'label':item['label'],'role':item['role'],'analysis':'direct_union','status':item['status']});continue
        for name in ['baseline_crude','age_principal_diagnosis']:
            a=item[name];row={'outcome':code,'label':item['label'],'role':item['role'],'analysis':name,'status':a['status']}
            if a['status']=='estimated':
                v=a if name=='baseline_crude' else a['standardized']
                row.update({k:v.get(k) for k in ['dys_events','dys_n','no_dys_events','no_dys_n','dys_rate','no_dys_rate','rr','risk_difference']})
                for k in ['rr','risk_difference']:
                    ci=v.get(k+'_ci95');row[k+'_ci_lower']=ci[0] if ci else None;row[k+'_ci_upper']=ci[1] if ci else None
                if name!='baseline_crude':
                    row.update(a['common_support']);row.update({k:a[k] for k in ['sparse_strata','boundary_strata','sparse_reference_weight','boundary_reference_weight']})
                    row['crude_rr_same_supported_adult_population']=a['crude_same_supported_adult_population']['rr']
            if 'availability' in a:
                row.update({k:a['availability'][k] for k in ['required_source_rows','available_source_rows','complete_event_strata','all_case_coverage_of_known_strata']})
                row['missing_exports']=';'.join(a['availability']['missing_exports'])
            rows.append(row)
    return rows


def public_summary_rows(result):
    """Whitelist model-level columns; omit event-cell/source-file disclosure."""
    keep=['outcome','label','role','analysis','status','all_n','dys_n','no_dys_n',
          'dys_rate','no_dys_rate','rr','rr_ci_lower','rr_ci_upper',
          'risk_difference','risk_difference_ci_lower','risk_difference_ci_upper',
          'crude_rr_same_supported_adult_population']
    rows=[]
    for original in summary_rows(result):
        row={key:original.get(key) for key in keep}
        name=original['analysis']
        row['population']='Original unrestricted acute cohort' if name=='baseline_crude' else 'Adults aged 18+, pooled common-support population' if name=='age_principal_diagnosis' else 'Not yet estimated'
        row['adjusted_factors']='None' if name=='baseline_crude' else 'Age band and principal diagnosis' if name=='age_principal_diagnosis' else 'Not yet estimated'
        if name=='baseline_crude' and original.get('status')=='estimated':
            row['all_n']=original['dys_n']+original['no_dys_n']
        if original['status']=='estimated':
            note='Nominal approximate 95% intervals; no multiplicity or hospital-cluster adjustment.'
            if original.get('sparse_strata',0):
                note+=' Sparse event/non-event strata are present.'
            if original.get('boundary_strata',0):
                note+=' Boundary-probability strata are present; interval calibration is uncertain.'
            row['interval_note']=note
        elif original['status']=='not_estimable_incomplete_event_grid':
            row['interval_note']='Missing or suppressed source outcome rows; no adjusted estimate and no zero imputation.'
        else:
            row['interval_note']='Not estimated; no inferred event counts or interval.'
        rows.append(row)
    return rows


METHODS='''# Existing acute binary-outcome extension

These analyses are a post hoc exploratory extension. All reported 95% confidence intervals are nominal and have not been adjusted for multiple comparisons. Individual endpoint estimates should therefore be interpreted as exploratory rather than as confirmatory hypothesis tests.

The script reads the two original unrestricted acute cohort exports and the twelve previously acquired adult denominator exports. It validates the exact 2025 delivery, OPS union, selected R13 secondary diagnoses, full explicit I63/I61 endcodes, both adult age selections, case counts, demographic partitions and reconciliation with the original cohort. Workbook hashes are retained only if the optional private audit is requested; the source workbooks are never modified. Case counts, not mentions, define events. Obtain workbooks separately in accordance with the provider's conditions. This script only reads local workbooks and performs no browser, download or network operation.

The updated exact-code set also includes hypoxemic acute respiratory failure (J96.00) and the pneumonia timing markers U69.01 and U69.04. Ten of the twelve individual codes have complete six-stratum event grids in this snapshot; E44.0 and E44.1 remain non-estimable because source rows are missing or suppressed. The same age-by-principal-diagnosis specification, reference weights, risk-ratio and risk-difference methods are used for every complete exact-code outcome. U69.01 and U69.04 describe coded timing relative to hospital admission, not timing relative to dysphagia; they are related timing markers and not independent additional complications. J96.00 is hypoxemic acute respiratory failure, not every respiratory-failure subtype.

The strata are age 18–74 or 75+ crossed with I63, I61 or all other principal diagnoses. The residual diagnosis group is recovered by subtracting the disjoint I63 and I61 populations from all diagnoses. Non-dysphagia counts and events are recovered by subtracting dysphagia from the same total. All nested counts and event bounds are checked. Each outcome must have its exact code row in all twelve source exports before a primary six-stratum analysis is produced. A missing row is unknown, never zero; incomplete outcomes receive a status without an adjusted estimate. No outcome-dependent restriction to visible rows is used.

For supported strata, w_g=N_total,g/sum(N_total,g). Standardized risk is sum(w_g p_j,g), with fixed-weight binomial variance sum(w_g^2 p_j,g(1-p_j,g)/N_j,g). The standardized risk ratio uses a log-delta 95% interval, and the risk difference uses a normal 95% interval. Unsupported denominator strata are identified before looking at outcomes; coverage is reported. The crude comparator is recalculated on exactly the supported adult population. Zero-event strata remain included, and zero/boundary probabilities plus event/non-event counts below five are flagged. No continuity correction is applied; an undefined ratio or interval remains null.

Unrestricted crude analyses use 279,277 hospital episodes, including 22 below age 18; their denominators are not the adult reference used for standardization. Adult analyses include 279,255 episodes before any common-support exclusions. These are separate hospital episodes, not identified unique patients. The intervals do not cover repeated admissions, hospital clustering, coding error or missing confounders. Broad age bands leave residual age confounding. There is no sex, PCCL or NIHSS adjustment in this extension.

The malnutrition union is specified as E40, E41, E42, E43, E44.0, E44.1 or E46. E45 denotes developmental delay and is excluded from this nutritional-status endpoint. The union is not computed by summing overlapping secondary-diagnosis rows and remains pending direct union exports. E43 alone is unspecified severe protein-energy malnutrition, not all malnutrition. E86 records volume depletion rather than a validated low-intake dehydration assessment. J69.0 is the defined pneumonitis code. OPS 8-701 records simple endotracheal intubation, not all ventilation; OPS 5-431.22 records one PEG technique, not all gastrostomies or enteral nutrition. FEES (1-613) is explicitly a diagnostic process marker. Timing relative to dysphagia is unknown, so these are coding associations, not proven incident complications or treatment effects.

The published CSV contains one row per outcome/model or pending status. It omits event counts, individual strata, small-cell diagnostics, source filenames, raw-workbook hash mappings and local paths. Denominators and statistical estimates are model-level aggregates; probabilities and risk differences use units from 0 to 1. The interval note retains sparse/boundary qualifications without exposing the underlying cells. Original exports are not redistribution-authorized by this script.

Run: `python outcomes_analyze_existing_binary.py --data-root /path/to/private_raw --out-dir /path/to/private_results`

The default outputs are `outcomes_existing_binary_outcomes.csv` and `OUTCOMES_BINARY_METHODS.md`. The optional `--private-audit /path/to/private_results/audit.json` writes detailed source hashes and reconstructed strata locally; this audit must remain private and is excluded from the repository bundle. Statistical calculations are unchanged from the development analysis; only output disclosure and portable file naming differ.
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--private-audit',type=Path,help='Optional detailed local audit; never publish this file')
    args=ap.parse_args();result=analyze(args.data_root.resolve())
    args.out_dir.mkdir(parents=True,exist_ok=True)
    if args.private_audit:
        args.private_audit.parent.mkdir(parents=True,exist_ok=True)
        args.private_audit.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    rows=public_summary_rows(result);columns=list(dict.fromkeys(k for row in rows for k in row))
    with (args.out_dir/'outcomes_existing_binary_outcomes.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    (args.out_dir/'OUTCOMES_BINARY_METHODS.md').write_text(METHODS,encoding='utf8')
    print(json.dumps({'outputs':str(args.out_dir.resolve()),'outcomes':{code:item.get('status',item.get('age_principal_diagnosis',{}).get('status')) for code,item in result['outcomes'].items()}},ensure_ascii=True))


if __name__=='__main__':main()
