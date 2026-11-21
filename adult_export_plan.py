"""Generate the manual research query list from existing adult cohort definitions."""
import csv
from itertools import product
from pathlib import Path
from outcomes_analyze_joint import DELIVERY, HD_CODES, OPS, R13
from outcomes_standardization_core import QUERY_AGES
from outcomes_within_drg import PROCEDURES, filename

ROOT = Path(__file__).resolve().parent
MISSING = ['J96.00', 'U69.01', 'U69.04', 'E44.0', 'E44.1', 'E46', '8-701', '5-431.22', '1-613']
COLUMNS = ['Nr','Zweck','Lieferung','Alter','Hauptdiagnosen','Prozeduren','Nebendiagnosen',
           'weitere Nebendiagnosen','weitere Prozeduren','Entlassungsgrund','DRG','Dateiname']
def make_row(stage, age, hd, pop, outcome, drg=''):
    is_proc = outcome in PROCEDURES
    outcome_filter = outcome if outcome not in (None,'mortality') else ''
    name = filename(age,hd,pop,outcome)
    if drg:
        name = name.replace('_2025.xlsx',f'_{drg}_2025.xlsx')
    return [stage, DELIVERY, ', '.join(QUERY_AGES[age]), ', '.join(HD_CODES.get(hd,[])),
            ', '.join(OPS), ', '.join(R13) if pop=='dys' else '',
            '' if is_proc else outcome_filter, outcome_filter if is_proc else '',
            '07 Tod' if outcome=='mortality' else '',drg,name]
def main():
    rows = []
    for outcome in MISSING:
        for hd,age,pop in product(['allhd','i63','i61'],QUERY_AGES,['all','dys']):
            rows.append(make_row('Modelle 2 und 3',age,hd,pop,outcome))
    for hd,age,pop in product(['allhd','i63','i61'],QUERY_AGES,['all','dys']):
        rows.append(make_row('E43 Original wiederbeschaffen für DRG-Sensitivitäten',age,hd,pop,'E43'))
    for age,outcome,pop in product(QUERY_AGES,[None,'mortality'],['all','dys']):
        rows.append(make_row('B70D-Sensitivitätsanalyse nach Alter und Geschlecht, nur Mortalität',age,'allhd',pop,outcome,'B70D'))
    with (ROOT/'adult_manual_exports.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';'); w.writerow(COLUMNS)
        for i,r in enumerate(rows,1): w.writerow([i,*r])
if __name__=='__main__': main()
