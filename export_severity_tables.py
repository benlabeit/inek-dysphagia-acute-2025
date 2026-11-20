"""Curate cohort-specific severity sensitivity tables from validated local results.

All planned functional categories remain visible. Rows with fewer than five
events or non-events in either arm retain a status flag but have count and effect
cells withheld in these shareable snapshots. Full flagged results remain local.
"""
from pathlib import Path
import argparse
import csv
import json

from analyze_functional_sensitivity import INSTRUMENTS

ROOT = Path(__file__).resolve().parent


def read_result(cohort, name):
    return json.loads((ROOT / 'results' / f'{cohort}_{name}.json').read_text(encoding='utf-8'))


def save(name, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (ROOT / 'results' / name).open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def effect_row(meta, values, standard=False):
    row = dict(meta)
    sparse = False
    if not standard and values:
        counts = [values.get(k) for k in ('dys_events', 'no_dys_events')]
        non_events = [values.get(n, 0) - values.get(e, 0)
                      for n, e in [('dys_n', 'dys_events'), ('no_dys_n', 'no_dys_events')]]
        sparse = any(v is not None and v < 5 for v in counts + non_events)
    row['reporting_status'] = ('small_cell_values_withheld' if sparse else
                               ('reported' if values else 'unknown_absent_source_row'))
    row['sparse_group_below_20'] = values.get('sparse_group', False) if values else ''
    for key in ['dys_events', 'dys_n', 'no_dys_events', 'no_dys_n', 'dys_rate',
                'no_dys_rate', 'rr', 'risk_difference']:
        row[key] = '' if sparse else values.get(key, '')
    for key in ['dys_rate_ci', 'no_dys_rate_ci', 'rr_ci', 'risk_difference_ci']:
        bounds = values.get(key)
        row[key + '_lower'] = '' if sparse or bounds is None else bounds[0]
        row[key + '_upper'] = '' if sparse or bounds is None else bounds[1]
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cohort', choices=['acute', 'rehab'], required=True)
    args = ap.parse_args()
    cohort = args.cohort
    pccl = read_result(cohort, 'pccl_standardization')[cohort]
    main_rows, pccl_rows = [], []
    for outcome, result in pccl.items():
        for kind in ['crude', 'standardized']:
            main_rows.append(effect_row({'cohort': cohort, 'outcome': outcome,
                'analysis': 'PCCL_' + kind, 'reference': result['reference']},
                result[kind], standard=(kind == 'standardized')))
        for stratum in result['strata']:
            pccl_rows.append(effect_row({'cohort': cohort, 'outcome': outcome,
                'pccl': stratum['pccl'], 'reference_weight': stratum['reference_weight']}, stratum))
    save('severity_summary.csv', main_rows)
    save('pccl_strata.csv', pccl_rows)

    hd = read_result(cohort, 'principal_diagnosis_sensitivity')[cohort]
    diagnosis_rows = []
    for name, group in hd['groups'].items():
        diagnosis_rows.append(effect_row({'cohort': cohort, 'outcome': 'death',
            'group': name, 'definition': ';'.join(group['definition']),
            'exact_counts_available': group['exact'],
            'missing_codes': json.dumps(group['missing_codes'], ensure_ascii=False)},
            group.get('comparison', {})))
    save('diagnosis_sensitivity.csv', diagnosis_rows)

    functional = read_result(cohort, 'functional_sensitivity')['cohorts'][cohort]
    functional_rows = []
    for result in functional['analyses']:
        if result['instrument'] not in INSTRUMENTS:
            continue
        for membership in ['code_present', 'code_absent']:
            functional_rows.append(effect_row({'cohort': cohort, 'outcome': result['outcome'],
                'instrument': result['instrument'], 'code': result['code'],
                'score_band': result['score_band'], 'membership': membership,
                'missing_rows': ';'.join(result['missing_rows'])}, result.get(membership, {})))
    save('functional_sensitivity.csv', functional_rows)
    coverage_rows = []
    for instrument, groups in functional['coverage_by_instrument'].items():
        if instrument not in INSTRUMENTS:
            continue
        for group_name, group in groups.items():
            row = {'cohort': cohort, 'instrument': instrument, 'group': group_name,
                   'n': group['n'], 'all_planned_codes_visible': group['all_planned_codes_visible'],
                   'interpretation': 'Set-theoretic bounds; not an observed unique assessment rate'}
            for key in ['unique_union_count_bounds', 'unique_union_fraction_bounds']:
                row[key + '_lower'], row[key + '_upper'] = group[key]
            coverage_rows.append(row)
    save('functional_coverage_bounds.csv', coverage_rows)
    print('Curated five severity tables for', cohort)


if __name__ == '__main__':
    main()
