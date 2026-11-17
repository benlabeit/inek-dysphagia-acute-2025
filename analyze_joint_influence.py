"""Post hoc deterministic influence diagnostics for three-factor standardization.

Outputs aggregate results only. Outcome-dependent stratum exclusions change
the target population; these diagnostics do not replace the primary model.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
Z = 1.959963984540054
ANALYSES = ['age_sex_principal_diagnosis', 'age_principal_diagnosis_pccl_sensitivity']


def ratio_interval(pd, pc, vd, vc):
    rr = pd/pc if pc else None
    if not pd or not pc:
        return float(rr) if rr is not None else None, None, None
    se = math.sqrt(float(vd/pd**2+vc/pc**2))
    return float(rr), float(rr)*math.exp(-Z*se), float(rr)*math.exp(Z*se)


def summarize(cells, full, selected):
    nt = sum(c['all_n'] for c in cells)
    nd = sum(c['dys_n'] for c in cells)
    nc = sum(c['no_dys_n'] for c in cells)
    full_n = sum(c['all_n'] for c in full)
    full_d = sum(c['dys_n'] for c in full)
    full_c = sum(c['no_dys_n'] for c in full)
    row = {'status': 'estimated' if cells else 'not_estimable',
           'retained_strata': len(cells), 'excluded_primary_supported_strata': len(full)-len(cells),
           'all_n': nt, 'dys_n': nd, 'no_dys_n': nc,
           'reference_weight_retained': nt/full_n,
           'reference_weight_excluded': 1-nt/full_n,
           'coverage_of_primary_supported_n': nt/full_n,
           'dys_coverage_of_primary_support': nd/full_d,
           'no_dys_coverage_of_primary_support': nc/full_c,
           'coverage_of_selected_adult_n': nt/selected['all_n'],
           'dys_coverage_of_selected_adult_n': nd/selected['dys_n'],
           'no_dys_coverage_of_selected_adult_n': nc/selected['no_dys_n']}
    fields = ['dys_standardized_risk', 'no_dys_standardized_risk', 'rr', 'rr_ci_lower', 'rr_ci_upper',
              'risk_difference', 'risk_difference_ci_lower', 'risk_difference_ci_upper',
              'matched_crude_rr', 'matched_crude_rr_ci_lower', 'matched_crude_rr_ci_upper']
    if not cells:
        row.update({k: None for k in fields})
        return row
    pd = pc = vd = vc = F(0)
    for c in cells:
        w = F(c['all_n'], nt)
        p, q = F(c['dys_events'], c['dys_n']), F(c['no_dys_events'], c['no_dys_n'])
        pd += w*p; pc += w*q
        vd += w*w*p*(1-p)/c['dys_n']
        vc += w*w*q*(1-q)/c['no_dys_n']
    rr, lo, hi = ratio_interval(pd, pc, vd, vc)
    ed = sum(c['dys_events'] for c in cells)
    ec = sum(c['no_dys_events'] for c in cells)
    cp, cq = F(ed, nd), F(ec, nc)
    crude, clo, chi = ratio_interval(cp, cq, cp*(1-cp)/nd, cq*(1-cq)/nc)
    rd = float(pd-pc)
    se_rd = math.sqrt(float(vd+vc))
    row.update(dys_standardized_risk=float(pd), no_dys_standardized_risk=float(pc),
               rr=rr, rr_ci_lower=lo, rr_ci_upper=hi, risk_difference=rd,
               risk_difference_ci_lower=rd-Z*se_rd, risk_difference_ci_upper=rd+Z*se_rd,
               matched_crude_rr=crude, matched_crude_rr_ci_lower=clo, matched_crude_rr_ci_upper=chi)
    return row


def analyze(cohort, results_dir):
    path = results_dir/f'{cohort}_joint_standardization.json'
    model = json.loads(path.read_text(encoding='utf-8'))
    if model['cohort'] != cohort:
        raise ValueError('Cohort does not match source result')
    rows = []
    for name in ANALYSES:
        result = model[name]
        if result['status'] != 'estimated':
            raise ValueError('Primary model is not estimable: '+name)
        cells = result['strata']
        for c in cells:
            d, a, m, b = [c[k] for k in ['dys_n','dys_events','no_dys_n','no_dys_events']]
            if any(not isinstance(x, int) or isinstance(x, bool) for x in [d,a,m,b]):
                raise ValueError('Non-integer source cell')
            if d <= 0 or m <= 0 or not 0 <= a <= d or not 0 <= b <= m or c['all_n'] != d+m:
                raise ValueError('Invalid supported source cell')
            if c['sparse_event_cell'] != (min(a,b,d-a,m-b)<5):
                raise ValueError('Sparse flag differs from events/non-events definition')
            if c['boundary_probability'] != (a in [0,d] or b in [0,m]):
                raise ValueError('Boundary flag differs from 0/1 probability definition')
        if sum(c['all_n'] for c in cells) != result['common_support']['all_n']:
            raise ValueError('Primary common-support population mismatch')
        selected = result['selected_population_before_common_support']
        scenarios = [('primary_supported_population', cells),
                     ('exclude_boundary_strata', [c for c in cells if not c['boundary_probability']]),
                     ('exclude_sparse_strata', [c for c in cells if not c['sparse_event_cell']])]
        baseline = None
        for scenario, retained in scenarios:
            summary = summarize(retained, cells, selected)
            if baseline is None:
                baseline = summary
                reported = result['standardized']
                for key, source_key in [('rr','rr'), ('risk_difference','risk_difference'),
                                        ('dys_standardized_risk','dys_rate'), ('no_dys_standardized_risk','no_dys_rate')]:
                    if summary[key] is None or reported[source_key] is None:
                        if summary[key] != reported[source_key]:
                            raise ValueError('Primary result mismatch: '+key)
                    elif not math.isclose(summary[key], reported[source_key], rel_tol=1e-11, abs_tol=1e-13):
                        raise ValueError('Primary result mismatch: '+key)
                if reported['rr_ci'] is not None:
                    for key, expected in zip(['rr_ci_lower','rr_ci_upper'],reported['rr_ci']):
                        if not math.isclose(summary[key],expected,rel_tol=1e-11,abs_tol=1e-13):
                            raise ValueError('Primary CI mismatch: '+key)
            summary['rr_difference_from_primary'] = summary['rr']-baseline['rr'] if summary['rr'] is not None and baseline['rr'] is not None else None
            summary['risk_difference_change_from_primary'] = summary['risk_difference']-baseline['risk_difference'] if summary['risk_difference'] is not None else None
            rows.append({'analysis': name, 'scenario': scenario, **summary})
    return {'cohort': cohort, 'analysis_type': 'post_hoc_outcome_dependent_influence_diagnostics',
            'source_result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'methods': 'Direct standardization recalculated with pooled weights renormalized within retained strata. Exact-rational risk/variance arithmetic; fixed-weight independent-binomial delta 95% intervals. Crude comparisons use the same retained population.',
            'sparse_definition': 'Fewer than five events or non-events in either group.',
            'boundary_definition': 'An event probability of zero or one in either group.',
            'warning': 'Exclusions depend on observed outcomes and alter the target population. These diagnostics assess numerical influence and do not replace the primary standardization or resolve confounding. Intervals retain the primary approximation limitations.',
            'individual_stratum_counts_included': False,
            'rows': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort', required=True, choices=['acute','rehab'])
    p.add_argument('--results-dir', type=Path, default=ROOT/'results')
    p.add_argument('--out-dir', type=Path, default=ROOT/'results')
    a = p.parse_args()
    report = analyze(a.cohort,a.results_dir)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    stem = a.cohort+'_joint_influence'
    (a.out_dir/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (a.out_dir/(stem+'.csv')).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report['rows'][0]));writer.writeheader();writer.writerows(report['rows'])
    print(json.dumps({'cohort':a.cohort,'aggregate_rows':len(report['rows']),'json':stem+'.json','csv':stem+'.csv'}))


if __name__=='__main__':main()
