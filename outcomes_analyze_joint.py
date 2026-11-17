"""Acute InEK diagnosis outcomes: observed age-sex-diagnosis and age-diagnosis-PCCL standardization.

This post hoc extension is specified before additional outcome-filtered exports.
Missing/suppressed exports are unknown; no estimates are computed for an incomplete
endpoint. The two three-factor models are separate; sex and PCCL are not jointly
available. Each event export must be the same cohort restricted by the endpoint.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,json,math,re
import openpyxl
from outcomes_standardization_core import read_info as core_read_info,standardize,contrast,QUERY_AGES,SEX_LABELS,MINOR_AGES

ROOT=Path(__file__).resolve().parent
DELIVERY='Unterjährige Datenlieferung DRG Januar bis Dezember 2025'
HD=['allhd','i63','i61']
POPULATIONS=['all','dys']
HD_CODES={h:[h.upper()+'.'+str(k) for k in [0,1,2,3,4,5,6,8,9]] for h in ['i63','i61']}
OPS=[p+'.'+str(k) for p in ['8-981','8-98b'] for k in [20,21,22,23,30,31,32,33]]
R13=['R13.0','R13.1','R13.9']
PNEUMONIA=['J12.0','J12.1','J12.2','J12.3','J12.8','J12.9','J13','J14',
 'J15.0','J15.1','J15.2','J15.3','J15.4','J15.5','J15.6','J15.7','J15.8','J15.9',
 'J16.0','J16.8','J17.0','J17.1','J17.2','J17.3','J17.8','J18.0','J18.1','J18.2','J18.8','J18.9']
ENDPOINTS={
 'pneumonia':{'label':'Coded pneumonia, J12-J18 secondary-diagnosis union','codes':PNEUMONIA,'role':'clinical outcome'},
 'aspiration_pneumonitis':{'label':'Coded pneumonitis/pneumonia due to food and vomit, J69.0 secondary diagnosis','codes':['J69.0'],'role':'clinical outcome'},
 'pulmonary_union':{'label':'Coded pneumonia or aspiration-related pneumonitis, J12-J18 or J69.0 unique-case union','codes':PNEUMONIA+['J69.0'],'role':'overlapping clinical composite; not independent of component outcomes'},
 'malnutrition_union':{'label':'Coded energy/protein malnutrition, E40-E44 or E46 secondary-diagnosis union','codes':['E40','E41','E42','E43','E44.0','E44.1','E46'],'role':'clinical outcome',
  'exclusion':'E45 developmental retardation following protein-energy malnutrition is excluded from this adult current-malnutrition definition; E64.0 sequelae, R64 cachexia and Z-codes are not substituted.'},
 'volume_depletion':{'label':'Coded volume depletion, E86 secondary diagnosis','codes':['E86'],'role':'clinical outcome; not specific for low-intake dehydration'},
 'severe_malnutrition':{'label':'Coded unspecified severe protein-energy malnutrition, E43 secondary diagnosis','codes':['E43'],'role':'secondary sensitivity and continuity with original manuscript; subset of malnutrition_union'}
}
MODELS={
 'age_sex_principal_diagnosis':'sex',
 'age_principal_diagnosis_pccl_sensitivity':'pccl',
 'age_principal_diagnosis':'total'
}

def save(obj,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def denominator_name(age,hd,pop):return f'acute_joint_{age}_{hd}_{pop}_2025.xlsx'
def event_name(endpoint,age,hd,pop):return f'acute_outcome_{endpoint}_{age}_{hd}_{pop}_2025.xlsx'
def reference_name(endpoint,pop):
 if endpoint=='pneumonia':return f'acute_{pop}_pneumonia_2025.xlsx'
 return event_name(endpoint,'allages','allhd',pop)

def selection_fields(text):
 """Parse the complete displayed query, rejecting unparsed or duplicate fields."""
 pattern=re.compile(r'\s*([^();]+?)\s*\(([^()]*)\)\s*;?')
 fields={}; pos=0
 for m in pattern.finditer(text):
  if text[pos:m.start()].strip(' ;\t\r\n'):raise ValueError('Unparsed query text')
  name=m.group(1).strip()
  if name in fields:raise ValueError('Duplicate query field: '+name)
  codes=[v.strip().rstrip('!*') for v in m.group(2).split(',') if v.strip()]
  if len(set(codes))!=len(codes):raise ValueError('Duplicate query value: '+name)
  fields[name]=set(codes);pos=m.end()
 if text[pos:].strip(' ;\t\r\n'):raise ValueError('Unparsed query suffix')
 return fields

def read_info(path):
 # Explicit query counts must be positive. Suppression/zero-query handling requires
 # separate, source-backed provenance, never a synthetic zero workbook.
 wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
 try:
  rows=list(wb['Info'].values)
 finally:wb.close()
 for indices,lc,vc in [(range(11,15),1,2),(range(8,15),7,8),(range(8,len(rows)+1),10,11)]:
  for row in indices:
   label,fraction=rows[row-1][lc-1],rows[row-1][vc-1]
   if label is None and fraction is None:continue
   if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or not 0<=fraction<=1:
    raise ValueError(path.name+': missing, suppressed, or invalid source proportion')
 e=core_read_info(path)
 if not isinstance(e['delivery'],str):raise ValueError('Missing delivery')
 for distribution in e['distributions'].values():
  if any(isinstance(n,bool) or not isinstance(n,int) or n<0 for n in distribution.values()):
   raise ValueError('Invalid recovered count')
 return e

def validate_export(e,age,hd,pop,endpoint=None):
 if e['delivery']!=DELIVERY:raise ValueError('Different InEK delivery: '+e['source']['path'])
 f=selection_fields(e['selection'])
 empty_only_procedure_fields={'weitere Prozeduren','weitere Prozedur','weitereProzedur'}
 allowed={'Prozeduren','Nebendiagnosen','weitere Nebendiagnosen','Hauptdiagnosen','Hauptdiagnose','Altersklasse','Altersklassen','Altersgruppe','Entlassungsgrund'}|empty_only_procedure_fields
 if set(f)-allowed:raise ValueError('Unexpected query filter: '+str(sorted(set(f)-allowed)))
 if f.get('Entlassungsgrund',set()):raise ValueError('Unexpected nonempty discharge filter')
 if any(f.get(k,set()) for k in empty_only_procedure_fields):raise ValueError('Unexpected nonempty further-procedure filter')
 if f.get('Prozeduren')!=set(OPS):raise ValueError('OPS cohort differs')
 if f.get('Nebendiagnosen',set())!=(set(R13) if pop=='dys' else set()):raise ValueError('R13 exposure definition differs')
 if f.get('weitere Nebendiagnosen',set())!=(set(ENDPOINTS[endpoint]['codes']) if endpoint else set()):raise ValueError('Outcome must be exact separate further-secondary-diagnosis union')
 h=[k for k in ['Hauptdiagnosen','Hauptdiagnose'] if k in f]
 if len(h)>1:raise ValueError('Duplicate principal-diagnosis selectors')
 if (f[h[0]] if h else set())!=(set(HD_CODES[hd]) if hd!='allhd' else set()):raise ValueError('Principal diagnosis definition differs')
 a=[k for k in ['Altersklasse','Altersklassen','Altersgruppe'] if k in f]
 if len(a)>1:raise ValueError('Duplicate age selectors')
 if age=='allages':
  if any(f[k] for k in a):raise ValueError('Unrestricted reference must not have age filter')
 else:
  if len(a)!=1 or f[a[0]]!=set(QUERY_AGES[age]):raise ValueError('Age selection differs')
  if sum(e['distributions']['age'][label] for label in QUERY_AGES[age])!=e['n']:raise ValueError('Cases outside selected adult age band')

def validate_subset(event,denominator):
 if event['n']>denominator['n']:raise ValueError('Event total exceeds denominator')
 for distribution in ['age','sex','pccl']:
  for label,n in event['distributions'][distribution].items():
   if n>denominator['distributions'][distribution][label]:raise ValueError('Event distribution exceeds denominator')

def ensure_nested(t,d):
 if d['n']>t['n']:raise ValueError('Dysphagia is not nested within total')
 for dim in ['age','sex','pccl']:
  if any(d['distributions'][dim][label]>n for label,n in t['distributions'][dim].items()):raise ValueError('Non-nested dysphagia marginal')

def validate_diagnosis_partition(exports):
 for a in QUERY_AGES:
  for p in POPULATIONS:
   t,i63,i61=[exports[a,h,p] for h in HD]
   if i63['n']+i61['n']>t['n']:raise ValueError('Negative residual diagnosis total')
   for dim in ['age','sex','pccl']:
    if any(i63['distributions'][dim][k]+i61['distributions'][dim][k]>n for k,n in t['distributions'][dim].items()):
     raise ValueError('Negative residual diagnosis marginal')

def build_cells(denominators,events,distribution):
 labels=SEX_LABELS if distribution=='sex' else [str(k) for k in range(7)] if distribution=='pccl' else ['all']
 cells=[]
 for age in QUERY_AGES:
  for label in labels:
   def value(e):return e['n'] if distribution=='total' else e['distributions'][distribution][label]
   v={h:{'all_n':value(denominators[age,h,'all']), 'dys_n':value(denominators[age,h,'dys']),
         'all_events':value(events[age,h,'all']), 'dys_events':value(events[age,h,'dys'])} for h in HD}
   v['otherhd']={k:v['allhd'][k]-v['i63'][k]-v['i61'][k] for k in v['allhd']}
   if any(n<0 for n in v['otherhd'].values()):raise ValueError('Negative residual principal-diagnosis group')
   for h in ['i63','i61','otherhd']:
    cell={'age_band':'18-74' if age=='age18_74' else '75+','principal_diagnosis':h,**v[h]}
    if distribution!='total':cell[distribution]=label
    t,d,et,ed=[cell[k] for k in ['all_n','dys_n','all_events','dys_events']]
    if min(t,d,t-d,et,ed,et-ed)<0 or ed>d or et-ed>t-d:raise ValueError('Impossible reconstructed event counts')
    cells.append(cell)
 return cells

def expected_files(endpoint):
 return [event_name(endpoint,a,h,p) for a in QUERY_AGES for h in HD for p in POPULATIONS]

def exact_complement_candidates(endpoint,raw_dir,enabled=False):
 """Availability candidates only. Scientific validation occurs before derivation."""
 candidates=[]
 if enabled and endpoint=='pneumonia':
  for p in POPULATIONS:
   for a in QUERY_AGES:
    other=next(k for k in QUERY_AGES if k!=a)
    name=event_name(endpoint,a,'allhd',p)
    if not(raw_dir/name).is_file() and (raw_dir/reference_name(endpoint,p)).is_file() and (raw_dir/event_name(endpoint,other,'allhd',p)).is_file():
     candidates.append(name)
 return candidates

def derive_pneumonia_complement(raw_dir,age,pop):
 """Exact observed set difference, never inferred sex/PCCL joint independence.

