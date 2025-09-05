import warnings
import pandas as pd
import pdb
 
from .catalog import stat_dict

def _islist(x):
    return isinstance(x,list)

def _isscalar(x):
    return not isinstance(x,list)

def _computestart(start=None,end=None,lookback=None):
    if start:
        return start
    else:
        return None if (not all([end,lookback])) else (pd.Timestamp(end)-pd.DateOffset(months=lookback-1)).strftime("%Y-%m") 

def _computelookback(start,end):
    start_dt,end_dt = [pd.to_datetime(_) for _ in [start,end]]
    return (12*(end_dt.year - start_dt.year) + (end_dt.month - start_dt.month))+1
    
def _computeperiod(start,end):
    if all([start,end]):
        return f"{start}:{end}"
    elif start:
        return f"{start}:"
    elif end:
        return f":{end}"
    else:
        return ""
    
def _computeperiodformat(start,end):
    def _safestr(_):
        return pd.Timestamp(_).strftime("%b%y") if _ else ""
    start,end=_safestr(start),_safestr(end)
    if all([start,end]):
        return f"{start}-{end}"
    elif start:
        return f"{start}-"
    elif end:
        return f"-{end}"
    else:
        return ""

def _completeparams(params={},ticker=None,label=None,label_as=None):
    if not label:
        label=_computelabel(params=params,ticker=ticker,label_as=label_as)
    out={_:__ for _,__ in params.items()}
    out.update(label=label,ticker=ticker)
    return out

def _build_period_struct(
    period=None, # has precedence over start, end
    start=None,
    end=None,
    lookback=None,
    _default_start=None,
    _default_end=None,
    ):
    # period => start,end

    if period:
        if _isscalar(period):
            period=[period]
        period=[_ if isinstance(_,str) else "" for _ in period]
        start=[]
        end=[]
        period_parse=[_.split(":") if ":" in _ else ["",""] for _ in period]
        start=[_[0] for _ in period_parse]
        end=[_[1] for _ in period_parse]

    # align start,end
    if _isscalar(start):
        start=[start]
    if _isscalar(end):
        end=[end]
    if _isscalar(lookback):
        lookback=[lookback]


    num_periods=max(len(start),len(end),len(lookback))
    if len(start)==1:
        start=start*num_periods
    if len(end)==1:
        end=end*num_periods
    if len(lookback)==1:
        lookback=lookback*num_periods
    if len(start)!=num_periods:
        warnings.warn('mismatch len(start)!=num_periods')
    if len(end)!=num_periods:
        warnings.warn('mismatch len(end)!=num_periods')
    if len(lookback)!=num_periods:
        warnings.warn('mismatch len(lookback)!=num_periods')
    
    # end x lookback => start
    end=[_ if _ else _default_end for _ in end]
    start=[_computestart(start_i,end_i,lookback_i) for start_i,end_i,lookback_i in zip(start,end,lookback)]
    start=[_ if _ else _default_start for _ in start]
    
    return [
        dict(
            start=start_i,
            end=end_i,
            lookback=_computelookback(start_i,end_i),
            period=_computeperiod(start_i,end_i),
            periodformat=_computeperiodformat(start_i,end_i),
        )
        for start_i, end_i in zip(start,end)
    ]

def _computelabel(params=None,ticker=None,label_as=None):
    if not label_as:
        label_as="ticker"
    if "+" in label_as:
        prefix_type,suffix_type=label_as.split("+")
    else:
        prefix_type,suffix_type=label_as,None
    prefix=stat_dict[ticker][prefix_type]
    if suffix_type=="lookback":
        suffix=f"{params['lookback']}M"
    elif suffix_type=="period":
        suffix=params['periodformat']
    else:
        suffix=None
    return f"{prefix} ({suffix})" if suffix else prefix
    
def configureParams(
    _usecase=None,
    stat=None,
    label=None,
    label_as=None,
    **providedPeriodInputs
    ):
    usecasemap={
        1:dict(start=None,end=None,stat="sharpe"),
        2:dict(lookback=[12,18],label_as="ticker+lookback",stat=['sharpe','annvol']),
        3:dict(start="2020-01",label_as="name+period",stat=['sharpe','annvol']),
    }
    if _usecase:
        return configureParams(_default_start="2020-01",_default_end="2025-07",**usecasemap[_usecase])
    

    params=_build_period_struct(**providedPeriodInputs)
    
    
    if _isscalar(stat):
        stats=[stat]
    else:
        stats=stat
    
    if len(params)==1 and len(stats)>1:
        params=params*len(stats)
        
    elif len(params)>1 and len(stats)==1:
        stats=stats*len(params)
    
    if len(params)!=len(stats):
        warnings.warn("mismatch len(params)!=len(stat_tickers)")

    if _isscalar(label):
        label=[label]
    if len(label)==1:
        label=label*len(params)
    if len(params)!=len(label):
        warnings.warn("mismatch len(params)!=len(label)")


    out=[
        _completeparams(params=param_i,ticker=ticker_i,label=label_i,label_as=label_as)
        for param_i, ticker_i,label_i in zip(params,stats,label)
    ]

    return out
    




