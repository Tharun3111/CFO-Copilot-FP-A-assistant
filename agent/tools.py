"""
Data loading and metric calculation tools.
All functions are deterministic and work with local CSV/Excel data.
"""

from typing import Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

def _load(fixtures_dir: str = 'fixtures') -> dict[str, pd.DataFrame]:
    """
    Load all CSV files from fixtures directory.
    
    Args:
        fixtures_dir: Path to directory containing CSV files
        
    Returns:
        Dictionary with keys: 'actuals', 'budget', 'cash', 'fx'
        
    Note:
        Normalizes 'month' column to YYYY-MM string format.
    """
    base_path = Path(fixtures_dir)
    
    data = {}
    for name in ['actuals', 'budget', 'cash', 'fx']:
        csv_path = base_path / f'{name}.csv'
        if not csv_path.exists():
            raise FileNotFoundError(f"Could not find {csv_path}")
        df = pd.read_csv(csv_path)
        # Normalize month to string YYYY-MM
        if 'month' in df.columns:
            df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
        data[name] = df
    
    return data

def _usd_rate(fx: pd.DataFrame, month: str, currency: str) -> float:
    """
    Get USD conversion rate for a currency in a given month.
    
    Fallback hierarchy:
    1. Exact month match
    2. Latest available rate for currency
    3. Default to 1.0 (assume USD or no conversion)
    
    Args:
        fx: FX rates DataFrame
        month: YYYY-MM format
        currency: Currency code (USD, EUR, etc.)
        
    Returns:
        Conversion rate (1 unit currency = X USD)
    """
    # Exact match
    match = fx[(fx['month'] == month) & (fx['currency'] == currency)]
    if not match.empty:
        return float(match.iloc[0]['rate_to_usd'])
    
    # Latest for currency
    currency_rates = fx[fx['currency'] == currency]
    if not currency_rates.empty:
        return float(currency_rates.iloc[-1]['rate_to_usd'])
    
    # Default
    return 1.0


def revenue_vs_budget(
    fixtures_dir: str = 'fixtures',
    month: Optional[str] = None,
    entity: Optional[str] = None
) -> Tuple[float, float, float]:
    """
    Calculate revenue vs budget for a given month and entity.
    
    Args:
        fixtures_dir: Path to data directory
        month: YYYY-MM format (if None, uses latest month)
        entity: ParentCo, EMEA, or None for consolidated
        
    Returns:
        Tuple of (actual_usd, budget_usd, variance_usd)
        
    Note:
        Consolidated sums ParentCo + EMEA (with FX conversion for EMEA)
    """
    data = _load(fixtures_dir)
    actuals = data['actuals']
    budget = data['budget']
    fx = data['fx']
    
    # Default to latest month if not specified
    if month is None:
        month = actuals['month'].max()
    
    def get_revenue(df: pd.DataFrame, ent: str) -> float:
        """Helper to get revenue for an entity in a month."""
        mask = (df['month'] == month) & \
               (df['entity'] == ent) & \
               (df['account_category'] == 'Revenue')
        if mask.sum() == 0:
            return 0.0
        row = df[mask].iloc[0]
        amount = float(row['amount'])
        currency = row['currency']
        
        # Convert to USD
        if currency != 'USD':
            rate = _usd_rate(fx, month, currency)
            amount *= rate
        
        return amount
    
    if entity is None:
        # Consolidated
        actual_usd = get_revenue(actuals, 'ParentCo') + get_revenue(actuals, 'EMEA')
        budget_usd = get_revenue(budget, 'ParentCo') + get_revenue(budget, 'EMEA')
    else:
        actual_usd = get_revenue(actuals, entity)
        budget_usd = get_revenue(budget, entity)
    
    variance = actual_usd - budget_usd
    
    return (actual_usd, budget_usd, variance)


def gross_margin_series(
    fixtures_dir: str = 'fixtures',
    end_month: Optional[str] = None,
    lookback: int = 3
) -> pd.DataFrame:
    """
    Calculate gross margin % time series.
    
    Args:
        fixtures_dir: Path to data directory
        end_month: End month in YYYY-MM (if None, uses latest)
        lookback: Number of months to include
        
    Returns:
        DataFrame with columns ['month', 'gross_margin_pct']
        
    Note:
        GM% = (Revenue - COGS) / Revenue * 100
        Handles division by zero by setting GM% to NaN
    """
    data = _load(fixtures_dir)
    actuals = data['actuals']
    fx = data['fx']
    
    # Get available months sorted
    all_months = sorted(actuals['month'].unique())
    
    if end_month is None:
        end_month = all_months[-1]
    
    # Get last N months ending at end_month
    end_idx = all_months.index(end_month)
    start_idx = max(0, end_idx - lookback + 1)
    months = all_months[start_idx:end_idx + 1]
    
    results = []
    for month in months:
        # Get consolidated revenue and COGS (USD)
        revenue = 0.0
        cogs = 0.0
        
        for entity in ['ParentCo', 'EMEA']:
            entity_data = actuals[(actuals['month'] == month) & (actuals['entity'] == entity)]
            
            for _, row in entity_data.iterrows():
                amount = float(row['amount'])
                currency = row['currency']
                category = row['account_category']
                
                # Convert to USD
                if currency != 'USD':
                    rate = _usd_rate(fx, month, currency)
                    amount *= rate
                
                if category == 'Revenue':
                    revenue += amount
                elif category == 'COGS':
                    cogs += amount
        
        # Calculate GM%
        if revenue == 0:
            gm_pct = np.nan
        else:
            gm_pct = ((revenue - cogs) / revenue) * 100
        
        results.append({'month': month, 'gross_margin_pct': gm_pct})
    
    return pd.DataFrame(results)


