"""Simultaneous age x PCCL and age x sex mortality standardization.

Uses eight directly filtered all-principal-diagnosis workbooks per cohort.
These are two SEPARATE two-factor analyses, not a three-factor model.
Missing inputs or diagnosis rows are never replaced with zero.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import json
import math

import openpyxl

from analyze_joint_standardization import (
    ROOT, DELIVERY, SEX_LABELS, KINDS, QUERY_AGES, OPS, HD_CODES,
    filename, read_info, selection_fields, validate_export, validate_reference, standardize, save,
)


def expected_files(cohort):
    return [filename(cohort, age, 'allhd', kind)
            for age in QUERY_AGES for kind in KINDS]


def build_cells(exports, distribution):
    labels = SEX_LABELS if distribution == 'sex' else [str(k) for k in range(7)]
    cells = []
    for age in QUERY_AGES:
        for label in labels:
            counts = {kind: exports[age, kind]['distributions'][distribution][label]
                      for kind in KINDS}
            cells.append({'age_band': '18-74' if age == 'age18_74' else '75+',
                          distribution: label,
                          'all_n': counts['all'], 'dys_n': counts['dys'],
                          'all_events': counts['all_death'],
                          'dys_events': counts['dys_death']})
    return cells


def read_principal_diagnoses(path, n):
    """Return exact listed principal-diagnosis counts, without zero imputation."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb['Hauptdiagnosen'].values)[1:]
    finally:
        wb.close()
    exact, rest, total = {}, 0, 0
    for row in rows:
        if row[0] is None:
            continue
        code = str(row[0]).rstrip('!*')
        count = row[2]
        if not isinstance(count, (int, float)) or not float(count).is_integer() or count < 0:
            raise ValueError(path.name+': invalid principal-diagnosis case count')
        count = int(count)
        total += count
        if code == '---' or code.startswith('Rest ('):
            rest += count
        else:
            if code in exact:
                raise ValueError(path.name+': duplicated principal diagnosis '+code)
            exact[code] = count
    if total != n:
        raise ValueError(path.name+': principal diagnoses do not partition N')
    return exact, rest


def diagnosis_completeness_audit(exports, raw_dir, cohort):
    rows = []
    for age in QUERY_AGES:
        for kind in KINDS:
            path = raw_dir / filename(cohort, age, 'allhd', kind)
            exact, rest = read_principal_diagnoses(path, exports[age, kind]['n'])
            for group, codes in HD_CODES.items():
                missing = [code for code in codes if code not in exact]
                rows.append({'age': age, 'kind': kind, 'diagnosis_group': group,
                             'required_codes': codes, 'unlisted_codes': missing,
                             'complete_explicit_code_listing': not missing,
                             'group_count': sum(exact[code] for code in codes) if not missing else None,
                             'principal_diagnosis_rest_count': rest})
    return {
        'status': 'audit_only_no_diagnosis_adjusted_estimate', 'rows': rows,
        'reason': ('An unlisted ICD row is unknown, not zero. This two-factor module does not '
                   'select an outcome-dependent complete-row diagnosis subset. The separate '
                   '24-export design directly queries full I63/I61 populations for diagnosis adjustment.')}


