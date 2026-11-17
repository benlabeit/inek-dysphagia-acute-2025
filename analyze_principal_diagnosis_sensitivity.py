"""Exact, explicitly defined main-diagnosis mortality groups; no missing zeros."""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parent
if ROOT.name=='results':ROOT=ROOT.parent
sys.path.insert(0,str(ROOT))
from analyze_acute_exports import contrast

GROUPS={
    'I63_except_I63_6':['I63.'+str(k) for k in [0,1,2,3,4,5,8,9]],
    'I61':['I61.'+str(k) for k in [0,1,2,3,4,5,6,8,9]],
    'I63_4':['I63.4'],
    'I61_0':['I61.0'],
    'G62_80':['G62.80'],
    'G93_1':['G93.1'],
    'S06_5':['S06.5'],
}
parser=argparse.ArgumentParser()
parser.add_argument('--cohort',choices=['all','acute','rehab'],default='all')
parser.add_argument('--data-root',type=Path,default=ROOT)
parser.add_argument('--out-dir',type=Path)
args=parser.parse_args()
cohorts=['acute','rehab'] if args.cohort=='all' else [args.cohort]
def load_export(cohort,kind):
    path=args.data_root/'parsed'/f'{cohort}_{kind}_2025.json'
    raw=args.data_root/'raw'/f'{cohort}_{kind}_2025.xlsx'
    if path.exists():
        e=json.loads(path.read_text(encoding='utf-8'))
        if raw.exists():assert hashlib.sha256(raw.read_bytes()).hexdigest()==e['source']['sha256'],'Stale parsed export'
        return e
    from analyze_acute_exports import parse_inek
    return parse_inek(raw)
result={}
for cohort in cohorts:
    names=['all','dys','all_death','dys_death']
    es={k:load_export(cohort,k) for k in names}
    assert len({e['delivery'] for e in es.values()})==1
    maps={k:{r['code']:r for r in e['tables']['Hauptdiagnosen'] if not r['is_rest']} for k,e in es.items()}
    result[cohort]={'sources':{k:e['source'] for k,e in es.items()},'selections':{k:e['selection'] for k,e in es.items()},'groups':{},'principal_diagnosis_rest':{}}
    for k,e in es.items():
        assert sum(r['cases'] for r in e['tables']['Hauptdiagnosen'])==e['n']
        rest=sum(r['cases'] for r in e['tables']['Hauptdiagnosen'] if r['is_rest'])
        result[cohort]['principal_diagnosis_rest'][k]={'cases':rest,'fraction':rest/e['n'],'displayed_fraction':1-rest/e['n']}
    for group,codes in GROUPS.items():
        missing={k:[c for c in codes if c not in rows] for k,rows in maps.items()}
        g={'definition':codes,'missing_codes':missing,'exact':not any(missing.values())}
        if g['exact']:
            totals={k:sum(rows[c]['cases'] for c in codes) for k,rows in maps.items()}
            assert totals['all']>=totals['dys'] and totals['all_death']>=totals['dys_death']
            g['counts']=totals
            g['comparison']=contrast(totals['dys_death'],totals['dys'],totals['all_death']-totals['dys_death'],totals['all']-totals['dys'])
        else:g['note']='Absent rows may be zero or suppressed; no exact comparison computed.'
        result[cohort]['groups'][group]=g
    result[cohort]['limitations']=[
        'Main diagnosis is single-valued, so explicit complete sets of endcodes may be summed without overlap.',
        'I63_except_I63_6 is explicitly restricted to the eight listed endcodes and is not the full I63 union.',
        'Whole-table Rest counts prevent assuming that other unlisted endcodes are zero.',
        'Within-diagnosis comparisons restrict diagnostic case mix but do not control within-diagnosis clinical severity, age, treatment or indication.',
        'No age-by-sex, age-by-PCCL or age-by-main-diagnosis joint cells are supplied by the available marginal tables.',
        'Exploratory, independent-episode model intervals; no hospital clustering or repeated-admission correction.'
    ]
dest=args.out_dir or args.data_root/'results';dest.mkdir(parents=True,exist_ok=True)
stem='principal_diagnosis_sensitivity' if args.cohort=='all' else args.cohort+'_principal_diagnosis_sensitivity'
(dest/(stem+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for cohort,r in result.items():
    for group,g in r['groups'].items():
        if g['exact']:
            c=g['comparison'];print(json.dumps({'cohort':cohort,'group':group,**c},ensure_ascii=True))
