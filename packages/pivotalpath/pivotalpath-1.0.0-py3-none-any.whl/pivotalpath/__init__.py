"""
PivotalPath: The Industry Standard for Hedge Fund INDEX Analytics

Analyzes hedge fund indices - composite benchmarks tracking groups of hedge funds.
"""

from .version import __version__

# Core functionality
from .core.main_library import (
    get_catalog,
    get_returns, 
    get_info,
    get_asset_list,
    get_stats,
    get_stats_list,
)

# Important tickers and examples
from .core import important_tickers
from .core import examples

# Stats catalog  
from .stats.catalog import stats_catalog

# LLM-optimized interface for hedge fund indices
try:
    from .llm.interface import (
        quick_index_stats,
        analyze_hedge_fund_index,
        compare_hedge_fund_indices,
        list_hedge_fund_indices,
        list_available_metrics,
        generate_index_report,
    )
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"LLM interface import failed: {e}")
    LLM_AVAILABLE = False

# Export everything
__all__ = [
    "__version__",
    "get_catalog",
    "get_returns",
    "get_info", 
    "get_asset_list",
    "get_stats",
    "get_stats_list",
    "stats_catalog",
    "important_tickers",
    "examples",
    "LLM_AVAILABLE",
]

# Add LLM functions if available
if LLM_AVAILABLE:
    __all__.extend([
        "quick_index_stats",
        "analyze_hedge_fund_index",
        "compare_hedge_fund_indices", 
        "list_hedge_fund_indices",
        "list_available_metrics",
        "generate_index_report",
    ])
