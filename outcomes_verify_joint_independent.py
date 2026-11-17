"""Independent Decimal audit of complete acute diagnosis-outcome exports.

No production analysis module is imported. Original XLSX filters, counts and
separate observed age/sex/diagnosis and age/diagnosis/PCCL margins are verified.
Detailed JSON is private audit material. The CSV contains model-level results.
"""
from pathlib import Path
from decimal import Decimal, getcontext
from datetime import datetime, timezone
from contextlib import closing
import argparse
import csv
import hashlib
import json
import math
import re
import openpyxl

getcontext().prec = 60
D = Decimal
Z = D('1.959963984540054')
AGES = {
    'age18_74': {'18-29 Jahre', '30-39 Jahre', '40-49 Jahre', '50-54 Jahre', '55-59 Jahre', '60-64 Jahre', '65-74 Jahre'},
    'age75plus': {'75-79 Jahre', '80+ Jahre'},
}
HDS = ['allhd', 'i63', 'i61']
POPS = ['all', 'dys']
OPS = {f'{p}.{s}' for p in ['8-981', '8-98b'] for s in ['20', '21', '22', '23', '30', '31', '32', '33']}
PNEUMONIA = {'J12.0','J12.1','J12.2','J12.3','J12.8','J12.9','J13','J14','J15.0','J15.1','J15.2','J15.3','J15.4','J15.5','J15.6','J15.7','J15.8','J15.9','J16.0','J16.8','J17.0','J17.1','J17.2','J17.3','J17.8','J18.0','J18.1','J18.2','J18.8','J18.9'}
ENDPOINTS = {
    'pneumonia': PNEUMONIA,
    'aspiration_pneumonitis': {'J69.0'},
    'pulmonary_union': PNEUMONIA | {'J69.0'},
    'malnutrition_union': {'E40', 'E41', 'E42', 'E43', 'E44.0', 'E44.1', 'E46'},
    'volume_depletion': {'E86'},
    'severe_malnutrition': {'E43'},
}
MODES = [('total','age_principal_diagnosis'), ('sex','age_sex_principal_diagnosis'), ('pccl','age_principal_diagnosis_pccl_sensitivity')]
DELIVERY = 'Unterj\u00e4hrige Datenlieferung DRG Januar bis Dezember 2025'


def serialize(x):
    return float(x) if isinstance(x, D) else str(x)


