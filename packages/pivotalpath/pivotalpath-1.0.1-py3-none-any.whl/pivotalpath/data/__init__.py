
import pandas as pd
from .api import GetFilteredDataFrame
from . import utils as tsutil

def _ticker2class(ticker):
    if isinstance(ticker,list):
        return [_ticker2class(_) for _ in ticker]
    else:
        # tba: add confirmation
        if ticker.startswith("PP"):
            return "index"
        else:
            return "factor"
            
def _ticker2map(ticker=[]):
    out=dict(
        index=[_ for _ in ticker if _.startswith("PP")],
        factor=[_ for _ in ticker if not (_.startswith("PP"))]
    )
    return {_:__ for _,__ in out.items() if __}


"""
main functions
"""

def get_catalog(asset_class="index",filter_by=dict(),select="*")->pd.DataFrame:
    if isinstance(asset_class,list):
        df=pd.DataFrame()
        for _ in asset_class:
            df_i=get_catalog(asset_class=_,filter_by=filter_by,select="*")
            df=pd.concat([df,df_i]).set_index("ticker")
        return df
    table_name=f"{asset_class}_catalog"
    return GetFilteredDataFrame(table_name,filter_by=filter_by)
    

def get_info(ticker=None):

    if not ticker:
        return {}

    if isinstance(ticker,str):
        asset_class=_ticker2class(ticker)
        table_name=f"{asset_class}_catalog"
        return GetFilteredDataFrame(table_name,filter_by=dict(ticker=ticker)).iloc[0].to_dict()
    
    if isinstance(ticker,list):
        tickermap=_ticker2map(ticker)
        out=pd.DataFrame()
        for asset_i,ticker_i in tickermap.items():
            table_name=f"{asset_i}_catalog"
            df_i=GetFilteredDataFrame(table_name, filter_by=dict(ticker=ticker_i))
            if isinstance(df_i,pd.DataFrame) and not (df_i.empty):
                out=pd.concat([out,df_i],axis=0)
        return out
    

def get_returns(
        ticker=[],
        month_list=[],
        start=None,
        end=None,
        lookback=None,
        column_label="ticker",
        freq="M",
        freq_aggregation="compounded",
        annualized=False,
        rounding_places=6,
        pivot=True,
        
    )->pd.DataFrame:

    """
    Get returns data for specified tickers.
    
    Returns:
        pd.DataFrame or None: DataFrame with returns data, or None if no ticker provided
    """
    if not ticker:
        return pd.DataFrame()
    if isinstance(ticker,str):
        ticker=[ticker]
    tickermap=_ticker2map(ticker=ticker)
    if not month_list:
        month_list=tsutil.build_month_list(start=start,end=end,lookback=lookback)
    df=pd.DataFrame()
    for asset_i, ticker_i in tickermap.items(): 
        table_name=f"{asset_i}_returns"
        rows=GetFilteredDataFrame(table_name, filter_by=dict(ticker=ticker_i))
        if start:
            rows=rows[rows['month']>=start]
        if end:
            rows=rows[rows['month']<=end]   

        if df.empty:
            df=rows
        else:
            df=pd.concat([df,rows])
            
    df=df[df['ticker'].isin(ticker)]
    if freq!="M":
        pivot=True

    if pivot:
        df=df.pivot_table(index='month', columns='ticker', values='return')
        df=df[[_ for _ in ticker if _ in df.columns]]
    
    if freq!="M":
        df=tsutil.frequency_aggregation(df, freq=freq,freq_aggregation=freq_aggregation,annualized=annualized)
       
    return round(df,rounding_places)

    
