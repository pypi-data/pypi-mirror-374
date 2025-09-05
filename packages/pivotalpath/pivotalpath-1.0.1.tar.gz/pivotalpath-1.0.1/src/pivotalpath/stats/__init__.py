
import warnings
import pandas as pd
from .params import configureParams
from .wrapper import basicstats
from .catalog import stats_catalog


def stats_calculator(
        target=None,
        base="SP500",
        riskfree="TBILL3M",
        configured_params=[],
        **kwargs
    )->pd.DataFrame:
    
    if not kwargs.get("_default_start"):
        kwargs.update(_default_start=target.index[0])
        
    if not kwargs.get("_default_end"):
        kwargs.update(_default_end=target.index[-1])
        
    if not configured_params:
        # note: configured_params will most certainly be empty, unles it is repurposed from a different call
        configured_params=configureParams(**kwargs)
    
    df=target
    out=None

    for i,param_i in enumerate(configured_params):
        stat_i=basicstats(df,base=base,riskfree=riskfree,**param_i)
        if stat_i is None:
            continue
        stat_i=pd.DataFrame(stat_i)
        if out is None:
            out=stat_i.copy()
        else:
            try:
                out=out.join(stat_i)
            except:
                warnings.warn("could not join the ith stat output")
        
    return out


# Import everything from catalog
from .catalog import stats_catalog, stat_dict

__all__ = [
    "stats_calculator",
    "stats_catalog",
    "stat_dict", 
    "basicstats",
    "configureParams",
]
