"""Independently reproduce adult destination contrasts from the original workbook cells."""
import argparse
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook

from adult_discharge import CATEGORIES, outcome_file
from outcomes_within_drg import filename

AGES = ('age18_74', 'age75plus')
POPS = ('all', 'dys')
Z = 1.959963984540054


@lru_cache(None)
def vector(path, dimension):
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        info = list(wb['Info'].values)
        n = int(info[7][1])
        if dimension == 'drg':
            return pd.Series({r[0]:int(r[2]) for r in list(wb['DRG-Verteilung'].values)[1:]
                              if r[0] not in (None,'---')}, dtype='int64')
        if dimension == 'total':
            return pd.Series({'total':n})
        rows, column = (info[10:14],0) if dimension == 'sex' else (info[7:14],6)
        counts = pd.Series({str(r[column]):round(r[column+1]*n) for r in rows},dtype='int64')
        assert counts.sum() == n
        return counts
    finally:
        wb.close()


def reconstruct(raw, out):
    actual = pd.read_csv(out).set_index(['outcome','model'])
    checked = set()
    cohort = actual.loc[('discharged_alive','crude')]

    @lru_cache(None)
    def observed(key,age,hd,dim,pilot=False):
        parts = []
        for pop in POPS:
            for kind in (None,'mortality','destination'):
                if kind == 'destination':
                    drg = 'B70D' if pilot else ''
                    fp = raw/outcome_file(key,age,hd,pop,drg)
                    if fp.exists():
                        parts.append(vector(fp,dim))
                    elif len(CATEGORIES[key])>1:
                        files = [raw/outcome_file(key+'_'+c,age,hd,pop,drg) for c in CATEGORIES[key]]
                        if not all(f.is_file() for f in files):return None
                        parts.append(pd.concat([vector(f,dim) for f in files],axis=1,join='inner').sum(axis=1))
                    else:
                        return None
                else:
                    name = filename(age,hd,pop,kind)
                    if pilot:name=name.replace('_2025.xlsx','_B70D_2025.xlsx')
                    if not (raw/name).is_file():
                        return None
                    parts.append(vector(raw/name,dim))
        frame=pd.concat(parts,axis=1,join='inner')
        frame.columns=['all','all_dead','all_ev','dys','dys_dead','dys_ev']
        return frame

    def check(key,model,blocks,all_admissions=False):
        row=actual.loc[(key,model)]
        if blocks is None:
            assert row.status=='unavailable'
            return
        df=pd.concat(blocks,ignore_index=True)
        dys=df.dys if all_admissions else df.dys-df.dys_dead
        all_n=df['all'] if all_admissions else df['all']-df.all_dead
        comp=all_n-dys
        e_dys=df.dys_ev
        e_comp=df.all_ev-e_dys
        keep=(dys>0)&(comp>0)
        n,m,a,b=[v[keep].to_numpy(float) for v in (dys,comp,e_dys,e_comp)]
        if n.size==0:
            assert row.status=='unavailable'
            return
        assert row.status=='estimated' and np.all((a>=0)&(a<=n)&(b>=0)&(b<=m))
        w=(n+m)/sum(n+m)
        p,q=a/n,b/m
        rp,rq=w@p,w@q
        vp=(w**2)@(p*(1-p)/n); vq=(w**2)@(q*(1-q)/m)
        rd=rp-rq; dr=Z*np.sqrt(vp+vq)
        rr=rp/rq if rq else np.nan
        ci=rr*np.exp(np.array([-1,1])*Z*np.sqrt(vp/rp**2+vq/rq**2)) if rp and rq else [np.nan,np.nan]
        cr=(a.sum()/n.sum())/(b.sum()/m.sum()) if b.sum() else np.nan
        coverage_base = '_n' if all_admissions else '_events'
        expected=dict(dys_coverage=n.sum()/cohort['dys'+coverage_base],
                      comparator_coverage=m.sum()/cohort['comparator'+coverage_base],
                      all_n=(n+m).sum(),dys_n=n.sum(),comparator_n=m.sum(),all_events=(a+b).sum(),
                      dys_events=a.sum(),comparator_events=b.sum(),dys_risk=rp,comparator_risk=rq,rr=rr,
                      rr_low=ci[0],rr_high=ci[1],rd=rd,rd_low=rd-dr,rd_high=rd+dr,
                      matched_crude_rr=cr,strata=n.size,all_observed_risk=(a+b).sum()/(n+m).sum(),
                      sparse_weight=w[(np.minimum.reduce((a,b,n-a,m-b))<5)].sum(),
                      boundary_weight=w[(p==0)|(q==0)|(p==1)|(q==1)].sum())
        np.testing.assert_allclose(row[list(expected)].astype(float),list(expected.values()),rtol=1e-10,
                                   atol=1e-12,err_msg=str((key,model)),equal_nan=True)
        checked.add((key,model))

    for key in CATEGORIES:
        def groups(dim,fine=False):
            all_groups=[]
            for age in AGES:
                diagnoses=['i63','i61'] if fine or age==AGES[1] else ['i63']
                parts=[observed(key,age,hd,dim) for hd in ['allhd']+diagnoses]
                if any(p is None for p in parts):return None
                other=parts[0]
                for part in parts[1:]:other=other.subtract(part)
                all_groups.extend(parts[1:]+[other.dropna()])
            return all_groups

        age_counts=[observed(key,a,'allhd','total') for a in AGES]
        complete=all(s is not None for s in age_counts)
        pooled=[pd.concat(age_counts).groupby(level=0).sum()] if complete else None
        check(key,'M1',pooled)
        check(key,'crude_all_discharges',pooled,all_admissions=True)
        check(key,'age',age_counts if complete else None)
        for model,dim in [('age_hd','total'),('M2','sex'),('M3','pccl')]:
            check(key,model,groups(dim))
            check(key,model+'_fine',groups(dim,True))
        check(key,'age_drg',[observed(key,a,'allhd','drg') for a in AGES] if complete else None)
        check(key,'age_hd_drg',groups('drg'))
        for model,dim in [('B70D_crude','total'),('B70D_age','total'),('B70D_age_sex','sex')]:
            b=[observed(key,a,'allhd',dim,True) for a in AGES]
            if any(v is None for v in b):b=None
            elif model=='B70D_crude':b=[pd.concat(b).groupby(level=0).sum()]
            check(key,model,b)
        assert actual.loc[(key,'M4'),'status']=='unavailable'

    published = actual[actual.index.get_level_values(0).isin(CATEGORIES)]
    assert checked==set(published[published.status=='estimated'].index)
    if ('other_or_unspecified_live_disposition','M1') in actual.index:
        crude=actual.loc[[(k,'M1') for k in list(CATEGORIES)+['other_or_unspecified_live_disposition']]]
        live=actual.loc[('discharged_alive','crude')]
        for arm in ('all','dys','comparator'):
            assert crude[arm+'_events'].sum()==live[arm+'_events']
    print(f'Verified {len(checked)} destination contrasts, their confidence intervals and common support.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',type=Path,required=True)
    parser.add_argument('--results',type=Path,default=Path(__file__).with_name('adult_discharge.csv'))
    args=parser.parse_args()
    reconstruct(args.raw,args.results)
