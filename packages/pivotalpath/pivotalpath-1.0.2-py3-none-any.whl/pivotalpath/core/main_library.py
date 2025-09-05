
from ..data import get_catalog, get_returns, get_info
from ..stats import stats_calculator,stats_catalog
import pandas as pd

def _notdf(df):
    return not(df is None) and not (isinstance(df,pd.DataFrame))

def get_stats(
        target=None,
        base=None,
        riskfree=None,
        index_as="ticker",
        transpose=False,
        **kwargs
    ):
    if _notdf(target):
        target=get_returns(ticker=target)
    if _notdf(base):
        base=get_returns(ticker=base)
    if _notdf(riskfree):   
        riskfree=get_returns(ticker=riskfree)
        return pd.DataFrame()
    df=stats_calculator(target=target,base=base,riskfree=riskfree,**kwargs)
    if isinstance(index_as,str) and index_as!="ticker":
        try:
            df_info=get_info(ticker=df.index.tolist())
            if isinstance(df_info,pd.DataFrame) and not (df_info.empty):
                info_map=df_info.set_index("ticker")[index_as].to_dict()
                df.index=[info_map.get(_,_) for _ in df.index.tolist()]
            df.index=df[index_as]
            df.index.name=index_as
        except:
            pass
    if transpose:
        df=df.T
    return df


def get_stats_list(select="ticker")->list:
    return [_.get(select) for _ in stats_catalog]

def get_asset_list(asset_class="index",select="ticker")->list:
    df=get_catalog(asset_class=asset_class,select=select)
    if isinstance(df,pd.DataFrame) and not (df.empty):
        return df[select].tolist()  
    return []
