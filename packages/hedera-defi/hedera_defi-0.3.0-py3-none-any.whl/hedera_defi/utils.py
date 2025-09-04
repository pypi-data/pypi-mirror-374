"""
Utility functions for Hedera DeFi SDK
"""

from datetime import datetime
from typing import Optional, Union


def parse_timestamp(timestamp: Optional[Union[str, int]]) -> Optional[datetime]:
    """Parse Hedera timestamp (nanoseconds) to datetime"""
    if timestamp is None:
        return None
    
    try:
        if isinstance(timestamp, str):
            timestamp = int(timestamp)
        
        # Convert nanoseconds to seconds
        seconds = timestamp / 1_000_000_000
        return datetime.fromtimestamp(seconds)
    except (ValueError, TypeError):
        return None


def format_number(value: float, decimals: int = 2, currency_symbol: str = "") -> str:
    """Format number with commas and decimals (no currency assumptions)"""
    if value >= 1_000_000_000:
        return f"{currency_symbol}{value/1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{currency_symbol}{value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{currency_symbol}{value/1_000:.{decimals}f}K"
    else:
        return f"{currency_symbol}{value:.{decimals}f}"


def calculate_apy(apr: float, compounds_per_year: int = 365) -> float:
    """Convert APR to APY (compounding calculation)"""
    if apr < 0 or compounds_per_year <= 0:
        return 0
    
    return ((1 + apr / compounds_per_year) ** compounds_per_year - 1) * 100


def calculate_il(
    price_ratio_change: float,
    pool_type: str = "50/50"
) -> float:
    """
    Calculate impermanent loss
    
    Args:
        price_ratio_change: Ratio of current price to initial price (must be > 0)
        pool_type: Pool weight distribution ("50/50" for equal weight)
        
    Returns:
        IL as percentage (0-100)
    
    Raises:
        ValueError: If price_ratio_change <= 0
    """
    if price_ratio_change <= 0:
        raise ValueError("Price ratio change must be positive")
    if pool_type == "50/50":
        # Standard Uniswap V2 formula
        il = 2 * (price_ratio_change ** 0.5) / (1 + price_ratio_change) - 1
    else:
        # Generic formula for other pool types - requires specific pool parameters
        # This is a simplified approximation
        il = abs(1 - price_ratio_change) * 0.5
    
    return abs(il) * 100


def estimate_transaction_cost(
    gas_used: int,
    gas_price_hbar: float
) -> float:
    """Calculate transaction cost in HBAR (requires current gas price)"""
    if gas_used <= 0 or gas_price_hbar <= 0:
        return 0
    return gas_used * gas_price_hbar


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Safe division with default value"""
    if denominator == 0:
        return default
    return numerator / denominator