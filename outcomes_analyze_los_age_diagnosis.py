"""Read-only acute InEK LOS standardization by age and principal diagnosis.

Reconstructs exact integer-day first/second moments from stored Info values.
Source workbooks are read only. Explicit --data-root and --out-dir are required.
Detailed results and source audits are private; only the model summary CSV is
intended for reviewed aggregate reporting.
The primary analysis needs 12 age/diagnosis total+dysphagia workbooks; the
separate survivor sensitivity additionally uses their 12 death workbooks.
"""
from pathlib import Path
from fractions import Fraction
from dataclasses import dataclass
from datetime import datetime, timezone
import argparse, csv, hashlib, json, math, re
import openpyxl

Z = 1.959963984540054
DELIVERY = 'Unterjährige Datenlieferung DRG Januar bis Dezember 2025'
AGES = {
    'age18_74': ['18-29 Jahre','30-39 Jahre','40-49 Jahre','50-54 Jahre','55-59 Jahre','60-64 Jahre','65-74 Jahre'],
    'age75plus': ['75-79 Jahre','80+ Jahre'],
}
HD = ('allhd','i63','i61')
KINDS = ('all','dys','all_death','dys_death')
OPS = {f'{prefix}.{k}' for prefix in ('8-981','8-98b') for k in (20,21,22,23,30,31,32,33)}
R13 = {'R13.0','R13.1','R13.9'}
MOMENT_TOL = 1e-5


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def selection_fields(selection):
    out = {}
    for label, body in re.findall(r'([^();]+)\(([^()]*)\)', selection):
        label = label.strip()
        if label in out:
            raise ValueError('Repeated selector: '+label)
        out[label] = {s.strip().rstrip('!*') for s in body.split(',') if s.strip()}
    return out


@dataclass(frozen=True)
class Moments:
    n: int
    s: int
    q: int

    def validate(self):
        if self.n < 0 or self.s < 0 or self.q < 0:
            raise ValueError('Negative moment/count: '+str(self))
        if self.n == 0:
            if self.s or self.q:
                raise ValueError('Nonzero moments in empty population')
        elif self.q*self.n < self.s*self.s:
            raise ValueError('Negative variance: '+str(self))
        elif self.q < self.s:
            raise ValueError('Integer nonnegative LOS requires Q>=S')
        return self

    def __add__(self, other):
        return Moments(self.n+other.n, self.s+other.s, self.q+other.q).validate()

    def __sub__(self, other):
        return Moments(self.n-other.n, self.s-other.s, self.q-other.q).validate()

    @property
    def mean(self):
        return Fraction(self.s,self.n) if self.n else None

    @property
    def sample_variance(self):
        return Fraction(self.q*self.n-self.s*self.s, self.n*(self.n-1)) if self.n > 1 else None

    @property
    def mean_variance(self):
        return self.sample_variance/self.n if self.n > 1 else None

    def result(self):
        return {'n':self.n, 'sum_days':self.s, 'sum_squared_days':self.q,
                'mean_days':float(self.mean) if self.n else None,
                'sample_variance':float(self.sample_variance) if self.n>1 else None,
                'sample_sd':math.sqrt(float(self.sample_variance)) if self.n>1 else None}


def sum_moments(items):
    answer = Moments(0,0,0)
    for m in items:
        answer = answer+m
    return answer


