"""
Data models for Hedera DeFi
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Token:
    """Token data model"""
    token_id: str
    symbol: str
    name: str
    decimals: int
    total_supply: int
    price: float
    tvl: float
    volume_24h: float
    holders: int
    
    def __repr__(self):
        return f"Token({self.symbol}, TVL=${self.tvl:,.0f})"


@dataclass
class Pool:
    """Liquidity pool data model"""
    pool_id: str
    protocol: str
    name: str
    type: str  # 'dex', 'lending', 'staking'
    tokens: List[str]
    tvl: float
    volume_24h: float
    apy: float
    fees_24h: float
    il_risk: float
    
    def __repr__(self):
        return f"Pool({self.name}, TVL=${self.tvl:,.0f}, APY={self.apy:.1f}%)"


@dataclass
class Protocol:
    """DeFi protocol data model"""
    contract_id: str
    name: str
    type: str  # 'dex', 'lending', 'staking', 'unknown'
    tvl: float
    volume_24h: float
    users_24h: int
    pools: List[str]
    tokens: List[str]
    created_at: datetime
    
    def __repr__(self):
        return f"Protocol({self.name}, {self.type}, TVL=${self.tvl:,.0f})"


@dataclass
class Transaction:
    """Transaction data model"""
    hash: str
    timestamp: datetime
    type: str
    from_address: str
    to_address: str
    value: float
    gas_used: int
    status: str
    
    def __repr__(self):
        return f"Tx({self.hash[:8]}..., ${self.value:,.2f})"


@dataclass
class WhaleAlert:
    """Whale transaction alert"""
    timestamp: datetime
    type: str  # 'transfer', 'swap', 'liquidity'
    token: str
    amount: int
    value_usd: float
    from_address: str
    to_address: str
    transaction_hash: str
    
    def __repr__(self):
        return f"WhaleAlert(${self.value_usd:,.0f} {self.token})"


@dataclass
class RiskMetrics:
    """Risk metrics for a protocol"""
    protocol_id: str
    tvl_change_24h: float
    volume_change_24h: float
    concentration_risk: float  # 0-1
    liquidity_risk: float  # 0-1
    smart_contract_risk: float  # 0-1
    overall_risk: str  # 'low', 'medium', 'high', 'critical'
    
    def __repr__(self):
        return f"Risk({self.overall_risk}, TVL Δ{self.tvl_change_24h:+.1f}%)"