def opex_breakdown(
    month: str,
    fixtures_dir: str = 'fixtures'
) -> pd.DataFrame:
    """
    Break down operating expenses by category for a given month.
    
    Args:
        month: YYYY-MM format
        fixtures_dir: Path to data directory
        
    Returns:
        DataFrame with columns ['category', 'usd']
        Categories: Marketing, Sales, R&D, Admin
        
    Note:
        Consolidated across ParentCo and EMEA with FX conversion
    """
    data = _load(fixtures_dir)
    actuals = data['actuals']
    fx = data['fx']
    
    # Filter for Opex categories in the given month
    opex_mask = (actuals['month'] == month) & \
                (actuals['account_category'].str.startswith('Opex:'))
    opex_data = actuals[opex_mask]
    
    # Aggregate by category
    breakdown = {}
    for _, row in opex_data.iterrows():
        category = row['account_category'].replace('Opex:', '')  # Remove prefix
        amount = float(row['amount'])
        currency = row['currency']
        
        # Convert to USD
        if currency != 'USD':
            rate = _usd_rate(fx, month, currency)
            amount *= rate
        
        breakdown[category] = breakdown.get(category, 0.0) + amount
    
    # Convert to DataFrame
    result = pd.DataFrame([
        {'category': cat, 'usd': amt}
        for cat, amt in breakdown.items()
    ])
    
    return result if not result.empty else pd.DataFrame(columns=['category', 'usd'])


def ebitda_for_month(
    month: str,
    fixtures_dir: str = 'fixtures'
) -> float:
    """
    Calculate EBITDA proxy for a given month.
    
    EBITDA (proxy) = Revenue - COGS - Total Opex
    
    Args:
        month: YYYY-MM format
        fixtures_dir: Path to data directory
        
    Returns:
        EBITDA in USD (consolidated)
    """
    data = _load(fixtures_dir)
    actuals = data['actuals']
    fx = data['fx']
    
    month_data = actuals[actuals['month'] == month]
    
    revenue = 0.0
    cogs = 0.0
    opex = 0.0
    
    for _, row in month_data.iterrows():
        amount = float(row['amount'])
        currency = row['currency']
        category = row['account_category']
        
        # Convert to USD
        if currency != 'USD':
            rate = _usd_rate(fx, month, currency)
            amount *= rate
        
        if category == 'Revenue':
            revenue += amount
        elif category == 'COGS':
            cogs += amount
        elif category.startswith('Opex:'):
            opex += amount
    
    return revenue - cogs - opex


def cash_runway_months(fixtures_dir: str = 'fixtures') -> float:
    """
    Calculate cash runway in months based on last 3 cash deltas.
    
    Runway = Current Cash / Avg Monthly Burn
    Burn = Average of last 3 month-over-month cash decreases
    
    Args:
        fixtures_dir: Path to data directory
        
    Returns:
        - Runway in months (float)
        - np.inf if cash is increasing or stable
        - np.nan if insufficient data (< 4 months)
        - 0.0 if current cash <= 0
        
    Note:
        Uses consolidated cash_usd from cash.csv
    """
    data = _load(fixtures_dir)
    cash = data['cash'].sort_values('month')
    
    if len(cash) < 4:
        return np.nan  # Need at least 4 months for 3 deltas
    
    # Get last 4 months to calculate 3 deltas
    recent = cash.tail(4)
    cash_values = recent['cash_usd'].values
    
    # Calculate deltas (negative = burn, positive = increase)
    deltas = np.diff(cash_values)
    
    # Average burn (take negative deltas only, or all if mixed)
    burns = -deltas[deltas < 0]  # Convert to positive burn amounts
    
    if len(burns) == 0:
        return np.inf  # Cash increasing or stable
    
    avg_burn = burns.mean()
    current_cash = cash_values[-1]
    
    if current_cash <= 0:
        return 0.0
    
    if avg_burn <= 0:
        return np.inf
    
    return current_cash / avg_burn