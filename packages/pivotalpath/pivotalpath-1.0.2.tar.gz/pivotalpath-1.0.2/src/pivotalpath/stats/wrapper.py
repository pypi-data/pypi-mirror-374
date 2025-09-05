import pandas as pd
import pdb

from . import kernel as statsKernel

def _align2target(df,target=None):
    out=pd.DataFrame(index=target.index,columns=df.columns)
    common_idx=[_ for _ in target.index.tolist() if _ in df.index.tolist()]
    out.loc[common_idx,:]=df.loc[common_idx,:].copy()
    return out

def basicstats(
        df,
        base=None,
        riskfree=None,
        ticker=None,
        start=None,
        end=None,
        label=None,
        _roundoff=6,
        **overflowParams,
    ):

    if not ticker:
        return pd.DataFrame()
    
    if any([start,end]):
        df=df.loc[start:end]
        if base is not None:
            base=base.loc[start:end]   
        if riskfree is not None:
            riskfree=riskfree.loc[start:end]

    if base is not None:
        base=_align2target(base,target=df)
    if riskfree is not None:
        riskfree=_align2target(riskfree,target=df)
    if not label:
        label=ticker
    
    out=getattr(statsKernel,ticker)(df,base=base,riskfree=riskfree,start=None,end=None,label=None)
    
    if isinstance(out,pd.DataFrame):
        out=out[out.columns[0]]
    if isinstance(out,pd.Series):
        out.name=label
        out=round(out,_roundoff)

    return out


