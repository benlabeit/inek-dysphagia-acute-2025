"""Functional-code sensitivity analyses from aggregate InEK exports.

Portable usage: python analyze_functional_sensitivity.py --cohort acute
Optional --data-root and --out-dir allow separate source/output locations.
Every planned instrument category is retained, including unknown/sparse cells.
No principal diagnosis, manuscript, source workbook or repository is modified.
"""
from pathlib import Path
import argparse, csv, hashlib, json, math

Z=1.959963984540054
INSTRUMENTS={
 'U50_motor_FIM':{'domain':'motor function','instrument':'Motor FIM',
   'codes':['U50.01','U50.11','U50.21','U50.31','U50.41','U50.51'],
   'score_bands':['85-91','69-84','59-68','43-58','31-42','13-30']},
 'U51_cognitive_FIM':{'domain':'cognitive function','instrument':'Cognitive FIM',
   'codes':['U51.01','U51.11','U51.21'],'score_bands':['30-35','11-29','5-10']},
 'U51_MMSE':{'domain':'cognitive function','instrument':'MMSE',
   'codes':['U51.02','U51.12','U51.22'],'score_bands':['24-30','17-23','0-16']},
}
LIMITATIONS=[
 'These are exploratory comparisons conditional on an explicitly recorded functional code, not joint multivariable adjustment or NIHSS adjustment.',
 'All planned categories are reported. Absent export rows are unknown, not zero. A displayed total minus a displayed subgroup may recover a zero or small cell; these are flagged.',
 'Instrument categories and instruments are not assumed to form a mutually exclusive episode partition; no sums are presented as verified unique coverage.',
 'Coverage bounds are set-theoretic bounds from observed marginals, not estimates or confidence intervals. Between-instrument overlap is unknown.',
 'The code-absent complement includes unassessed/unrecorded cases and other severity categories; it is not a normal-function or low-severity group.',
 'The coding assessment cannot be aligned with dysphagia onset or the outcome using these exports. Functional scales may include feeding-related dependence and are not pure baseline neurological injury measures.',
 'Conditional comparisons can be affected by measurement, residual confounding and selection; variation across code categories is not proof of a causal interaction.',
 'CI models assume independent episodes and omit repeated admissions, hospital clustering, coding error and multiple-testing uncertainty.',
 'Sparse event or non-event cells make log-Wald approximations unstable. No continuity correction is applied when either event count is zero; RR CI is then unavailable.',
 'Pneumonia denotes the exact J12-J18 secondary-diagnosis union, not J69.0 or the combined pulmonary endpoint.',
]


def wilson(x,n):
 p=x/n;den=1+Z*Z/n;c=(p+Z*Z/(2*n))/den
 h=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
 return [c-h,c+h]


def compare(a,n,b,m):
 assert isinstance(a,int) and isinstance(b,int) and 0<=a<=n and 0<=b<=m
 if n<=0 or m<=0:return {'status':'not_estimable_empty_group','dys_events':a,'dys_n':n,'no_dys_events':b,'no_dys_n':m}
 p,q=a/n,b/m;se=math.sqrt(p*(1-p)/n+q*(1-q)/m)
 r={'status':'exact_counts','dys_events':a,'dys_n':n,'no_dys_events':b,'no_dys_n':m,
    'dys_rate':p,'no_dys_rate':q,'dys_rate_ci':wilson(a,n),'no_dys_rate_ci':wilson(b,m),
    'risk_difference':p-q,'risk_difference_ci':[p-q-Z*se,p-q+Z*se],
    'small_event_cell':min(a,b)<5,'small_non_event_cell':min(n-a,m-b)<5,
    'sparse_group':min(n,m)<20,'rr':None,'rr_ci':None}
 if a>0 and b>0:
  rr=p/q;selog=math.sqrt(1/a-1/n+1/b-1/m)
  r.update(rr=rr,rr_ci=[rr*math.exp(-Z*selog),rr*math.exp(Z*selog)])
 else:r['rr_unavailable_reason']='At least one event count is zero; no continuity correction used.'
 return r


def load_export(root,cohort,kind):
 stem=f'{cohort}_{kind}_2025';p=root/'parsed'/(stem+'.json');raw=root/'raw'/(stem+'.xlsx')
 if p.exists():
  e=json.loads(p.read_text(encoding='utf-8'))
  if raw.exists():assert hashlib.sha256(raw.read_bytes()).hexdigest()==e['source']['sha256'],f'Stale parsed data: {stem}'
 else:
  from analyze_acute_exports import parse_inek
  e=parse_inek(raw)
 rows={r['code'].rstrip('!*'):r for r in e['tables']['Nebendiagnosen'] if not r['is_rest']}
 assert len(rows)==len([r for r in e['tables']['Nebendiagnosen'] if not r['is_rest']])
 return e,rows


