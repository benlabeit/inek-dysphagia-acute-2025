"""Independently recalculate published binary and hospital stay estimates from the private workbook cells."""
import argparse
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from outcomes_within_drg import filename

AGES = ('age18_74','age75plus')
Z = 1.959963984540054


@lru_cache(None)
def workbook(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        info = list(wb['Info'].values)
        n = info[7][1]
        def margin(start,end,column):
            return {str(r[column]):round(r[column+1]*n) for r in info[start:end]}
        labels = {'sex':margin(10,14,0), 'pccl':margin(7,14,6), 'total':{'all':n}}
        for dimension in labels.values():
            assert sum(dimension.values()) == n
        labels['child'] = {'pediatric':sum(round(r[10]*n) for r in info[7:14])}
        labels['drg'] = {r[0]:r[2] for r in list(wb['DRG-Verteilung'].values)[1:] if r[0] not in ('---',None)}
        return labels
    finally:
        wb.close()


def verify(raw, file):
    frame = pd.read_csv(file).set_index(['outcome','model'])
    checked = 0
    @lru_cache(None)
    def vector(endpoint,age,hd,pop,dimension,pilot=False):
        name = filename(age,hd,pop,endpoint)
        if pilot:
            name = name.replace('_2025.xlsx','_B70D_2025.xlsx')
        if not (raw/name).exists() and endpoint=='PNEUMONIA_UNION' and age=='age18_74' and hd=='allhd':
            ref = workbook(raw/filename('allages',hd,pop,endpoint))
            assert ref['child']['pediatric'] == 0
            older = vector(endpoint,AGES[1],hd,pop,dimension)
            return pd.Series(ref[dimension],dtype='int64').subtract(older).dropna()
        return pd.Series(workbook(raw/name)[dimension],dtype='int64')

    def four(endpoint,age,hd,dimension,pilot=False):
        return pd.concat([vector(k,age,hd,p,dimension,pilot)
                          for k in [None,endpoint] for p in ['all','dys']],axis=1,join='inner')

    def check(endpoint,model,blocks):
        nonlocal checked
        m = pd.concat(blocks).dropna().to_numpy(dtype=float)
        total,d,events,e = m.T
        c = total-d
        sel = (c>0)&(d>0)
        n1,n0,a,b = d[sel],c[sel],e[sel],(events-e)[sel]
        assert np.all((0<=a)&(a<=n1)&(0<=b)&(b<=n0))
        weights = (n1+n0)/(n1+n0).sum()
        risks,variances = [],[]
        for v,n in ((a,n1),(b,n0)):
            p=v/n;risks.append(weights@p);variances.append((weights**2)@(p*(1-p)/n))
        r,c = risks
        ratio = r/c
        rr_se = math.sqrt(variances[0]/r**2+variances[1]/c**2)
        rd_se = math.sqrt(sum(variances))
        expect = dict(dys_n=n1.sum(),comparator_n=n0.sum(),dys_events=a.sum(),comparator_events=b.sum(),
                      dys_risk=r,comparator_risk=c,rr=ratio,rd=r-c,rr_low=ratio*math.exp(-Z*rr_se),
                      rr_high=ratio*math.exp(Z*rr_se),rd_low=r-c-Z*rd_se,rd_high=r-c+Z*rd_se,
                      matched_crude_rr=(a.sum()/n1.sum())/(b.sum()/n0.sum()),strata=sel.sum())
        row = frame.loc[(endpoint,model)]
        assert row.status=='estimated'
        np.testing.assert_allclose(row[list(expect)].astype(float), list(expect.values()), rtol=1e-11,atol=1e-12)
        checked += 1

    for end in frame.index.get_level_values(0).unique():
        ages = [four(end,age,'allhd','total') for age in AGES]
        check(end,'M1',[sum(ages)])
        check(end,'age',ages)
        for model,dim in [('age_hd','total'),('M2','sex'),('M3','pccl'),('age_hd_drg','drg')]:
            for fine in (False,True):
                if fine and (dim=='drg' or end in ('E44.0','E44.1')):
                    continue
                blocks=[]
                for age in AGES:
                    allhd=four(end,age,'allhd',dim)
                    i63=four(end,age,'i63',dim)
                    other=allhd-i63
                    blocks.append(i63)
                    if fine or age=='age75plus':
                        i61=four(end,age,'i61',dim)
                        blocks.append(i61);other=other-i61
                    blocks.append(other)
                check(end,model+('_fine' if fine else ''),blocks)
        check(end,'age_drg',[four(end,a,'allhd','drg') for a in AGES])
    pilot = [four('mortality',a,'allhd','total',True) for a in AGES]
    check('mortality','B70D_crude',[sum(pilot)])
    check('mortality','B70D_age',pilot)
    check('mortality','M4_B70D',[four('mortality',a,'allhd','sex',True) for a in AGES])
    assert checked == (frame.status=='estimated').sum()
    print(f'Verified {checked} binary contrasts against workbook counts, including intervals and common support.')


def verify_stay(raw, file):
    """Read the native moment cells independently of the production Moments class."""
    @lru_cache(None)
    def moments(age, hd, pop, deaths, by_drg):
        name = filename(age,hd,pop,'mortality' if deaths else None)
        wb = openpyxl.load_workbook(raw/name, read_only=True, data_only=True)
        try:
            if by_drg:
                rows = list(wb['DRG-Verteilung'].values)[1:]
                return {code: np.array([n,round(n*mean),round(n*(mean**2+sd**2))])
                        for code,_,n,_,mean,sd in rows if code not in (None,'---')}
            info = list(wb['Info'].values)
            n,mean,sd = info[7][1],info[11][4],info[12][4]
            return {'all': np.array([n,round(n*mean),round(n*mean**2+(n-1)*sd**2)])}
        finally:
            wb.close()

    def group(age,hd,deaths,by_drg):
        total,dys = (moments(age,hd,p,deaths,by_drg) for p in ('all','dys'))
        return {k:np.array([total[k],dys[k]]) for k in total.keys() & dys.keys()}

    def minus(whole,part):
        return {k:whole[k]-part[k] for k in whole.keys() & part.keys()}

    frame = pd.read_csv(file).set_index('model')
    for model,row in frame.iterrows():
        strata = []
        for age in AGES:
            by_drg = 'drg' in model or 'B70D' in model
            levels = {}
            for hd in ('allhd','i63','i61'):
                subset = group(age,hd,False,by_drg)
                if 'survivors' in model:
                    subset = minus(subset,group(age,hd,True,False))
                levels[hd] = subset
            if 'B70D' in model:
                strata.append(levels['allhd']['B70D'])
            elif 'age_hd' in model:
                residual = minus(levels['allhd'],levels['i63'])
                strata.extend(levels['i63'].values())
                if age=='age75plus' or 'fine' in model:
                    residual = minus(residual,levels['i61'])
                    strata.extend(levels['i61'].values())
                strata.extend(residual.values())
            else:
                strata.extend(levels['allhd'].values())
        if model=='M1':
            strata = [sum(strata)]
        minimum = 2 if model.endswith('_n2') else 1
        v = np.array([g for g in strata if min(g[1,0],g[0,0]-g[1,0])>=minimum])
        weights = v[:,0,0]/sum(v[:,0,0])
        nd,sd,qd = v[:,1,:].T
        nc,sc,qc = (v[:,0,:]-v[:,1,:]).T
        md,mc = weights@(sd/nd),weights@(sc/nc)
        delta = md-mc
        lower = upper = np.nan
        if min(nd.min(),nc.min())>=2:
            arm_variances = (qd-sd**2/nd)/(nd*(nd-1))+(qc-sc**2/nc)/(nc*(nc-1))
            se = math.sqrt((weights**2)@arm_variances)
            lower,upper = delta-Z*se,delta+Z*se
        expected = dict(dys_n=nd.sum(),comparator_n=nc.sum(),strata=len(weights),dys_mean=md,
                        comparator_mean=mc,difference=delta,ci_low=lower,ci_high=upper,
                        matched_crude_difference=sd.sum()/nd.sum()-sc.sum()/nc.sum())
        np.testing.assert_allclose(row[list(expected)].astype(float),list(expected.values()),atol=1e-9,equal_nan=True)
    print(f'Verified {len(frame)} hospital stay analyses, including obtainable intervals and matched crude differences.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw',required=True,type=Path)
    ap.add_argument('--results',type=Path,default=Path(__file__).with_name('adult_binary.csv'))
    args=ap.parse_args()
    verify(args.raw,args.results)
    verify_stay(args.raw,args.results.with_name("adult_los.csv"))
