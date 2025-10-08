"""
Smoke tests for metric calculation functions.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np
from agent.tools import (
    revenue_vs_budget,
    gross_margin_series,
    opex_breakdown,
    ebitda_for_month,
    cash_runway_months
)


def test_revenue_vs_budget_returns_floats():
    """Test that revenue_vs_budget returns three floats."""
    try:
        actual, budget, variance = revenue_vs_budget(fixtures_dir='fixtures')
        assert isinstance(actual, float)
        assert isinstance(budget, float)
        assert isinstance(variance, float)
    except FileNotFoundError:
        pytest.skip("Fixtures not available")


def test_gross_margin_series_has_correct_columns():
    """Test that gross_margin_series returns expected columns."""
    try:
        df = gross_margin_series(fixtures_dir='fixtures', lookback=3)
        assert 'month' in df.columns
        assert 'gross_margin_pct' in df.columns
    except FileNotFoundError:
        pytest.skip("Fixtures not available")


def test_opex_breakdown_returns_usd_column():
    """Test that opex_breakdown returns a 'usd' column."""
    try:
        df = opex_breakdown(fixtures_dir='fixtures', month='2025-06')
        if not df.empty:
            assert 'usd' in df.columns
            assert 'category' in df.columns
    except FileNotFoundError:
        pytest.skip("Fixtures not available")


def test_ebitda_for_month_is_float():
    """Test that ebitda_for_month returns a float."""
    try:
        result = ebitda_for_month(fixtures_dir='fixtures', month='2025-06')
        assert isinstance(result, (float, np.floating))
    except FileNotFoundError:
        pytest.skip("Fixtures not available")


def test_cash_runway_months_is_numeric():
    """Test that cash_runway_months returns float/inf/nan."""
    try:
        result = cash_runway_months(fixtures_dir='fixtures')
        assert isinstance(result, (float, np.floating)) or np.isnan(result) or np.isinf(result)
    except FileNotFoundError:
        pytest.skip("Fixtures not available")


def test_variance_calculation():
    """Test that variance = actual - budget."""
    try:
        actual, budget, variance = revenue_vs_budget(fixtures_dir='fixtures')
        assert abs(variance - (actual - budget)) < 0.01  # Allow small floating point error
    except FileNotFoundError:
        pytest.skip("Fixtures not available")