No XLSX is generated. The logical event stratum is explicitly marked derived.
The full-age source must contain zero minors in every displayed age category.
"""
 other=next(k for k in QUERY_AGES if k!=age)
 ref=read_info(raw_dir/reference_name('pneumonia',pop))
 observed=read_info(raw_dir/event_name('pneumonia',other,'allhd',pop))
 validate_export(ref,'allages','allhd',pop,'pneumonia')
 validate_export(observed,other,'allhd',pop,'pneumonia')
 if any(ref['distributions']['age'][k]!=0 for k in MINOR_AGES):raise ValueError('Exact complement requires explicitly zero minors in the full-age event source')
 validate_subset(observed,ref)
 n=ref['n']-observed['n'];distributions={}
 for dim in ['age','sex','pccl']:
  distributions[dim]={k:value-observed['distributions'][dim][k] for k,value in ref['distributions'][dim].items()}
  if any(v<0 for v in distributions[dim].values()) or sum(distributions[dim].values())!=n:
   raise ValueError('Invalid exact complement distribution')
 if any(distributions['age'][k] for k in distributions['age'] if k not in QUERY_AGES[age]):
  raise ValueError('The exact complement includes ages outside the intended age band')
 if sum(distributions['age'][k] for k in QUERY_AGES[age])!=n:raise ValueError('Exact complement age partition mismatch')
 name=event_name('pneumonia',age,'allhd',pop)
 proof={'operation':'full_age_event_source_minus_other_adult_age_band_event_source',
   'minors_explicitly_zero':True,'minuend':ref['source'],'subtrahend':observed['source'],
   'logical_query':{'endpoint':'pneumonia','age':age,'hd':'allhd','population':pop}}
 proof_hash=hashlib.sha256(json.dumps(proof,sort_keys=True,ensure_ascii=True).encode('utf-8')).hexdigest()
 return {'n':n,'delivery':DELIVERY,'distributions':distributions,
   'selection':'DERIVED EXACT SET DIFFERENCE; not a native workbook query: '+name,
   'source':{'kind':'exact_set_difference','path':'derived:'+name,'sha256':proof_hash,
    'sha256_role':'provenance_digest_not_workbook_hash','size_bytes':None,'proof':proof}}

def load_denominators(raw_dir):
 den={}
 for a in QUERY_AGES:
  for h in HD:
   for p in POPULATIONS:
    e=read_info(raw_dir/denominator_name(a,h,p));validate_export(e,a,h,p);den[a,h,p]=e
   ensure_nested(den[a,h,'all'],den[a,h,'dys'])
 validate_diagnosis_partition(den)
 references={p:read_info(raw_dir/f'acute_{p}_2025.xlsx') for p in POPULATIONS}
 checks={}
 for p,r in references.items():
  validate_export(r,'allages','allhd',p)
  expected=sum(r['distributions']['age'][label] for label in sum(QUERY_AGES.values(),[]))
  observed=sum(den[a,'allhd',p]['n'] for a in QUERY_AGES)
  if observed!=expected:raise ValueError('Adult denominator total disagrees with original')
  for a,labels in QUERY_AGES.items():
   if any(den[a,'allhd',p]['distributions']['age'][label]!=r['distributions']['age'][label] for label in labels):raise ValueError('Native denominator age counts disagree with original')
  checks[p]={'reference_source':r['source'],'original_n':r['n'],'adult_n':observed,'native_age_counts_match':True}
 return den,references,checks

def analyze_endpoint(endpoint,raw_dir,den,references,den_checks,allow_exact_pneumonia_complement=False):
 candidates=exact_complement_candidates(endpoint,raw_dir,allow_exact_pneumonia_complement)
 missing=[n for n in expected_files(endpoint) if not(raw_dir/n).is_file() and n not in candidates]
 if missing:raise ValueError('Incomplete endpoint: '+endpoint+'; '+str(len(missing))+' missing exports')
 events={}
 for a in QUERY_AGES:
  for h in HD:
   for p in POPULATIONS:
    path=raw_dir/event_name(endpoint,a,h,p)
    if path.is_file():
     e=read_info(path);validate_export(e,a,h,p,endpoint)
    elif path.name in candidates:
     e=derive_pneumonia_complement(raw_dir,a,p)
    else:raise ValueError('No observed or explicitly permitted exact event source')
    validate_subset(e,den[a,h,p]);events[a,h,p]=e
   ensure_nested(events[a,h,'all'],events[a,h,'dys'])
 validate_diagnosis_partition(events)
 event_refs={};event_ref_checks={}
 for p in POPULATIONS:
  path=raw_dir/reference_name(endpoint,p)
  if path.is_file():
   r=read_info(path);validate_export(r,'allages','allhd',p,endpoint);validate_subset(r,references[p]);event_refs[p]=r
   expected=sum(r['distributions']['age'][label] for label in sum(QUERY_AGES.values(),[]))
   observed=sum(events[a,'allhd',p]['n'] for a in QUERY_AGES)
   if expected!=observed:raise ValueError('Event adult total disagrees with unrestricted reference')
   for a,labels in QUERY_AGES.items():
    if any(events[a,'allhd',p]['distributions']['age'][label]!=r['distributions']['age'][label] for label in labels):raise ValueError('Native event age counts disagree with unrestricted reference')
   event_ref_checks[p]={'status':'checked','source':r['source'],'original_n':r['n'],'adult_n':observed,'native_age_counts_match':True}
  else:event_ref_checks[p]={'status':'not_available','note':'No all-age reference validation claimed; all 12 joint source queries are still mandatory.'}
 models={name:standardize(build_cells(den,events,dim)) for name,dim in MODELS.items()}
 for name,r in models.items():
  r['factors']=name
  if r['status']=='estimated':
   r['diagnostics']={'sparse_strata':sum(c['sparse_event_cell'] for c in r['strata']),
     'boundary_strata':sum(c['boundary_probability'] for c in r['strata']),
     'sparse_reference_weight':sum(c['reference_weight'] for c in r['strata'] if c['sparse_event_cell']),
     'boundary_reference_weight':sum(c['reference_weight'] for c in r['strata'] if c['boundary_probability'])}
 all_age_crude=None
 if len(event_refs)==2:
  ensure_nested(event_refs['all'],event_refs['dys'])
  all_age_crude=contrast(event_refs['dys']['n'],references['dys']['n'],event_refs['all']['n']-event_refs['dys']['n'],references['all']['n']-references['dys']['n'])
 return {'cohort':'acute','endpoint':endpoint,'endpoint_definition':ENDPOINTS[endpoint],
  'design_status':'post_hoc_extension_specified_before_additional_outcome_exports',
  'exact_complement_amendment':{'enabled':allow_exact_pneumonia_complement,
    'derived_logical_queries':[event_name(endpoint,*k) for k,e in events.items() if e['source'].get('kind')=='exact_set_difference'],
    'date':'2026-11-17','method':'Optional exact full-age pneumonia minus directly observed age band, restricted to references with explicitly zero minors; no synthetic workbook.'},
  'computed_utc':datetime.now(timezone.utc).isoformat(),'delivery':DELIVERY,'population':'Adults aged 18+ in original acute OPS cohort; selected secondary dysphagia coding versus its complement',
  'denominator_reference_checks':den_checks,'event_reference_checks':event_ref_checks,
  'denominator_sources':{denominator_name(*k):{'source':e['source'],'selection':e['selection'],'n':e['n']} for k,e in den.items()},
  'event_sources':{event_name(endpoint,*k):{'source':e['source'],'selection':e['selection'],'n':e['n']} for k,e in events.items()},
  'all_age_crude_if_direct_union_reference_available':all_age_crude,'models':models,
  'limitations':['Administrative coding, not validated clinical ascertainment or incidence. Temporal relation to dysphagia is unknown.',
   'No NIHSS or other validated admission stroke severity is available; residual confounding remains.',
   'Sex and PCCL are separate three-factor standardizations, never one four-factor model.',
   'PCCL may include the outcome itself and other downstream diagnoses: descriptive sensitivity, not pure baseline adjustment.',
   'Two broad age groups leave residual age confounding; diagnostic residual includes heterogeneous conditions.',
   'Fixed-weight model-based intervals omit hospital clustering, repeated admissions and coding uncertainty.',
   'Multiple post hoc outcomes and overlapping composites are reported without interpreting isolated statistical significance as causal evidence.',
   'Missing/suppressed source queries are never zero; unsupported cells are excluded using denominator information only.']}

def public_summary(result):
 rows=[]
 for name,r in result['models'].items():
  row={'endpoint':result['endpoint'],'label':result['endpoint_definition']['label'],'analysis':name,'status':r['status']}
  if r['status']!='estimated':rows.append(row);continue
  crude=r['crude_same_common_support_population'];s=r['standardized'];ci=s['rr_ci'] or [None,None]
  aggregate_safe=min(crude['dys_events'],crude['no_dys_events'],crude['dys_n']-crude['dys_events'],crude['no_dys_n']-crude['no_dys_events'])>=5
  row.update({**r['common_support'],**r['diagnostics'],'status':'reported' if aggregate_safe else 'suppressed_aggregate_cell_below_5',
   'crude_rr_same_population':crude['rr'] if aggregate_safe else None,
   'dys_standardized_risk':s['dys_rate'] if aggregate_safe else None,'no_dys_standardized_risk':s['no_dys_rate'] if aggregate_safe else None,
   'rr':s['rr'] if aggregate_safe else None,'rr_ci_lower':ci[0] if aggregate_safe else None,'rr_ci_upper':ci[1] if aggregate_safe else None,
   'risk_difference':s['risk_difference'] if aggregate_safe else None,'risk_difference_ci_lower':s['risk_difference_ci'][0] if aggregate_safe else None,
   'risk_difference_ci_upper':s['risk_difference_ci'][1] if aggregate_safe else None})
  rows.append(row)
 return rows

def query_manifest():
 queries=[];baseline=[]
 for endpoint,definition in ENDPOINTS.items():
  for a in QUERY_AGES:
   for h in HD:
    for p in POPULATIONS:
     filters={'Prozeduren':OPS,'Altersklassen':QUERY_AGES[a],'weitere Nebendiagnosen':definition['codes']}
     if p=='dys':filters['Nebendiagnosen']=R13
     if h!='allhd':filters['Hauptdiagnosen']=HD_CODES[h]
     queries.append({'filename':event_name(endpoint,a,h,p),'endpoint':endpoint,'age_band':a,'principal_diagnosis':h,'population':p,
      'denominator_file':denominator_name(a,h,p),'filters':filters})
  for p in POPULATIONS:
   filters={'Prozeduren':OPS,'weitere Nebendiagnosen':definition['codes']}
   if p=='dys':filters['Nebendiagnosen']=R13
   baseline.append({'filename':reference_name(endpoint,p),'endpoint':endpoint,'population':p,'role':'optional full-age union reference, no age or principal diagnosis filter',
     'already_available_for_pneumonia':endpoint=='pneumonia','filters':filters})
 return {'schema_version':1,'cohort':'acute','definition_locked_date':'2026-11-17','delivery':DELIVERY,'source_url':'https://datenbrowser.inek.org/',
  'status':'defined_before_additional_event_exports','scope':'Diagnosis outcomes only. Procedural endpoints require an independent AND procedure selector; never add them to the cohort OPS OR field.',
  'query_logic':'OR within each selector; AND across selectors. Dysphagia ND and outcome further-ND selectors are distinct.',
  'endpoint_definitions':ENDPOINTS,'event_export_count':len(queries),'event_exports_per_endpoint':12,
  'reference_export_count':len(baseline),'reference_export_role':'Optional verification and full-age crude prevalence; adult analysis remains separate.',
  'models':MODELS,'no_joint_sex_pccl':True,'zero_rule':'No absent query or row is treated as zero. Explicit zero-query handling requires source-backed protocol amendment.',
  'optional_exact_reuse_amendment':{'date':'2026-11-17','cli_flag':'--allow-exact-pneumonia-complement',
   'default_enabled':False,'endpoint':'pneumonia','eligible_principal_diagnosis':'allhd',
   'required_proof':'Existing full-age endpoint source has explicit zero in every minor age group; one opposite adult age-band endpoint source is directly exported and valid.',
   'reused_sources':['acute_all_pneumonia_2025.xlsx','acute_dys_pneumonia_2025.xlsx'],
   'maximum_downloads_saved':2,'new_event_downloads_if_used':70,
   'no_synthetic_workbooks':True,'method':'Exact subtraction of counts for each age/sex/PCCL category; complete source hashes retained.'},
  'denominators_reused':[denominator_name(a,h,p) for a in QUERY_AGES for h in HD for p in POPULATIONS],
  'event_queries':queries,'full_age_reference_queries':baseline}

def write_results(results,out_dir,suffix):
 """Write already validated complete endpoint results, keeping detailed cells private."""
 rows=[]
 for endpoint,result in results.items():
  save(result,out_dir/'private_audit'/f'acute_{endpoint}_joint_audit.json');rows.extend(public_summary(result))
 save({'results':rows,'note':'Aggregate output only; detailed source cells remain in private_audit.'},out_dir/'aggregate'/f'acute_joint_outcomes_{suffix}.json')
 fields=list(dict.fromkeys(k for row in rows for k in row))
 target=out_dir/'aggregate'/f'acute_joint_outcomes_{suffix}.csv';target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 return rows

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--data-root',type=Path,required=True)
 ap.add_argument('--out-dir',type=Path,required=True,help='Private local output directory; do not commit detailed audits')
 ap.add_argument('--endpoint',choices=['all']+list(ENDPOINTS),default='all')
 ap.add_argument('--status-only',action='store_true')
 ap.add_argument('--write-manifest',type=Path)
 ap.add_argument('--allow-exact-pneumonia-complement',action='store_true',help='Allow two explicitly proven full-age-minus-age pneumonia sources; no synthetic workbook')
 args=ap.parse_args()
 if args.write_manifest:save(query_manifest(),args.write_manifest)
 selected=list(ENDPOINTS) if args.endpoint=='all' else [args.endpoint]
 denames=[denominator_name(a,h,p) for a in QUERY_AGES for h in HD for p in POPULATIONS]+['acute_all_2025.xlsx','acute_dys_2025.xlsx']
 missing_den=[n for n in denames if not(args.data_root/n).is_file()]
 status={'checked_utc':datetime.now(timezone.utc).isoformat(),'status':'available','effects_computed':False,'missing_denominator_files':missing_den,'endpoints':{},
  'note':'Availability is not validation. Status-only and pending runs do not refresh prior result files.'}
 for endpoint in selected:
  names=expected_files(endpoint);absent=[n for n in names if not(args.data_root/n).is_file()]
  candidates=exact_complement_candidates(endpoint,args.data_root,args.allow_exact_pneumonia_complement)
  missing=[n for n in absent if n not in candidates]
  status['endpoints'][endpoint]={'required':len(names),'available':len(names)-len(absent),'potential_exact_complements':candidates,
    'logical_queries_resolvable':len(names)-len(missing),'missing_files':missing,'absent_native_workbooks':absent,
    'optional_missing_full_age_references':[reference_name(endpoint,p) for p in POPULATIONS if not(args.data_root/reference_name(endpoint,p)).is_file()]}
 if missing_den or any(e['missing_files'] for e in status['endpoints'].values()):status['status']='pending'
 save(status,args.out_dir/'joint_outcomes_status.json')
 print(json.dumps({'status':status['status'],'effects_computed':False,'endpoints':{k:{f:v[f] for f in ['required','available','logical_queries_resolvable']} for k,v in status['endpoints'].items()}},indent=2))
 if args.status_only:return
 if status['status']=='pending':raise SystemExit(2)
 den,refs,checks=load_denominators(args.data_root)
 # Validate and compute all selected endpoints before writing any new estimates.
 results={e:analyze_endpoint(e,args.data_root,den,refs,checks,args.allow_exact_pneumonia_complement) for e in selected}
 rows=write_results(results,args.out_dir,args.endpoint)
 status.update(status='computed',effects_computed=True);save(status,args.out_dir/'joint_outcomes_status.json')
 print(json.dumps({'status':'computed','endpoints':selected,'aggregate_rows':len(rows)}))

if __name__=='__main__':main()
