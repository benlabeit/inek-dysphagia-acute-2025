"""Independent actual-data numerical QA; requires a complete published model JSON."""
from pathlib import Path
from fractions import Fraction as F
import argparse, json, math
import openpyxl

ROOT = Path(__file__).resolve().parent
Z = 1.959963984540054

def read_counts(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb['Info'].values)
    finally:
        wb.close()
    n = int(rows[7][1])
    out = {'n': n}
    for dim, indices, lc, vc in [('sex', range(10,14),0,1),('pccl',range(7,14),6,7)]:
        out[dim] = {}
        for i in indices:
            label = str(rows[i][lc])
            if dim == 'pccl': label = str(int(float(label)))
            value = n * float(rows[i][vc])
            assert abs(value-round(value)) < 1e-6, (path, dim, label, value)
            out[dim][label] = round(value)
        assert sum(out[dim].values()) == n
    return out

def compare(actual, expected, label):
    if expected is None:
        assert actual is None, label
    else:
        assert math.isclose(actual, float(expected), rel_tol=1e-11, abs_tol=1e-12), (label, actual, expected)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cohort', required=True, choices=['acute','rehab']); ap.add_argument('--twofactor',action='store_true')
    args = ap.parse_args(); cohort = args.cohort
    model_name = 'joint_twofactor' if args.twofactor else 'joint_standardization'
    model = json.loads((ROOT/'results'/f'{cohort}_{model_name}.json').read_text(encoding='utf-8'))
    ages = ['age18_74','age75plus']; hds = ['allhd'] if args.twofactor else ['allhd','i63','i61']; kinds=['all','dys','all_death','dys_death']
    exports = {(age,hd,k):read_counts(ROOT/'raw'/f'{cohort}_joint_{age}_{hd}_{k}_2025.xlsx') for age in ages for hd in hds for k in kinds}
    audit = {'cohort':cohort,'status':'passed','method':'Independent openpyxl source reads and exact-rational pooled risk/variance calculation','dimensions':{}}
    for dim, modelkey in [('sex','age_sex_principal_diagnosis'),('pccl','age_principal_diagnosis_pccl_sensitivity')]:
        cells=[]
        for age in ages:
            for label in exports[age,'allhd','all'][dim]:
                counts={hd:{k:exports[age,hd,k][dim][label] for k in kinds} for hd in hds}
                if not args.twofactor: counts['otherhd']={k:counts['allhd'][k]-counts['i63'][k]-counts['i61'][k] for k in kinds}
                for hd in (['allhd'] if args.twofactor else ['i63','i61','otherhd']):
                    x=counts[hd]; n=x['dys']; m=x['all']-n; a=x['dys_death']; b=x['all_death']-a
                    assert 0<=a<=n and 0<=b<=m
                    cells.append({'n':n,'m':m,'a':a,'b':b,'age':age,'hd':hd,dim:label})
        selected=[x for x in cells if x['n']>0 and x['m']>0]
        observed=model['analyses']['age_'+dim] if args.twofactor else model[modelkey]
        assert len(selected)==observed['common_support']['included_cells']
        assert len(cells)-len(selected)==observed['common_support']['excluded_cells']
        total=sum(x['n']+x['m'] for x in selected)
        weights=[F(x['n']+x['m'],total) for x in selected]
        assert sum(weights)==1
        reported={(x['age_band'],x.get('principal_diagnosis','allhd'),x[dim]):x for x in observed['strata']}
        for x,w in zip(selected,weights):
            y=reported[('18-74' if x['age']=='age18_74' else '75+',x['hd'],x[dim])]
            assert (y['all_n'],y['dys_n'],y['all_events'],y['dys_events'])==(x['n']+x['m'],x['n'],x['a']+x['b'],x['a'])
            compare(y['reference_weight'],w,'stratum weight')
        ps=[F(x['a'],x['n']) for x in selected]; qs=[F(x['b'],x['m']) for x in selected]
        pd=sum(w*p for w,p in zip(weights,ps)); pc=sum(w*q for w,q in zip(weights,qs))
        vd=sum(w*w*p*(1-p)/x['n'] for w,p,x in zip(weights,ps,selected)); vc=sum(w*w*q*(1-q)/x['m'] for w,q,x in zip(weights,qs,selected))
        rr=pd/pc if pc else None; rd=pd-pc
        result=observed['standardized']
        for key,value in [('dys_rate',pd),('no_dys_rate',pc),('rr',rr),('risk_difference',rd)]: compare(result[key],value,key)
        if pd>0 and pc>0:
            se=math.sqrt(float(vd/pd**2+vc/pc**2)); ci=[float(rr)*math.exp(-Z*se),float(rr)*math.exp(Z*se)]
            for actual,expected in zip(result['rr_ci'],ci):compare(actual,expected,'RR CI')
        se=math.sqrt(float(vd+vc))
        for actual,expected in zip(result['risk_difference_ci'],[float(rd)-Z*se,float(rd)+Z*se]):compare(actual,expected,'RD CI')
        crude=observed['crude_same_common_support_population']
        for key,col in [('dys_n','n'),('no_dys_n','m'),('dys_events','a'),('no_dys_events','b')]:assert crude[key]==sum(x[col] for x in selected)
        for key,num,den in [('all_coverage',sum(x['n']+x['m'] for x in selected),sum(x['n']+x['m'] for x in cells)),('dys_coverage',sum(x['n'] for x in selected),sum(x['n'] for x in cells)),('no_dys_coverage',sum(x['m'] for x in selected),sum(x['m'] for x in cells))]:compare(observed['common_support'][key],F(num,den),key)
        for kind,col in [('all','n'),('all_death','a')]:
            expected=sum(exports[age,'allhd',kind]['n'] for age in ages)
            actual=sum(x['n']+x['m'] if kind=='all' else x['a']+x['b'] for x in cells)
            assert actual==expected
        audit['dimensions'][dim]={'source_cells':len(cells),'retained_cells':len(selected),'exact_weight_sum':str(sum(weights)),'rr':float(rr) if rr is not None else None,'ci':result['rr_ci'],'adult_all_n':sum(x['n']+x['m'] for x in cells),'adult_all_deaths':sum(x['a']+x['b'] for x in cells),'common_support':observed['common_support']}
    path=ROOT/'results'/f'{cohort}_{model_name}_independent_qa.json'
    path.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
