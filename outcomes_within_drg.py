"""Direct standardization for binary outcomes from independently obtained InEK exports."""
import argparse
import csv
import math
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import openpyxl

from outcomes_analyze_joint import ENDPOINTS, HD_CODES, OPS, R13, DELIVERY, selection_fields
from outcomes_standardization_core import MINOR_AGES, QUERY_AGES, Z, read_info

ROOT = Path(__file__).resolve().parent
SLUG = {
    'mortality': 'death', 'J69.0': 'aspiration_pneumonitis', 'PNEUMONIA_UNION': 'pneumonia',
    'PULMONARY_UNION': 'pulmonary_union', 'MALNUT_UNION': 'malnutrition_union',
    'E43': 'severe_malnutrition', 'E86': 'volume_depletion',
}
PROCEDURES = {'1-613', '8-701', '5-431.22'}


def filename(age, hd, pop, outcome):
    unrestricted = age == 'allages' and hd == 'allhd'
    if not outcome or outcome == 'mortality':
        stem = f'acute_{pop}' if unrestricted else f'acute_joint_{age}_{hd}_{pop}'
        return stem + ('_death' if outcome else '') + '_2025.xlsx'
    if unrestricted and outcome == 'PNEUMONIA_UNION':
        return f'acute_{pop}_pneumonia_2025.xlsx'
    slug = SLUG.get(outcome, outcome.lower().replace('.', '_').replace('-', '_'))
    return f'acute_outcome_{slug}_{age}_{hd}_{pop}_2025.xlsx'


@lru_cache(None)
def source(folder, age, hd, pop, outcome):
    path = folder / filename(age, hd, pop, outcome)
    if not path.exists():
        if outcome == 'PNEUMONIA_UNION' and age == 'age18_74' and hd == 'allhd':
            full = source(folder, 'allages', hd, pop, outcome)
            older = source(folder, 'age75plus', hd, pop, outcome)
            if full and older and all(full[1]['distributions']['age'][k] == 0 for k in MINOR_AGES):
                return difference(full[0], older[0]), {'n': full[1]['n'] - older[1]['n']}
        return None
    info = read_info(path)
    fields = {k: v for k, v in selection_fields(info['selection']).items() if v}
    expected = {'Prozeduren': set(OPS)}
    if pop == 'dys':
        expected['Nebendiagnosen'] = set(R13)
    if hd != 'allhd':
        expected['Hauptdiagnose'] = set(HD_CODES[hd])
    if age != 'allages':
        expected['Altersgruppe'] = set(QUERY_AGES[age])
    if outcome == 'mortality':
        expected['Entlassungsgrund'] = {'07 Tod'}
    elif outcome in PROCEDURES:
        expected['weitere Prozeduren'] = {outcome}
    elif outcome:
        expected['weitere Nebendiagnosen'] = set(ENDPOINTS.get(SLUG.get(outcome), {'codes': [outcome]})['codes'])
    aliases = {'Hauptdiagnosen': 'Hauptdiagnose', 'Altersklassen': 'Altersgruppe',
               'Altersklasse': 'Altersgruppe', 'weitere Prozedur': 'weitere Prozeduren',
               'weitereProzedur': 'weitere Prozeduren'}
    normalized = {aliases.get(k, k): v for k, v in fields.items()}
    if len(normalized) != len(fields) or normalized != expected or info['delivery'] != DELIVERY:
        raise ValueError(f'{path.name}: unexpected selection or delivery')
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = iter(workbook['DRG-Verteilung'].values)
        if next(rows)[:3] != ('DRG', 'Bezeichnung', 'Fälle'):
            raise ValueError(f'{path.name}: unrecognized header')
        counts = {}
        total = 0
        for code, label, n, *_ in rows:
            if code is None and n is None:
                continue
            if not isinstance(n, (int, float)) or not float(n).is_integer() or n < 0:
                raise ValueError(f'{path.name}: invalid case count')
            total += int(n)
            if code == '---' and str(label).startswith('Rest'):
                continue
            if not re.fullmatch(r'[A-Z0-9][0-9]{2}[A-Z]', str(code)) or code in counts:
                raise ValueError(f'{path.name}: unexpected or duplicate DRG')
            counts[code] = int(n)
        if total != info['n']:
            raise ValueError(f'{path.name}: DRG rows do not partition total')
    finally:
        workbook.close()
    return counts, info


def difference(whole, *parts):
    common = set(whole).intersection(*parts)
    result = {k: whole[k] - sum(p[k] for p in parts) for k in common}
    if any(x < 0 for x in result.values()):
        raise ValueError('Negative residual in disjoint partition')
    return result


def observed(folder, age, hd, outcome):
    sources = [source(folder, age, hd, pop, end) for end in (None, outcome) for pop in ('all', 'dys')]
    if not all(sources):
        return {}
    total, dys, events, dys_events = (s[0] for s in sources)
    return {k: (dys[k], total[k]-dys[k], dys_events[k], events[k]-dys_events[k])
            for k in sorted(total.keys() & dys.keys() & events.keys() & dys_events.keys())}


