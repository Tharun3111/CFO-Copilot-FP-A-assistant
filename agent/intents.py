"""
Rule-based intent classifier for FP&A questions.
Extracts query kind, month, and lookback period from user input.
"""

from dataclasses import dataclass
from typing import Optional, Literal
import re
from datetime import datetime


QueryKind = Literal[
    'revenue_vs_budget',
    'gm_trend',
    'opex_breakdown',
    'cash_runway',
    'unknown'
]


@dataclass
class Intent:
    """Parsed intent from user question."""
    kind: QueryKind
    month: Optional[str] = None  # YYYY-MM format
    lookback: Optional[int] = None  # Number of months to look back


def parse_question(question: str) -> Intent:
    """
    Parse user question into structured intent.
    
    Args:
        question: User's natural language question
        
    Returns:
        Intent object with kind, month, and lookback
        
    Examples:
        >>> parse_question("What was June 2025 revenue vs budget?")
        Intent(kind='revenue_vs_budget', month='2025-06', lookback=None)
        
        >>> parse_question("Show GM trend for last 3 months")
        Intent(kind='gm_trend', month=None, lookback=3)
    """
    q_lower = question.lower()
    
    # Extract month
    month = _extract_month(question)
    
    # Extract lookback
    lookback = _extract_lookback(q_lower)
    
    # Determine kind
    kind = _classify_kind(q_lower)
    
    return Intent(kind=kind, month=month, lookback=lookback)


def _extract_month(question: str) -> Optional[str]:
    """
    Extract month in YYYY-MM format from question.
    
    Handles:
    - "June 2025" -> "2025-06"
    - "2025-06" -> "2025-06"
    - "6/2025" -> "2025-06"
    """
    # Try YYYY-MM format
    match = re.search(r'\b(\d{4})-(\d{2})\b', question)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    
    # Try "Month YYYY" format
    months = {
        'january': '01', 'jan': '01',
        'february': '02', 'feb': '02',
        'march': '03', 'mar': '03',
        'april': '04', 'apr': '04',
        'may': '05',
        'june': '06', 'jun': '06',
        'july': '07', 'jul': '07',
        'august': '08', 'aug': '08',
        'september': '09', 'sep': '09', 'sept': '09',
        'october': '10', 'oct': '10',
        'november': '11', 'nov': '11',
        'december': '12', 'dec': '12'
    }
    
    for month_name, month_num in months.items():
        pattern = rf'\b{month_name}\s+(\d{{4}})\b'
        match = re.search(pattern, question.lower())
        if match:
            year = match.group(1)
            return f"{year}-{month_num}"
    
    return None


def _extract_lookback(q_lower: str) -> Optional[int]:
    """
    Extract lookback period from question.
    
    Examples:
    - "last 3 months" -> 3
    - "past 6 months" -> 6
    """
    match = re.search(r'\b(?:last|past)\s+(\d+)\s+months?\b', q_lower)
    if match:
        return int(match.group(1))
    return None


def _classify_kind(q_lower: str) -> QueryKind:
    """
    Classify question into one of the supported kinds.
    
    Rules:
    - "gross margin" or ("gm" & "trend") -> gm_trend
    - "cash runway" -> cash_runway
    - "opex" & ("breakdown" | "by category") -> opex_breakdown
    - ("revenue" & "budget") or "vs budget" -> revenue_vs_budget
    - else -> unknown
    """
    # Cash runway
    if 'cash runway' in q_lower or 'runway' in q_lower:
        return 'cash_runway'
    
    # Gross margin trend
    if 'gross margin' in q_lower or ('gm' in q_lower and 'trend' in q_lower):
        return 'gm_trend'
    
    # Opex breakdown
    if 'opex' in q_lower and ('breakdown' in q_lower or 'by category' in q_lower or 'categories' in q_lower):
        return 'opex_breakdown'
    
    # Revenue vs budget
    if ('revenue' in q_lower and 'budget' in q_lower) or 'vs budget' in q_lower or 'versus budget' in q_lower:
        return 'revenue_vs_budget'
    
    return 'unknown'