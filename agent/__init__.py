"""
Agent package for FP&A Copilot.
Contains intent classification and metric calculation tools.
"""

from .intents import Intent, parse_question
from .tools import (
    revenue_vs_budget,
    gross_margin_series,
    opex_breakdown,
    ebitda_for_month,
    cash_runway_months
)

__all__ = [
    'Intent',
    'parse_question',
    'revenue_vs_budget',
    'gross_margin_series',
    'opex_breakdown',
    'ebitda_for_month',
    'cash_runway_months'
]