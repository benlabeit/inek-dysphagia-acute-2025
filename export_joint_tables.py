"""Export aggregate joint-analysis tables and source manifests, never raw cells."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math

from analyze_joint_standardization import expected_files as threefactor_files
from analyze_joint_twofactor import expected_files as twofactor_files, csv_rows as twofactor_rows

ROOT = Path(__file__).resolve().parent
THREE = ['age_sex_principal_diagnosis', 'age_principal_diagnosis_pccl_sensitivity']


def write_json(value, path):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def threefactor_rows(result):
    rows = []
    for name in THREE:
        r = result[name]
        if r['status'] != 'estimated':
            raise ValueError('No estimable common support for '+name)
        s = r['standardized']
        ci = s['rr_ci'] or [None, None]
        rdci = s['risk_difference_ci']
        cells = r['strata']
        rows.append({
            'analysis': name,
            'adjusted_factors': 'age_band + sex + principal_diagnosis' if name == THREE[0] else 'age_band + principal_diagnosis + pccl',
            'dys_standardized_risk': s['dys_rate'], 'no_dys_standardized_risk': s['no_dys_rate'],
            'rr': s['rr'], 'rr_ci_lower': ci[0], 'rr_ci_upper': ci[1],
            'risk_difference': s['risk_difference'], 'risk_difference_ci_lower': rdci[0], 'risk_difference_ci_upper': rdci[1],
            'crude_rr_same_common_support': r['crude_same_common_support_population']['rr'],
            'sparse_event_or_nonevent_strata': sum(c['sparse_event_cell'] for c in cells),
            'boundary_probability_strata': sum(c['boundary_probability'] for c in cells),
            'sparse_reference_weight': sum(c['reference_weight'] for c in cells if c['sparse_event_cell']),
            'boundary_reference_weight': sum(c['reference_weight'] for c in cells if c['boundary_probability']),
            'selected_adult_n_before_common_support': r['selected_population_before_common_support']['all_n'],
            **r['common_support']})
    return rows


def check_independent_qa(qa, result, cohort, analysis):
    if qa.get('cohort') != cohort or qa.get('status') != 'passed':
        raise ValueError('Independent validation is not a passing matching cohort report')
    if set(qa.get('dimensions', {})) != {'sex', 'pccl'}:
        raise ValueError('Unexpected independent QA dimensions')
    def compare(actual, expected, label):
        if actual is None or expected is None:
            okay = actual is None and expected is None
        else:
            okay = (isinstance(actual, (int, float)) and isinstance(expected, (int, float))
                    and math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12))
        if not okay:
            raise ValueError('Independent QA does not match current model: '+label)
    allowed = {'source_cells', 'retained_cells', 'exact_weight_sum', 'rr', 'ci',
               'adult_all_n', 'adult_all_deaths', 'common_support'}
    support_keys = {'included_cells', 'excluded_cells', 'all_n', 'dys_n', 'no_dys_n',
                    'all_coverage', 'dys_coverage', 'no_dys_coverage'}
    for dim, key in [('sex', THREE[0]), ('pccl', THREE[1])]:
        observed = qa['dimensions'][dim]
        if set(observed) != allowed or set(observed['common_support']) != support_keys:
            raise ValueError('Independent validation contains missing or unreviewed fields')
        r = result['analyses']['age_'+dim] if analysis == 'twofactor' else result[key]
        s = r['standardized']; support = r['common_support']
        compare(observed['source_cells'], len(r['strata'])+len(r['excluded_cells']), dim+' source cells')
        compare(observed['retained_cells'], len(r['strata']), dim+' retained cells')
        if observed['exact_weight_sum'] != '1':
            raise ValueError('Independent reference weights do not sum exactly to one')
        compare(observed['rr'], s['rr'], dim+' RR')
        if observed['ci'] is None or s['rr_ci'] is None:
            if observed['ci'] is not None or s['rr_ci'] is not None:
                raise ValueError('Independent QA CI status differs')
        else:
            if len(observed['ci']) != 2:
                raise ValueError('Independent QA CI is malformed')
            for a, b in zip(observed['ci'], s['rr_ci']):
                compare(a, b, dim+' RR CI')
        compare(observed['adult_all_n'], r['selected_population_before_common_support']['all_n'], dim+' adult N')
        compare(observed['adult_all_deaths'], sum(c['all_events'] for c in r['strata']+r['excluded_cells']), dim+' adult deaths')
        for key in support_keys:
            compare(observed['common_support'][key], support[key], dim+' '+key)


def export(cohort, analysis, results_dir, out_dir):
    stem = 'joint_twofactor' if analysis == 'twofactor' else 'joint_standardization'
    source = results_dir/f'{cohort}_{stem}.json'
    result = json.loads(source.read_text(encoding='utf-8'))
    if result['cohort'] != cohort:
        raise ValueError('Result cohort mismatch')
    expected = twofactor_files(cohort) if analysis == 'twofactor' else threefactor_files(cohort)
    if set(result['inputs']) != set(expected):
        raise ValueError('Unexpected or incomplete source manifest')
    rows = twofactor_rows(result) if analysis == 'twofactor' else threefactor_rows(result)
    if len(rows) != 2:
        raise ValueError('Both planned aggregate analyses must be estimable')
    independent_path = results_dir/f'{cohort}_{stem}_independent_qa.json'
    if not independent_path.is_file():
        raise ValueError('Independent actual-data QA is required before curated export')
    qa = json.loads(independent_path.read_text(encoding='utf-8'))
    check_independent_qa(qa, result, cohort, analysis)
    public_stem = 'joint_twofactor' if analysis == 'twofactor' else 'joint_threefactor'
    out_dir.mkdir(parents=True, exist_ok=True)
    table_path = out_dir/(public_stem+'_summary.csv')
    with table_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    manifest = {
        'cohort': cohort, 'analysis': analysis,
        'delivery': result['delivery'], 'source_result_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'exports': {name: {'source': {k: item['source'][k] for k in ['path', 'sha256', 'size_bytes']},
                           'selection': item['selection'], 'n': item['n']} for name, item in result['inputs'].items()},
        'original_reference_checks': {kind: {
            **{k: item[k] for k in ['original_n', 'expected_adult_n', 'new_adult_n', 'native_age_counts_match']},
            'original_source': {k: item['original_source'][k] for k in ['path', 'sha256', 'size_bytes']},
            **({'excluded_under18_n': item['excluded_under18_n']} if 'excluded_under18_n' in item else {})}
            for kind, item in result['original_reference_checks'].items()},
        'raw_workbooks_included': False, 'individual_stratum_counts_included': False,
        'verification': 'Exact query filters, delivery, integer distributions, population partitions, original adult totals, native age counts and event nesting validated; independent numerical QA reported separately.'}
    if analysis == 'threefactor':
        manifest['diagnosis_partition'] = result['diagnosis_partition']
    write_json(manifest, out_dir/(public_stem+'_query_manifest.json'))
    public_qa = {key: qa[key] for key in ['cohort', 'status', 'method', 'dimensions']}
    write_json(public_qa, out_dir/(public_stem+'_independent_validation.json'))
    return {'analysis': analysis, 'table': table_path.name, 'aggregate_rows': len(rows), 'source_exports': len(expected)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort', required=True, choices=['acute', 'rehab'])
    p.add_argument('--analysis', choices=['twofactor', 'threefactor', 'both'], default='both')
    p.add_argument('--results-dir', type=Path, default=ROOT/'results')
    p.add_argument('--out-dir', type=Path, default=ROOT/'results')
    a = p.parse_args()
    analyses = ['twofactor', 'threefactor'] if a.analysis == 'both' else [a.analysis]
    output = [export(a.cohort, kind, a.results_dir, a.out_dir) for kind in analyses]
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
