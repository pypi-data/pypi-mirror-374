"""
LLM-optimized interface for PivotalPath.
Designed for hedge fund INDEX analysis only.

PivotalPath analyzes hedge fund indices - composite benchmarks that track 
groups of hedge funds by strategy. It does NOT analyze individual hedge funds.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime

# Import from your existing modules
from ..core.main_library import get_stats, get_returns, get_asset_list, get_catalog


def quick_index_stats(
    index_ticker: str,
    benchmark: str = "SP500",
    period: str = "5Y"
) -> Dict[str, Any]:
    """
    Get essential performance stats for a hedge fund index.
    
    Args:
        index_ticker: Hedge fund index ticker (e.g., "PP-HFC")
        benchmark: Market benchmark (default: "SP500")
        period: Time period - "1Y", "3Y", "5Y", "YTD"
        
    Returns:
        Dictionary with essential index performance metrics
    """
    import pandas as pd
    
    end_date = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%Y-%m")
    
    if period == "YTD":
        start_date = f"{pd.Timestamp.now().year}-01"
    elif period.endswith("Y"):
        years = int(period[:-1])
        start_date = (pd.Timestamp.now() - pd.DateOffset(years=years)).strftime("%Y-%m")
    else:
        start_date = "2020-01"
    
    essential_stats = ['annret', 'annvol', 'sharpe', 'maxddc', 'beta']
    
    try:
        results = get_stats(
            target=index_ticker,
            base=benchmark,
            start=start_date,
            end=end_date,
            stat=essential_stats
        )
        
        if isinstance(results, pd.DataFrame) and not results.empty:
            data = results.iloc[:, 0].to_dict()
            data.update({
                'index_ticker': index_ticker,
                'asset_type': 'hedge_fund_index',
                'benchmark': benchmark,
                'period': period,
                'analysis_date': pd.Timestamp.now().strftime("%Y-%m-%d")
            })
            return data
        else:
            return {
                'error': f"No data available for index {index_ticker}",
                'suggested_indices': list_hedge_fund_indices()[:3]
            }
    except Exception as e:
        return {
            'error': f"Index analysis failed: {str(e)}",
            'index_ticker': index_ticker
        }


def analyze_hedge_fund_index(
    index_ticker: str,
    benchmark: str = "SP500",
    start_date: str = "2020-01",
    end_date: str = "2024-12"
) -> Dict[str, Any]:
    """
    Comprehensive analysis of a hedge fund index.
    
    Args:
        index_ticker: Hedge fund index ticker (e.g., "PP-HFC")
        benchmark: Market benchmark (default: "SP500")
        start_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format
        
    Returns:
        Dictionary with comprehensive index performance metrics
    """
    all_stats = ['annret', 'annvol', 'sharpe', 'beta', 'alpha', 'maxddc', 'sortino', 'calmar']
    
    try:
        results = get_stats(
            target=index_ticker,
            base=benchmark,
            start=start_date,
            end=end_date,
            stat=all_stats
        )
        
        if isinstance(results, pd.DataFrame) and not results.empty:
            analysis_dict = results.iloc[:, 0].to_dict()
            analysis_dict.update({
                'index_ticker': index_ticker,
                'asset_type': 'hedge_fund_index',
                'benchmark': benchmark,
                'period': f"{start_date} to {end_date}",
                'analysis_date': datetime.now().strftime("%Y-%m-%d")
            })
            return analysis_dict
        else:
            return {
                'error': f"No data available for index {index_ticker}",
                'index_ticker': index_ticker
            }
    except Exception as e:
        return {
            'error': f"Index analysis failed: {str(e)}",
            'index_ticker': index_ticker
        }


def compare_hedge_fund_indices(
    index_tickers: List[str],
    benchmark: str = "SP500",
    metrics: List[str] = ['annret', 'annvol', 'sharpe', 'maxddc'],
    start_date: str = "2020-01",
    end_date: str = "2024-12"
) -> pd.DataFrame:
    """
    Compare multiple hedge fund indices side by side.
    
    Args:
        index_tickers: List of hedge fund index tickers
        benchmark: Market benchmark (default: "SP500")
        metrics: Metrics to compare
        start_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format
        
    Returns:
        DataFrame comparing indices
    """
    try:
        results = get_stats(
            target=index_tickers,
            base=benchmark,
            start=start_date,
            end=end_date,
            stat=metrics,
            transpose=True
        )
        
        if isinstance(results, pd.DataFrame) and not results.empty:
            return results.round(4)
        else:
            return pd.DataFrame(index=metrics, columns=index_tickers)
            
    except Exception as e:
        print(f"Index comparison failed: {e}")
        return pd.DataFrame(index=metrics, columns=index_tickers)


def list_hedge_fund_indices() -> List[str]:
    """Get list of all available hedge fund index tickers."""
    try:
        return get_asset_list(asset_class="index", select="ticker")
    except Exception:
        return ["PP-HFC", "PP-L-EH", "PP-L-MA", "PP-L-ED", "PP-L-EM"]


def list_available_metrics() -> List[str]:
    """Get list of all available performance metrics."""
    try:
        from ..core.main_library import get_stats_list
        return get_stats_list(select="ticker")
    except Exception:
        return ['annret', 'annvol', 'sharpe', 'maxddc', 'beta', 'alpha', 'sortino', 'calmar']


def generate_index_report(
    index_ticker: str,
    benchmark: str = "SP500",
    start_date: str = "2020-01",
    end_date: str = "2024-12"
) -> str:
    """
    Generate a formatted report for a hedge fund index.
    
    Returns:
        Formatted string report for the index
    """
    analysis = analyze_hedge_fund_index(index_ticker, benchmark, start_date, end_date)
    
    if 'error' in analysis:
        return f"Index Report Failed: {analysis['error']}"
    
    return f"""
HEDGE FUND INDEX PERFORMANCE REPORT
{'='*50}

Index: {analysis.get('index_ticker', 'N/A')}
Period: {analysis.get('period', 'N/A')}
Benchmark: {analysis.get('benchmark', 'N/A')}

PERFORMANCE METRICS
{''*25}
Annual Return:     {analysis.get('annret', 0):>8.1%}
Volatility:        {analysis.get('annvol', 0):>8.1%}
Sharpe Ratio:      {analysis.get('sharpe', 0):>8.2f}
Max Drawdown:      {analysis.get('maxddc', 0):>8.1%}

MARKET EXPOSURE
{''*25}
Beta:              {analysis.get('beta', 0):>8.2f}
Alpha:             {analysis.get('alpha', 0):>8.1%}

Analysis Date: {analysis.get('analysis_date', 'N/A')}

NOTE: This report analyzes a hedge fund INDEX, which represents
aggregated performance of multiple hedge funds, not an individual fund.
"""
