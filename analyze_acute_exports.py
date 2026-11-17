"""Read-only InEK export parser and reproducible aggregate comparisons.

Never edits workbooks. Uses full stored numeric values, distinguishes cases
from mentions and retains suppressed Rest rows. Info uses sample SD, whereas
DRG rows use population SD, independently verified by integer LOS moments.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, statistics
import openpyxl

Z=1.959963984540054

def clean_number(x):
    return int(x) if isinstance(x,(int,float)) and float(x).is_integer() else x

def parse_inek(path):
    path=Path(path)
    wb=openpyxl.load_workbook(path, read_only=True, data_only=True)
    si=wb['Info']; n=int(si['B8'].value)
    assert si['A8'].value=='Fallzahl', 'Unrecognized Info layout'
    out={'source':{'path':(Path('raw')/path.name).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                   'size_bytes':path.stat().st_size,'created':str(wb.properties.created),'modified':str(wb.properties.modified)},
         'delivery':si['A5'].value,'selection':si['A2'].value,'n':n,
         'los':{'mean':si['E12'].value,'sd':si['E13'].value,'hk':si['E14'].value},
         'distributions':{},'tables':{},'checks':{},'warnings':[]}
    for name,label_col,value_col,rows in [('sex',1,2,range(11,15)),('los_group',4,5,range(8,11)),
                                        ('pccl',7,8,range(8,15)),('age',10,11,range(8,si.max_row+1))]:
        dist=[]
        for row in rows:
            label=si.cell(row,label_col).value; value=si.cell(row,value_col).value
            if label is None or value is None: continue
            raw=value*n; count=round(raw); err=abs(raw-count)
            dist.append({'label':str(label),'fraction':value,'count':count if err<1e-6 else None,
                         'integer_recovery_error':err,'source_row':row})
        out['distributions'][name]=dist
        out['checks'][name+'_partition']=sum(x['count'] for x in dist if x['count'] is not None)==n
    for sheet in ['Hauptdiagnosen','Nebendiagnosen','Prozeduren','DRG-Verteilung','Krankenhausverteilung']:
        ws=wb[sheet]; vals=list(ws.values); records=[]
        for row,values in enumerate(vals[1:],start=2):
            if values[0] is None: continue
            code=str(values[0]); rec={'code':code,'label':str(values[1]),'cases':int(values[2]),'source_row':row}
            if sheet in ['Nebendiagnosen','Prozeduren']:
                rec.update(mentions=int(values[3]),fraction_cases=values[4],fraction_mentions=values[5])
            elif sheet=='DRG-Verteilung':
                rec.update(fraction_cases=values[3],los_mean=values[4],los_sd=values[5])
            else: rec.update(fraction_cases=values[3])
            rec['is_rest']=code=='---' or code.startswith('Rest (')
            records.append(rec)
        out['tables'][sheet]=records
        out['checks'][sheet+'_fraction_max_error']=max(abs(r['fraction_cases']*n-r['cases']) for r in records)
        if sheet in ['Hauptdiagnosen','DRG-Verteilung','Krankenhausverteilung']:
            out['checks'][sheet+'_partition']=sum(r['cases'] for r in records)==n
    drg=[r for r in out['tables']['DRG-Verteilung'] if not r['is_rest'] and r['los_mean'] is not None]
    errs={'population':[],'sample':[]}
    for r in drg:
        nn,m,s=r['cases'],r['los_mean'],r['los_sd']
        for kind,k in [('population',nn),('sample',nn-1)]:
            q=k*s*s+nn*m*m
            errs[kind].append(abs(q-round(q)))
    out['sd_convention_diagnostic']={k:{'n_drg':len(v),'median_distance_Q_to_integer':statistics.median(v),
      'max_distance_Q_to_integer':max(v),'fraction_within_1e_5':sum(x<1e-5 for x in v)/len(v)} for k,v in errs.items()}
    info_errors={}
    for kind,k in [('population',n),('sample',n-1)]:
        q=k*out['los']['sd']**2+n*out['los']['mean']**2
        info_errors[kind]={'second_raw_moment':q,'distance_Q_to_integer':abs(q-round(q))}
    out['info_sd_convention_diagnostic']=info_errors
    out['sd_conventions']={'Info':'sample','DRG-Verteilung':'population'}
    out['warnings'].append('Distinct SD conventions: Info sample SD; DRG population SD, checked independently using integer LOS second moments.')
    out['warnings'].append('ND/OPS Rest values aggregate omitted code rows and are not a unique-patient union.')
    wb.close()
    return out

def lookup(export,sheet,code):
    matches=[r for r in export['tables'][sheet] if r['code'].rstrip('!*')==code.rstrip('!*') and not r['is_rest']]
    return matches[0] if matches else None

def wilson(x,n):
    p=x/n; d=1+Z*Z/n; c=(p+Z*Z/(2*n))/d
    h=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/d
    return [c-h,c+h]

def contrast(a,n,b,m):
    p,q=a/n,b/m; d=p-q
    se=math.sqrt(p*(1-p)/n+q*(1-q)/m)
    result={'dys_events':a,'dys_n':n,'no_dys_events':b,'no_dys_n':m,'dys_rate':p,'no_dys_rate':q,
            'risk_difference':d,'risk_difference_ci':[d-Z*se,d+Z*se],
            'dys_rate_ci':wilson(a,n),'no_dys_rate_ci':wilson(b,m),'small_derived_cell':min(a,b)<5}
    if a>0 and b>0:
        rr=p/q; selog=math.sqrt(1/a-1/n+1/b-1/m)
        result.update(rr=rr,rr_ci=[rr*math.exp(-Z*selog),rr*math.exp(Z*selog)])
    else: result.update(rr=None,rr_ci=None)
    return result

def complement(nt,mt,st,nd,md,sd,sd_convention='sample'):
    """Subtract a subgroup. Default matches Info sample SD; DRG must pass population.

    Returns both variance conventions explicitly. Never apply a DRG convention
    to Info moments or vice versa.
    """
    nc=nt-nd
    if nc<=0: return None
    mc=(nt*mt-nd*md)/nc
    if sd_convention not in ['sample','population']:
        raise ValueError(f'Unknown SD convention: {sd_convention}')
    kt,kd=(nt-1,nd-1) if sd_convention=='sample' else (nt,nd)
    q=(kt*st*st+nt*mt*mt)-(kd*sd*sd+nd*md*md)
    vc=q/nc-mc*mc
    if vc < -1e-6: raise ValueError(f'Negative complementary variance: {vc}')
    vp=max(vc,0); vs=vp*nc/(nc-1) if nc>1 else None
    return {'n':nc,'mean':mc,'variance_population':vp,'sd_population':math.sqrt(vp),
            'variance_sample':vs,'sd_sample':math.sqrt(vs) if vs is not None else None,
            'input_sd_convention':sd_convention}

def los_compare(all_,dys):
    nt,nd=all_['n'],dys['n']; mt,md=all_['los']['mean'],dys['los']['mean']; st,sd=all_['los']['sd'],dys['los']['sd']
    c=complement(nt,mt,st,nd,md,sd,sd_convention='sample')
    delta=md-c['mean']; se=math.sqrt(sd*sd/nd+c['variance_sample']/c['n'])
    return {'all':dict(n=nt,mean=mt,sd_sample=st,sd_population=st*math.sqrt((nt-1)/nt)),
            'dys':dict(n=nd,mean=md,sd_sample=sd,sd_population=sd*math.sqrt((nd-1)/nd)),
            'no_dys':c,'mean_difference':delta,'mean_difference_ci':[delta-Z*se,delta+Z*se],
            'mean_ratio':md/c['mean'],'associated_bed_days':nd*delta,
            'sd_convention':'Info sample SD',
            'variance_method':'Sample second moments subtracted; Welch normal approximation using sample variances/n; independent cases model.'}

def drg_compare(all_,dys):
    allrows={r['code']:r for r in all_['tables']['DRG-Verteilung'] if not r['is_rest']}
    rows=[]; skips=[]
    for d in dys['tables']['DRG-Verteilung']:
        if d['is_rest']: continue
        t=allrows.get(d['code'])
        if t is None: skips.append({'code':d['code'],'reason':'not listed in total export'}); continue
        if t['cases']<=d['cases']: skips.append({'code':d['code'],'reason':'no comparator cases'}); continue
        try: c=complement(t['cases'],t['los_mean'],t['los_sd'],d['cases'],d['los_mean'],d['los_sd'],sd_convention='population')
        except ValueError as e: skips.append({'code':d['code'],'reason':str(e)}); continue
        delta=d['los_mean']-c['mean']
        var=(d['los_sd']**2/(d['cases']-1)+c['variance_population']/(c['n']-1)) if c['n']>1 and d['cases']>1 else None
        rows.append({'code':d['code'],'label':d['label'],'n_all':t['cases'],'n_dys':d['cases'],'n_no_dys':c['n'],
                     'mean_dys':d['los_mean'],'mean_no_dys':c['mean'],'sd_no_dys':c['sd_population'],
                     'difference':delta,'difference_variance':var})
    result={'rows':rows,'skips':skips,'analyses':{}}
    for name,subset in [('all_comparable',rows),('both_arms_ge20',[r for r in rows if min(r['n_dys'],r['n_no_dys'])>=20]),
                        ('dys_ge20',[r for r in rows if r['n_dys']>=20]),('all_ge20',[r for r in rows if r['n_all']>=20]),
                        ('variance_estimable',[r for r in rows if r['difference_variance'] is not None])]:
        cover=sum(r['n_dys'] for r in subset)
        if not cover: continue
        est=sum(r['n_dys']*r['difference'] for r in subset)/cover
        v=sum((r['n_dys']/cover)**2*r['difference_variance'] for r in subset) if all(r['difference_variance'] is not None for r in subset) else None
        result['analyses'][name]={'drgs':len(subset),'dys_covered':cover,'dys_coverage':cover/dys['n'],
              'mean_difference':est,'associated_bed_days':est*cover,'model_ci':[est-Z*math.sqrt(v),est+Z*math.sqrt(v)] if v is not None else None,
              'ci_assumptions':'Conditional on observed DRG weights, independent cases; does not cover coding, clustering or selection bias.'}
    return result

KEY_CODES={
 'Nebendiagnosen':['J69.0','J96.00','E43','E44.0','E44.1','E46','E86','U69.01','U69.04','Z93.0','Z93.1','Z43.0','G81.0','R47.0','R47.1'],
 'Prozeduren':['1-613','8-701','8-633','8-836.80','8-020.8','9-320','9-984.7','9-984.8','9-984.9','9-984.a']}

def compare_exports(all_,dys):
    if all_['delivery']!=dys['delivery']: raise ValueError('Different deliveries')
    n,m=dys['n'],all_['n']-dys['n']
    result={'delivery':all_['delivery'],'sources':{'all':all_['source'],'dys':dys['source']},
            'selections':{'all':all_['selection'],'dys':dys['selection']},'n_all':all_['n'],'n_dys':n,'n_no_dys':m,
            'dysphagia_prevalence':n/all_['n'],'dysphagia_prevalence_ci':wilson(n,all_['n']),
            'los':los_compare(all_,dys),'single_code_outcomes':{},'distributions':{},'principal_diagnoses':{},
            'drg_standardization':drg_compare(all_,dys),'warnings':[]}
    for sheet,codes in KEY_CODES.items():
        for code in codes:
            a=lookup(all_,sheet,code); d=lookup(dys,sheet,code)
            if a is not None and d is not None:
                if a['cases']<d['cases']: raise ValueError('Subset count exceeds total')
                result['single_code_outcomes'][code]={'sheet':sheet,'label':a['label'],'all_events':a['cases'],
                  'all_mentions':a.get('mentions'),'dys_mentions':d.get('mentions'),**contrast(d['cases'],n,a['cases']-d['cases'],m)}
            else: result['single_code_outcomes'][code]={'sheet':sheet,'status':'not listed in one or both exports; do not assume zero'}
    for dist,allrows in all_['distributions'].items():
        drows={r['label']:r for r in dys['distributions'][dist]}; records=[]
        for t in allrows:
            d=drows.get(t['label'])
            if d is None or d['count'] is None or t['count'] is None: continue
            records.append({'label':t['label'],'all_count':t['count'],'dys_count':d['count'],
                'no_dys_count':t['count']-d['count'],'dys_prevalence_within_category':d['count']/t['count'] if t['count'] else None,
                'dys_share':d['count']/n,'no_dys_share':(t['count']-d['count'])/m})
        result['distributions'][dist]=records
    for prefix in ['I60','I61','I62','I63','I64','G45','H34']:
        groups={}
        for name,exp in [('all',all_),('dys',dys)]:
            rows=[r for r in exp['tables']['Hauptdiagnosen'] if r['code'].startswith(prefix)]
            groups[name]={'listed_cases':sum(r['cases'] for r in rows),'listed_codes':[r['code'] for r in rows]}
        a,d=groups['all']['listed_cases'],groups['dys']['listed_cases']
        groups['listed_case_prevalence']=d/a if a else None
        expected={'I60':['I60.'+str(i) for i in range(10)],'I61':['I61.'+str(i) for i in [0,1,2,3,4,5,6,8,9]],
                  'I62':['I62.00','I62.01','I62.02','I62.09','I62.1','I62.9'],
                  'I63':['I63.'+str(i) for i in [0,1,2,3,4,5,6,8,9]],'I64':['I64']}.get(prefix)
        groups['missing_expected_codes']={arm:sorted(set(expected)-set(groups[arm]['listed_codes'])) for arm in ['all','dys']} if expected else None
        groups['complete_code_set']=bool(expected) and all(not x for x in groups['missing_expected_codes'].values())
        groups['warning']=None if groups['complete_code_set'] else 'Sum of displayed mutually exclusive principal diagnoses; missing subcodes may be suppressed, not zero.'
        result['principal_diagnoses'][prefix]=groups
    result['exposure_code_composition']=[{'code':c,'cases':lookup(dys,'Nebendiagnosen',c)['cases'],
        'fraction_of_dys':lookup(dys,'Nebendiagnosen',c)['cases']/n} for c in ['R13.0','R13.1','R13.9'] if lookup(dys,'Nebendiagnosen',c)]
    evtall=lookup(all_,'Prozeduren','8-836.80'); evtdys=lookup(dys,'Prozeduren','8-836.80')
    if evtall and evtdys:
        result['dysphagia_by_evt']=contrast(evtdys['cases'],evtall['cases'],n-evtdys['cases'],all_['n']-evtall['cases'])
        result['dysphagia_by_evt']['note']='Here the comparison groups are EVT/no EVT and the outcome is coded dysphagia; generic dys/no_dys keys denote first/second group.'
    longrow=next(r for r in result['distributions']['los_group'] if r['label']=='Langlieger')
    result['long_stay']=contrast(longrow['dys_count'],n,longrow['no_dys_count'],m)
    result['warnings']=['Aggregate associations, not adjusted causal effects.','Exact case fractions recovered from stored full-precision fractions after integer checks.',
      'CI models assume independent cases; repeat admissions and hospital clustering not accounted for.',
      'U69 codes distinguish pneumonia timing relative to hospital admission, not dysphagia onset; coverage may be incomplete.',
      'Explicit listed row case counts are used, never mentions; multi-code groups require a separate union export.',
      'PES or other complementary cells below 5 are flagged as small_derived_cell; disclosure review required before tabulation.']
    return result

def save_json(obj,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--all',default='raw/acute_all_2025.xlsx'); parser.add_argument('--dys',default='raw/acute_dys_2025.xlsx'); parser.add_argument('--out',default='results/acute_reanalysis.json'); parser.add_argument('--parse-only',action='store_true'); args=parser.parse_args()
    a=parse_inek(args.all); save_json(a,Path('parsed')/(Path(args.all).stem+'.json'))
    print(json.dumps({'n':a['n'],'sheets':{s:len(r) for s,r in a['tables'].items()},'checks':a['checks'],'sd_diagnostic':a['sd_convention_diagnostic']},ensure_ascii=True))
    if not args.parse_only and Path(args.dys).exists():
        d=parse_inek(args.dys); save_json(d,Path('parsed')/(Path(args.dys).stem+'.json'))
        r=compare_exports(a,d); save_json(r,args.out)
        print(json.dumps({'n_all':r['n_all'],'n_dys':r['n_dys'],'los':r['los'],'drg_analyses':r['drg_standardization']['analyses'],'key_outcomes':r['single_code_outcomes']},ensure_ascii=True))
