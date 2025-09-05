import pandas as pd

def _do_compound(df):
    return (1 +df).prod(min_count=1) - 1
def _do_sum(df):
    return df.sum()
def _compute_default_end():
    return (pd.Timestamp.today()-pd.DateOffset(months=1)).strftime("%Y-%m")
def _compute_default_start():
    return "1998-01"


def build_month_list(start=None,end=None,lookback=None, _default_start="1998-01",_default_rule="rule_of_7"):
    if not end:
        end=_compute_default_end()
    if not start:
        if lookback:
            start=(pd.Timestamp(end)-pd.DateOffset(months=lookback-1)).strftime("%Y-%m")
        else:
            start=_compute_default_start()
    return [_.strftime("%Y-%m") for _ in pd.period_range(start=start,end=end,freq="M")]

def timeseries_aggregation(df,freq="Q",freq_aggregation="compounded",annualized=False,rounding_places=6):
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, format='%Y-%m')
    df_agg=df.resample(freq)
    if freq_aggregation=="compounded":
        out=df_agg.apply(_do_compound)
        if annualized:
            out=(1+out)**4-1
    elif freq_aggregation=="sum":
        out= df_agg.apply(_do_sum)
        if annualized:
            out=4*out
    if rounding_places:
        out=round(out,rounding_places)
    out.index=out.index.to_period(freq).astype(str)
    if freq=="Y":
        out.index=[f"Y{_}" for _ in out.index]
    return out