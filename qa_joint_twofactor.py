"""Independent rational-arithmetic checks for the two-factor extension."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json
import math

import analyze_joint_twofactor as m


def independent(cells):
    cells = [x for x in cells if x['dys_n'] > 0 and x['all_n'] > x['dys_n']]
    nt = sum(c['all_n'] for c in cells)
    pd = pc = vd = vc = Fraction(0)
    for c in cells:
        w = Fraction(c['all_n'], nt)
        d, nd = c['dys_events'], c['dys_n']
        ec, nc = c['all_events']-d, c['all_n']-nd
        p, q = Fraction(d, nd), Fraction(ec, nc)
        pd += w*p
        pc += w*q
        vd += w*w*p*(1-p)/nd
        vc += w*w*q*(1-q)/nc
    rr = float(pd/pc)
    se = math.sqrt(float(vd/pd**2 + vc/pc**2))
    rd = float(pd-pc)
    se_rd = math.sqrt(float(vd+vc))
    z = 1.959963984540054
    return {'dys_rate': float(pd), 'no_dys_rate': float(pc), 'rr': rr,
            'rr_ci': [rr*math.exp(-z*se), rr*math.exp(z*se)],
            'risk_difference': rd, 'risk_difference_ci': [rd-z*se_rd, rd+z*se_rd]}


def main():
    checks = []
    def check(name, ok):
        if not ok:
            raise AssertionError(name)
        checks.append(name)
    def close(a, b):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-14)
    def rejects(name, call):
        try:
            call()
        except ValueError:
            checks.append(name)
        else:
            raise AssertionError(name)

    cells = [
        {'age_band': '18-74', 'pccl': '0', 'all_n': 100, 'dys_n': 20, 'all_events': 10, 'dys_events': 4},
        {'age_band': '75+', 'pccl': '1', 'all_n': 200, 'dys_n': 150, 'all_events': 50, 'dys_events': 45},
        {'age_band': '18-74', 'pccl': '6', 'all_n': 10, 'dys_n': 0, 'all_events': 1, 'dys_events': 0},
        {'age_band': '75+', 'pccl': '6', 'all_n': 8, 'dys_n': 8, 'all_events': 2, 'dys_events': 2},
    ]
    result = m.standardize(cells)
    expected = independent(cells)
    for key in ['dys_rate', 'no_dys_rate', 'rr', 'risk_difference']:
        check('rational_'+key, close(result['standardized'][key], expected[key]))
    for key in ['rr_ci', 'risk_difference_ci']:
        check('rational_'+key, all(close(x, y) for x, y in zip(result['standardized'][key], expected[key])))
    check('denominator_only_exclusion', result['common_support']['included_cells'] == 2 and result['common_support']['excluded_cells'] == 2)
    check('matching_crude_denominators', result['crude_same_common_support_population']['dys_n'] == 170 and result['crude_same_common_support_population']['no_dys_n'] == 130)
    check('matching_crude_events', result['crude_same_common_support_population']['dys_events'] == 49 and result['crude_same_common_support_population']['no_dys_events'] == 11)
    check('coverage_all', close(result['common_support']['all_coverage'], 300/318))
    check('weights_sum_one', close(sum(x['reference_weight'] for x in result['strata']), 1))
    shuffled = m.standardize(list(reversed(cells)))
    check('order_invariance', close(shuffled['standardized']['rr'], result['standardized']['rr']))
    zero = deepcopy(cells[:2]); zero[0]['dys_events'] = 0
    zresult = m.standardize(zero)
    check('zero_event_stratum_retained', zresult['common_support']['included_cells'] == 2 and zresult['strata'][0]['boundary_probability'])
    bad = deepcopy(cells[:2]); bad[0]['dys_events'] = 11
    rejects('negative_complement_event_rejected', lambda: m.standardize(bad))
    bad = deepcopy(cells[:2]); bad[0]['dys_n'] = 101
    rejects('negative_complement_denominator_rejected', lambda: m.standardize(bad))
    bad = deepcopy(cells[:2]); bad[0]['all_events'] = 99
    rejects('complement_events_over_denominator_rejected', lambda: m.standardize(bad))
    allzero = deepcopy(cells[:2])
    for cell in allzero:
        cell['all_events'] = cell['dys_events'] = 0
    zeror = m.standardize(allzero)
    check('zero_total_risk_no_log_ci', zeror['standardized']['rr'] is None and zeror['standardized']['rr_ci'] is None)

    # A crossed grid must use each directly observed age-by-factor cell, not a
    # product of independent marginals or an averaging of separate RRs.
    exports = {}
    for age_i, age in enumerate(m.QUERY_AGES):
        for kind_i, kind in enumerate(m.KINDS):
            values = {label: (age_i+1)*100+(kind_i+1)*10+i for i, label in enumerate(m.SEX_LABELS)}
            exports[age, kind] = {'distributions': {'sex': values}}
    built = m.build_cells(exports, 'sex')
    check('direct_joint_cell_mapping', len(built) == 8 and built[4]['all_n'] == 210 and built[4]['dys_events'] == 240)
    check('all_sex_categories_kept', {c['sex'] for c in built} == set(m.SEX_LABELS))
    check('eight_queries_only', len(m.expected_files('acute')) == 8 and all('_allhd_' in n for n in m.expected_files('acute')))

    # The raw source reader must distinguish absent diagnosis rows from zero.
    import openpyxl
    path = Path(__file__).resolve().parent/'tmp'/'qa_joint_twofactor_synthetic_fixture.xlsx'
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Hauptdiagnosen'
    ws.append(['Code', 'Label', 'Cases']); ws.append(['I63.0', 'Synthetic example', 7]); ws.append(['---', 'Rest', 3])
    wb.save(path); wb.close()
    exact, rest = m.read_principal_diagnoses(path, 10)
    check('missing_code_not_zero', 'I63.1' not in exact and exact['I63.0'] == 7 and rest == 3)
    rejects('diagnosis_partition_mismatch_rejected', lambda: m.read_principal_diagnoses(path, 11))
    payload = {'status': 'PASS', 'synthetic_not_clinical_results': True,
               'checks_passed': len(checks), 'checks': checks,
               'note': 'Does not substitute for independent actual-workbook verification.'}
    m.save(payload, Path(__file__).resolve().parent/'joint_twofactor_validation.json')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
