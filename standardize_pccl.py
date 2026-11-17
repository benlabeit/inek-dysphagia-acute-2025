"""Direct PCCL-standardized outcomes from existing parsed InEK exports.

Run from any working directory: python results/standardize_pccl.py
Uses the standard library for parsed JSON inputs; raw-XLSX fallback uses the
project parser and openpyxl. No source data or manuscript is modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parent
if ROOT.name == 'results': ROOT = ROOT.parent
sys.path.insert(0,str(ROOT))
Z = 1.959963984540054


def comparison(a, n, b, m):
    assert 0 <= a <= n and 0 <= b <= m and n > 0 and m > 0
    p, q = a/n, b/m
    vd, vc = p*(1-p)/n, q*(1-q)/m
    result = {'dys_events': a, 'dys_n': n, 'no_dys_events': b, 'no_dys_n': m,
              'dys_rate': p, 'no_dys_rate': q,
              'small_derived_event_cell': min(a, b) < 5,
              'risk_difference': p-q,
              'risk_difference_ci': [p-q-Z*math.sqrt(vd+vc), p-q+Z*math.sqrt(vd+vc)]}
    if a > 0 and b > 0:
        rr = p/q
        se = math.sqrt(1/a-1/n+1/b-1/m)
        result.update(rr=rr, rr_ci=[rr*math.exp(-Z*se), rr*math.exp(Z*se)])
    else:
        result.update(rr=None, rr_ci=None)
    return result


def load(cohort, kind, root=ROOT):
    path = root/'parsed'/f'{cohort}_{kind}_2025.json'
    raw = root/'raw'/f'{cohort}_{kind}_2025.xlsx'
    if path.exists():
        export = json.loads(path.read_text(encoding='utf-8'))
        if raw.exists():
            assert hashlib.sha256(raw.read_bytes()).hexdigest() == export['source']['sha256'], 'Stale parsed export'
    else:
        from analyze_acute_exports import parse_inek
        export = parse_inek(raw)
    rows = export['distributions']['pccl']
    assert len(rows) == 7
    assert {row['label'] for row in rows} == {str(k) for k in range(7)}
    counts = {int(row['label']): row['count'] for row in rows}
    assert all(isinstance(n, int) and n >= 0 for n in counts.values())
    assert sum(counts.values()) == export['n']
    assert max(row['integer_recovery_error'] for row in rows) < 1e-6
    assert all(abs(row['fraction']*export['n']-row['count']) < 1e-6 for row in rows)
    return export, counts


def outcome(cohort, suffix, root=ROOT):
    keys = ['all', 'dys', 'all_'+suffix, 'dys_'+suffix]
    inputs = [load(cohort, k, root) for k in keys]
    exports = [x[0] for x in inputs]
    all_n, dys_n, all_e, dys_e = [x[1] for x in inputs]
    assert len({e['delivery'] for e in exports}) == 1
    n = exports[0]['n']
    pd = pc = vd = vc = 0.0
    strata = []
    for k in range(7):
        nd, nc = dys_n[k], all_n[k]-dys_n[k]
        ed, ec = dys_e[k], all_e[k]-dys_e[k]
        c = comparison(ed, nd, ec, nc)
        w = all_n[k]/n
        pd += w*c['dys_rate']
        pc += w*c['no_dys_rate']
        vd += w*w*c['dys_rate']*(1-c['dys_rate'])/nd
        vc += w*w*c['no_dys_rate']*(1-c['no_dys_rate'])/nc
        strata.append({'pccl': k, 'pooled_n': all_n[k], 'pooled_events': all_e[k],
                       'reference_weight': w, **c})
    assert abs(sum(s['reference_weight'] for s in strata)-1) < 1e-12
    assert sum(s['dys_events'] for s in strata) == exports[3]['n']
    assert sum(s['no_dys_events'] for s in strata) == exports[2]['n']-exports[3]['n']
    rr = pd/pc
    se_log_rr = math.sqrt(vd/(pd*pd)+vc/(pc*pc))
    se_rd = math.sqrt(vd+vc)
    crude = comparison(exports[3]['n'], exports[1]['n'],
                       exports[2]['n']-exports[3]['n'], exports[0]['n']-exports[1]['n'])
    return {
        'cohort': cohort, 'outcome': suffix, 'delivery': exports[0]['delivery'],
        'reference': 'Pooled full cohort PCCL distribution (0-6); observed weights fixed',
        'source_files': {k:e['source'] for k,e in zip(keys,exports)},
        'selections': {k:e['selection'] for k,e in zip(keys,exports)},
        'validation': {'all_seven_pccl_categories_present': True,
                       'all_counts_exact_integer_recovery': True,
                       'all_four_partitions_sum_to_their_cohort_n': True,
                       'each_event_count_is_between_zero_and_its_group_n': True,
                       'all_seven_strata_have_both_groups': True,
                       'note': 'PCCL is a single-valued Info distribution, unlike overlapping diagnosis rows.'},
        'crude': crude, 'strata': strata,
        'standardized': {
            'dys_rate': pd, 'no_dys_rate': pc,
            'dys_rate_ci': [pd-Z*math.sqrt(vd), pd+Z*math.sqrt(vd)],
            'no_dys_rate_ci': [pc-Z*math.sqrt(vc), pc+Z*math.sqrt(vc)],
            'rr': rr, 'rr_ci': [rr*math.exp(-Z*se_log_rr), rr*math.exp(Z*se_log_rr)],
            'risk_difference': pd-pc,
            'risk_difference_ci': [pd-pc-Z*se_rd, pd-pc+Z*se_rd],
            'dys_variance': vd, 'no_dys_variance': vc,
        },
        'method': 'Direct standardization over seven exhaustive PCCL strata. Independent binomial stratum variances; delta-method normal intervals for risk difference and log RR. Reference weights treated as fixed.',
        'limitations': [
            'PCCL standardization is descriptive case-mix standardization, not baseline NIHSS adjustment.',
            'PCCL is derived from recorded complications/comorbidities and may incorporate exposure- or outcome-related diagnoses; temporal order is unavailable.',
            'Conditioning on PCCL can remove mediated associations or introduce selection/collider bias.',
            'No simultaneous age, sex, clinical severity, or hospital adjustment is possible from the available marginals.',
            'Model-based intervals omit hospital clustering, repeated admissions, coding uncertainty and residual confounding.',
            'Strata with fewer than five reconstructed outcome events in either arm are flagged; their individual intervals are sparse-data approximations and should not be highlighted as robust subgroup findings.',
            'All analyses are exploratory; pneumonia is the unique J12-J18 secondary-diagnosis union, not the combined J69.0 endpoint.',
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cohort',choices=['all','acute','rehab'],default='all')
    parser.add_argument('--data-root',type=Path,default=ROOT)
    parser.add_argument('--out-dir',type=Path)
    args=parser.parse_args()
    cohorts=['acute','rehab'] if args.cohort=='all' else [args.cohort]
    result = {cohort: {suffix:outcome(cohort,suffix,args.data_root) for suffix in ['death','pneumonia']}
              for cohort in cohorts}
    dest=args.out_dir or args.data_root/'results'
    dest.mkdir(parents=True,exist_ok=True)
    stem='pccl_standardization' if args.cohort=='all' else args.cohort+'_pccl_standardization'
    path = dest/(stem+'.json')
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    for cohort, outcomes in result.items():
        for name, r in outcomes.items():
            print(json.dumps({'cohort':cohort,'outcome':name,'crude_rr':r['crude']['rr'],
                              'standardized':r['standardized'],
                              'conditional_rr':[[s['pccl'],s['dys_events'],s['dys_n'],s['no_dys_events'],s['no_dys_n'],s['rr'],s['rr_ci']] for s in r['strata']]},ensure_ascii=True))


if __name__ == '__main__':
    main()
