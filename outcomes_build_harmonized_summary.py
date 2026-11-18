"""Assemble disclosure-safe outcome/model summaries and the explicit availability matrix.
Uses original whole-cohort totals for exact pulmonary unions and verified model CSVs.
No cell independence assumptions, synthetic source workbooks, or zero imputation.
"""
from pathlib import Path
import argparse,csv,json,math
import openpyxl
from outcomes_standardization_core import contrast
from outcomes_analyze_joint import read_info,validate_export

MODELS=['baseline_crude','age_principal_diagnosis','age_sex_principal_diagnosis','age_principal_diagnosis_pccl_sensitivity']
META={
'mortality':('In-hospital death','clinical','mortality'),
'J69.0':('Aspiration-related pneumonitis/pneumonia (J69.0)','clinical','pulmonary'),
'PNEUMONIA_UNION':('Pneumonia (J12-J18), unique union','clinical','pulmonary'),
'PULMONARY_UNION':('Pneumonia or aspiration-related pneumonitis, unique union','overlapping_composite','pulmonary'),
'J96.00':('Hypoxemic acute respiratory failure (J96.00)','clinical','pulmonary'),
'U69.01':('Pneumonia after 48 hours (U69.01)','clinical_timing_marker','pulmonary_timing'),
'U69.04':('Pneumonia by 48 hours (U69.04)','clinical_timing_marker','pulmonary_timing'),
'E43':('Unspecified severe protein-energy malnutrition (E43)','clinical','nutrition'),
'E44.0':('Moderate protein-energy malnutrition (E44.0)','clinical','nutrition'),
'E44.1':('Mild protein-energy malnutrition (E44.1)','clinical','nutrition'),
'E46':('Unspecified protein-energy malnutrition (E46)','clinical','nutrition'),
'MALNUT_UNION':('Protein-energy malnutrition, unique E40/E41/E42/E43/E44.0/E44.1/E46 union','clinical','nutrition'),
'E86':('Volume depletion (E86)','clinical','hydration'),
'8-701':('Simple endotracheal intubation (8-701)','procedure','procedures'),
'5-431.22':('PEG by thread-pull technique (5-431.22)','procedure','procedures'),
'1-613':('FEES coding (1-613)','process_marker','assessment')}
FIELDS=['outcome','label','role','domain','analysis','status','all_n','dys_n','no_dys_n','dys_events','no_dys_events',
'dys_rate','no_dys_rate','rr','rr_ci_lower','rr_ci_upper','risk_difference','risk_difference_ci_lower','risk_difference_ci_upper',
'crude_rr_same_supported_adult_population','included_strata','sparse_strata','sparse_reference_weight','boundary_strata','boundary_reference_weight','note']
def readcsv(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def num(x):
 if x in ['',None]:return None
 try:return float(x)
 except (TypeError,ValueError):return x

def start(code,model,status='estimated',note=''):
 label,role,domain=META[code]
 return dict(outcome=code,label=label,role=role,domain=domain,analysis=model,status=status,note=note)
def writecsv(path,rows,fields):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def count_code(w,code,sheet='Nebendiagnosen'):
 rows=[r for r in w[sheet].iter_rows(values_only=True) if r[0]==code]
 assert len(rows)==1
 x=rows[0][2];assert isinstance(x,(int,float)) and float(x).is_integer()
 return int(x)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,required=True);ap.add_argument('--data-root',type=Path,required=True);ap.add_argument('--new-results',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True)
 ap.add_argument('--joint-results',type=Path,help='Directory containing the three aggregate union-model CSVs. Defaults to the repository root.')
 a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True);rows={};checks=[]
 expanded=readcsv(a.new_results/'outcomes_existing_binary_outcomes.csv')
 for x in expanded:
  if x['analysis'] not in MODELS:continue
  r=start(x['outcome'],x['analysis'],x['status'],x['interval_note'])
  for k in FIELDS:
   if k in x and k not in ['label','role','domain','note']:r[k]=num(x[k]) if k not in ['outcome','analysis','status'] else x[k]
  rows[r['outcome'],r['analysis']]=r
 for x in readcsv(a.new_results/'outcomes_mortality_age_diagnosis.csv'):
  r=start('mortality','age_principal_diagnosis')
  for k in FIELDS:
   if k in x and k not in ['label','role','domain','note','outcome','analysis','status']:r[k]=num(x[k])
  rows['mortality',r['analysis']]=r
 # The original, unrestricted cohort and event workbook totals are read directly.
 wb={p:openpyxl.load_workbook(a.data_root/f'acute_{p}_2025.xlsx',read_only=True,data_only=True) for p in ['all','dys']}
 n={p:int(w['Info']['B8'].value) for p,w in wb.items()};assert n=={'all':279277,'dys':33643}
 # Confirm every existing crude probability against the original whole-cohort code count.
 for (code,model),r in list(rows.items()):
  if model!='baseline_crude':continue
  sheet='Prozeduren' if code in ['8-701','5-431.22','1-613'] else 'Nebendiagnosen'
  ed=count_code(wb['dys'],code,sheet);ec=count_code(wb['all'],code,sheet)-ed
  assert abs(r['dys_rate']-ed/n['dys'])<1e-12 and abs(r['no_dys_rate']-ec/(n['all']-n['dys']))<1e-12
  r.update(dys_events=ed,no_dys_events=ec);checks.append('crude code '+code)
 death={}
 for p in ['all','dys']:
  w=openpyxl.load_workbook(a.data_root/f'acute_{p}_death_2025.xlsx',read_only=True,data_only=True);death[p]=int(w['Info']['B8'].value);w.close()
 def addcrude(code,all_events,dys_events):
  c=contrast(dys_events,n['dys'],all_events-dys_events,n['all']-n['dys']);r=start(code,'baseline_crude')
  r.update({k:c[k] for k in ['dys_n','no_dys_n','dys_events','no_dys_events','dys_rate','no_dys_rate','rr','risk_difference']})
  r.update(all_n=n['all'],rr_ci_lower=c['rr_ci'][0],rr_ci_upper=c['rr_ci'][1],risk_difference_ci_lower=c['risk_difference_ci'][0],risk_difference_ci_upper=c['risk_difference_ci'][1],note='Unrestricted whole-cohort episodes; nominal model-based confidence intervals.')
  rows[code,'baseline_crude']=r
 addcrude('mortality',death['all'],death['dys'])
 pn={};overlap={}
 for p in ['all','dys']:
  e=read_info(a.data_root/f'acute_{p}_pneumonia_2025.xlsx');validate_export(e,'allages','allhd',p,'pneumonia');pn[p]=e['n']
  w=openpyxl.load_workbook(a.data_root/f'acute_{p}_pneumonia_2025.xlsx',read_only=True,data_only=True);overlap[p]=count_code(w,'J69.0');w.close()
 addcrude('PNEUMONIA_UNION',pn['all'],pn['dys'])
 j69={p:count_code(w,'J69.0') for p,w in wb.items()}
 union={p:pn[p]+j69[p]-overlap[p] for p in ['all','dys']}
 assert union=={'all':22404,'dys':11175}
 addcrude('PULMONARY_UNION',union['all'],union['dys']);checks.append('exact pulmonary inclusion-exclusion')
 for w in wb.values():w.close()
 malnutrition={}
 for pop in ['all','dys']:
  event=read_info(a.data_root/f'acute_outcome_malnutrition_union_allages_allhd_{pop}_2025.xlsx')
  validate_export(event,'allages','allhd',pop,'malnutrition_union')
  malnutrition[pop]=event['n']
 addcrude('MALNUT_UNION',malnutrition['all'],malnutrition['dys'])
 checks.append('direct unrestricted malnutrition union')
 unions={'PNEUMONIA_UNION':'pneumonia','PULMONARY_UNION':'pulmonary_union','MALNUT_UNION':'malnutrition_union'}
 for code in unions:
  rows[code,'baseline_crude']['note']='All-age unique-episode contrast.'
 # Existing separately observed three-factor models, never combined across margins.
 sources=[('mortality','joint_threefactor_summary.csv'),('E43','outcomes_severe_malnutrition_joint_aggregate.csv'),('E86','outcomes_volume_depletion_joint_aggregate.csv'),('J69.0','outcomes_aspiration_pneumonitis_joint_aggregate.csv')]
 for code,file in sources:
  for x in readcsv(a.repo_root/file):
   model=x['analysis']
   if model not in MODELS:continue
   r=start(code,model,note='Separate observed model. PCCL may reflect downstream diagnoses; sex and PCCL are not jointly included. Nominal approximate intervals.')
   aliases={'dys_rate':'dys_standardized_risk','no_dys_rate':'no_dys_standardized_risk','included_strata':'included_cells','sparse_strata':'sparse_event_or_nonevent_strata','boundary_strata':'boundary_probability_strata','crude_rr_same_supported_adult_population':'crude_rr_same_common_support'}
   for k in FIELDS:
    if k in ['outcome','label','role','domain','analysis','status','note','dys_events','no_dys_events']:continue
    v=x.get(k,x.get(aliases.get(k,'')))
    if k=='crude_rr_same_supported_adult_population' and v in [None,'']:
     v=x.get('crude_rr_same_population')
    if v not in [None,'']:r[k]=num(v)
   if (code,model) in rows:
    old=rows[code,model]
    for k in ['dys_rate','no_dys_rate','rr','rr_ci_lower','rr_ci_upper','risk_difference']:
     assert abs(r[k]-old[k])<1e-10,(code,model,k)
    r={**old,**{k:v for k,v in r.items() if v is not None}}
   rows[code,model]=r
 joint_dir=a.joint_results or a.repo_root
 for code,endpoint in unions.items():
  model_rows=readcsv(joint_dir/f'acute_joint_outcomes_{endpoint}.csv')
  if len(model_rows)!=3 or {x['analysis'] for x in model_rows}!=set(MODELS[1:]):
   raise ValueError(f'Expected three distinct adult standardizations for {endpoint}')
  for x in model_rows:
   if x['endpoint']!=endpoint or x['status']!='reported':
    raise ValueError(f'Unexpected endpoint or model status in {endpoint}')
   model=x['analysis']
   row=start(code,model,note='Standardized unique-episode contrast, independently reconstructed from aggregate exports.')
   source={'dys_rate':'dys_standardized_risk','no_dys_rate':'no_dys_standardized_risk','included_strata':'included_cells','crude_rr_same_supported_adult_population':'crude_rr_same_population'}
   for key in FIELDS:
    column=source.get(key,key)
    if column in x and key not in row:
     row[key]=num(x[column])
   rows[code,model]=row
 # Clearly explicit unavailable cells retain empty estimates rather than zeros.
 matrix=[]
 for code,(label,role,domain) in META.items():
  statuses={}
  for model in MODELS:
   key=(code,model)
   if key not in rows:
    why='Outcome-filtered joint sex/PCCL distributions were not collected; no independence assumption used.'
    rows[key]=start(code,model,'not_available',why)
   r=rows[key];statuses[model]=r['status']
   if r['status']!='estimated':assert not any(r.get(k) not in [None,''] for k in ['dys_rate','no_dys_rate','rr','risk_difference'])
  matrix.append({'outcome':code,'label':label,'role':role,'domain':domain,**statuses,'other_analyses':'Single-factor PCCL and functional-category sensitivities retained separately.' if code=='PNEUMONIA_UNION' else 'Post hoc coarsened-PCCL sensitivity retained separately.' if code=='E43' else ''})
 matrix.append({'outcome':'LOS','label':'Length of hospital stay','role':'resource_use','domain':'resource_use','baseline_crude':'estimated','age_principal_diagnosis':'estimated','age_sex_principal_diagnosis':'not_available','age_principal_diagnosis_pccl_sensitivity':'not_available','other_analyses':'Within-DRG comparison and discharge-alive sensitivity available; sex/PCCL-specific first and second LOS moments absent.'})
 ordered=[rows[code,model] for code in META for model in MODELS]
 writecsv(a.out_dir/'outcomes_harmonized_binary_summary.csv',ordered,FIELDS)
 writecsv(a.out_dir/'outcomes_model_availability.csv',matrix,list(matrix[0]))
 (a.out_dir/'outcomes_harmonized_binary_summary.json').write_text(json.dumps({'schema_version':1,'unit':'hospital episode','risk_units':'probability (0-1)','risk_difference_units':'absolute probability difference; multiply by 100 for percentage points','analysis_order':MODELS,'rows':ordered},indent=2,allow_nan=False),encoding='utf-8')
 summary={'status':'PASS','whole_cohort_code_checks':len(checks),'binary_endpoints':len(META),'model_slots':len(ordered),'age_diagnosis_estimates':sum(r['analysis']=='age_principal_diagnosis' and r['status']=='estimated' for r in ordered),'three_factor_endpoint_count':sum(all(rows[c,m]['status']=='estimated' for m in MODELS[2:]) for c in META),'crude_population':279277,'standardization_adult_population':279255,'source_cell_counts_published':False,'note':'Only model-level results and whole-cohort event totals are included; no detailed source strata or source hashes.'}
 (a.out_dir/'outcomes_harmonized_assembly_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary))
if __name__=='__main__':main()