def read_source(path, age=None, hd=None, kind=None, original=False):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    wb = openpyxl.load_workbook(path,read_only=True,data_only=True)
    try:
        rows = list(wb['Info'].values)
    finally:
        wb.close()
    def cell(r,c): return rows[r-1][c-1]
    if cell(8,1) != 'Fallzahl' or cell(5,1) != DELIVERY:
        raise ValueError(path.name+': layout/delivery mismatch')
    n_raw = cell(8,2)
    if isinstance(n_raw,bool) or not isinstance(n_raw,(int,float)) or not math.isfinite(n_raw) or n_raw<=0 or not float(n_raw).is_integer():
        raise ValueError(path.name+': invalid N')
    n = int(n_raw)
    fields = selection_fields(str(cell(2,1)))
    allowed = {'Prozeduren','Nebendiagnosen','Entlassungsgrund','Hauptdiagnosen','Hauptdiagnose','Altersgruppe','Altersgruppen','Altersklasse','Altersklassen'}
    if set(fields)-allowed or fields.get('Prozeduren') != OPS:
        raise ValueError(path.name+': unexpected filters')
    if fields.get('Nebendiagnosen',set()) != (R13 if kind.startswith('dys') else set()):
        raise ValueError(path.name+': exposure definition mismatch')
    death = fields.get('Entlassungsgrund',set())
    if kind.endswith('death'):
        if len(death)!=1 or not next(iter(death)).startswith('07'):
            raise ValueError(path.name+': must select discharge death')
    elif death:
        raise ValueError(path.name+': unexpected discharge filter')
    hd_actual = fields.get('Hauptdiagnosen',fields.get('Hauptdiagnose',set()))
    hd_expected = {hd.upper()+'.'+str(k) for k in (0,1,2,3,4,5,6,8,9)} if hd in ('i61','i63') else set()
    if hd_actual != hd_expected:
        raise ValueError(path.name+': principal diagnosis mismatch')
    age_keys = [k for k in fields if k.startswith('Alters')]
    if original:
        if age_keys:
            raise ValueError(path.name+': original reference has age filter')
    elif len(age_keys)!=1 or fields[age_keys[0]]!=set(AGES[age]):
        raise ValueError(path.name+': age filter mismatch')
    distributions = {}
    for label, indices, lc, vc in [('sex',range(11,15),1,2),('pccl',range(8,15),7,8),('age',range(8,len(rows)+1),10,11)]:
        counts = {}
        for r in indices:
            name, fraction = cell(r,lc),cell(r,vc)
            if name is None and fraction is None: continue
            if name is None or fraction is None: raise ValueError(path.name+': incomplete distribution')
            raw = n*float(fraction); count = round(raw)
            if abs(raw-count)>1e-6 or count<0: raise ValueError(path.name+': unrecoverable distribution count')
            name = str(int(name)) if isinstance(name,(int,float)) and float(name).is_integer() else str(name)
            if name in counts: raise ValueError(path.name+': duplicate distribution label')
            counts[name]=count
        if sum(counts.values()) != n: raise ValueError(path.name+': distribution does not partition N')
        distributions[label]=counts
    if not original and sum(distributions['age'][a] for a in AGES[age]) != n:
        raise ValueError(path.name+': cases outside selected ages')
    if set(distributions['sex'])!={'männlich','weiblich','divers','unbekannt'} or set(distributions['pccl'])!={str(i) for i in range(7)}:
        raise ValueError(path.name+': unexpected sex/PCCL labels')
    mean, sd = float(cell(12,5)),float(cell(13,5))
    if not math.isfinite(mean) or not math.isfinite(sd) or min(mean,sd)<0:
        raise ValueError(path.name+': invalid mean/SD')
    s_raw = n*mean
    sample_q = (n-1)*sd*sd+n*mean*mean
    population_q = n*(sd*sd+mean*mean)
    err_s, err_q = abs(s_raw-round(s_raw)), abs(sample_q-round(sample_q))
    if max(err_s,err_q)>MOMENT_TOL:
        raise ValueError(path.name+': integer moment consistency failed')
    m = Moments(n,round(s_raw),round(sample_q)).validate()
    if abs(float(m.mean)-mean)>1e-10 or abs(math.sqrt(float(m.sample_variance))-sd)>1e-9:
        raise ValueError(path.name+': moments fail back-calculation')
    audit = {'file':path.name,'sha256':digest,'size_bytes':path.stat().st_size,'selection':str(cell(2,1)),'delivery':str(cell(5,1)),
             'n':n,'mean_days':mean,'sd':sd,'first_moment_integer_error':err_s,
             'sample_q_integer_error':err_q,'population_q_integer_error':abs(population_q-round(population_q)),
             'sum_days':m.s,'sum_squared_days':m.q,'age_counts':distributions['age'],
             'sex_partition_verified':True,'pccl_partition_verified':True}
    return m,audit,distributions


