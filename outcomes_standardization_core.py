"""Validated fixed-weight InEK standardization primitives.

Copied without mathematical changes from the existing mortality analysis.
read_info is subsequently wrapped by the outcome pipeline with additional
finite-value and strict query validation. No new outcome estimates are included.
"""
from pathlib import Path
import hashlib
import math
import openpyxl
Z=1.959963984540054
SEX_LABELS=['männlich','weiblich','divers','unbekannt']
QUERY_AGES={
 'age18_74':['18-29 Jahre','30-39 Jahre','40-49 Jahre','50-54 Jahre','55-59 Jahre','60-64 Jahre','65-74 Jahre'],
 'age75plus':['75-79 Jahre','80+ Jahre']
}
MINOR_AGES=['< 28 Tage','28 Tage - 1. Jahr','1-2 Jahre','3-5 Jahre','6-9 Jahre','10-15 Jahre','16-17 Jahre']
def read_info(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb['Info'].values)
    finally:
        wb.close()
    def cell(row, column):
        return rows[row-1][column-1]
    if cell(8,1) != 'Fallzahl':
        raise ValueError(path.name+': unrecognized Info layout')
    raw_n = cell(8,2)
    if (isinstance(raw_n, bool) or not isinstance(raw_n, (int, float))
            or not math.isfinite(raw_n) or not float(raw_n).is_integer()):
        raise ValueError(path.name+': non-integer source population')
    n = int(raw_n)
    if n <= 0:
        raise ValueError(path.name+': no positive source population')
    distributions = {}
    for name, indices, lc, vc in [('sex', range(11,15), 1, 2),
                                  ('pccl', range(8,15), 7, 8),
                                  ('age', range(8,len(rows)+1), 10, 11)]:
        counts = {}
        for row in indices:
            label, fraction = cell(row,lc), cell(row,vc)
            if label is None and fraction is None:
                continue
            if label is None or fraction is None:
                raise ValueError(path.name+': incomplete '+name+' row')
            value = float(fraction)*n
            recovered = round(value)
            if abs(value-recovered) >= 1e-6 or recovered < 0:
                raise ValueError(path.name+': nonrecoverable '+name+' count')
            label = str(int(label)) if isinstance(label,(float,int)) and float(label).is_integer() else str(label)
            if label in counts:
                raise ValueError(path.name+': repeated '+name+' category')
            counts[label] = recovered
        if sum(counts.values()) != n:
            raise ValueError(path.name+': '+name+' does not partition N')
        distributions[name] = counts
    expected_age = set(MINOR_AGES + sum(QUERY_AGES.values(), []))
    if set(distributions['age']) != expected_age or set(distributions['pccl']) != {str(k) for k in range(7)}:
        raise ValueError(path.name+': unexpected age/PCCL categories')
    if set(distributions['sex']) != set(SEX_LABELS):
        raise ValueError(path.name+': unexpected sex categories')
    return {'n': n, 'selection': str(cell(2,1)), 'delivery': cell(5,1),
            'distributions': distributions,
            'source': {'path': 'raw/'+path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'size_bytes': path.stat().st_size}}

def contrast(a, n, b, m):
    if n<=0 or m<=0 or not(0<=a<=n and 0<=b<=m):
        raise ValueError('Invalid two-group contrast')
    p,q = a/n,b/m
    variance = p*(1-p)/n+q*(1-q)/m
    rr = p/q if q>0 else None
    interval = None
    if a>0 and b>0:
        se = math.sqrt(1/a-1/n+1/b-1/m)
        interval = [rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    return {'dys_events': a,'dys_n': n,'no_dys_events': b,'no_dys_n': m,
            'dys_rate': p,'no_dys_rate': q,'rr': rr,'rr_ci': interval,
            'risk_difference': p-q,
            'risk_difference_ci': [p-q-Z*math.sqrt(variance),p-q+Z*math.sqrt(variance)]}

def standardize(cells):
    """Fixed pooled weights, denominator-based common support, matched crude."""
    included, excluded = [], []
    for cell in cells:
        t,d,et,ed = [cell[k] for k in ['all_n','dys_n','all_events','dys_events']]
        c,ec = t-d,et-ed
        if min(t,d,c,et,ed,ec)<0 or ed>d or ec>c:
            raise ValueError('Invalid reconstructed cell: '+str(cell))
        item = dict(cell, no_dys_n=c, no_dys_events=ec)
        if d==0 or c==0:
            item['reason'] = 'No dysphagia cases' if d==0 else 'No comparator cases'
            excluded.append(item)
        else:
            included.append(item)
    if not included:
        return {'status':'not_estimable','reason':'No common-support cells','excluded_cells':excluded}
    full_t = sum(c['all_n'] for c in cells)
    full_d = sum(c['dys_n'] for c in cells)
    nt = sum(c['all_n'] for c in included)
    nd = sum(c['dys_n'] for c in included)
    nc = nt-nd
    ed = sum(c['dys_events'] for c in included)
    ec = sum(c['no_dys_events'] for c in included)
    pd=pc=vd=vc=0.0
    for cell in included:
        w = cell['all_n']/nt
        p = cell['dys_events']/cell['dys_n']
        q = cell['no_dys_events']/cell['no_dys_n']
        pd += w*p; pc += w*q
        vd += w*w*p*(1-p)/cell['dys_n']
        vc += w*w*q*(1-q)/cell['no_dys_n']
        cell.update(reference_weight=w, dys_rate=p, no_dys_rate=q,
                    sparse_event_cell=min(cell['dys_events'],cell['no_dys_events'],
                                          cell['dys_n']-cell['dys_events'],
                                          cell['no_dys_n']-cell['no_dys_events'])<5,
                    boundary_probability=p in [0,1] or q in [0,1])
    rr = pd/pc if pc>0 else None
    ci = None
    if pd>0 and pc>0:
        se = math.sqrt(vd/pd**2+vc/pc**2)
        ci = [rr*math.exp(-Z*se),rr*math.exp(Z*se)]
    se_rd = math.sqrt(vd+vc)
    return {'status':'estimated','strata':included,'excluded_cells':excluded,
            'selected_population_before_common_support':{'all_n':full_t,'dys_n':full_d,'no_dys_n':full_t-full_d},
            'common_support':{'included_cells':len(included),'excluded_cells':len(excluded),
                              'all_n':nt,'dys_n':nd,'no_dys_n':nc,
                              'all_coverage':nt/full_t if full_t else None,
                              'dys_coverage':nd/full_d if full_d else None,
                              'no_dys_coverage':nc/(full_t-full_d) if full_t>full_d else None},
            'crude_same_common_support_population':contrast(ed,nd,ec,nc),
            'standardized':{'dys_rate':pd,'no_dys_rate':pc,'rr':rr,'rr_ci':ci,
                            'rr_ci_status':'available' if ci is not None else 'undefined because a standardized event risk is zero',
                            'dys_rate_ci':[pd-Z*math.sqrt(vd),pd+Z*math.sqrt(vd)],
                            'no_dys_rate_ci':[pc-Z*math.sqrt(vc),pc+Z*math.sqrt(vc)],
                            'risk_difference':pd-pc,
                            'risk_difference_ci':[pd-pc-Z*se_rd,pd-pc+Z*se_rd]},
            'method':'Direct standardization to pooled common-support population; fixed observed weights; independent-binomial delta intervals. Zero-event cells retained; unsupported cells excluded using denominators only.'}
