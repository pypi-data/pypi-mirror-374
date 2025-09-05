"""LLM-optimized interface for hedge fund index analysis."""

from .interface import (
    quick_index_stats,
    analyze_hedge_fund_index,
    compare_hedge_fund_indices,
    list_hedge_fund_indices,
    list_available_metrics,
    generate_index_report,
)

__all__ = [
    "quick_index_stats",
    "analyze_hedge_fund_index",
    "compare_hedge_fund_indices",
    "list_hedge_fund_indices",
    "list_available_metrics", 
    "generate_index_report",
]