def summarize(groups, label):
    selected_t = sum_moments(g['total'] for g in groups)
    selected_d = sum_moments(g['dys'] for g in groups)
    selected_c = selected_t-selected_d
    included=[];excluded=[]
    for g in groups:
        c = g['total']-g['dys']
        (included if g['dys'].n>0 and c.n>0 else excluded).append({**g,'no_dys':c})
    if not included: raise ValueError('No common support')
    total = sum_moments(g['total'] for g in included)
    dys = sum_moments(g['dys'] for g in included)
    no_dys = total-dys
    standardized_d=Fraction(0); standardized_c=Fraction(0)
    variance_d=Fraction(0); variance_c=Fraction(0); have_variance=True
    rows=[]; float_d=0.0;float_c=0.0;float_v=0.0
    for g in included:
        t,d,c = g['total'],g['dys'],g['no_dys']
        weight = Fraction(t.n,total.n)
        standardized_d+=weight*d.mean;standardized_c+=weight*c.mean
        if d.n<2 or c.n<2: have_variance=False
        else:
            variance_d+=weight*weight*d.mean_variance
            variance_c+=weight*weight*c.mean_variance
            # Separate floating-point implementation of the same moment formula.
            float_v+=float(weight)**2*((d.q-d.s*d.s/d.n)/(d.n-1)/d.n+(c.q-c.s*c.s/c.n)/(c.n-1)/c.n)
        float_d+=float(weight)*d.s/d.n;float_c+=float(weight)*c.s/c.n
        rows.append({'age_band':g['age'],'principal_diagnosis':g['hd'],'all_n':t.n,
                     'dys':d.result(),'no_dys':c.result(),'reference_weight':float(weight),
                     'reference_weight_exact':str(weight),'difference_days':float(d.mean-c.mean)})
    assert sum(Fraction(g['total'].n,total.n) for g in included)==1
    difference=standardized_d-standardized_c
    variance=variance_d+variance_c if have_variance else None
    ci=[float(difference)-Z*math.sqrt(float(variance)),float(difference)+Z*math.sqrt(float(variance))] if variance is not None else None
    crude=dys.mean-no_dys.mean
    crude_v=dys.mean_variance+no_dys.mean_variance if min(dys.n,no_dys.n)>1 else None
    crude_ci=[float(crude)-Z*math.sqrt(float(crude_v)),float(crude)+Z*math.sqrt(float(crude_v))] if crude_v is not None else None
    assert abs(float_d-float(standardized_d))<1e-10
    assert abs(float_c-float(standardized_c))<1e-10
    if variance is not None: assert abs(float_v-float(variance))<1e-10
    # Weighted total means must reproduce the pooled total mean exactly.
    assert sum(Fraction(g['total'].n,total.n)*g['total'].mean for g in included)==total.mean
    return {'analysis':label,'adjusted_factors':'adult_age_band + principal_diagnosis',
            'reference':'Pooled target-population age-by-principal-diagnosis distribution; observed weights fixed',
            'selected_population':{'all_n':selected_t.n,'dys_n':selected_d.n,'no_dys_n':selected_c.n},
            'common_support':{'included_strata':len(included),'excluded_strata':len(excluded),
                              'all_n':total.n,'dys_n':dys.n,'no_dys_n':no_dys.n,
                              'all_coverage':total.n/selected_t.n,'dys_coverage':dys.n/selected_d.n,'no_dys_coverage':no_dys.n/selected_c.n},
            'standardized':{'dys_mean_days':float(standardized_d),'no_dys_mean_days':float(standardized_c),
                            'mean_difference_days':float(difference),'ci95':ci,
                            'variance':float(variance) if variance is not None else None,
                            'mean_difference_exact':str(difference)},
            'crude_same_population':{'dys':dys.result(),'no_dys':no_dys.result(),
                                     'mean_difference_days':float(crude),'ci95':crude_ci},
            'strata':rows,'excluded_strata':[{'age_band':g['age'],'principal_diagnosis':g['hd'],'all_n':g['total'].n,'dys_n':g['dys'].n,'no_dys_n':g['no_dys'].n} for g in excluded],
            'floating_point_crosscheck':{'mean_dys_error':float_d-float(standardized_d),'mean_no_dys_error':float_c-float(standardized_c),'variance_error':float_v-float(variance) if variance is not None else None}}


