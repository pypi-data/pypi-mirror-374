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


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with commas and decimals"""
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"${value/1_000:.{decimals}f}K"
    else:
        return f"${value:.{decimals}f}"


def calculate_apy(apr: float, compounds_per_year: int = 365) -> float:
    """Convert APR to APY"""
    if apr <= 0 or compounds_per_year <= 0:
        return 0
    
    return ((1 + apr / compounds_per_year) ** compounds_per_year - 1) * 100


def calculate_il(
    price_ratio_change: float,
    pool_type: str = "50/50"
) -> float:
    """
    Calculate impermanent loss
    
    Args:
        price_ratio_change: Ratio of current price to initial price
        pool_type: Pool weight distribution
        
    Returns:
        IL as percentage (0-100)
    """
    if pool_type == "50/50":
        # Standard Uniswap V2 formula
        il = 2 * (price_ratio_change ** 0.5) / (1 + price_ratio_change) - 1
    else:
        # Simplified for other pool types
        il = abs(1 - price_ratio_change) * 0.5
    
    return abs(il) * 100


def estimate_gas_cost(
    gas_used: int,
    gas_price: float = 0.000001
) -> float:
    """Estimate transaction cost in HBAR"""
    return gas_used * gas_price


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Safe division with default value"""
    if denominator == 0:
        return default
    return numerator / denominator