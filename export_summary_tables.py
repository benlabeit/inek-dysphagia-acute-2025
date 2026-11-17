"""Curated acute-only tables from the two reproducible acute result JSON files."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'


def read(name):
    return json.loads((RESULTS / (name + '.json')).read_text(encoding='utf-8'))


def write(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (RESULTS / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    base, ext = read('acute_reanalysis'), read('acute_extensions')
    rows, drgs = [], []

    def risk(endpoint, value, note=''):
        if value.get('small_derived_cell'):
            raise ValueError('Selected summary has an event cell below 5: ' + endpoint)
        ci, rd = value.get('rr_ci') or [None, None], value.get('risk_difference_ci') or [None, None]
        rows.append(dict(cohort='acute', endpoint=endpoint, measure='risk_ratio',
                         exposed_events=value.get('dys_events'), exposed_n=value.get('dys_n'),
                         comparator_events=value.get('no_dys_events'), comparator_n=value.get('no_dys_n'),
                         exposed_rate=value.get('dys_rate'), comparator_rate=value.get('no_dys_rate'),
                         estimate=value.get('rr'), ci_lower=ci[0], ci_upper=ci[1],
                         risk_difference=value.get('risk_difference'), rd_ci_lower=rd[0], rd_ci_upper=rd[1], note=note))

    def los(endpoint, value, note=''):
        rows.append(dict(cohort='acute', endpoint=endpoint, measure='mean_difference_days',
                         exposed_n=value['dys']['n'], comparator_n=value['no_dys']['n'],
                         exposed_mean=value['dys']['mean'], comparator_mean=value['no_dys']['mean'],
                         estimate=value['mean_difference'], ci_lower=value['mean_difference_ci'][0],
                         ci_upper=value['mean_difference_ci'][1], note=note))

    los('hospital_length_of_stay', base['los'])
    for code in ['J69.0', '1-613', '8-701', 'E43', 'E86']:
        risk(code, base['single_code_outcomes'][code], 'Single-code case counts; coded association.')
    risk('in_hospital_death', ext['mortality'])
    risk('in_hospital_death_age_standardized', ext['mortality_age_standardized'],
         'Direct pooled weights: <65, 65-79, 80+; exploratory.')
    los('length_of_stay_discharge_alive', ext['survivor_los'], 'Conditions on survival; selection remains.')
    risk('J12_J18_union', ext['pneumonia']['comparison'])
    risk('J12_J18_or_J69_0_union', ext['pneumonia']['combined_J12_J18_or_J69_0'])
    risk('dysphagia_by_intracranial_thrombectomy', base['dysphagia_by_evt'],
         'Exposed=OPS 8-836.80; comparator=no such OPS; outcome=R13 secondary diagnosis.')
    for cohort, analyses, selected, note in [
        ('acute', base['drg_standardization']['analyses'],
         ['all_comparable', 'both_arms_ge20', 'variance_estimable'],
         'Dysphagia-case weights; descriptive standardization within observable DRGs.'),
        ('acute_survivors', ext['survivor_drg']['analyses'],
         ['all_comparable', 'both_arms_ge20'],
         'Requires explicit death rows in both exports; coverage denominator is all dysphagia survivors.')]:
        for name in selected:
            value = analyses[name]
            ci = value.get('model_ci') or [None, None]
            drgs.append(dict(cohort=cohort, analysis=name, drgs=value['drgs'],
                             exposed_cases_covered=value['dys_covered'], coverage=value['dys_coverage'],
                             mean_difference_days=value['mean_difference'], ci_lower=ci[0], ci_upper=ci[1], note=note))
    write('key_results.csv', rows)
    write('drg_standardization.csv', drgs)
    manifest = json.loads((ROOT / 'query_manifest.json').read_text(encoding='utf-8'))
    sd_rows = []
    for item in manifest['exports']:
        parsed = json.loads((ROOT / 'parsed' / (Path(item['filename']).stem + '.json')).read_text(encoding='utf-8'))
        info, drg = parsed['info_sd_convention_diagnostic'], parsed['sd_convention_diagnostic']
        sd_rows.append(dict(filename=item['filename'], n=parsed['n'],
                            info_sample_Q=info['sample']['second_raw_moment'],
                            info_sample_Q_integer_error=info['sample']['distance_Q_to_integer'],
                            info_population_Q_integer_error=info['population']['distance_Q_to_integer'],
                            listed_drg_rows=drg['population']['n_drg'],
                            drg_population_Q_max_integer_error=drg['population']['max_distance_Q_to_integer'],
                            drg_population_fraction_integer=drg['population']['fraction_within_1e_5'],
                            drg_sample_Q_median_integer_error=drg['sample']['median_distance_Q_to_integer']))
    write('sd_convention_audit.csv', sd_rows)


if __name__ == '__main__':
    main()
