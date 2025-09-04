"""
Main client for Hedera DeFi data access using Mirror Node REST API
Comprehensive SDK with 40+ methods for Hedera developers
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import requests
from .models import Token, Pool, Protocol, Transaction, WhaleAlert, RiskMetrics
from .utils import parse_timestamp, format_number


class HederaDeFi:
    """
    Comprehensive Hedera DeFi SDK with 40+ methods for developers
    
    Usage:
        client = HederaDeFi()
        
        # Get all protocols
        protocols = client.get_protocols()
        
        # Get whale transactions
        whales = client.get_whale_transactions(threshold=10000)
        
        # Get top tokens
        tokens = client.get_top_tokens(limit=10)
    """
    
    # Known DeFi protocols on Hedera
    DEFI_PROTOCOLS = {
        "SaucerSwap": {
            "router": "0.0.1082166",
            "factory": "0.0.1082165",
            "type": "dex",
            "name": "SaucerSwap"
        },
        "HeliSwap": {
            "router": "0.0.1237181",
            "factory": "0.0.223960",
            "type": "dex",
            "name": "HeliSwap"
        },
        "Pangolin": {
            "router": "0.0.1242116",
            "factory": "0.0.798819",
            "type": "dex",
            "name": "Pangolin"
        },
        "Stader": {
            "staking": "0.0.3902492",
            "type": "staking",
            "name": "Stader"
        },
        "HSuite": {
            "router": "0.0.2830828",
            "type": "dex",
            "name": "HSuite"
        }
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://mainnet-public.mirrornode.hedera.com/api/v1",
        cache_ttl: int = 60,
    ):
        """
        Initialize Hedera DeFi client
        
        Args:
            api_key: Optional API key (not needed for public Mirror Node)
            endpoint: Mirror Node REST API endpoint
            cache_ttl: Cache time-to-live in seconds
        """
        self.endpoint = endpoint
        self.cache_ttl = cache_ttl
        self.cache = {}
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    # ========== CORE REQUEST METHOD ==========
    
    def _request(self, path: str, params: Optional[Dict] = None) -> Dict:
        """Execute REST API request with caching"""
        cache_key = f"{path}:{str(params)}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        # Execute request
        url = f"{self.endpoint}/{path}"
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Cache result
            self.cache[cache_key] = (data, time.time())
            return data
        else:
            return {}
    
    # ========== 1. PROTOCOL DISCOVERY ==========
    
    def get_protocols(
        self,
        min_tvl: float = 0,
        protocol_type: Optional[str] = None,
    ) -> List[Protocol]:
        """
        Get all DeFi protocols
        
        Args:
            min_tvl: Minimum TVL in USD (estimated)
            protocol_type: Filter by type ('dex', 'lending', 'staking')
            
        Returns:
            List of Protocol objects
        """
        protocols = []
        
        for name, info in self.DEFI_PROTOCOLS.items():
            if protocol_type and info["type"] != protocol_type:
                continue
            
            # Get the main account for TVL calculation
            main_account = info.get("router") or info.get("factory") or info.get("staking")
            if not main_account:
                continue
            
            # Get account info
            account_data = self._request(f"accounts/{main_account}")
            if not account_data:
                continue
            
            # Get token balances for TVL
            tokens_data = self._request(f"accounts/{main_account}/tokens")
            token_list = tokens_data.get("tokens", [])
            
            # Get actual account balance (no USD conversion without price oracle)
            hbar_balance = int(account_data.get("balance", {}).get("balance", 0)) / 100_000_000
            
            # Only count HBAR balance - no mock token values
            tvl = hbar_balance
            
            if tvl >= min_tvl:
                protocol = Protocol(
                    contract_id=main_account,
                    name=name,
                    type=info["type"],
                    tvl=tvl,
                    volume_24h=0,  # Real data would need event log analysis
                    users_24h=0,   # Real data would need transaction analysis  
                    pools=[],      # Real data would need factory event analysis
                    tokens=[t.get("token_id") for t in token_list[:5]],
                    created_at=parse_timestamp(account_data.get("created_timestamp"))
                )
                protocols.append(protocol)
        
        return sorted(protocols, key=lambda p: p.tvl, reverse=True)
    
    # ========== 2-6. TOKEN ANALYTICS ==========
    
    def get_top_tokens(self, limit: int = 50, sort_by: str = "supply") -> List[Token]:
        """Get top tokens by various metrics"""
        data = self._request("tokens", {"type": "FUNGIBLE_COMMON", "limit": limit})
        
        tokens = []
        for token_data in data.get("tokens", []):
            token = Token(
                token_id=token_data.get("token_id"),
                symbol=token_data.get("symbol", ""),
                name=token_data.get("name", ""),
                decimals=int(token_data.get("decimals", 8)),
                total_supply=int(token_data.get("total_supply", 0)),
                price=0,  # Real price data requires external price oracle
                tvl=0,    # Real TVL requires comprehensive holder analysis
                volume_24h=0,  # Real volume requires transfer analysis
                holders=0,     # Real holder count requires separate API calls
            )
            tokens.append(token)
        
        return tokens
    
    def get_token_info(self, token_id: str) -> Optional[Token]:
        """Get detailed information about a specific token"""
        data = self._request(f"tokens/{token_id}")
        if not data:
            return None
        
        return Token(
            token_id=token_id,
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            decimals=int(data.get("decimals", 8)),
            total_supply=int(data.get("total_supply", 0)),
            price=0,  # Real price requires external oracle
            tvl=0,    # Real TVL requires holder analysis
            volume_24h=0,  # Real volume requires transfer analysis 
            holders=0     # Real holder count requires balance queries
        )
    
    def get_token_transfers(self, token_id: str, limit: int = 100) -> List[Dict]:
        """Get recent token transfers"""
        data = self._request("transactions", {
            "transactiontype": "CRYPTOTRANSFER",
            "limit": limit
        })
        
        transfers = []
        for tx in data.get("transactions", []):
            for token_transfer in tx.get("token_transfers", []):
                if token_transfer.get("token_id") == token_id:
                    transfers.append({
                        "transaction_id": tx.get("transaction_id"),
                        "timestamp": parse_timestamp(tx.get("consensus_timestamp")),
                        "amount": token_transfer.get("amount"),
                        "account": token_transfer.get("account_id"),
                    })
        
        return transfers
    
    def get_token_holders(self, token_id: str, min_balance: int = 0) -> List[Dict]:
        """Get token holders (limited by API)"""
        # Note: Full holder list not available via REST API
        # This returns a simplified version
        data = self._request(f"tokens/{token_id}/balances", {"limit": 100})
        
        holders = []
        for balance in data.get("balances", []):
            amount = int(balance.get("balance", 0))
            if amount >= min_balance:
                holders.append({
                    "account": balance.get("account"),
                    "balance": amount
                })
        
        return holders
    
    def get_nft_collections(self, limit: int = 50) -> List[Dict]:
        """Get NFT collections"""
        data = self._request("tokens", {
            "type": "NON_FUNGIBLE_UNIQUE",
            "limit": limit
        })
        
        collections = []
        for token in data.get("tokens", []):
            collections.append({
                "token_id": token.get("token_id"),
                "name": token.get("name", ""),
                "symbol": token.get("symbol", ""),
                "total_supply": token.get("total_supply", 0),
                "created": parse_timestamp(token.get("created_timestamp"))
            })
        
        return collections
    
    # ========== 7-11. ACCOUNT ANALYTICS ==========
    
    def get_account_info(self, account_id: str) -> Dict:
        """Get comprehensive account information"""
        data = self._request(f"accounts/{account_id}")
        return data if data else {}
    
    def get_account_balance(self, account_id: str) -> float:
        """Get account HBAR balance"""
        data = self.get_account_info(account_id)
        if data:
            return int(data.get("balance", {}).get("balance", 0)) / 100_000_000
        return 0
    
    def get_account_tokens(self, account_id: str) -> List[Dict]:
        """Get all tokens held by an account"""
        data = self._request(f"accounts/{account_id}/tokens")
        return data.get("tokens", [])
    
    def get_account_nfts(self, account_id: str) -> List[Dict]:
        """Get all NFTs owned by an account"""
        data = self._request(f"accounts/{account_id}/nfts")
        return data.get("nfts", [])
    
    def get_account_transactions(
        self, 
        account_id: str, 
        limit: int = 100,
        transaction_type: Optional[str] = None
    ) -> List[Dict]:
        """Get account transaction history"""
        params = {"account.id": account_id, "limit": limit}
        if transaction_type:
            params["transactiontype"] = transaction_type
        
        data = self._request("transactions", params)
        return data.get("transactions", [])
    
    # ========== 12-16. WHALE & TRANSACTION TRACKING ==========
    
    def get_whale_transactions(
        self,
        threshold: float = 10000,
        window_minutes: int = 60,
        transaction_type: Optional[str] = None
    ) -> List[WhaleAlert]:
        """Get whale transactions above threshold"""
        data = self._request("transactions", {"limit": 100})
        
        alerts = []
        threshold_tinybars = int(threshold * 100_000_000)
        
        for tx in data.get("transactions", []):
            for transfer in tx.get("transfers", []):
                amount = abs(int(transfer.get("amount", 0)))
                if amount >= threshold_tinybars:
                    alert = WhaleAlert(
                        timestamp=parse_timestamp(tx.get("consensus_timestamp")),
                        type="transfer",
                        token="HBAR",
                        amount=amount,
                        value_usd=0,  # Real USD value requires price oracle
                        from_address=transfer.get("account", ""),
                        to_address="",
                        transaction_hash=tx.get("transaction_id", "")
                    )
                    alerts.append(alert)
        
        return sorted(alerts, key=lambda a: a.value_usd, reverse=True)
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Get most recent transactions on the network"""
        data = self._request("transactions", {"limit": limit})
        return data.get("transactions", [])
    
    def get_transaction_info(self, transaction_id: str) -> Dict:
        """Get detailed transaction information"""
        data = self._request(f"transactions/{transaction_id}")
        return data if data else {}
    
    def get_contract_results(self, contract_id: str, limit: int = 100) -> List[Dict]:
        """Get contract execution results"""
        data = self._request(f"contracts/{contract_id}/results", {"limit": limit})
        return data.get("results", [])
    
    def get_transaction_fees(self, transaction_id: str) -> Dict:
        """Get transaction fee breakdown"""
        tx = self.get_transaction_info(transaction_id)
        if tx:
            return {
                "node_fee": tx.get("node_fee", 0),
                "network_fee": tx.get("network_fee", 0),
                "service_fee": tx.get("service_fee", 0),
                "total": tx.get("charged_tx_fee", 0)
            }
        return {}
    
    # ========== 17-21. STAKING & REWARDS ==========
    
    def get_staking_info(self, account_id: str) -> Dict:
        """Get account staking information"""
        data = self.get_account_info(account_id)
        if data:
            return {
                "staked_node_id": data.get("staked_node_id"),
                "staked_account_id": data.get("staked_account_id"),
                "decline_reward": data.get("decline_reward", False),
                "stake_period_start": data.get("stake_period_start"),
                "pending_reward": data.get("pending_reward", 0)
            }
        return {}
    
    def get_node_stakes(self, node_id: int) -> Dict:
        """Get staking information for a specific node"""
        data = self._request(f"network/nodes/{node_id}")
        return data if data else {}
    
    def get_reward_rate(self) -> float:
        """Get current network reward rate"""
        data = self._request("network/stake")
        if data:
            total_stake = int(data.get("total_stake", 0))
            reward_rate = data.get("reward_rate", 0)
            return reward_rate
        return 0
    
    def get_staking_accounts(self, limit: int = 100) -> List[Dict]:
        """Get top staking accounts"""
        data = self._request("accounts", {
            "account.stakedaccountid": "gte:0",
            "limit": limit,
            "order": "desc"
        })
        return data.get("accounts", [])
    
    def calculate_staking_apr(self, staked_amount: float) -> float:
        """Calculate staking APR based on network reward rate"""
        reward_rate = self.get_reward_rate()
        if reward_rate > 0:
            # Convert daily rate to annual percentage
            apr = reward_rate * 365 * 100
            return apr
        return 0
    
    # ========== 22-26. NETWORK STATISTICS ==========
    
    def get_network_supply(self) -> Dict:
        """Get total network supply information"""
        data = self._request("network/supply")
        if data:
            return {
                "total_supply": int(data.get("total_supply", 0)) / 100_000_000,
                "circulating_supply": int(data.get("released_supply", 0)) / 100_000_000,
                "timestamp": parse_timestamp(data.get("timestamp"))
            }
        return {}
    
    def get_network_nodes(self) -> List[Dict]:
        """Get list of network nodes"""
        data = self._request("network/nodes")
        return data.get("nodes", [])
    
    def get_network_fees(self) -> Dict:
        """Get current network fee schedule"""
        data = self._request("network/fees")
        return data if data else {}
    
    def get_network_exchangerate(self) -> Dict:
        """Get HBAR to USD exchange rate"""
        data = self._request("network/exchangerate")
        if data:
            return {
                "current_rate": data.get("current_rate", {}),
                "next_rate": data.get("next_rate", {}),
                "timestamp": parse_timestamp(data.get("timestamp"))
            }
        return {}
    
    def get_network_statistics(self) -> Dict:
        """Get comprehensive network statistics"""
        supply = self.get_network_supply()
        nodes = self.get_network_nodes()
        
        return {
            "total_supply": supply.get("total_supply", 0),
            "circulating_supply": supply.get("circulating_supply", 0),
            "node_count": len(nodes),
            "active_accounts": 0,  # Would need to query
            "total_transactions": 0,  # Would need to query
        }
    
    # ========== 27-31. SMART CONTRACT ANALYTICS ==========
    
    def get_contract_info(self, contract_id: str) -> Dict:
        """Get smart contract information"""
        data = self._request(f"contracts/{contract_id}")
        return data if data else {}
    
    def get_contract_bytecode(self, contract_id: str) -> str:
        """Get contract bytecode"""
        data = self.get_contract_info(contract_id)
        return data.get("bytecode", "")
    
    def get_contract_state(self, contract_id: str) -> List[Dict]:
        """Get contract state"""
        data = self._request(f"contracts/{contract_id}/state")
        return data.get("state", [])
    
    def get_contract_logs(
        self, 
        contract_id: str, 
        limit: int = 100,
        topic0: Optional[str] = None
    ) -> List[Dict]:
        """Get contract event logs"""
        params = {"limit": limit}
        if topic0:
            params["topic0"] = topic0
        
        data = self._request(f"contracts/{contract_id}/results/logs", params)
        return data.get("logs", [])
    
    def get_contract_executions(self, contract_id: str, limit: int = 100) -> List[Dict]:
        """Get contract execution history"""
        return self.get_contract_results(contract_id, limit)
    
    # ========== 32-36. POOL & LIQUIDITY ANALYTICS ==========
    
    def get_pools(
        self,
        protocol_id: Optional[str] = None,
        min_tvl: float = 1000,
        pool_type: Optional[str] = None
    ) -> List[Pool]:
        """Get liquidity pools - requires contract event analysis for real data"""
        # Real pool data would need:
        # 1. Factory contract event logs for pool creation
        # 2. Pool contract state for reserves/TVL
        # 3. Transaction analysis for volume/fees
        # Returning empty list as no mock data should be provided
        return []
    
    def get_pool_transactions(self, pool_id: str, limit: int = 100) -> List[Dict]:
        """Get recent pool transactions - requires contract event analysis"""
        # Real pool transactions require contract event log analysis
        return []
    
    def calculate_impermanent_loss(
        self, 
        token_a_price_change: float,
        token_b_price_change: float
    ) -> float:
        """Calculate impermanent loss for a pool"""
        ratio_change = token_a_price_change / token_b_price_change
        il = 2 * (ratio_change ** 0.5) / (1 + ratio_change) - 1
        return abs(il) * 100
    
    def get_pool_apr(self, pool_id: str) -> float:
        """Get pool APR - requires fee and reward analysis"""
        # Real APR calculation requires fee collection and reward data analysis
        return 0
    
    def get_liquidity_providers(self, pool_id: str) -> List[Dict]:
        """Get liquidity providers - requires LP token analysis"""
        # Real LP data requires analyzing LP token holders
        return []
    
    # ========== 37-45. ADVANCED ANALYTICS ==========
    
    def get_defi_overview(self) -> Dict[str, Any]:
        """Get complete DeFi ecosystem overview"""
        protocols = self.get_protocols()
        tokens = self.get_top_tokens(limit=10)
        whales = self.get_whale_transactions(threshold=10000)
        supply = self.get_network_supply()
        
        total_tvl = sum(p.tvl for p in protocols)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tvl": total_tvl,
            "total_supply": supply.get("total_supply", 0),
            "circulating_supply": supply.get("circulating_supply", 0),
            "protocol_count": len(protocols),
            "top_protocols": [
                {"name": p.name, "tvl": p.tvl, "type": p.type}
                for p in protocols[:5]
            ],
            "top_tokens": [
                {"symbol": t.symbol, "name": t.name, "token_id": t.token_id}
                for t in tokens[:5]
            ],
            "whale_activity": {
                "count": len(whales),
                "total_value": sum(w.value_usd for w in whales),
                "largest": max(whales, key=lambda w: w.value_usd).value_usd if whales else 0
            },
            "market_health": self._calculate_market_health(protocols, whales)
        }
    
    def get_trending_tokens(self, window_hours: int = 24) -> List[Dict]:
        """Get trending tokens - requires transfer volume analysis"""
        # Real trending analysis requires tracking transfer volumes over time
        return []
    
    def get_new_tokens(self, hours: int = 24) -> List[Dict]:
        """Get newly created tokens"""
        # Real new token detection requires filtering by creation timestamp
        data = self._request("tokens", {"type": "FUNGIBLE_COMMON", "order": "desc", "limit": 100})
        
        new_tokens = []
        for token in data.get("tokens", []):
            # Only include tokens with creation timestamp if available
            if token.get("created_timestamp"):
                new_tokens.append({
                    "token_id": token.get("token_id"),
                    "symbol": token.get("symbol", ""),
                    "name": token.get("name", ""),
                    "created": parse_timestamp(token.get("created_timestamp"))
                })
        
        return new_tokens
    
    def get_top_traders(self, limit: int = 10) -> List[Dict]:
        """Get top traders - requires transaction volume analysis"""
        # Real trader ranking requires analyzing transaction volumes per account
        return []
    
    def get_arbitrage_opportunities(self) -> List[Dict]:
        """Detect arbitrage opportunities - requires price comparison"""
        # Real arbitrage detection requires comparing prices across DEXs
        return []
    
    def get_liquidation_events(self, protocol_id: str) -> List[Dict]:
        """Get liquidation events - requires contract event analysis"""
        # Real liquidation data requires analyzing lending protocol events
        return []
    
    def get_governance_proposals(self, protocol_id: str) -> List[Dict]:
        """Get governance proposals - requires governance contract analysis"""
        # Real governance data requires analyzing governance contract state
        return []
    
    def get_protocol_revenue(self, protocol_id: str, days: int = 30) -> float:
        """Calculate protocol revenue - requires fee analysis"""
        # Real revenue calculation requires analyzing fee collection events
        return 0
    
    def get_user_positions(self, account_id: str) -> Dict:
        """Get all DeFi positions for a user"""
        tokens = self.get_account_tokens(account_id)
        balance = self.get_account_balance(account_id)
        
        return {
            "account": account_id,
            "hbar_balance": balance,
            "token_count": len(tokens),
            "tokens": tokens[:10],
            "estimated_value": 0  # Real value requires price oracle
        }
    
    # ========== RISK & ANALYTICS ==========
    
    def get_risk_metrics(
        self,
        protocol_id: str,
        include_liquidations: bool = True
    ) -> RiskMetrics:
        """Get comprehensive risk metrics for a protocol"""
        # Real risk metrics require comprehensive data analysis
        return RiskMetrics(
            protocol_id=protocol_id,
            tvl_change_24h=0,
            volume_change_24h=0,
            concentration_risk=0,
            liquidity_risk=0,
            smart_contract_risk=0,
            overall_risk="unknown"
        )
    
    def calculate_portfolio_risk(self, positions: List[Dict]) -> float:
        """Calculate portfolio risk - requires complex risk modeling"""
        # Real risk calculation requires comprehensive analysis
        return 0
    
    # ========== HISTORICAL DATA ==========
    
    def get_tvl_history(
        self,
        protocol_id: Optional[str] = None,
        days: int = 7,
        interval: str = "daily"
    ) -> pd.DataFrame:
        """Get historical TVL data"""
        protocols = self.get_protocols()
        
        if protocol_id:
            protocols = [p for p in protocols if p.contract_id == protocol_id]
        
        total_tvl = sum(p.tvl for p in protocols)
        
        # Real historical TVL requires time-series data collection
        # Returning empty DataFrame as no mock data should be provided
        return pd.DataFrame(columns=["timestamp", "tvl"])
    
    def get_volume_history(
        self,
        protocol_id: str,
        days: int = 7
    ) -> pd.DataFrame:
        """Get historical volume data"""
        # Real volume history requires transaction analysis over time
        # Returning empty DataFrame as no mock data should be provided
        return pd.DataFrame(columns=["timestamp", "volume"])
    
    # ========== YIELD FARMING ==========
    
    def get_best_yields(
        self,
        min_apy: float = 5.0,
        max_risk: float = 50.0,
        limit: int = 20
    ) -> pd.DataFrame:
        """Get best yield opportunities"""
        pools = self.get_pools()
        
        # Real yield opportunities require pool data analysis
        # Since pools are empty (no mock data), returning empty DataFrame
        return pd.DataFrame(columns=["pool", "protocol", "type", "apy", "tvl", "risk_score", "tokens"])
    
    def get_farming_positions(self, account_id: str) -> List[Dict]:
        """Get farming positions - requires LP token analysis"""
        # Real farming positions require analyzing LP token holdings
        return []
    
    # ========== SEARCH & DISCOVERY ==========
    
    def search_protocols(
        self,
        query: str,
        search_type: str = "name"
    ) -> List[Protocol]:
        """Search for protocols"""
        all_protocols = self.get_protocols()
        
        results = []
        query_lower = query.lower()
        
        for protocol in all_protocols:
            if search_type == "name" and query_lower in protocol.name.lower():
                results.append(protocol)
            elif search_type == "address" and query_lower in protocol.contract_id.lower():
                results.append(protocol)
        
        return results
    
    def search_tokens(self, query: str) -> List[Token]:
        """Search for tokens by name or symbol"""
        tokens = self.get_top_tokens(limit=100)
        query_lower = query.lower()
        
        results = []
        for token in tokens:
            if (query_lower in token.symbol.lower() or 
                query_lower in token.name.lower()):
                results.append(token)
        
        return results
    
    def search_accounts(self, query: str) -> Dict:
        """Search for account information"""
        if query.startswith("0.0."):
            return self.get_account_info(query)
        return {}
    
    # ========== UTILITY METHODS ==========
    
    def _calculate_market_health(self, protocols: List[Protocol], whales: List[WhaleAlert]) -> str:
        """Calculate overall market health indicator"""
        if not protocols:
            return "inactive"
        
        total_tvl = sum(p.tvl for p in protocols)
        whale_activity = len(whales)
        
        if total_tvl > 1_000_000 and whale_activity > 10:
            return "very_active"
        elif total_tvl > 100_000 or whale_activity > 5:
            return "active"
        elif whale_activity > 0:
            return "moderate"
        else:
            return "quiet"
    
    def validate_account_id(self, account_id: str) -> bool:
        """Validate Hedera account ID format"""
        import re
        pattern = r'^0\.0\.\d+$'
        return bool(re.match(pattern, account_id))
    
    def format_hbar(self, tinybars: int) -> str:
        """Format tinybars to HBAR string"""
        hbar = tinybars / 100_000_000
        return f"{hbar:,.8f} HBAR"
    
    def get_hbar_price(self) -> float:
        """Get current HBAR price - requires external price oracle"""
        # Real price data requires connection to price oracle or exchange API
        return 0
    
    def clear_cache(self):
        """Clear the request cache"""
        self.cache = {}