def analyze(cohort, raw_dir):
    exports = {}
    for age in QUERY_AGES:
        for kind in KINDS:
            e = read_info(raw_dir / filename(cohort, age, 'allhd', kind))
            validate_export(e, cohort, age, 'allhd', kind)
            exports[age, kind] = e
    reference_checks = {}
    for kind in KINDS:
        reference = read_info(raw_dir / f'{cohort}_{kind}_2025.xlsx')
        validate_reference(reference, cohort, kind)
        adult_expected = sum(reference['distributions']['age'][label]
                             for labels in QUERY_AGES.values() for label in labels)
        adult_observed = sum(exports[age, kind]['n'] for age in QUERY_AGES)
        if adult_expected != adult_observed:
            raise ValueError(f'{cohort}/{kind}: adult total differs from original export')
        for age, labels in QUERY_AGES.items():
            for label in labels:
                if exports[age, kind]['distributions']['age'][label] != reference['distributions']['age'][label]:
                    raise ValueError(f'{cohort}/{kind}: native age count differs for '+label)
        reference_checks[kind] = {
            'original_source': reference['source'], 'original_n': reference['n'],
            'expected_adult_n': adult_expected, 'new_adult_n': adult_observed,
            'excluded_under18_n': reference['n'] - adult_expected,
            'native_age_counts_match': True}
    estimates = {}
    for distribution in ['pccl', 'sex']:
        cells = build_cells(exports, distribution)
        estimate = standardize(cells)
        estimate['factors'] = ['age_band', distribution]
        estimate['unadjusted_factors'] = ['principal_diagnosis', 'NIHSS',
                                         'sex' if distribution == 'pccl' else 'PCCL']
        estimate['population_scope'] = 'Adults aged 18+, all recorded sex categories; all principal diagnoses'
        estimate['boundary_event_strata'] = sum(s['boundary_probability'] for s in estimate.get('strata', []))
        estimate['sparse_event_strata'] = sum(s['sparse_event_cell'] for s in estimate.get('strata', []))
        estimates['age_'+distribution] = estimate
    return {
        'schema_version': 1, 'cohort': cohort,
        'analysis_design': 'Two separate simultaneous two-factor standardizations',
        'outcome': 'In-hospital death, discharge reason 07', 'delivery': DELIVERY,
        'inputs': {filename(cohort, age, 'allhd', kind): {'source': e['source'], 'selection': e['selection'], 'n': e['n']}
                   for (age, kind), e in exports.items()},
        'original_reference_checks': reference_checks, 'analyses': estimates,
        'diagnosis_completeness': diagnosis_completeness_audit(exports, raw_dir, cohort),
        'limitations': [
            'The analyses adjust simultaneously for age and PCCL, or for age and sex; not all three together.',
            'Neither analysis adjusts for principal diagnosis or NIHSS.',
            'Age uses two broad categories (18-74 and 75+); within-band residual age confounding remains.',
            'PCCL can include dysphagia-related or outcome-related diagnoses; this is a descriptive sensitivity, not pure admission severity adjustment.',
            'No causal or NIHSS-independent dysphagia effect is identified.',
            'Common-support exclusions are based on denominators and reported with population coverage; zero-event cells are retained.',
            'Intervals use independent-binomial delta approximations and fixed observed pooled weights; hospital clustering, readmissions, coding uncertainty and selection bias are not included.',
            'Sparse and boundary-event strata can make normal/delta intervals less reliable.',
            'Unlisted diagnosis rows are not imputed as zero and no diagnosis-adjusted estimate is produced by this module.',
            'Mortality only; these exports do not jointly adjust pneumonia or length of stay.']}


def csv_rows(result):
    rows = []
    for name, r in result['analyses'].items():
        if r['status'] != 'estimated':
            continue
        s = r['standardized']
        ci = s['rr_ci'] or [None, None]
        rdci = s['risk_difference_ci']
        rows.append({'analysis': name, 'adjusted_factors': ' + '.join(r['factors']),
                     'dys_standardized_risk': s['dys_rate'], 'no_dys_standardized_risk': s['no_dys_rate'],
                     'rr': s['rr'], 'rr_ci_lower': ci[0], 'rr_ci_upper': ci[1],
                     'risk_difference': s['risk_difference'],
                     'risk_difference_ci_lower': rdci[0], 'risk_difference_ci_upper': rdci[1],
                     'crude_rr_same_common_support': r['crude_same_common_support_population']['rr'],
                     'sparse_event_strata': r['sparse_event_strata'],
                     'boundary_event_strata': r['boundary_event_strata'], **r['common_support']})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort', required=True, choices=['acute', 'rehab', 'both'])
    parser.add_argument('--raw-dir', type=Path, default=ROOT/'raw')
    parser.add_argument('--out-dir', type=Path, default=ROOT/'results')
    parser.add_argument('--status-only', action='store_true')
    args = parser.parse_args()
    cohorts = ['acute', 'rehab'] if args.cohort == 'both' else [args.cohort]
    status = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'status': 'available',
              'effects_computed': False, 'cohorts': {},
              'note': 'Availability is not validation. Missing files stay unknown. Pending/status-only runs do not refresh previous results.'}
    for cohort in cohorts:
        names = expected_files(cohort)
        missing = [name for name in names if not (args.raw_dir/name).is_file()]
        missing_ref = [f'{cohort}_{kind}_2025.xlsx' for kind in KINDS
                       if not (args.raw_dir/f'{cohort}_{kind}_2025.xlsx').is_file()]
        status['cohorts'][cohort] = {'required': 8, 'available': 8-len(missing),
                                    'missing_files': missing, 'missing_reference_files': missing_ref}
        if missing or missing_ref:
            status['status'] = 'pending'
    save(status, args.out_dir/'joint_twofactor_status.json')
    print(json.dumps(status, ensure_ascii=False, indent=2))
    if args.status_only:
        return
    if status['status'] == 'pending':
        raise SystemExit(2)
    results = {cohort: analyze(cohort, args.raw_dir) for cohort in cohorts}
    for cohort, result in results.items():
        save(result, args.out_dir/f'{cohort}_joint_twofactor.json')
        rows = csv_rows(result)
        if rows:
            with (args.out_dir/f'{cohort}_joint_twofactor.csv').open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    status.update(status='computed', effects_computed=True)
    save(status, args.out_dir/'joint_twofactor_status.json')


if __name__ == '__main__':
    main()
