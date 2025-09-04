"""
Main client for Hedera DeFi data access
"""

import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import requests
from .queries import GraphQLQueries
from .models import Token, Pool, Protocol, Transaction, WhaleAlert, RiskMetrics
from .utils import parse_timestamp, format_number


class HederaDeFi:
    """
    Simple interface to get all Hedera DeFi data
    
    Usage:
        client = HederaDeFi(api_key="your_key")
        
        # Get all protocols
        protocols = client.get_protocols(min_tvl=10000)
        
        # Get whale transactions
        whales = client.get_whale_transactions(threshold=100000)
        
        # Get top tokens
        tokens = client.get_top_tokens(limit=100)
    """
    
    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://mainnet.mirrornode.hgraph.io/graphql",
        cache_ttl: int = 60,
    ):
        """
        Initialize Hedera DeFi client
        
        Args:
            api_key: Hgraph API key
            endpoint: GraphQL endpoint
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.queries = GraphQLQueries()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        })
    
    # ========== CORE QUERY METHOD ==========
    
    def query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query with caching"""
        cache_key = f"{query}:{str(variables)}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        # Execute query
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.session.post(self.endpoint, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        # Cache result
        self.cache[cache_key] = (data, time.time())
        return data
    
    # ========== PROTOCOL DISCOVERY ==========
    
    def get_protocols(
        self,
        min_tvl: float = 10000,
        protocol_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Protocol]:
        """
        Get all DeFi protocols above minimum TVL
        
        Args:
            min_tvl: Minimum TVL in USD
            protocol_type: Filter by type ('dex', 'lending', 'staking')
            limit: Maximum number of protocols
            
        Returns:
            List of Protocol objects
        """
        query = self.queries.get_protocols_query()
        window = int((time.time() - 7 * 24 * 60 * 60) * 1_000_000_000)
        
        result = self.query(query, {
            "window": str(window),
            "limit": limit
        })
        
        protocols = []
        for contract_data in result["data"].get("contracts", []):
            protocol = self._parse_protocol(contract_data)
            
            # Filter by TVL and type
            if protocol.tvl >= min_tvl:
                if protocol_type is None or protocol.type == protocol_type:
                    protocols.append(protocol)
        
        return sorted(protocols, key=lambda p: p.tvl, reverse=True)
    
    # ========== TOKEN ANALYTICS ==========
    
    def get_top_tokens(
        self,
        limit: int = 50,
        sort_by: str = "tvl"
    ) -> List[Token]:
        """
        Get top tokens by various metrics
        
        Args:
            limit: Number of tokens to return
            sort_by: 'tvl', 'holders', 'volume', 'supply'
            
        Returns:
            List of Token objects
        """
        query = self.queries.get_tokens_query(sort_by)
        result = self.query(query, {"limit": limit})
        
        tokens = []
        for token_data in result["data"].get("tokens", []):
            token = self._parse_token(token_data)
            tokens.append(token)
        
        return tokens
    
    # ========== POOL/LP ANALYTICS ==========
    
    def get_pools(
        self,
        protocol_id: Optional[str] = None,
        min_tvl: float = 1000,
        pool_type: Optional[str] = None
    ) -> List[Pool]:
        """
        Get liquidity pools
        
        Args:
            protocol_id: Filter by protocol
            min_tvl: Minimum pool TVL
            pool_type: 'dex', 'lending', 'staking'
            
        Returns:
            List of Pool objects
        """
        query = self.queries.get_pools_query()
        window = int((time.time() - 24 * 60 * 60) * 1_000_000_000)
        
        variables = {
            "window": str(window),
            "minTvl": min_tvl
        }
        
        if protocol_id:
            variables["protocol"] = protocol_id
        
        result = self.query(query, variables)
        
        pools = []
        for pool_data in result["data"].get("pools", []):
            pool = self._parse_pool(pool_data)
            if pool_type is None or pool.type == pool_type:
                pools.append(pool)
        
        return sorted(pools, key=lambda p: p.tvl, reverse=True)
    
    # ========== WHALE TRACKING ==========
    
    def get_whale_transactions(
        self,
        threshold: float = 100000,
        window_minutes: int = 60,
        transaction_type: Optional[str] = None
    ) -> List[WhaleAlert]:
        """
        Get whale transactions above threshold
        
        Args:
            threshold: Minimum transaction value in USD
            window_minutes: Time window to search
            transaction_type: Filter by type ('swap', 'transfer', 'liquidity')
            
        Returns:
            List of WhaleAlert objects
        """
        query = self.queries.get_whale_transactions_query()
        window_nanos = int((time.time() - window_minutes * 60) * 1_000_000_000)
        
        result = self.query(query, {
            "window": str(window_nanos),
            "threshold": str(int(threshold * 100_000_000))  # Convert to tinybars
        })
        
        alerts = []
        
        # Process HBAR transfers
        for transfer in result["data"].get("hbar_transfers", []):
            alert = self._parse_whale_transfer(transfer, "HBAR")
            if alert.value_usd >= threshold:
                if transaction_type is None or alert.type == transaction_type:
                    alerts.append(alert)
        
        # Process token transfers
        for transfer in result["data"].get("token_transfers", []):
            alert = self._parse_whale_transfer(transfer, "TOKEN")
            if alert.value_usd >= threshold:
                if transaction_type is None or alert.type == transaction_type:
                    alerts.append(alert)
        
        return sorted(alerts, key=lambda a: a.value_usd, reverse=True)
    
    # ========== RISK ANALYTICS ==========
    
    def get_risk_metrics(
        self,
        protocol_id: str,
        include_liquidations: bool = True
    ) -> RiskMetrics:
        """
        Get risk metrics for a protocol
        
        Args:
            protocol_id: Protocol contract ID
            include_liquidations: Include liquidation data
            
        Returns:
            RiskMetrics object
        """
        query = self.queries.get_risk_metrics_query()
        window = int((time.time() - 24 * 60 * 60) * 1_000_000_000)
        
        result = self.query(query, {
            "protocol": protocol_id,
            "window": str(window)
        })
        
        return self._parse_risk_metrics(result["data"])
    
    # ========== TVL & VOLUME ==========
    
    def get_tvl_history(
        self,
        protocol_id: Optional[str] = None,
        days: int = 30,
        interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Get historical TVL data
        
        Args:
            protocol_id: Protocol to get TVL for (None for total)
            days: Number of days of history
            interval: 'hourly', 'daily', 'weekly'
            
        Returns:
            DataFrame with timestamp and TVL columns
        """
        query = self.queries.get_tvl_history_query()
        
        # Calculate time windows
        intervals = []
        current_time = time.time()
        
        if interval == "hourly":
            step = 3600
        elif interval == "daily":
            step = 86400
        elif interval == "weekly":
            step = 604800
        else:
            step = 86400
        
        for i in range(days):
            start = int((current_time - (i + 1) * step) * 1_000_000_000)
            end = int((current_time - i * step) * 1_000_000_000)
            intervals.append((start, end))
        
        tvl_data = []
        for start, end in intervals:
            result = self.query(query, {
                "start": str(start),
                "end": str(end),
                "protocol": protocol_id
            })
            
            tvl = self._calculate_tvl_from_result(result["data"])
            tvl_data.append({
                "timestamp": datetime.fromtimestamp(end / 1_000_000_000),
                "tvl": tvl
            })
        
        return pd.DataFrame(tvl_data)
    
    # ========== YIELD FARMING ==========
    
    def get_best_yields(
        self,
        min_apy: float = 5.0,
        max_risk: float = 50.0,
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Get best yield opportunities
        
        Args:
            min_apy: Minimum APY percentage
            max_risk: Maximum risk score (0-100)
            limit: Number of results
            
        Returns:
            DataFrame with yield opportunities
        """
        pools = self.get_pools(min_tvl=10000)
        
        opportunities = []
        for pool in pools:
            if pool.apy >= min_apy:
                risk_score = self._calculate_pool_risk(pool)
                if risk_score <= max_risk:
                    opportunities.append({
                        "pool": pool.name,
                        "protocol": pool.protocol,
                        "type": pool.type,
                        "apy": pool.apy,
                        "tvl": pool.tvl,
                        "risk_score": risk_score,
                        "tokens": ", ".join(pool.tokens),
                    })
        
        df = pd.DataFrame(opportunities)
        return df.nlargest(limit, "apy")
    
    # ========== AGGREGATED ANALYTICS ==========
    
    def get_defi_overview(self) -> Dict[str, Any]:
        """
        Get complete DeFi ecosystem overview
        
        Returns:
            Dictionary with key metrics
        """
        protocols = self.get_protocols(min_tvl=1000)
        tokens = self.get_top_tokens(limit=10)
        whales = self.get_whale_transactions(window_minutes=60)
        
        total_tvl = sum(p.tvl for p in protocols)
        total_volume = sum(p.volume_24h for p in protocols)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tvl": total_tvl,
            "total_volume_24h": total_volume,
            "protocol_count": len(protocols),
            "top_protocols": [
                {"name": p.name, "tvl": p.tvl, "type": p.type}
                for p in protocols[:5]
            ],
            "top_tokens": [
                {"symbol": t.symbol, "tvl": t.tvl, "price": t.price}
                for t in tokens[:5]
            ],
            "whale_activity": {
                "count": len(whales),
                "total_value": sum(w.value_usd for w in whales),
                "largest": max(whales, key=lambda w: w.value_usd).value_usd if whales else 0
            },
            "market_health": self._calculate_market_health(protocols)
        }
    
    # ========== SEARCH & DISCOVERY ==========
    
    def search_protocols(
        self,
        query: str,
        search_type: str = "name"
    ) -> List[Protocol]:
        """
        Search for protocols by name or address
        
        Args:
            query: Search query
            search_type: 'name', 'address', 'token'
            
        Returns:
            List of matching protocols
        """
        all_protocols = self.get_protocols(min_tvl=0)
        
        results = []
        query_lower = query.lower()
        
        for protocol in all_protocols:
            if search_type == "name":
                if query_lower in protocol.name.lower():
                    results.append(protocol)
            elif search_type == "address":
                if query_lower in protocol.contract_id.lower():
                    results.append(protocol)
            elif search_type == "token":
                if any(query_lower in t.lower() for t in protocol.tokens):
                    results.append(protocol)
        
        return results
    
    # ========== PRIVATE HELPER METHODS ==========
    
    def _parse_protocol(self, data: Dict) -> Protocol:
        """Parse protocol from GraphQL data"""
        return Protocol(
            contract_id=data.get("contract_id", ""),
            name=data.get("name", "Unknown"),
            type=self._determine_protocol_type(data),
            tvl=float(data.get("tvl", 0)),
            volume_24h=float(data.get("volume_24h", 0)),
            users_24h=int(data.get("users_24h", 0)),
            pools=data.get("pools", []),
            tokens=data.get("tokens", []),
            created_at=parse_timestamp(data.get("created_timestamp")),
        )
    
    def _parse_token(self, data: Dict) -> Token:
        """Parse token from GraphQL data"""
        return Token(
            token_id=data.get("token_id", ""),
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            decimals=int(data.get("decimals", 8)),
            total_supply=int(data.get("total_supply", 0)),
            price=float(data.get("price", 0)),
            tvl=float(data.get("tvl", 0)),
            volume_24h=float(data.get("volume_24h", 0)),
            holders=int(data.get("holders", 0)),
        )
    
    def _parse_pool(self, data: Dict) -> Pool:
        """Parse pool from GraphQL data"""
        return Pool(
            pool_id=data.get("pool_id", ""),
            protocol=data.get("protocol", ""),
            name=data.get("name", ""),
            type=data.get("type", "unknown"),
            tokens=data.get("tokens", []),
            tvl=float(data.get("tvl", 0)),
            volume_24h=float(data.get("volume_24h", 0)),
            apy=float(data.get("apy", 0)),
            fees_24h=float(data.get("fees_24h", 0)),
            il_risk=float(data.get("il_risk", 0)),
        )
    
    def _parse_whale_transfer(self, data: Dict, transfer_type: str) -> WhaleAlert:
        """Parse whale transfer from GraphQL data"""
        if transfer_type == "HBAR":
            amount = abs(int(data.get("amount", 0)))
            value_usd = amount / 100_000_000 * 0.05  # Assume $0.05 per HBAR
            token = "HBAR"
        else:
            amount = int(data.get("amount", 0))
            # Would need price oracle for accurate USD value
            value_usd = amount / 1e8  # Placeholder
            token = data.get("token_id", "")
        
        return WhaleAlert(
            timestamp=parse_timestamp(data.get("consensus_timestamp")),
            type="transfer",
            token=token,
            amount=amount,
            value_usd=value_usd,
            from_address=data.get("from", ""),
            to_address=data.get("to", ""),
            transaction_hash=data.get("transaction_hash", ""),
        )
    
    def _parse_risk_metrics(self, data: Dict) -> RiskMetrics:
        """Parse risk metrics from GraphQL data"""
        return RiskMetrics(
            protocol_id=data.get("protocol_id", ""),
            tvl_change_24h=float(data.get("tvl_change_24h", 0)),
            volume_change_24h=float(data.get("volume_change_24h", 0)),
            concentration_risk=float(data.get("concentration_risk", 0)),
            liquidity_risk=float(data.get("liquidity_risk", 0)),
            smart_contract_risk=float(data.get("smart_contract_risk", 0)),
            overall_risk=data.get("overall_risk", "medium"),
        )
    
    def _determine_protocol_type(self, data: Dict) -> str:
        """Determine protocol type from event signatures"""
        events = data.get("events", [])
        
        if any("Swap" in e for e in events):
            return "dex"
        elif any("Borrow" in e or "Lend" in e for e in events):
            return "lending"
        elif any("Stake" in e for e in events):
            return "staking"
        else:
            return "unknown"
    
    def _calculate_tvl_from_result(self, data: Dict) -> float:
        """Calculate TVL from query result"""
        total = 0
        for balance in data.get("balances", []):
            # Simplified calculation - would need price oracle
            amount = float(balance.get("balance", 0))
            decimals = int(balance.get("decimals", 8))
            total += amount / (10 ** decimals)
        return total
    
    def _calculate_pool_risk(self, pool: Pool) -> float:
        """Calculate risk score for a pool (0-100)"""
        risk = 0
        
        # TVL risk (lower TVL = higher risk)
        if pool.tvl < 100_000:
            risk += 30
        elif pool.tvl < 1_000_000:
            risk += 15
        
        # IL risk
        risk += pool.il_risk * 30
        
        # Volume risk (low volume = higher risk)
        if pool.tvl > 0:
            volume_ratio = pool.volume_24h / pool.tvl
            if volume_ratio < 0.01:
                risk += 25
            elif volume_ratio < 0.1:
                risk += 10
        
        return min(100, risk)
    
    def _calculate_market_health(self, protocols: List[Protocol]) -> str:
        """Calculate overall market health"""
        if not protocols:
            return "unknown"
        
        avg_tvl_change = sum(p.tvl for p in protocols) / len(protocols)
        total_volume = sum(p.volume_24h for p in protocols)
        
        if avg_tvl_change > 0 and total_volume > 10_000_000:
            return "healthy"
        elif total_volume > 1_000_000:
            return "moderate"
        else:
            return "low_activity"