def coverage(codes,maps,ns):
 out={}
 for group in ['all','dys','no_dys']:
  counts={}
  for code in codes:
   if group=='no_dys':
    v=maps['all'].get(code);d=maps['dys'].get(code)
    counts[code]=v['cases']-d['cases'] if v is not None and d is not None else None
   else:counts[code]=maps[group][code]['cases'] if code in maps[group] else None
  known=[v for v in counts.values() if v is not None]
  complete=len(known)==len(codes);lo=max(known,default=0)
  hi=min(sum(known),ns[group]) if complete else ns[group]
  out[group]={'n':ns[group],'code_case_counts':counts,'all_planned_codes_visible':complete,
              'code_case_fractions':{k:(v/ns[group] if v is not None else None) for k,v in counts.items()},
              'sum_of_visible_code_case_counts':sum(known),
              'unique_union_count_bounds':[lo,hi],'unique_union_fraction_bounds':[lo/ns[group],hi/ns[group]],
              'unique_union_not_identified':True,
              'sum_is_not_verified_unique_coverage':True}
 return out


def analyze(root,cohort):
 names=['all','dys','all_death','dys_death','all_pneumonia','dys_pneumonia']
 inputs={k:load_export(root,cohort,k) for k in names}
 es={k:v[0] for k,v in inputs.items()};maps={k:v[1] for k,v in inputs.items()}
 assert len({e['delivery'] for e in es.values()})==1
 ns={'all':es['all']['n'],'dys':es['dys']['n'],'no_dys':es['all']['n']-es['dys']['n']}
 out={'cohort':cohort,'cohort_n':ns,'delivery':es['all']['delivery'],
      'source_manifest':{k:{'file':'raw/'+f'{cohort}_{k}_2025.xlsx','sha256':e['source']['sha256'],'n':e['n'],'selection':e['selection']} for k,e in es.items()},
      'coverage_by_instrument':{},'analyses':[]}
 for inst,definition in INSTRUMENTS.items():
  out['coverage_by_instrument'][inst]=coverage(definition['codes'],maps,ns)
  for code,band in zip(definition['codes'],definition['score_bands']):
   base_all=maps['all'].get(code);base_d=maps['dys'].get(code)
   label=next((m[code]['label'] for m in maps.values() if code in m),None)
   for outcome in ['death','pneumonia']:
    keys=['all','dys','all_'+outcome,'dys_'+outcome]
    cells={k:maps[k][code]['cases'] if code in maps[k] else None for k in keys}
    missing=[k for k,v in cells.items() if v is None]
    row={'instrument':inst,'code':code,'score_band':band,'code_label':label,'outcome':outcome,
         'source_code_counts':cells,'missing_rows':missing,
         'status':'exact_counts' if not missing else 'unknown_due_to_absent_export_row'}
    if not missing:
     t,d,te,de=[cells[k] for k in keys]
     assert 0<=d<=t<=ns['all'] and 0<=de<=te
     row['code_present']=compare(de,d,te-de,t-d)
     row['code_absent']=compare(es['dys_'+outcome]['n']-de,ns['dys']-d,
        (es['all_'+outcome]['n']-es['dys_'+outcome]['n'])-(te-de),ns['no_dys']-(t-d))
     assert row['code_present']['dys_events']+row['code_absent']['dys_events']==es['dys_'+outcome]['n']
     assert row['code_present']['no_dys_events']+row['code_absent']['no_dys_events']==es['all_'+outcome]['n']-es['dys_'+outcome]['n']
    out['analyses'].append(row)
 return out


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cohort',choices=['all','acute','rehab'],default='all')
 ap.add_argument('--data-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--out-dir',type=Path)
 args=ap.parse_args();dest=args.out_dir or args.data_root/'results';dest.mkdir(parents=True,exist_ok=True)
 cohorts=['acute','rehab'] if args.cohort=='all' else [args.cohort]
 result={'definitions':INSTRUMENTS,'analysis_type':'Exploratory single-functional-code conditional association',
         'ci_method':'Wilson rate intervals; log-Wald RR intervals; Wald risk-difference intervals; independent episodes.',
         'limitations':LIMITATIONS,'cohorts':{c:analyze(args.data_root,c) for c in cohorts}}
 stem='functional_sensitivity' if args.cohort=='all' else f'{args.cohort}_functional_sensitivity'
 (dest/(stem+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
 rows=[]
 for cohort,cr in result['cohorts'].items():
  for r in cr['analyses']:
   for membership in ['code_present','code_absent']:
    row={k:r[k] for k in ['instrument','code','score_band','code_label','outcome']}
    row.update(cohort=cohort,membership=membership,status=r['status'],missing_rows=';'.join(r['missing_rows']))
    for k,v in r.get(membership,{}).items():
     if isinstance(v,list):row[k+'_lower'],row[k+'_upper']=v
     else:row[k]=v
    rows.append(row)
 fields=list(dict.fromkeys(k for row in rows for k in row))
 with (dest/(stem+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
 print(json.dumps({'json':str(dest/(stem+'.json')),'csv':str(dest/(stem+'.csv')),
   'planned_code_outcome_rows':{c:len(r['analyses']) for c,r in result['cohorts'].items()},
   'exact_code_outcome_rows':{c:sum(r['status']=='exact_counts' for r in x['analyses']) for c,x in result['cohorts'].items()}},indent=2))


if __name__=='__main__':main()