def run(raw_dir, out_dir, survivors=True, reference_manifest=None):
    raw_dir=raw_dir.resolve();out_dir=out_dir.resolve();out_dir.mkdir(parents=True,exist_ok=True)
    source_m={};source_a=[];source_dist={};used_kinds=KINDS if survivors else KINDS[:2]
    for age in AGES:
        for hd in HD:
            for kind in used_kinds:
                p=raw_dir/f'acute_joint_{age}_{hd}_{kind}_2025.xlsx'
                m,a,d=read_source(p,age,hd,kind)
                source_m[age,hd,kind]=m;source_a.append(a);source_dist[age,hd,kind]=d
    manifest_check={'status':'not_requested'}
    if reference_manifest is not None:
        prior=json.loads(reference_manifest.read_text(encoding='utf-8'))
        if prior.get('cohort')!='acute' or prior.get('delivery')!=DELIVERY:
            raise ValueError('Previously verified manifest cohort/delivery mismatch')
        for a in source_a:
            expected=prior['exports'][a['file']]
            if (a['sha256']!=expected['source']['sha256'] or a['n']!=expected['n'] or a['selection']!=expected['selection']):
                raise ValueError('Source differs from previously verified manifest: '+a['file'])
        manifest_check={'status':'passed','matching_workbooks':len(source_a),'file':reference_manifest.name,
                        'sha256':hashlib.sha256(reference_manifest.read_bytes()).hexdigest()}
    # Check age totals and distributions against independently exported unrestricted cohorts.
    refs=[]
    for kind in used_kinds:
        m,a,dist=read_source(raw_dir/f'acute_{kind}_2025.xlsx',kind=kind,original=True)
        refs.append(a)
        for age,labels in AGES.items():
            mm=source_m[age,'allhd',kind]
            if mm.n != sum(dist['age'][s] for s in labels): raise ValueError('Original adult count mismatch')
            for s in labels:
                if source_dist[age,'allhd',kind]['age'][s] != dist['age'][s]: raise ValueError('Original native-age count mismatch')
        child=m-sum_moments(source_m[age,'allhd',kind] for age in AGES)
        if child.n != sum(v for k,v in dist['age'].items() if k not in sum(AGES.values(),[])):
            raise ValueError('Pediatric complement mismatch')
    # Principal diagnoses are mutually exclusive; other means all remaining principal diagnoses.
    diagnosis_m={}
    for age in AGES:
        for kind in used_kinds:
            for hd in ('i63','i61'):diagnosis_m[age,hd,kind]=source_m[age,hd,kind]
            diagnosis_m[age,'other',kind]=source_m[age,'allhd',kind]-source_m[age,'i63',kind]-source_m[age,'i61',kind]
            assert sum_moments(diagnosis_m[age,h,kind] for h in ('i63','i61','other'))==source_m[age,'allhd',kind]
    primary=[];alive=[]
    for age in AGES:
        for hd in ('i63','i61','other'):
            t=diagnosis_m[age,hd,'all'];d=diagnosis_m[age,hd,'dys'];c=t-d
            assert d+c==t
            primary.append({'age':age,'hd':hd,'total':t,'dys':d})
            if survivors:
                td=diagnosis_m[age,hd,'all_death'];dd=diagnosis_m[age,hd,'dys_death'];cd=td-dd
                ts=t-td;ds=d-dd;cs=c-cd
                assert ts-ds==cs and ds+cs==ts
                alive.append({'age':age,'hd':hd,'total':ts,'dys':ds})
    results={'schema_version':1,'computed_at_utc':datetime.now(timezone.utc).isoformat(),
             'cohort':'acute','delivery':DELIVERY,'primary':summarize(primary,'LOS_age_principal_diagnosis'),
             'scope':'Adult hospital episodes; same age and principal-diagnosis groups as joint mortality analyses. Sex and PCCL are not adjusted.',
             'variance_method':'Exact integer first/second moments with sample Info SD; fixed pooled weights; independent-episode normal approximation',
             'sd_convention_status':'Empirically consistent with sample SD in every source; no official denominator definition retrieved.',
             'limitations':['Age 18-74 vs 75+ leaves residual within-band confounding.','Broad principal-diagnosis groups do not measure neurological severity.','No NIHSS, simultaneous sex/PCCL, hospital clustering or patient-level repeated-admission adjustment.','Confidence intervals condition on observed reference weights and do not include coding/completeness uncertainty.','Associated extra hospital days are not proven caused by dysphagia or avoidable.']}
    if survivors:
        results['survivor_sensitivity']=summarize(alive,'LOS_age_principal_diagnosis_discharge_alive')
        results['survivor_sensitivity']['selection_warning']='Conditions on surviving hospital discharge; uses a separate pooled survivor reference and is descriptive, not a causal correction.'
    all_a=source_a+refs
    for a in all_a:
        if hashlib.sha256((raw_dir/a['file']).read_bytes()).hexdigest()!=a['sha256']:
            raise ValueError('Source bytes changed during analysis')
    audits={'source_workbooks':source_a,'reference_workbooks':refs,
            'source_count':len(source_a),'primary_source_count':12,'survivor_additional_source_count':12 if survivors else 0,
            'max_source_first_moment_integer_error':max(a['first_moment_integer_error'] for a in source_a),
            'max_source_sample_q_integer_error':max(a['sample_q_integer_error'] for a in source_a),
            'min_source_population_q_integer_error':min(a['population_q_integer_error'] for a in source_a),
            'max_source_population_q_integer_error':max(a['population_q_integer_error'] for a in source_a),
            'all_filter_checks_passed':True,'original_age_partitions_verified':True,'all_source_hashes_unchanged':True,
            'exact_moment_partition_and_complement_checks_passed':True,'fixed_weight_fraction_crosscheck_passed':True,
            'previously_verified_mortality_source_manifest':manifest_check}
    json_write(out_dir/'los_age_diagnosis_results.json',results)
    json_write(out_dir/'los_source_audit.json',audits)
    columns=['analysis','adjusted_factors','all_n','dys_n','no_dys_n','included_strata','dys_standardized_mean_days','no_dys_standardized_mean_days','mean_difference_days','ci_lower','ci_upper','crude_mean_difference_days','crude_ci_lower','crude_ci_upper']
    rows=[]
    for k in ('primary','survivor_sensitivity'):
        if k not in results:continue
        r=results[k];s=r['standardized'];c=r['crude_same_population'];support=r['common_support']
        rows.append({'analysis':r['analysis'],'adjusted_factors':r['adjusted_factors'],
                     **{n:support[n] for n in ('all_n','dys_n','no_dys_n','included_strata')},
                     'dys_standardized_mean_days':s['dys_mean_days'],'no_dys_standardized_mean_days':s['no_dys_mean_days'],
                     'mean_difference_days':s['mean_difference_days'],'ci_lower':s['ci95'][0] if s['ci95'] else None,'ci_upper':s['ci95'][1] if s['ci95'] else None,
                     'crude_mean_difference_days':c['mean_difference_days'],'crude_ci_lower':c['ci95'][0] if c['ci95'] else None,'crude_ci_upper':c['ci95'][1] if c['ci95'] else None})
    with (out_dir/'los_age_diagnosis_summary.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    print(json.dumps({'status':'passed','rows':rows,'source_audit':{k:v for k,v in audits.items() if not isinstance(v,list)}},ensure_ascii=True))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root','--raw-dir',dest='raw_dir',type=Path,required=True,help='Directory containing the native InEK workbooks; read only')
    ap.add_argument('--out-dir',type=Path,required=True,help='Private analysis output directory; do not publish detailed audit or strata files')
    ap.add_argument('--primary-only',action='store_true')
    ap.add_argument('--reference-manifest',type=Path,help='Optional verified three-factor mortality source manifest for byte-identity checks')
    args=ap.parse_args();run(args.raw_dir,args.out_dir,not args.primary_only,args.reference_manifest)
