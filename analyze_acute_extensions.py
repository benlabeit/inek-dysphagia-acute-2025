"""Exact aggregate acute-cohort extensions from six unchanged InEK exports.

Run from the project directory. Stores parsed sources, all filters/hashes and
derived results. Missing table rows are never interpreted as zero.
"""
from pathlib import Path
import json
import math

from analyze_acute_exports import (Z, parse_inek, save_json, lookup, contrast,
                                  complement, los_compare, drg_compare)

ROOT = Path(__file__).resolve().parent


def read(stem):
    result = parse_inek(ROOT / 'raw' / (stem + '.xlsx'))
    save_json(result, ROOT / 'parsed' / (stem + '.json'))
    return result


def count(export, sheet, code):
    row = lookup(export, sheet, code)
    if row is None:
        raise ValueError(f'Missing {sheet} {code} in {export["source"]["path"]}')
    return row['cases']


def age_band(label):
    if label.startswith('65-') or label.startswith('75-'):
        return '65-79'
    if label.startswith('80'):
        return '80+'
    return '<65'


def age_counts(export):
    groups = {k: 0 for k in ['<65', '65-79', '80+']}
    for row in export['distributions']['age']:
        if row['count'] is None:
            raise ValueError('Age count could not be recovered exactly')
        groups[age_band(row['label'])] += row['count']
    assert sum(groups.values()) == export['n']
    return groups


def standardize_age(total, dys, total_death, dys_death):
    ta, da, te, de = map(age_counts, [total, dys, total_death, dys_death])
    rows = []
    pd = pc = vd = vc = 0.0
    log_effects = []
    for band in ta:
        nd, nc, ed, ec = da[band], ta[band]-da[band], de[band], te[band]-de[band]
        assert 0 <= ed <= nd and 0 <= ec <= nc
        w = ta[band]/total['n']
        row = {'age_band': band, 'all_n': ta[band], 'reference_weight': w,
               **contrast(ed, nd, ec, nc)}
        rows.append(row)
        pd += w*ed/nd
        pc += w*ec/nc
        vd += w*w*(ed/nd)*(1-ed/nd)/nd
        vc += w*w*(ec/nc)*(1-ec/nc)/nc
        if ed and ec:
            log_effects.append((math.log(row['rr']), 1/ed-1/nd+1/ec-1/nc))
    rr = pd/pc
    selog = math.sqrt(vd/(pd*pd)+vc/(pc*pc))
    sediff = math.sqrt(vd+vc)
    het = None
    if len(log_effects) == 3:
        pooled = sum(v/s for v,s in log_effects)/sum(1/s for v,s in log_effects)
        q = sum((v-pooled)**2/s for v,s in log_effects)
        het = {'cochran_q_log_rr': q, 'df': 2, 'p': math.exp(-q/2),
               'note': 'Exploratory between-age-band RR heterogeneity, independent-binomial model.'}
    return {'rows': rows, 'reference': 'Entire selected acute OPS cohort',
            'dys_rate': pd, 'no_dys_rate': pc,
            'dys_rate_ci': [pd-Z*math.sqrt(vd), pd+Z*math.sqrt(vd)],
            'no_dys_rate_ci': [pc-Z*math.sqrt(vc), pc+Z*math.sqrt(vc)],
            'rr': rr, 'rr_ci': [rr*math.exp(-Z*selog),rr*math.exp(Z*selog)],
            'risk_difference': pd-pc,
            'risk_difference_ci': [pd-pc-Z*sediff,pd-pc+Z*sediff],
            'heterogeneity': het,
            'method': 'Direct standardization over three broad age bands; observed reference weights fixed; delta-method normal CI; exploratory age-only comparison, not multivariable adjustment.',
            'warning': '<65 includes the 22 cases aged under 18 in this OPS-defined cohort; within-band age differences and other confounding remain.'}


def survivor_info(total, dead):
    c = complement(total['n'], total['los']['mean'], total['los']['sd'],
                   dead['n'], dead['los']['mean'], dead['los']['sd'],
                   sd_convention='sample')
    return {'n': c['n'], 'los': {'mean': c['mean'], 'sd': c['sd_sample']},
            'moment_subtraction': c}


def survivor_drg(total, dead):
    rows, skipped = [], []
    for t in total['tables']['DRG-Verteilung']:
        if t['is_rest']:
            continue
        d = lookup(dead, 'DRG-Verteilung', t['code'])
        if d is None:
            skipped.append({'code': t['code'], 'reason': 'Death row absent: zero or suppressed, cannot reconstruct exactly'})
            continue
        if t['cases'] == d['cases']:
            continue
        c = complement(t['cases'],t['los_mean'],t['los_sd'],
                       d['cases'],d['los_mean'],d['los_sd'],sd_convention='population')
        rows.append({'code': t['code'], 'label': t['label'], 'cases': c['n'],
                     'los_mean': c['mean'], 'los_sd': c['sd_population'], 'is_rest': False})
    return {'n': total['n']-dead['n'], 'tables': {'DRG-Verteilung':rows}, 'skipped':skipped}


def principal_mortality(total, dys, total_death, dys_death, prefix):
    expected = [prefix+'.'+str(i) for i in [0,1,2,3,4,5,6,8,9]]
    sums, missing = {}, {}
    for name, export in [('all', total),('dys',dys),('death_all',total_death),('death_dys',dys_death)]:
        rs = [lookup(export,'Hauptdiagnosen',code) for code in expected]
        missing[name] = [code for code,row in zip(expected,rs) if row is None]
        sums[name] = sum(row['cases'] for row in rs if row is not None)
    complete = not any(missing.values())
    result = {'expected_codes': expected, 'listed_counts':sums,
              'missing_codes':missing, 'exact':complete}
    if complete:
        result['comparison'] = contrast(sums['death_dys'],sums['dys'],
                                        sums['death_all']-sums['death_dys'],sums['all']-sums['dys'])
    else:
        result['note'] = 'Exact subgroup mortality not available from these marginal tables: absent rows may contain suppressed cases. Direct principal-diagnosis union query needed.'
    return result