class Auditor:
    def __init__(self, raw, endpoint, allow_complement=False):
        self.raw, self.endpoint, self.allow_complement = raw, endpoint, allow_complement
        self.checks, self.sources, self.cache = [], {}, {}

    def check(self, label, truth):
        self.checks.append({'check': label, 'passed': bool(truth)})
        if not truth:
            raise AssertionError(label)

    def compare(self, label, a, b):
        self.check(label, abs(D(str(a))-D(str(b))) < D('1e-10'))

    def integer(self, v, label):
        self.check(label+': finite observed number', not isinstance(v, bool) and isinstance(v,(float,int)) and math.isfinite(v))
        x = D(str(v)); n = int(x.to_integral())
        self.check(label+': nonnegative integer', n >= 0 and abs(x-n) < D('1e-8'))
        return n

    def filename(self, age, hd, pop, event):
        return (f'acute_outcome_{self.endpoint}_{age}_{hd}_{pop}_2025.xlsx' if event else f'acute_joint_{age}_{hd}_{pop}_2025.xlsx')

    def native(self, path, age, hd, pop, event):
        name = path.name
        if name in self.cache:
            return self.cache[name]
        with closing(openpyxl.load_workbook(path, read_only=True, data_only=True)) as w:
            s = w['Info']; query = s['A2'].value
            self.check(name+': observed query', isinstance(query, str))
            fields = {}
            for segment in query.split(';'):
                if not segment.strip():
                    continue
                m = re.fullmatch(r'([^()]+)\(([^()]*)\)', segment.strip())
                self.check(name+': full query parse', m is not None)
                key = m.group(1).strip()
                self.check(name+': unique selector '+key, key not in fields)
                values = [x.strip().rstrip('!*') for x in m.group(2).split(',') if x.strip()]
                self.check(name+': unique selector entries '+key, len(values) == len(set(values)))
                fields[key] = set(values)
            self.check(name+': exact acute OPS', fields.get('Prozeduren') == OPS)
            self.check(name+': exact dysphagia selector', fields.get('Nebendiagnosen',set()) == ({'R13.0','R13.1','R13.9'} if pop == 'dys' else set()))
            self.check(name+': exact separate outcome selector', fields.get('weitere Nebendiagnosen',set()) == (ENDPOINTS[self.endpoint] if event else set()))
            hd_keys = [k for k in ('Hauptdiagnose','Hauptdiagnosen') if k in fields]
            self.check(name+': no duplicate HD selectors', len(hd_keys) <= 1)
            hd_expected = {f'{hd.upper()}.{i}' for i in ['0','1','2','3','4','5','6','8','9']} if hd != 'allhd' else set()
            self.check(name+': exact HD', (fields[hd_keys[0]] if hd_keys else set()) == hd_expected)
            age_keys = [k for k in ('Altersgruppe','Altersklasse','Altersklassen') if k in fields]
            self.check(name+': no duplicate age selectors', len(age_keys) <= 1)
            age_actual = fields[age_keys[0]] if age_keys else set()
            self.check(name+': exact age selector', age_actual == (set() if age == 'allages' else AGES[age]))
            allowed = {'Prozeduren','Nebendiagnosen','weitere Nebendiagnosen','Hauptdiagnose','Hauptdiagnosen','Altersgruppe','Altersklasse','Altersklassen','Entlassungsgrund','weitere Prozedur','weitere Prozeduren','weitereProzedur'}
            self.check(name+': no unwanted selectors', not (set(fields)-allowed))
            self.check(name+': no discharge/procedure restrictions', not any(fields.get(k) for k in ['Entlassungsgrund','weitere Prozedur','weitere Prozeduren','weitereProzedur']))
            self.check(name+': correct data delivery', s['A5'].value == DELIVERY)
            n = self.integer(s['B8'].value, name+': N')
            self.check(name+': positive observed query N', n > 0)
            out = {'n': n, 'sex': {}, 'pccl': {}, 'age': {}, 'name': name, 'kind':'native'}
            for mode,rows,keycol,valcol in [('sex',range(11,15),'A','B'), ('pccl',range(8,15),'G','H'), ('age',range(8,24),'J','K')]:
                for r in rows:
                    key = str(s[f'{keycol}{r}'].value); prop = s[f'{valcol}{r}'].value
                    self.check(f'{name}/{mode}/{key}: finite observed proportion', not isinstance(prop,bool) and isinstance(prop,(int,float)) and math.isfinite(prop) and 0 <= prop <= 1)
                    value = D(str(prop))*n; count = int(value.to_integral())
                    self.check(f'{name}/{mode}/{key}: exact integer recovery', abs(value-count) < D('1e-8'))
                    self.check(f'{name}/{mode}/{key}: unique category', key not in out[mode])
                    out[mode][key] = count
                self.check(name+': exhaustive '+mode, sum(out[mode].values()) == n)
            if age != 'allages':
                self.check(name+': native ages obey filter', all(v == 0 or k in AGES[age] for k,v in out['age'].items()))
            if len(ENDPOINTS[self.endpoint]) == 1 and 'Nebendiagnosen' in w.sheetnames:
                code = next(iter(ENDPOINTS[self.endpoint]))
                vals = [r[2] for r in w['Nebendiagnosen'].iter_rows(min_row=2,values_only=True) if r[0] == code]
                self.check(name+': at most one code row', len(vals) <= 1)
                if vals and isinstance(vals[0],(int,float)) and not isinstance(vals[0],bool):
                    out['single_code_table_n'] = self.integer(vals[0], name+': previous diagnosis count')
        out['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.sources[name] = {'kind':'native','sha256':out['sha256'],'query':query,'n':n}
        self.cache[name] = out
        return out

    def read(self, age, hd, pop, event):
        name = self.filename(age,hd,pop,event); path = self.raw/name
        if path.is_file():
            return self.native(path,age,hd,pop,event)
        self.check(name+': authorized exact reuse only', event and self.endpoint == 'pneumonia' and hd == 'allhd' and self.allow_complement)
        other = next(a for a in AGES if a != age)
        ref = self.native(self.raw/f'acute_{pop}_pneumonia_2025.xlsx','allages','allhd',pop,True)
        obs = self.native(self.raw/self.filename(other,hd,pop,event),other,hd,pop,event)
        self.check(name+': all seven minor categories explicitly zero', len([k for k in ref['age'] if k not in set.union(*AGES.values())]) == 7 and all(v == 0 for k,v in ref['age'].items() if k not in set.union(*AGES.values())))
        out = {'n': ref['n']-obs['n'], 'name':name,'kind':'exact_set_difference'}
        self.check(name+': positive exact complement', out['n'] > 0)
        for mode in ['sex','pccl','age']:
            self.check(name+': matching observed complement categories '+mode, set(ref[mode]) == set(obs[mode]))
            out[mode] = {k:v-obs[mode][k] for k,v in ref[mode].items()}
            self.check(name+': nonnegative exhaustive exact '+mode, min(out[mode].values()) >= 0 and sum(out[mode].values()) == out['n'])
        self.check(name+': complement has intended ages only', all(v == 0 or k in AGES[age] for k,v in out['age'].items()))
        self.sources[name] = {'kind':'exact_set_difference','minuend':ref['name'],'subtrahend':obs['name'],'n':out['n'],'workbook_created':False}
        return out

    def audit(self, production):
        src = {(a,h,p,e):self.read(a,h,p,e) for a in AGES for h in HDS for p in POPS for e in [False,True]}
        for a in AGES:
            for h in HDS:
                for p in POPS:
                    den, ev = src[a,h,p,False], src[a,h,p,True]
                    self.check(f'{a}/{h}/{p}: events nested in cases', ev['n'] <= den['n'])
                    if 'single_code_table_n' in den:
                        self.check(f'{a}/{h}/{p}: previous code table matches direct events', den['single_code_table_n'] == ev['n'])
                    if 'single_code_table_n' in ev:
                        self.check(f'{a}/{h}/{p}: event code table matches its own N', ev['single_code_table_n'] == ev['n'])
                    for mode in ['sex','pccl','age']:
                        self.check(f'{a}/{h}/{p}/{mode}: common categories', set(den[mode]) == set(ev[mode]))
                        self.check(f'{a}/{h}/{p}/{mode}: marginal event subset', all(ev[mode][k] <= den[mode][k] for k in den[mode]))
        def value(age,hd,pop,event,mode,key):
            if hd == 'otherhd':
                return value(age,'allhd',pop,event,mode,key)-value(age,'i63',pop,event,mode,key)-value(age,'i61',pop,event,mode,key)
            s = src[age,hd,pop,event]
            return s['n'] if mode == 'total' else s[mode][key]
        models = {}
        for mode, model in MODES:
            keys = ['total'] if mode == 'total' else list(src['age18_74','allhd','all',False][mode])
            included, excluded = [], []
            for age in AGES:
                for hd in ['i63','i61','otherhd']:
                    for key in keys:
                        c = {'age':age,'hd':hd,'factor':key}
                        for p in POPS:
                            c[p+'_n'] = value(age,hd,p,False,mode,key)
                            c[p+'_events'] = value(age,hd,p,True,mode,key)
                        c['no_dys_n'] = c['all_n']-c['dys_n']
                        c['no_dys_events'] = c['all_events']-c['dys_events']
                        for p in ['all','dys','no_dys']:
                            self.check(f'{model}/{age}/{hd}/{key}/{p}: valid disjoint cell', 0 <= c[p+'_events'] <= c[p+'_n'])
                        if c['dys_n'] > 0 and c['no_dys_n'] > 0:
                            c['sparse'] = min(c['dys_events'],c['dys_n']-c['dys_events'],c['no_dys_events'],c['no_dys_n']-c['no_dys_events']) < 5
                            c['boundary'] = any(c[p+'_events'] in (0,c[p+'_n']) for p in ['dys','no_dys'])
                            included.append(c)
                        else:
                            excluded.append(c)
            totals = {k:sum(c[k] for c in included) for k in ['all_n','dys_n','no_dys_n','all_events','dys_events','no_dys_events']}
            result = estimate(included)
            for kind in ['sparse','boundary']:
                result[kind+'_strata'] = sum(c[kind] for c in included)
                result[kind+'_reference_weight'] = D(sum(c['all_n'] for c in included if c[kind]))/totals['all_n']
            result.update({k:totals[k] for k in ['all_n','dys_n','no_dys_n']})
            result.update(included_cells=len(included),excluded_cells=len(excluded))
            target = next(r for r in production['results'] if r['analysis'] == model)
            for k,v in result.items():
                self.compare(model+': production '+k,v,target[k])
            expected_n = {'total':279255,'sex':279248,'pccl':279254}[mode]
            self.check(model+': same prespecified denominator support', totals['all_n'] == expected_n)
            models[model] = {'estimates':result,'event_totals':totals,'included_private':included,'excluded_private':excluded}
        return {'status':'PASS','endpoint':self.endpoint,'checked_utc':datetime.now(timezone.utc).isoformat(),'checks_passed':len(self.checks),'checks':self.checks,'sources':self.sources,'models':models,'scope':'Independent original-XLSX parsing and Decimal formulas. Sex and PCCL are separate observed marginal models; no crossclassification or independence assumption. Nominal approximate CIs; no hospital clustering or multiplicity adjustment.'}


def estimate(cells):
    total = sum(c['all_n'] for c in cells)
    risks, variances = [], []
    for p in ['dys','no_dys']:
        ps = [D(c[p+'_events'])/c[p+'_n'] for c in cells]
        ws = [D(c['all_n'])/total for c in cells]
        risks.append(sum(w*prop for w,prop in zip(ws,ps)))
        variances.append(sum(w*w*prop*(1-prop)/c[p+'_n'] for c,w,prop in zip(cells,ws,ps)))
    rr = risks[0]/risks[1]; rd = risks[0]-risks[1]
    logse = (variances[0]/risks[0]**2+variances[1]/risks[1]**2).sqrt()
    rdse = sum(variances).sqrt()
    crude = (D(sum(c['dys_events'] for c in cells))/sum(c['dys_n'] for c in cells))/(D(sum(c['no_dys_events'] for c in cells))/sum(c['no_dys_n'] for c in cells))
    return {'dys_standardized_risk':risks[0],'no_dys_standardized_risk':risks[1], 'rr':rr,'rr_ci_lower':(rr.ln()-Z*logse).exp(),'rr_ci_upper':(rr.ln()+Z*logse).exp(), 'risk_difference':rd,'risk_difference_ci_lower':rd-Z*rdse,'risk_difference_ci_upper':rd+Z*rdse,'crude_rr_same_population':crude}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--endpoint',action='append',choices=list(ENDPOINTS))
    ap.add_argument('--raw',type=Path,required=True,help='Directory of original native workbooks; kept private.')
    ap.add_argument('--production-dir',type=Path,required=True,help='Model-level JSON directory generated by outcomes_analyze_joint.py.')
    ap.add_argument('--out-dir',type=Path,required=True,help='Private audit output directory; includes stratum counts and source hashes.')
    ap.add_argument('--allow-exact-pneumonia-complement',action='store_true')
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    selected = args.endpoint or list(ENDPOINTS)
    summary, rows = {}, []
    for ep in selected:
        target = args.production_dir/f'acute_joint_outcomes_{ep}.json'
        if not target.is_file():
            summary[ep] = {'status':'pending','reason':'No completed production result; no effects computed by QA.'}
            continue
        auditor = Auditor(args.raw,ep,args.allow_exact_pneumonia_complement)
        result = auditor.audit(json.loads(target.read_text(encoding='utf-8')))
        (args.out_dir/f'independent_{ep}_validation.json').write_text(json.dumps(result,indent=2,default=serialize)+'\n',encoding='utf-8')
        summary[ep] = {'status':'PASS','checks_passed':result['checks_passed'],'models':{k:v['estimates'] for k,v in result['models'].items()}}
        for model, values in result['models'].items():
            rows.append({'endpoint':ep,'analysis':model,**values['estimates']})
    report = {'checked_utc':datetime.now(timezone.utc).isoformat(),'endpoints':summary,'all_selected_passed':all(v['status']=='PASS' for v in summary.values())}
    (args.out_dir/'independent_joint_outcomes_status.json').write_text(json.dumps(report,indent=2,default=serialize)+'\n',encoding='utf-8')
    if rows:
        with (args.out_dir/'independent_joint_outcomes_aggregate.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
            writer.writerows([{k:serialize(v) if isinstance(v,D) else v for k,v in r.items()} for r in rows])
    print(json.dumps(report,indent=2,default=serialize))


if __name__ == '__main__':
    main()
