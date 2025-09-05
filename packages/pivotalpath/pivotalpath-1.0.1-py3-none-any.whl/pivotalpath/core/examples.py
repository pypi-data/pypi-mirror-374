
from . import main_library as mli
from . import important_tickers as it

"""
USECASES AND EXAMPLES OF THE MAIN LIBRARY FUNCTIONS

"""

"""
example1: example of tickers
"""
def example1():
    return [it.market_ticker, it.riskfree_ticker, it.hedge_fund_composite_index_ticker]

"""
example2: hedge fund index catalog
"""
def example2():
    return mli.get_catalog(asset_class="index")

"""
example3: list all hedge fund index tickers
"""
def example3():
    return mli.get_asset_list(asset_class="index")

"""
example4: list all hedge fund index names
"""
def example4():
    return mli.get_asset_list(asset_class="index", select="name")
"""
example5: market returns
"""
def example5():
    return mli.get_returns(ticker=it.market_ticker)

"""
example6: list available stats tickers
""" 
def example6():
    return mli.get_stats_list()
"""
example7: list available stats names
"""
def example7():
    return mli.get_stats_list(select="name")
"""
example8: example stats for first 2 hedge fund indices
"""     
def example8():
    return mli.get_stats(
        target=mli.get_asset_list(asset_class="index")[:2],
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=['annret','annvol','sharpe']
        )

"""
example9: example stats with custom labels
"""
def example9():
    return mli.get_stats(
        target=mli.get_asset_list(asset_class='index')+['SP500'],
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=mli.get_stats_list(),
        label_as="shortname",
        )
"""
example10: example structured stats
""" 
def example10():
    return mli.get_stats(
        target=mli.get_asset_list(asset_class='index'),
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=['sharpe','annvol'],
        label_as="name+period",
        index_as="name",
    )   