def main():
    a,d,pa,pd,ad,dd = [read('acute_'+x+'_2025') for x in
                       ['all','dys','all_pneumonia','dys_pneumonia','all_death','dys_death']]
    exports = dict(all=a,dys=d,pneumonia_all=pa,pneumonia_dys=pd,death_all=ad,death_dys=dd)
    assert len({x['delivery'] for x in exports.values()}) == 1
    assert all(all(v for k,v in x['checks'].items() if k.endswith('_partition')) for x in exports.values())
    n,m=d['n'],a['n']-d['n']
    result={'delivery':a['delivery'],'source_files':{k:x['source'] for k,x in exports.items()},
            'selections':{k:x['selection'] for k,x in exports.items()},
            'cohort_n':{'all':a['n'],'dys':n,'no_dys':m},
            'warnings':['All comparisons are case-based coding associations. Repeated admissions and hospital clustering are unavailable.',
                        'Info SD is sample SD; DRG SD is population SD. This convention is inferred independently from integer LOS second moments, not a retrieved provider definition.',
                        'Exploratory extensions were selected after the original slides were reviewed; they are not prespecified analyses.']}
    asp_all=count(a,'Nebendiagnosen','J69.0');asp_d=count(d,'Nebendiagnosen','J69.0')
    both_all=count(pa,'Nebendiagnosen','J69.0');both_d=count(pd,'Nebendiagnosen','J69.0')
    pneumonia={'definition':'Unique cases with at least one secondary J12-J18 diagnosis (exact selected endcodes in query metadata)',
               'comparison':contrast(pd['n'],n,pa['n']-pd['n'],m),
               'overlap_J69_0':{'all':both_all,'dys':both_d,'no_dys':both_all-both_d},
               'disjoint_groups':{}}
    groups={'J12_J18_only':(pa['n']-both_all,pd['n']-both_d),
            'J69_0_only':(asp_all-both_all,asp_d-both_d),
            'both':(both_all,both_d),
            'neither':(a['n']-(pa['n']+asp_all-both_all),n-(pd['n']+asp_d-both_d))}
    for name,(total,exposed) in groups.items():
        pneumonia['disjoint_groups'][name]={'all_cases':total,**contrast(exposed,n,total-exposed,m)}
    assert sum(t for t,e in groups.values())==a['n'] and sum(e for t,e in groups.values())==n
    pneumonia['combined_J12_J18_or_J69_0']=contrast(pd['n']+asp_d-both_d,n,
                pa['n']+asp_all-both_all-(pd['n']+asp_d-both_d),m)
    timing={}
    for name,exp in [('all_pneumonia',pa),('dys_pneumonia',pd)]:
        late=count(exp,'Nebendiagnosen','U69.01'); early=count(exp,'Nebendiagnosen','U69.04')
        timing[name]={'n':exp['n'],'U69_01':late,'U69_04':early,
                      'minimum_cocoded_cases':max(0,late+early-exp['n']),
                      'union_count_bounds':[max(late,early),min(late+early,exp['n'])],
                      'union_coverage_bounds':[max(late,early)/exp['n'],min(late+early,exp['n'])/exp['n']]}
    pneumonia['timing_code_coverage']=timing
    pneumonia['timing_warning']='The two U69 marginals can overlap and must not be summed as disjoint timing categories. Timing is relative to hospital admission, not dysphagia onset. Exact union coverage requires a further intersection query.'
    result['pneumonia']=pneumonia
    result['mortality']=contrast(dd['n'],n,ad['n']-dd['n'],m)
    result['mortality_age_standardized']=standardize_age(a,d,ad,dd)
    result['mortality_principal_diagnosis']={p:principal_mortality(a,d,ad,dd,p) for p in ['I63','I61']}
    sa,sd=survivor_info(a,ad),survivor_info(d,dd)
    result['survivor_los']=los_compare(sa,sd)
    result['survivor_los']['selection_warning']='Conditions on discharge alive; mortality-related selection prevents causal interpretation.'
    sda,sdd=survivor_drg(a,ad),survivor_drg(d,dd)
    result['survivor_drg']=drg_compare(sda,sdd)
    result['survivor_drg']['reconstruction']={'all_skipped':sda['skipped'],'dys_skipped':sdd['skipped'],
        'warning':'Restricted to DRGs with explicit death rows in both total and dysphagia exports. Missing death rows are not zero. This restricted estimate is not the full survivor-cohort DRG-standardized estimate.'}
    result['table1_distributions']={}
    for distribution in ['sex','age','pccl']:
        ds={r['label']:r['count'] for r in d['distributions'][distribution]}
        result['table1_distributions'][distribution]=[{'label':r['label'],'all':r['count'],
            'dys':ds[r['label']],'no_dys':r['count']-ds[r['label']]} for r in a['distributions'][distribution]]
    result['los_input_moments']={k:{'n':x['n'],**x['los'],'sd_convention':'sample',
            'integer_second_moment_check':x['info_sd_convention_diagnostic']} for k,x in exports.items()}
    save_json(result,ROOT/'results'/'acute_extensions.json')
    summary={k:result[k] for k in ['mortality','mortality_age_standardized','mortality_principal_diagnosis','survivor_los']}
    summary['survivor_drg_analyses']=result['survivor_drg']['analyses']
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':
    main()
