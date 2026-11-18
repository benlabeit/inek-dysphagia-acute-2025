"""Mortality using the same six-stratum age/diagnosis standardization as other endpoints.

Reads original local workbooks only; no acquisition/network. Independent Fraction
arithmetic verifies the risks and plug-in binomial variances. All contrasts are
post hoc and model based; they do not establish causal or NIHSS-independent effects.
"""
from pathlib import Path
from fractions import Fraction
import argparse,csv,json,math
import analyze_joint_standardization as source
from outcomes_standardization_core import standardize,contrast

Z=1.959963984540054

def run(raw):
    refs={k:source.read_info(raw/f'acute_{k}_2025.xlsx') for k in source.KINDS}
    for k,e in refs.items():source.validate_reference(e,'acute',k)
    exports={}
    for age in source.QUERY_AGES:
        for hd in source.HD:
            for kind in source.KINDS:
                e=source.read_info(raw/source.filename('acute',age,hd,kind))
                source.validate_export(e,'acute',age,hd,kind)
                exports[age,hd,kind]=e
    for kind,ref in refs.items():
        expected=sum(ref['distributions']['age'][a] for ages in source.QUERY_AGES.values() for a in ages)
        assert sum(exports[a,'allhd',kind]['n'] for a in source.QUERY_AGES)==expected
        for age,labels in source.QUERY_AGES.items():
            for lab in labels:assert exports[age,'allhd',kind]['distributions']['age'][lab]==ref['distributions']['age'][lab]
    cells=[]
    for age in source.QUERY_AGES:
        vals={h:{k:exports[age,h,k]['n'] for k in source.KINDS} for h in source.HD}
        vals['otherhd']={k:vals['allhd'][k]-vals['i63'][k]-vals['i61'][k] for k in source.KINDS}
        for hd in ['i63','i61','otherhd']:
            a=vals[hd]
            assert all(isinstance(v,int) and v>=0 for v in a.values())
            cells.append({'age_band':age,'principal_diagnosis':hd,'all_n':a['all'],'dys_n':a['dys'],
                          'all_events':a['all_death'],'dys_events':a['dys_death']})
    result=standardize(cells)
    assert result['status']=='estimated' and result['common_support']['included_cells']==6
    # Independent rational formulas from the six original-export totals.
    nt=sum(c['all_n'] for c in cells)
    p=q=vp=vq=Fraction(0)
    for c in cells:
        t,d,a,ed=(c[k] for k in ['all_n','dys_n','all_events','dys_events'])
        nc=t-d;ec=a-ed
        p+=Fraction(t*ed,nt*d);q+=Fraction(t*ec,nt*nc)
        vp+=Fraction(t*t*ed*(d-ed),nt*nt*d*d*d)
        vq+=Fraction(t*t*ec*(nc-ec),nt*nt*nc*nc*nc)
    pp,qq,vpp,vqq=map(float,[p,q,vp,vq]);rr=pp/qq;rd=pp-qq
    sl=math.sqrt(vpp/pp**2+vqq/qq**2);sr=math.sqrt(vpp+vqq)
    independently=[pp,qq,rr,rr*math.exp(-Z*sl),rr*math.exp(Z*sl),rd,rd-Z*sr,rd+Z*sr]
    s=result['standardized'];observed=[s['dys_rate'],s['no_dys_rate'],s['rr'],*s['rr_ci'],s['risk_difference'],*s['risk_difference_ci']]
    assert all(abs(x-y)<1e-12 for x,y in zip(independently,observed))
    full=contrast(refs['dys_death']['n'],refs['dys']['n'],refs['all_death']['n']-refs['dys_death']['n'],refs['all']['n']-refs['dys']['n'])
    audit={'status':'PASS','source_workbooks_read':28,'joint_original_workbooks_read':24,'independent_numeric_checks':8,
           'maximum_numeric_difference':max(abs(x-y) for x,y in zip(independently,observed)),
           'method':'Original workbook exact-filter validation, native-age reconciliation, nested counts; independent rational risks and binomial variances.',
           'scope':'Numerical verification is not confidence-interval calibration or elimination of residual confounding.'}
    return result,full,audit,{str(k):v['source'] for k,v in exports.items()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--private-audit',type=Path)
    a=ap.parse_args();result,full,audit,sources=run(a.data_root);a.out_dir.mkdir(parents=True,exist_ok=True)
    s=result['standardized'];c=result['common_support'];sparse=[r for r in result['strata'] if r['sparse_event_cell']];boundary=[r for r in result['strata'] if r['boundary_probability']]
    row={'outcome':'mortality','label':'In-hospital death','role':'clinical','analysis':'age_principal_diagnosis','status':'estimated',
         **{k:c[k] for k in ['all_n','dys_n','no_dys_n']},'dys_rate':s['dys_rate'],'no_dys_rate':s['no_dys_rate'],'rr':s['rr'],
         'rr_ci_lower':s['rr_ci'][0],'rr_ci_upper':s['rr_ci'][1],'risk_difference':s['risk_difference'],
         'risk_difference_ci_lower':s['risk_difference_ci'][0],'risk_difference_ci_upper':s['risk_difference_ci'][1],
         'crude_rr_same_supported_adult_population':result['crude_same_common_support_population']['rr'],'included_strata':c['included_cells'],
         'sparse_strata':len(sparse),'sparse_reference_weight':sum(r['reference_weight'] for r in sparse),
         'boundary_strata':len(boundary),'boundary_reference_weight':sum(r['reference_weight'] for r in boundary)}
    with (a.out_dir/'outcomes_mortality_age_diagnosis.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
    (a.out_dir/'outcomes_mortality_age_diagnosis_validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    if a.private_audit:
        a.private_audit.parent.mkdir(parents=True,exist_ok=True)
        a.private_audit.write_text(json.dumps({'result':result,'baseline':full,'source_hashes':sources,'validation':audit},indent=2),encoding='utf-8')
    print(json.dumps({'aggregate':row,'validation':audit}))
if __name__=='__main__':main()