def residual_cells(whole, *parts):
    return {k: tuple(whole[k][i]-sum(part[k][i] for part in parts) for i in range(len(whole[k])))
            for k in sorted(set(whole).intersection(*parts))}


def write_table(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rows[0], lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def combine_by_drg(cells):
    merged = defaultdict(lambda: [0]*4)
    for key, values in cells.items():
        for i, x in enumerate(values):
            merged[key[-1]][i] += x
    return {(k,): tuple(v) for k, v in merged.items()}


def eligible(cells):
    for n, m, a, b in cells.values():
        if not (0 <= a <= n and 0 <= b <= m):
            raise ValueError('Non-nested numerator or invalid exposure complement')
    return {k: v for k, v in cells.items() if min(v[:2]) > 0}


def estimate(outcome, model, cells, population):
    cells = eligible(cells)
    if not cells:
        return None
    D, C, A, B = map(sum, zip(*cells.values()))
    risks, variances = [], []
    for arm in (0, 1):
        risk = var = 0
        for v in cells.values():
            w = v[0]/D
            p = v[arm+2]/v[arm]
            risk += w*p
            var += w*w*p*(1-p)/v[arm]
        risks.append(risk)
        variances.append(var)
    p, q = risks
    vp, vq = variances
    rr = lo = hi = None
    if min(p, q) > 0:
        rr = p/q
        se = math.sqrt(vp/p**2 + vq/q**2)
        lo, hi = rr*math.exp(-Z*se), rr*math.exp(Z*se)
    rd = p-q
    se_rd = math.sqrt(vp+vq)
    return dict(outcome=outcome, model=model, strata=len(cells), drgs=len({k[-1] for k in cells}),
                dys_n=D, comparator_n=C, dys_coverage=D/population[0], comparator_coverage=C/population[1],
                dys_events=A, comparator_events=B, dys_risk=p, comparator_risk=q,
                crude_rr_same_cases=(A/D)/(B/C) if B else None, rr=rr, rr_low=lo, rr_high=hi,
                rd=rd, rd_low=rd-Z*se_rd, rd_high=rd+Z*se_rd,
                sparse_weight=sum(n/D for n,m,a,b in cells.values() if min(a,n-a,b,m-b)<5),
                boundary_weight=sum(n/D for n,m,a,b in cells.values() if min(a,n-a,b,m-b)==0))


def risk_bounds(events, capacity, outside, weights):
    # Each event contributes w[k]/n[k] within support and zero outside it.
    slots = [(0., outside)] + [(w/n, n) for n,w in zip(capacity,weights)]
    if not 0 <= events <= sum(n for _, n in slots) or min(n for _,n in slots) < 0:
        raise ValueError('Incompatible event margin or capacity')
    limits = []
    for descending in (False, True):
        remaining, risk = events, 0.
        for coefficient, available in sorted(slots, reverse=descending):
            used = min(remaining, available)
            risk += used*coefficient
            remaining -= used
        limits.append(risk)
    return limits


@lru_cache(None)
def code_margins(folder, age, hd, pop, sheet):
    path = folder / filename(age, hd, pop, None)
    source(folder, age, hd, pop, None)  # verify cohort, delivery and age/diagnosis selectors
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = iter(wb[sheet].values)
        if next(rows)[2] != 'Fälle':
            raise ValueError('Expected case counts, not number of coding mentions')
        result = {}
        for code, _, count, *_ in rows:
            if code and code != '---':
                if code in result or not isinstance(count,(int,float)) or not float(count).is_integer():
                    raise ValueError(f'{path.name}: invalid code count')
                result[code] = int(count)
        return result
    finally:
        wb.close()


def margin_block(folder, age, hd, key):
    sources = [source(folder, age, hd, p, None) for p in ('all','dys')]
    totals = [s[1]['n'] for s in sources]
    tab = 'Prozeduren' if key in PROCEDURES else 'Nebendiagnosen'
    events = [code_margins(folder, age, hd, p, tab).get(key) for p in ('all','dys')]
    if None in events:
        return None
    total, dys = [s[0] for s in sources]
    cells = {k: (dys[k],total[k]-dys[k]) for k in sorted(total.keys() & dys.keys())}
    return cells, (totals[1], totals[0]-totals[1], events[1], events[0]-events[1])


def bounds_row(key, model, blocks):
    if not blocks or any(b is None for b in blocks):
        return None
    for cells, (n, m, a, b) in blocks:
        if not (0 <= a <= n and 0 <= b <= m) or any(min(v) < 0 for v in cells.values()):
            raise ValueError('Invalid observed margin or non-nested DRG denominator')
    blocks = [({k:v for k,v in cells.items() if min(v)>0}, margins) for cells,margins in blocks]
    D, C = (sum(v[i] for cells,_ in blocks for v in cells.values()) for i in (0,1))
    if not D or not C:
        return None
    dl = du = cl = cu = 0.
    for cells,(n,m,a,b) in blocks:
        ds = [v[0] for v in cells.values()]
        cs = [v[1] for v in cells.values()]
        weights = [d/D for d in ds]
        l,u = risk_bounds(a,ds,n-sum(ds),weights)
        dl += l
        du += u
        l,u = risk_bounds(b,cs,m-sum(cs),weights)
        cl += l
        cu += u
    return dict(outcome=key,model=model,drgs=len(set().union(*(x.keys() for x,_ in blocks))),
                strata=sum(len(x) for x,_ in blocks),dys_n=D,comparator_n=C,
                dys_coverage=D/sum(v[0] for _,v in blocks),comparator_coverage=C/sum(v[1] for _,v in blocks),
                dys_risk_lower=dl,dys_risk_upper=du,comparator_risk_lower=cl,comparator_risk_upper=cu,
                rr_lower=dl/cu if cu else None,rr_upper=du/cl if cl else 'Inf',
                rd_lower=dl-cu,rd_upper=du-cl)


def bounds_from_margins(folder,key,baseline):
    blocks = [margin_block(folder,'allages','allhd',key)]
    totals = tuple(int(float(baseline[k])) for k in ('dys_n','no_dys_n','dys_events','no_dys_events'))
    if blocks[0] is None or totals != blocks[0][1]:
        raise ValueError('Native whole-cohort margins disagree with published crude data')
    results = [bounds_row(key,'all_age_drg',blocks)]
    age_blocks, joint_blocks = [], []
    for age in QUERY_AGES:
        allhd,i61,i63 = [margin_block(folder,age,h,key) for h in ('allhd','i61','i63')]
        age_blocks.append(allhd)
        if any(x is None for x in (allhd,i61,i63)):
            joint_blocks.append(None)
            continue
        residual = residual_cells(allhd[0],i61[0],i63[0])
        residual_margins = tuple(t-u-v for t,u,v in zip(allhd[1],i61[1],i63[1]))
        joint_blocks.extend([i61,i63,(residual,residual_margins)])
    results += [bounds_row(key,'adult_age_drg',age_blocks), bounds_row(key,'adult_age_hd_drg',joint_blocks)]
    return [r for r in results if r is not None]


def analyze(folder, dest):
    with (ROOT/'outcomes_harmonized_binary_summary.csv').open() as f:
        endpoints = [r for r in csv.DictReader(f) if r['analysis']=='baseline_crude']
    population = {}
    for age in ['allages', *QUERY_AGES]:
        n, d = (source(folder, age, 'allhd', pop, None)[1]['n'] for pop in ('all','dys'))
        population[age] = (d, n-d)
    adults = tuple(map(sum,zip(*(population[k] for k in QUERY_AGES))))
    rows, bounds, availability = [], [], []
    for r in endpoints:
        key = r['outcome']
        whole = population['allages']
        if whole != tuple(int(float(r[k])) for k in ['dys_n','no_dys_n']):
            raise ValueError('Baseline population mismatch')
        def record(model, cells, reference):
            if cells:
                row = estimate(key, model, cells, reference)
                if row:
                    rows.append(row)
        all_age = observed(folder, 'allages', 'allhd', key)
        if all_age:
            e, d = (source(folder,'allages','allhd',p,key)[1]['n'] for p in ('all','dys'))
            if (d,e-d) != tuple(int(float(r[k])) for k in ['dys_events','no_dys_events']):
                raise ValueError('Unrestricted event counts disagree with published margins')
            record('all_age_drg', {(k,):v for k,v in all_age.items()},whole)
            if key == 'mortality':
                record('all_age_drg_excluding_B70G_B70H',
                       {(k,):v for k,v in all_age.items() if k not in {'B70G','B70H'}},whole)
        age_cells, joint = {}, {}
        for age in QUERY_AGES:
            hd = {h: observed(folder, age, h, key) for h in ('allhd','i61','i63')}
            age_cells.update({(age,k):v for k,v in eligible(hd['allhd']).items()})
            hd['other'] = residual_cells(hd['allhd'],hd['i61'],hd['i63'])
            for h in ('i61','i63','other'):
                joint.update({(age,h,k):v for k,v in eligible(hd[h]).items()})
        record('adult_drg',combine_by_drg(age_cells),adults)
        record('adult_age_drg',age_cells,adults)
        record('adult_age_hd_drg',joint,adults)
        if not any(x['outcome']==key and x['model'] in {'adult_drg','all_age_drg','adult_age_hd_drg'} for x in rows):
            bounds.extend(bounds_from_margins(folder,key,r))
        availability.append(dict(outcome=key,label=r['label'],**{m:any(x['outcome']==key and x['model']==m for x in rows)
                            for m in ('all_age_drg','adult_drg','adult_age_drg','adult_age_hd_drg')},
                            marginal_bounds_only=any(b['outcome']==key for b in bounds)))
    dest.mkdir(parents=True,exist_ok=True)
    write_table(dest/'within_drg_binary_estimates.csv', rows)
    if bounds:
        write_table(dest/'within_drg_binary_bounds.csv', bounds)
    write_table(dest/'within_drg_binary_availability.csv', availability)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args()
    analyze(args.raw, args.output)
