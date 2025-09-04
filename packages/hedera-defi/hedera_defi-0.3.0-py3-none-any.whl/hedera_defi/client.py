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
            "name": "SaucerSwap",
        },
        "HeliSwap": {
            "router": "0.0.1237181",
            "factory": "0.0.223960",
            "type": "dex",
            "name": "HeliSwap",
        },
        "Pangolin": {
            "router": "0.0.1242116",
            "factory": "0.0.798819",
            "type": "dex",
            "name": "Pangolin",
        },
        "Stader": {"staking": "0.0.3902492", "type": "staking", "name": "Stader"},
        "HSuite": {"router": "0.0.2830828", "type": "dex", "name": "HSuite"},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://mainnet-public.mirrornode.hedera.com/api/v1",
        cache_ttl: int = 60,
        bonzo_api: str = "https://mainnet-data.bonzo.finance",
        saucerswap_api: str = "https://server.saucerswap.finance/api/public",
    ):
        """
        Initialize Hedera DeFi client

        Args:
            api_key: Optional API key (not needed for public APIs)
            endpoint: Mirror Node REST API endpoint
            cache_ttl: Cache time-to-live in seconds
            bonzo_api: Bonzo Finance API endpoint
            saucerswap_api: SaucerSwap API endpoint
        """
        self.endpoint = endpoint
        self.bonzo_api = bonzo_api
        self.saucerswap_api = saucerswap_api
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.call_counts = {}  # Track API call frequency

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ========== CORE REQUEST METHOD ==========

    def _request(self, path: str, params: Optional[Dict] = None) -> Dict:
        """Execute REST API request with caching and robust error handling"""
        if not path:
            raise ValueError("Path cannot be empty")

        cache_key = f"{path}:{str(params)}"

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data

        try:
            # Execute request
            url = f"{self.endpoint}/{path}"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    # Cache result
                    self.cache[cache_key] = (data, time.time())
                    return data
                except ValueError as e:
                    print(f"Warning: Invalid JSON response from {url}: {e}")
                    return {}
            elif response.status_code == 429:
                print(
                    f"Warning: Rate limited by Mirror Node API. Status: {response.status_code}"
                )
                return {}
            elif response.status_code >= 400:
                print(f"Warning: API error {response.status_code} for {url}")
                return {}
            else:
                print(f"Warning: Unexpected status {response.status_code} from {url}")
                return {}

        except requests.exceptions.Timeout:
            print(f"Warning: Request timeout for {url}")
            return {}
        except requests.exceptions.ConnectionError:
            print(f"Warning: Connection error for {url}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Warning: Request failed for {url}: {e}")
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
            main_account = (
                info.get("router") or info.get("factory") or info.get("staking")
            )
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
            hbar_balance = (
                int(account_data.get("balance", {}).get("balance", 0)) / 100_000_000
            )

            # Only count HBAR balance - no mock token values
            tvl = hbar_balance

            if tvl >= min_tvl:
                protocol = Protocol(
                    contract_id=main_account,
                    name=name,
                    type=info["type"],
                    tvl=tvl,
                    volume_24h=0,  # Real data would need event log analysis
                    users_24h=0,  # Real data would need transaction analysis
                    pools=[],  # Real data would need factory event analysis
                    tokens=[t.get("token_id") for t in token_list[:5]],
                    created_at=parse_timestamp(account_data.get("created_timestamp")),
                )
                protocols.append(protocol)

        return sorted(protocols, key=lambda p: p.tvl, reverse=True)

    # ========== 2-6. TOKEN ANALYTICS ==========

    def get_top_tokens(self, limit: int = 50, sort_by: str = "supply") -> List[Token]:
        """Get top tokens from Mirror Node API with SaucerSwap price data"""
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        if sort_by not in ["supply", "created_timestamp"]:
            sort_by = "supply"  # Default fallback
        data = self._request("tokens", {"type": "FUNGIBLE_COMMON", "limit": limit})

        # Get SaucerSwap token prices for price data
        saucer_tokens = {t["id"]: t for t in self.get_saucerswap_tokens()}

        tokens = []
        for token_data in data.get("tokens", []):
            token_id = token_data.get("token_id")
            saucer_data = saucer_tokens.get(token_id, {})
            
            token = Token(
                token_id=token_id,
                symbol=token_data.get("symbol", ""),
                name=token_data.get("name", ""),
                decimals=int(token_data.get("decimals", 8)),
                total_supply=int(token_data.get("total_supply", 0)),
                price=saucer_data.get("priceUsd", 0),  # Real price from SaucerSwap
                tvl=0,  # Real TVL requires comprehensive holder analysis
                volume_24h=0,  # Real volume requires transfer analysis
                holders=0,  # Real holder count requires separate API calls
            )
            tokens.append(token)

        return tokens

    def get_token_info(self, token_id: str) -> Optional[Token]:
        """Get detailed information about a specific token"""
        if not token_id or not token_id.startswith("0.0."):
            raise ValueError(f"Invalid token ID format: {token_id}")

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
            tvl=0,  # Real TVL requires holder analysis
            volume_24h=0,  # Real volume requires transfer analysis
            holders=0,  # Real holder count requires balance queries
        )

    def get_token_transfers(self, token_id: str, limit: int = 100) -> List[Dict]:
        """Get recent token transfers"""
        if not token_id or not token_id.startswith("0.0."):
            raise ValueError(f"Invalid token ID format: {token_id}")
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")

        data = self._request(
            "transactions", {"transactiontype": "CRYPTOTRANSFER", "limit": limit}
        )

        transfers = []
        for tx in data.get("transactions", []):
            for token_transfer in tx.get("token_transfers", []):
                if token_transfer.get("token_id") == token_id:
                    transfers.append(
                        {
                            "transaction_id": tx.get("transaction_id"),
                            "timestamp": parse_timestamp(tx.get("consensus_timestamp")),
                            "amount": token_transfer.get("amount"),
                            "account": token_transfer.get("account_id"),
                        }
                    )

        return transfers

    def get_token_holders(self, token_id: str, min_balance: int = 0) -> List[Dict]:
        """Get token holders (limited by Mirror Node API capabilities)"""
        if not token_id or not token_id.startswith("0.0."):
            raise ValueError(f"Invalid token ID format: {token_id}")
        if min_balance < 0:
            raise ValueError("Minimum balance must be non-negative")

        # Note: Full holder list not available via REST API
        data = self._request(f"tokens/{token_id}/balances", {"limit": 100})

        holders = []
        for balance in data.get("balances", []):
            amount = int(balance.get("balance", 0))
            if amount >= min_balance:
                holders.append({"account": balance.get("account"), "balance": amount})

        return holders

    def get_nft_collections(self, limit: int = 50) -> List[Dict]:
        """Get NFT collections"""
        data = self._request("tokens", {"type": "NON_FUNGIBLE_UNIQUE", "limit": limit})

        collections = []
        for token in data.get("tokens", []):
            collections.append(
                {
                    "token_id": token.get("token_id"),
                    "name": token.get("name", ""),
                    "symbol": token.get("symbol", ""),
                    "total_supply": token.get("total_supply", 0),
                    "created": parse_timestamp(token.get("created_timestamp")),
                }
            )

        return collections

    # ========== 7-11. ACCOUNT ANALYTICS ==========

    def get_account_info(self, account_id: str) -> Dict:
        """Get comprehensive account information"""
        if not self.validate_account_id(account_id):
            raise ValueError(f"Invalid account ID format: {account_id}")

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
        self, account_id: str, limit: int = 100, transaction_type: Optional[str] = None
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
        transaction_type: Optional[str] = None,
    ) -> List[WhaleAlert]:
        """Get whale transactions above threshold (HBAR amount only)"""
        if threshold <= 0:
            raise ValueError("Threshold must be positive")
        if window_minutes <= 0:
            raise ValueError("Window minutes must be positive")
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
                        value_usd=0,  # USD value requires external price oracle
                        from_address=transfer.get("account", ""),
                        to_address="",  # To address not available in this API response
                        transaction_hash=tx.get("transaction_id", ""),
                    )
                    alerts.append(alert)

        # Sort by HBAR amount since USD values are not available
        return sorted(alerts, key=lambda a: a.amount, reverse=True)

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
                "total": tx.get("charged_tx_fee", 0),
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
                "pending_reward": data.get("pending_reward", 0),
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
        data = self._request(
            "accounts",
            {"account.stakedaccountid": "gte:0", "limit": limit, "order": "desc"},
        )
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
                "timestamp": parse_timestamp(data.get("timestamp")),
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
                "timestamp": parse_timestamp(data.get("timestamp")),
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
        if not self.validate_account_id(contract_id):
            raise ValueError(f"Invalid contract ID format: {contract_id}")

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
        self, contract_id: str, limit: int = 100, topic0: Optional[str] = None
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
        pool_type: Optional[str] = None,
    ) -> List[Pool]:
        """Get liquidity pools from SaucerSwap and other protocols"""
        pools = []
        
        # Get SaucerSwap pools with real data
        saucer_pools = self.get_saucerswap_pools()
        
        for pool_data in saucer_pools:
            tvl = self.get_saucerswap_pool_tvl(pool_data.get("id", 0))
            
            if tvl >= min_tvl:
                pool = Pool(
                    contract_id=pool_data.get("contractId", ""),
                    name=f"{pool_data.get('tokenA', {}).get('symbol', '')}-{pool_data.get('tokenB', {}).get('symbol', '')}",
                    type="v3",  # SaucerSwap is Uniswap V3 style
                    tvl=tvl,
                    volume_24h=0,  # Would need historical data
                    fee=pool_data.get("fee", 0) / 10000,  # Convert from basis points
                    apy=0,  # Would need fee analysis
                    tokens=[
                        pool_data.get("tokenA", {}).get("id", ""),
                        pool_data.get("tokenB", {}).get("id", "")
                    ]
                )
                pools.append(pool)
        
        return sorted(pools, key=lambda p: p.tvl, reverse=True)

    def get_pool_transactions(self, pool_id: str, limit: int = 100) -> List[Dict]:
        """Get recent pool transactions - requires contract event analysis"""
        # Real pool transactions require contract event log analysis
        return []

    def calculate_impermanent_loss(
        self, token_a_price_change: float, token_b_price_change: float
    ) -> float:
        """Calculate impermanent loss for a pool"""
        if token_a_price_change <= 0 or token_b_price_change <= 0:
            raise ValueError("Price changes must be positive")

        ratio_change = token_a_price_change / token_b_price_change
        il = 2 * (ratio_change**0.5) / (1 + ratio_change) - 1
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
                {"name": p.name, "tvl": p.tvl, "type": p.type} for p in protocols[:5]
            ],
            "top_tokens": [
                {"symbol": t.symbol, "name": t.name, "token_id": t.token_id}
                for t in tokens[:5]
            ],
            "whale_activity": {
                "count": len(whales),
                "total_value_hbar": sum(w.amount for w in whales) / 100_000_000,
                "largest_hbar": (
                    max(whales, key=lambda w: w.amount).amount / 100_000_000
                    if whales
                    else 0
                ),
            },
            "market_health": self._calculate_market_health(protocols, whales),
        }

    def get_trending_tokens(self, window_hours: int = 24) -> List[Dict]:
        """Get trending tokens - requires transfer volume analysis"""
        # Real trending analysis requires tracking transfer volumes over time
        return []

    def get_new_tokens(self, hours: int = 24) -> List[Dict]:
        """Get newly created tokens"""
        # Real new token detection requires filtering by creation timestamp
        data = self._request(
            "tokens", {"type": "FUNGIBLE_COMMON", "order": "desc", "limit": 100}
        )

        new_tokens = []
        for token in data.get("tokens", []):
            # Only include tokens with creation timestamp if available
            if token.get("created_timestamp"):
                new_tokens.append(
                    {
                        "token_id": token.get("token_id"),
                        "symbol": token.get("symbol", ""),
                        "name": token.get("name", ""),
                        "created": parse_timestamp(token.get("created_timestamp")),
                    }
                )

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
            "hbar_value": balance,  # HBAR value without USD conversion
            "estimated_usd_value": 0,  # USD value requires external price oracle
        }

    # ========== RISK & ANALYTICS ==========

    def get_risk_metrics(
        self, protocol_id: str, include_liquidations: bool = True
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
            overall_risk="unknown",
        )

    def calculate_portfolio_risk(self, positions: List[Dict]) -> float:
        """Calculate portfolio risk - requires complex risk modeling"""
        if not positions:
            return 0
        # Real risk calculation requires comprehensive market data analysis
        # This would need position sizes, correlations, volatility data, etc.
        return 0

    # ========== HISTORICAL DATA ==========

    def get_tvl_history(
        self, protocol_id: Optional[str] = None, days: int = 7, interval: str = "daily"
    ) -> pd.DataFrame:
        """Get historical TVL data"""
        protocols = self.get_protocols()

        if protocol_id:
            protocols = [p for p in protocols if p.contract_id == protocol_id]

        total_tvl = sum(p.tvl for p in protocols)

        # Real historical TVL requires time-series data collection
        # Returning empty DataFrame as no mock data should be provided
        return pd.DataFrame(columns=["timestamp", "tvl"])

    def get_volume_history(self, protocol_id: str, days: int = 7) -> pd.DataFrame:
        """Get historical volume data"""
        # Real volume history requires transaction analysis over time
        # Returning empty DataFrame as no mock data should be provided
        return pd.DataFrame(columns=["timestamp", "volume"])

    # ========== YIELD FARMING ==========

    def get_best_yields(
        self, min_apy: float = 5.0, max_risk: float = 50.0, limit: int = 20
    ) -> pd.DataFrame:
        """Get best yield opportunities from SaucerSwap and other protocols"""
        # Combine SaucerSwap pools with Bonzo Finance lending rates
        yield_opportunities = []
        
        # Add Bonzo lending opportunities
        bonzo_rates = self.get_bonzo_best_lending_rates(min_apy=min_apy)
        for rate in bonzo_rates[:limit//2]:
            yield_opportunities.append({
                "pool": rate["token"],
                "protocol": "Bonzo Finance", 
                "type": "lending",
                "apy": rate["supply_apy"],
                "tvl": 0,  # Would need to parse USD value
                "risk_score": {"Low": 20, "Medium": 50, "High": 80}.get(rate["risk_level"], 50),
                "tokens": [rate["token"]]
            })
        
        # Add SaucerSwap pool opportunities (using fee tiers as proxy for yield)
        saucer_pools = self.get_saucerswap_top_pools(limit//2)
        for pool in saucer_pools:
            fee_apy = pool.get("fee", 0) * 100  # Rough APY estimate from fees
            if fee_apy >= min_apy:
                yield_opportunities.append({
                    "pool": f"{pool.get('tokenA', {}).get('symbol', '')}-{pool.get('tokenB', {}).get('symbol', '')}",
                    "protocol": "SaucerSwap",
                    "type": "liquidity",
                    "apy": fee_apy,
                    "tvl": pool.get("tvl_usd", 0),
                    "risk_score": 30,  # Medium risk for LP
                    "tokens": [
                        pool.get("tokenA", {}).get("symbol", ""),
                        pool.get("tokenB", {}).get("symbol", "")
                    ]
                })
        
        # Filter by max risk and sort by APY
        filtered_yields = [y for y in yield_opportunities if y["risk_score"] <= max_risk]
        sorted_yields = sorted(filtered_yields, key=lambda y: y["apy"], reverse=True)
        
        return pd.DataFrame(sorted_yields[:limit])

    def get_farming_positions(self, account_id: str) -> List[Dict]:
        """Get farming positions - requires LP token analysis"""
        # Real farming positions require analyzing LP token holdings
        return []

    # ========== SEARCH & DISCOVERY ==========

    def search_protocols(self, query: str, search_type: str = "name") -> List[Protocol]:
        """Search for protocols"""
        all_protocols = self.get_protocols()

        results = []
        query_lower = query.lower()

        for protocol in all_protocols:
            if search_type == "name" and query_lower in protocol.name.lower():
                results.append(protocol)
            elif (
                search_type == "address" and query_lower in protocol.contract_id.lower()
            ):
                results.append(protocol)

        return results

    def search_tokens(self, query: str) -> List[Token]:
        """Search for tokens by name or symbol"""
        tokens = self.get_top_tokens(limit=100)
        query_lower = query.lower()

        results = []
        for token in tokens:
            if query_lower in token.symbol.lower() or query_lower in token.name.lower():
                results.append(token)

        return results

    def search_accounts(self, query: str) -> Dict:
        """Search for account information"""
        if query.startswith("0.0."):
            return self.get_account_info(query)
        return {}

    # ========== UTILITY METHODS ==========

    def _calculate_market_health(
        self, protocols: List[Protocol], whales: List[WhaleAlert]
    ) -> str:
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

        pattern = r"^0\.0\.\d+$"
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
    
    def show_call_statistics(self) -> Dict:
        """Show API call statistics to identify performance bottlenecks"""
        print("\n📊 API Call Statistics:")
        for method, count in sorted(self.call_counts.items(), key=lambda x: x[1], reverse=True):
            status = "🔥 EXCESSIVE" if count > 10 else "⚠️ HIGH" if count > 5 else "✅ OK"
            print(f"   {status} {method}: {count} calls")
        
        return {
            "call_counts": self.call_counts,
            "total_calls": sum(self.call_counts.values()),
            "unique_methods": len(self.call_counts),
            "excessive_methods": [k for k, v in self.call_counts.items() if v > 10]
        }
    
    def reset_call_counts(self):
        """Reset API call statistics for clean testing"""
        self.call_counts = {}
        print("🔄 API call statistics reset")

    # ========== BONZO FINANCE API INTEGRATION ==========

    def _bonzo_request(self, path: str) -> Dict:
        """Execute Bonzo Finance API request with caching"""
        cache_key = f"bonzo:{path}"
        request_start = time.time()

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                print(f"   💾 Bonzo cache hit for {path} ({time.time() - request_start:.3f}s)")
                return cached_data

        try:
            # Execute request to Bonzo Finance API
            url = f"{self.bonzo_api}/{path}"
            print(f"   🏦 Bonzo API call: {path}")
            
            # Bonzo Finance requires specific headers for CORS
            headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://app.bonzo.finance",
                "Referer": "https://app.bonzo.finance/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }
            
            network_start = time.time()
            response = self.session.get(url, headers=headers, timeout=30)
            network_time = time.time() - network_start

            if response.status_code == 200:
                try:
                    parse_start = time.time()
                    data = response.json()
                    parse_time = time.time() - parse_start
                    
                    # Cache result
                    self.cache[cache_key] = (data, time.time())
                    
                    total_time = time.time() - request_start
                    data_size = len(str(data))
                    print(f"   ✅ Bonzo {path} completed in {total_time:.3f}s (network: {network_time:.3f}s, parse: {parse_time:.3f}s, size: {data_size:,} chars)")
                    return data
                except ValueError as e:
                    print(f"Warning: Invalid JSON from Bonzo API {url}: {e}")
                    return {}
            else:
                print(f"Warning: Bonzo API error {response.status_code} for {url} after {time.time() - request_start:.3f}s")
                return {}

        except requests.exceptions.Timeout:
            print(f"Warning: Bonzo API timeout for {url} after {time.time() - request_start:.3f}s")
            return {}
        except requests.exceptions.ConnectionError:
            print(f"Warning: Bonzo API connection error for {url}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Warning: Bonzo API request failed for {url}: {e}")
            return {}

    def get_bonzo_markets(self) -> Dict:
        """Get complete Bonzo Finance market data"""
        self.call_counts["get_bonzo_markets"] = self.call_counts.get("get_bonzo_markets", 0) + 1
        if self.call_counts["get_bonzo_markets"] > 5:
            print(f"   ⚠️  WARNING: get_bonzo_markets called {self.call_counts['get_bonzo_markets']} times!")
        print(f"   🏦 Fetching Bonzo markets data... (call #{self.call_counts['get_bonzo_markets']})")
        markets = self._bonzo_request("Market")
        if markets:
            reserves_count = len(markets.get("reserves", []))
            tvl_str = markets.get("total_market_supplied", {}).get("usd_display", "$0")
            print(f"   💵 Bonzo markets: {reserves_count} reserves, TVL: {tvl_str}")
        return markets

    def get_bonzo_total_markets(self, cached_data: Optional[Dict] = None) -> Dict:
        """Get Bonzo Finance total market statistics"""
        data = cached_data or self.get_bonzo_markets()
        if data:
            return {
                "chain_id": data.get("chain_id"),
                "network_name": data.get("network_name"),
                "total_market_supplied": data.get("total_market_supplied", {}),
                "total_market_borrowed": data.get("total_market_borrowed", {}),
                "total_market_liquidity": data.get("total_market_liquidity", {}),
                "total_market_reserve": data.get("total_market_reserve", {}),
                "timestamp": data.get("timestamp"),
                "total_reserves": len(data.get("reserves", [])),
            }
        return {}

    def get_bonzo_reserves(self, cached_data: Optional[Dict] = None) -> List[Dict]:
        """Get all Bonzo Finance lending reserves"""
        data = cached_data or self.get_bonzo_markets()
        return data.get("reserves", [])

    def get_bonzo_reserve(self, token_symbol: str) -> Dict:
        """Get specific Bonzo Finance reserve by token symbol"""
        reserves = self.get_bonzo_reserves()
        for reserve in reserves:
            if reserve.get("symbol", "").upper() == token_symbol.upper():
                return reserve
        return {}

    def get_bonzo_best_lending_rates(self, min_apy: float = 0) -> List[Dict]:
        """Get best lending rates from Bonzo Finance"""
        reserves = self.get_bonzo_reserves()

        good_rates = []
        for reserve in reserves:
            supply_apy = reserve.get("supply_apy", 0)
            if supply_apy >= min_apy and reserve.get("active", False):
                good_rates.append(
                    {
                        "token": reserve["symbol"],
                        "supply_apy": supply_apy,
                        "borrow_apy": reserve.get("variable_borrow_apy", 0),
                        "utilization_rate": reserve.get("utilization_rate", 0),
                        "available_liquidity": reserve.get(
                            "available_liquidity", {}
                        ).get("usd_display", "0"),
                        "ltv": reserve.get("ltv", 0),
                        "liquidation_threshold": reserve.get(
                            "liquidation_threshold", 0
                        ),
                        "risk_level": self._assess_bonzo_risk(reserve),
                    }
                )

        # Sort by supply APY descending
        return sorted(good_rates, key=lambda x: x["supply_apy"], reverse=True)

    def get_bonzo_borrowing_rates(self) -> List[Dict]:
        """Get borrowing rates from Bonzo Finance"""
        reserves = self.get_bonzo_reserves()

        borrowing_options = []
        for reserve in reserves:
            if reserve.get("variable_borrowing_enabled", False) and reserve.get(
                "active", False
            ):
                borrowing_options.append(
                    {
                        "token": reserve["symbol"],
                        "variable_borrow_apy": reserve.get("variable_borrow_apy", 0),
                        "stable_borrow_apy": reserve.get("stable_borrow_apy", 0),
                        "utilization_rate": reserve.get("utilization_rate", 0),
                        "ltv": reserve.get("ltv", 0),
                        "liquidation_threshold": reserve.get(
                            "liquidation_threshold", 0
                        ),
                        "liquidation_bonus": reserve.get("liquidation_bonus", 0),
                        "available_to_borrow": reserve.get(
                            "total_borrowable_liquidity", {}
                        ).get("usd_display", "0"),
                    }
                )

        # Sort by borrow APY ascending (lower is better for borrowing)
        return sorted(borrowing_options, key=lambda x: x["variable_borrow_apy"])

    def _assess_bonzo_risk(self, reserve: Dict) -> str:
        """Assess risk level for a Bonzo Finance reserve"""
        utilization = reserve.get("utilization_rate", 0)
        ltv = reserve.get("ltv", 0)
        liquidation_threshold = reserve.get("liquidation_threshold", 0)

        # Risk scoring based on multiple factors
        risk_score = 0

        # High utilization increases risk
        if utilization > 90:
            risk_score += 40
        elif utilization > 80:
            risk_score += 30
        elif utilization > 70:
            risk_score += 20

        # High LTV increases risk
        if ltv > 0.8:
            risk_score += 30
        elif ltv > 0.6:
            risk_score += 20
        elif ltv > 0.4:
            risk_score += 10

        # Low liquidation threshold increases risk
        if liquidation_threshold < 0.6:
            risk_score += 20
        elif liquidation_threshold < 0.7:
            risk_score += 10

        if risk_score >= 60:
            return "High"
        elif risk_score >= 30:
            return "Medium"
        else:
            return "Low"

    # ========== SAUCERSWAP API INTEGRATION ==========

    def _saucerswap_request(self, path: str) -> Dict:
        """Execute SaucerSwap API request with caching"""
        cache_key = f"saucer:{path}"
        request_start = time.time()

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                print(f"   💾 SaucerSwap cache hit for {path} ({time.time() - request_start:.3f}s)")
                return cached_data

        try:
            # Execute request to SaucerSwap API with required headers
            url = f"{self.saucerswap_api}/{path}"
            print(f"   🌐 SaucerSwap API call: {path}")
            
            # SaucerSwap requires specific headers for CORS
            headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9", 
                "Origin": "https://www.saucerswap.finance",
                "Referer": "https://www.saucerswap.finance/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }
            
            network_start = time.time()
            response = self.session.get(url, headers=headers, timeout=30)
            network_time = time.time() - network_start

            if response.status_code == 200:
                try:
                    parse_start = time.time()
                    data = response.json()
                    parse_time = time.time() - parse_start
                    
                    # Cache result
                    self.cache[cache_key] = (data, time.time())
                    
                    total_time = time.time() - request_start
                    print(f"   ✅ SaucerSwap {path} completed in {total_time:.3f}s (network: {network_time:.3f}s, parse: {parse_time:.3f}s)")
                    return data
                except ValueError as e:
                    print(f"Warning: Invalid JSON from SaucerSwap API {url}: {e}")
                    return {}
            elif response.status_code == 304:
                print(f"Warning: SaucerSwap API not modified (304) for {url}")
                return {}
            else:
                print(f"Warning: SaucerSwap API error {response.status_code} for {url}")
                return {}

        except requests.exceptions.Timeout:
            print(f"Warning: SaucerSwap API timeout for {url} after {time.time() - request_start:.3f}s")
            return {}
        except requests.exceptions.ConnectionError:
            print(f"Warning: SaucerSwap API connection error for {url}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Warning: SaucerSwap API request failed for {url}: {e}")
            return {}

    def get_saucerswap_pools(self) -> List[Dict]:
        """Get all SaucerSwap liquidity pools"""
        self.call_counts["get_saucerswap_pools"] = self.call_counts.get("get_saucerswap_pools", 0) + 1
        if self.call_counts["get_saucerswap_pools"] > 5:
            print(f"   ⚠️  WARNING: get_saucerswap_pools called {self.call_counts['get_saucerswap_pools']} times!")
        print(f"   🏊 Fetching SaucerSwap pools... (call #{self.call_counts['get_saucerswap_pools']})")
        pools = self._saucerswap_request("pools")
        print(f"   📊 Found {len(pools)} SaucerSwap pools")
        return pools

    def get_saucerswap_tokens(self) -> List[Dict]:
        """Get all SaucerSwap tokens with price data"""
        self.call_counts["get_saucerswap_tokens"] = self.call_counts.get("get_saucerswap_tokens", 0) + 1
        if self.call_counts["get_saucerswap_tokens"] > 5:
            print(f"   ⚠️  WARNING: get_saucerswap_tokens called {self.call_counts['get_saucerswap_tokens']} times!")
        print(f"   🪙 Fetching SaucerSwap tokens... (call #{self.call_counts['get_saucerswap_tokens']})")
        tokens = self._saucerswap_request("tokens")
        print(f"   📈 Found {len(tokens)} SaucerSwap tokens with price data")
        return tokens

    def get_saucerswap_pool_by_id(self, pool_id: int) -> Dict:
        """Get specific SaucerSwap pool by ID"""
        pools = self.get_saucerswap_pools()
        for pool in pools:
            if pool.get("id") == pool_id:
                return pool
        return {}

    def get_saucerswap_token_by_id(self, token_id: str) -> Dict:
        """Get SaucerSwap token data by token ID from pools"""
        tokens = self.get_saucerswap_tokens()
        for token in tokens:
            if token.get("id") == token_id:
                return token
        return {}

    def get_saucerswap_token_price(self, token_id: str) -> float:
        """Get token price in USD from SaucerSwap"""
        token = self.get_saucerswap_token_by_id(token_id)
        return token.get("priceUsd", 0.0)

    def get_saucerswap_pool_tvl(self, pool_id: int) -> float:
        """Calculate pool TVL in USD from SaucerSwap data"""
        pool = self.get_saucerswap_pool_by_id(pool_id)
        if not pool:
            return 0.0

        token_a = pool.get("tokenA", {})
        token_b = pool.get("tokenB", {})
        amount_a = int(pool.get("amountA", 0))
        amount_b = int(pool.get("amountB", 0))

        # Calculate TVL using token prices and amounts
        decimals_a = token_a.get("decimals", 8)
        decimals_b = token_b.get("decimals", 8)
        price_a = token_a.get("priceUsd", 0)
        price_b = token_b.get("priceUsd", 0)

        value_a = (amount_a / (10**decimals_a)) * price_a
        value_b = (amount_b / (10**decimals_b)) * price_b

        return value_a + value_b

    def get_saucerswap_top_pools(self, limit: int = 10) -> List[Dict]:
        """Get top SaucerSwap pools by TVL - OPTIMIZED to avoid 2000+ TVL calculations"""
        print(f"   🏊 Getting top {limit} pools (optimized method)...")
        start_time = time.time()
        
        pools = self.get_saucerswap_pools()
        tokens = self.get_saucerswap_tokens()
        
        # Create price lookup for faster TVL calculation
        token_prices = {t.get("id"): t.get("priceUsd", 0) for t in tokens}
        
        # Calculate TVL efficiently using pre-fetched token prices
        pool_tvls = []
        calc_start = time.time()
        
        for pool in pools:
            # Fast TVL calculation using cached prices
            token_a = pool.get("tokenA", {})
            token_b = pool.get("tokenB", {})
            amount_a = int(pool.get("amountA", 0))
            amount_b = int(pool.get("amountB", 0))
            
            price_a = token_prices.get(token_a.get("id"), 0)
            price_b = token_prices.get(token_b.get("id"), 0)
            
            if price_a > 0 and price_b > 0 and amount_a > 0 and amount_b > 0:
                decimals_a = token_a.get("decimals", 8)
                decimals_b = token_b.get("decimals", 8)
                
                value_a = (amount_a / (10**decimals_a)) * price_a
                value_b = (amount_b / (10**decimals_b)) * price_b
                tvl = value_a + value_b
                
                if tvl > 0:
                    pool_data = pool.copy()
                    pool_data["tvl_usd"] = tvl
                    pool_data["value_a_usd"] = value_a
                    pool_data["value_b_usd"] = value_b
                    pool_tvls.append(pool_data)
        
        calc_time = time.time() - calc_start
        
        # Sort by TVL descending
        pool_tvls.sort(key=lambda p: p["tvl_usd"], reverse=True)
        
        total_time = time.time() - start_time
        print(f"   ✅ Calculated TVL for {len(pool_tvls)}/{len(pools)} pools in {total_time:.3f}s (calc: {calc_time:.3f}s)")
        
        return pool_tvls[:limit]

    def get_saucerswap_token_pairs(self, token_id: str, cached_pools: Optional[List[Dict]] = None) -> List[Dict]:
        """Get all pools containing a specific token"""
        pools = cached_pools or self.get_saucerswap_pools()
        token_pools = []

        for pool in pools:
            token_a_id = pool.get("tokenA", {}).get("id")
            token_b_id = pool.get("tokenB", {}).get("id")

            if token_a_id == token_id or token_b_id == token_id:
                pool_data = pool.copy()
                pool_data["tvl_usd"] = self.get_saucerswap_pool_tvl(pool.get("id", 0))
                token_pools.append(pool_data)

        return sorted(token_pools, key=lambda p: p.get("tvl_usd", 0), reverse=True)

    def get_saucerswap_analytics(self) -> Dict:
        """Get comprehensive SaucerSwap analytics - OPTIMIZED"""
        print("   📊 Calculating SaucerSwap analytics (optimized)...")
        start_time = time.time()
        
        pools = self.get_saucerswap_pools()
        tokens = self.get_saucerswap_tokens()

        # Use optimized top pools method that doesn't make 2000+ calls
        top_pools = self.get_saucerswap_top_pools(5)
        total_tvl = sum(p.get("tvl_usd", 0) for p in top_pools)

        # Count active pools (with liquidity > 0)
        active_pools = [p for p in pools if int(p.get("liquidity", 0)) > 0]

        # Get token count with price data
        tokens_with_prices = [t for t in tokens if t.get("priceUsd", 0) > 0]
        
        analytics_time = time.time() - start_time
        print(f"   ✅ Analytics completed in {analytics_time:.3f}s")

        return {
            "total_pools": len(pools),
            "active_pools": len(active_pools),
            "total_tokens": len(tokens),
            "tokens_with_prices": len(tokens_with_prices),
            "total_tvl_usd": total_tvl,
            "top_pools": top_pools,
            "timestamp": datetime.now().isoformat(),
            "analytics_time": analytics_time
        }
    
    def get_saucerswap_stats(self) -> Dict:
        """Get SaucerSwap protocol statistics"""
        print(f"   📈 Fetching SaucerSwap stats...")
        stats = self._saucerswap_request("stats")
        tvl = stats.get("tvlUsd", 0)
        print(f"   💰 SaucerSwap TVL: ${tvl:,.2f}")
        return stats
    
    def get_saucerswap_known_pools(self) -> List[Dict]:
        """Get SaucerSwap known/verified pools"""
        return self._saucerswap_request("pools/known")
    
    def get_saucerswap_protocol_tvl(self) -> float:
        """Get total SaucerSwap protocol TVL in USD"""
        stats = self.get_saucerswap_stats()
        return stats.get("tvlUsd", 0.0)
    
    def get_saucerswap_volume_24h(self) -> float:
        """Get SaucerSwap 24h volume in USD"""
        stats = self.get_saucerswap_stats()
        return stats.get("volumeTotalUsd", 0.0) / 1000  # Approximate daily from total
    
    def get_combined_defi_overview(self) -> Dict[str, Any]:
        """Get comprehensive DeFi overview combining all protocols"""
        # Get base overview
        base_overview = self.get_defi_overview()
        
        # Add SaucerSwap data
        saucer_stats = self.get_saucerswap_stats()
        saucer_pools = self.get_saucerswap_top_pools(10)
        
        # Add Bonzo Finance data
        bonzo_totals = self.get_bonzo_total_markets()
        bonzo_reserves = self.get_bonzo_reserves()
        
        # Calculate combined TVL
        saucer_tvl = saucer_stats.get("tvlUsd", 0)
        bonzo_tvl_str = bonzo_totals.get("total_market_supplied", {}).get("usd_display", "0")
        bonzo_tvl = float(bonzo_tvl_str.replace("$", "").replace(",", "")) if bonzo_tvl_str != "0" else 0
        
        combined_tvl = base_overview.get("total_tvl", 0) + saucer_tvl + bonzo_tvl
        
        base_overview.update({
            "combined_tvl_usd": combined_tvl,
            "saucerswap": {
                "tvl_usd": saucer_tvl,
                "total_pools": len(saucer_pools),
                "total_volume_usd": saucer_stats.get("volumeTotalUsd", 0),
                "swap_count": saucer_stats.get("swapTotal", 0),
                "sauce_circulating": saucer_stats.get("circulatingSauce", 0)
            },
            "bonzo_finance": {
                "tvl_usd": bonzo_tvl,
                "reserves_count": len(bonzo_reserves),
                "network": bonzo_totals.get("network_name", ""),
                "total_supplied": bonzo_totals.get("total_market_supplied", {}),
                "total_borrowed": bonzo_totals.get("total_market_borrowed", {})
            },
            "protocol_breakdown": {
                "dex_tvl": saucer_tvl,
                "lending_tvl": bonzo_tvl,
                "other_tvl": base_overview.get("total_tvl", 0)
            }
        })
        
        return base_overview
    
    # ========== PRICE AGGREGATION METHODS ==========
    
    def get_aggregated_token_price(self, token_id: str) -> Dict:
        """Get token price aggregated across multiple data sources"""
        prices = {}
        
        # Get SaucerSwap price
        saucer_price = self.get_saucerswap_token_price(token_id)
        if saucer_price > 0:
            prices["saucerswap"] = saucer_price
        
        # Check if token exists in Bonzo reserves
        saucer_token = self.get_saucerswap_token_by_id(token_id)
        if saucer_token:
            symbol = saucer_token.get("symbol", "")
            bonzo_reserve = self.get_bonzo_reserve(symbol)
            if bonzo_reserve:
                # Bonzo doesn't provide direct USD prices, but we can note it's available
                prices["bonzo_available"] = True
        
        if not prices:
            return {"token_id": token_id, "prices": {}, "average_price": 0, "source_count": 0}
        
        # Calculate average from available prices
        price_values = [p for p in prices.values() if isinstance(p, (int, float)) and p > 0]
        average_price = sum(price_values) / len(price_values) if price_values else 0
        
        return {
            "token_id": token_id,
            "prices": prices,
            "average_price": average_price,
            "source_count": len(price_values),
            "data_sources": list(prices.keys())
        }
    
    def get_multi_protocol_token_data(self, token_id: str) -> Dict:
        """Get comprehensive token data across all integrated protocols"""
        result = {
            "token_id": token_id,
            "mirror_node": {},
            "saucerswap": {},
            "bonzo_finance": {},
            "aggregated_price": 0
        }
        
        # Mirror Node data
        mirror_token = self.get_token_info(token_id)
        if mirror_token:
            result["mirror_node"] = {
                "symbol": mirror_token.symbol,
                "name": mirror_token.name,
                "decimals": mirror_token.decimals,
                "total_supply": mirror_token.total_supply
            }
        
        # SaucerSwap data
        saucer_token = self.get_saucerswap_token_by_id(token_id)
        if saucer_token:
            result["saucerswap"] = {
                "price_usd": saucer_token.get("priceUsd", 0),
                "in_top_pools": saucer_token.get("inTopPools", False),
                "in_v2_pools": saucer_token.get("inV2Pools", False),
                "due_diligence": saucer_token.get("dueDiligenceComplete", False),
                "icon": saucer_token.get("icon"),
                "trading_pairs": len(self.get_saucerswap_token_pairs(token_id))
            }
        
        # Bonzo Finance data (if available)
        if saucer_token:
            symbol = saucer_token.get("symbol", "")
            bonzo_reserve = self.get_bonzo_reserve(symbol)
            if bonzo_reserve:
                result["bonzo_finance"] = {
                    "available_for_lending": bonzo_reserve.get("active", False),
                    "supply_apy": bonzo_reserve.get("supply_apy", 0),
                    "borrow_apy": bonzo_reserve.get("variable_borrow_apy", 0),
                    "utilization_rate": bonzo_reserve.get("utilization_rate", 0),
                    "ltv": bonzo_reserve.get("ltv", 0),
                    "liquidation_threshold": bonzo_reserve.get("liquidation_threshold", 0)
                }
        
        # Set aggregated price
        price_data = self.get_aggregated_token_price(token_id)
        result["aggregated_price"] = price_data["average_price"]
        
        return result
    
    def compare_token_prices_across_protocols(self, token_ids: List[str]) -> List[Dict]:
        """Compare token prices across multiple protocols"""
        comparisons = []
        
        for token_id in token_ids:
            price_data = self.get_aggregated_token_price(token_id)
            token_data = self.get_multi_protocol_token_data(token_id)
            
            comparison = {
                "token_id": token_id,
                "symbol": token_data.get("mirror_node", {}).get("symbol", ""),
                "name": token_data.get("mirror_node", {}).get("name", ""),
                "price_data": price_data,
                "protocol_availability": {
                    "saucerswap": bool(token_data.get("saucerswap")),
                    "bonzo_finance": bool(token_data.get("bonzo_finance")),
                    "mirror_node": bool(token_data.get("mirror_node"))
                }
            }
            comparisons.append(comparison)
        
        return comparisons
    
    # ========== DIRECT CONTRACT QUERYING METHODS ==========
    
    def get_pool_contract_state(self, pool_contract_id: str) -> Dict:
        """Get pool contract state directly from Hedera node"""
        try:
            contract_info = self.get_contract_info(pool_contract_id)
            contract_state = self.get_contract_state(pool_contract_id)
            
            return {
                "contract_id": pool_contract_id,
                "contract_info": contract_info,
                "state": contract_state,
                "is_active": bool(contract_info),
                "state_size": len(contract_state)
            }
        except Exception as e:
            print(f"Warning: Failed to query pool contract {pool_contract_id}: {e}")
            return {}
    
    def get_pool_reserves_from_contract(self, pool_contract_id: str) -> Dict:
        """Get pool reserves directly from contract state"""
        try:
            state = self.get_contract_state(pool_contract_id)
            
            # Parse contract state for reserve information
            reserves = {}
            for state_item in state:
                key = state_item.get("key", "")
                value = state_item.get("value", "")
                
                # Look for reserve-related state variables
                if "reserve" in key.lower() or "amount" in key.lower():
                    reserves[key] = value
            
            return {
                "contract_id": pool_contract_id,
                "reserves": reserves,
                "raw_state_count": len(state)
            }
        except Exception as e:
            print(f"Warning: Failed to get reserves from contract {pool_contract_id}: {e}")
            return {}
    
    def get_token_contract_metadata(self, token_id: str) -> Dict:
        """Get token metadata directly from contract"""
        try:
            # Get token info from Mirror Node
            token_info = self.get_contract_info(token_id)
            
            if not token_info:
                return {}
            
            return {
                "token_id": token_id,
                "contract_info": token_info,
                "evm_address": token_info.get("evm_address"),
                "created_timestamp": token_info.get("created_timestamp"),
                "auto_renew_period": token_info.get("auto_renew_period"),
                "memo": token_info.get("memo", "")
            }
        except Exception as e:
            print(f"Warning: Failed to get token contract metadata for {token_id}: {e}")
            return {}
    
    def get_all_protocol_contracts(self) -> Dict:
        """Get contract information for all known protocol addresses"""
        protocol_contracts = {}
        
        # SaucerSwap protocol contracts
        saucer_pools = self.get_saucerswap_pools()
        saucer_contract_ids = [pool.get("contractId") for pool in saucer_pools if pool.get("contractId")]
        
        protocol_contracts["saucerswap"] = {
            "pool_contracts": saucer_contract_ids[:10],  # Limit to first 10 for performance
            "factory_contract": self.DEFI_PROTOCOLS["SaucerSwap"]["factory"],
            "router_contract": self.DEFI_PROTOCOLS["SaucerSwap"]["router"]
        }
        
        # Add other known protocols
        for name, info in self.DEFI_PROTOCOLS.items():
            if name != "SaucerSwap":
                protocol_contracts[name.lower()] = {
                    "main_contract": info.get("router") or info.get("factory") or info.get("staking"),
                    "type": info["type"]
                }
        
        return protocol_contracts
    
    def validate_pool_contract(self, pool_contract_id: str) -> Dict:
        """Validate if a contract ID corresponds to a valid pool"""
        # Check if contract exists in SaucerSwap pools
        saucer_pools = self.get_saucerswap_pools()
        saucer_pool = next((p for p in saucer_pools if p.get("contractId") == pool_contract_id), None)
        
        if saucer_pool:
            contract_state = self.get_pool_contract_state(pool_contract_id)
            return {
                "is_valid_pool": True,
                "protocol": "SaucerSwap",
                "pool_data": saucer_pool,
                "contract_accessible": bool(contract_state.get("contract_info")),
                "token_pair": f"{saucer_pool.get('tokenA', {}).get('symbol', '')}-{saucer_pool.get('tokenB', {}).get('symbol', '')}"
            }
        
        # Check other protocols
        contract_info = self.get_contract_info(pool_contract_id)
        return {
            "is_valid_pool": bool(contract_info),
            "protocol": "unknown", 
            "contract_accessible": bool(contract_info),
            "contract_info": contract_info
        }
    
    # ========== ENHANCED TOKEN DISCOVERY ==========
    
    def discover_tokens_by_trading_activity(self, min_pairs: int = 1) -> List[Dict]:
        """Discover tokens based on trading activity in SaucerSwap"""
        tokens = self.get_saucerswap_tokens()
        active_tokens = []
        
        for token in tokens:
            token_id = token.get("id")
            if token_id:
                pairs = self.get_saucerswap_token_pairs(token_id)
                if len(pairs) >= min_pairs:
                    token_data = {
                        "token_id": token_id,
                        "symbol": token.get("symbol", ""),
                        "name": token.get("name", ""),
                        "price_usd": token.get("priceUsd", 0),
                        "trading_pairs_count": len(pairs),
                        "in_top_pools": token.get("inTopPools", False),
                        "due_diligence": token.get("dueDiligenceComplete", False),
                        "created_at": token.get("createdAt")
                    }
                    active_tokens.append(token_data)
        
        return sorted(active_tokens, key=lambda t: t["trading_pairs_count"], reverse=True)
    
    def get_token_ecosystem_presence(self, token_id: str, cached_tokens: Optional[List[Dict]] = None, cached_pools: Optional[List[Dict]] = None, cached_bonzo_data: Optional[Dict] = None) -> Dict:
        """Get comprehensive view of token presence across Hedera ecosystem"""
        presence = {
            "token_id": token_id,
            "mirror_node_exists": False,
            "saucerswap_listed": False,
            "bonzo_supported": False,
            "trading_pairs": 0,
            "total_supply": 0,
            "ecosystem_score": 0
        }
        
        # Check Mirror Node
        mirror_token = self.get_token_info(token_id)
        if mirror_token:
            presence["mirror_node_exists"] = True
            presence["total_supply"] = mirror_token.total_supply
            presence["ecosystem_score"] += 1
        
        # Check SaucerSwap using cached data
        saucer_tokens = cached_tokens or self.get_saucerswap_tokens()
        saucer_token = next((t for t in saucer_tokens if t.get("id") == token_id), None)
        
        if saucer_token:
            presence["saucerswap_listed"] = True
            # Use cached pools to count pairs
            pools = cached_pools or self.get_saucerswap_pools()
            pairs = [p for p in pools if p.get("tokenA", {}).get("id") == token_id or p.get("tokenB", {}).get("id") == token_id]
            presence["trading_pairs"] = len(pairs)
            presence["ecosystem_score"] += 2 if saucer_token.get("inTopPools") else 1
        
        # Check Bonzo Finance using cached data
        if saucer_token:
            symbol = saucer_token.get("symbol", "")
            bonzo_data = cached_bonzo_data or self.get_bonzo_markets()
            bonzo_reserves = bonzo_data.get("reserves", [])
            bonzo_reserve = next((r for r in bonzo_reserves if r.get("symbol", "").upper() == symbol.upper()), None)
            
            if bonzo_reserve:
                presence["bonzo_supported"] = True
                presence["ecosystem_score"] += 1
        
        return presence
    
    def find_arbitrage_opportunities_real_data(self) -> List[Dict]:
        """Find arbitrage opportunities using real price data from multiple sources"""
        opportunities = []
        
        # Get tokens that exist in multiple protocols
        saucer_tokens = self.get_saucerswap_tokens()
        
        for token in saucer_tokens:
            token_id = token.get("id")
            if not token_id:
                continue
                
            # Get multi-protocol data
            multi_data = self.get_multi_protocol_token_data(token_id)
            
            saucer_price = multi_data.get("saucerswap", {}).get("price_usd", 0)
            bonzo_data = multi_data.get("bonzo_finance", {})
            
            # Look for opportunities where token is available in both protocols
            if saucer_price > 0 and bonzo_data:
                opportunity = {
                    "token_id": token_id,
                    "symbol": token.get("symbol", ""),
                    "saucerswap_price": saucer_price,
                    "bonzo_available": True,
                    "bonzo_supply_apy": bonzo_data.get("supply_apy", 0),
                    "bonzo_borrow_apy": bonzo_data.get("borrow_apy", 0),
                    "opportunity_type": "lending_vs_trading",
                    "potential_yield": bonzo_data.get("supply_apy", 0)
                }
                opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda o: o["potential_yield"], reverse=True)
    
    # ========== UNIFIED PAIR DISCOVERY ==========
    
    def get_all_token_pairs(self, token_id: str) -> Dict:
        """Get all trading and lending pairs for a token across both protocols"""
        pairs_data = {
            "token_id": token_id,
            "saucerswap_pairs": [],
            "bonzo_opportunities": {},
            "total_pair_count": 0,
            "protocols": []
        }
        
        # Get SaucerSwap trading pairs
        saucer_pairs = self.get_saucerswap_token_pairs(token_id)
        pairs_data["saucerswap_pairs"] = [
            {
                "pool_id": pair.get("id"),
                "contract_id": pair.get("contractId"),
                "pair_tokens": [
                    pair.get("tokenA", {}).get("symbol", ""),
                    pair.get("tokenB", {}).get("symbol", "")
                ],
                "fee_tier": pair.get("fee", 0),
                "tvl_usd": pair.get("tvl_usd", 0),
                "liquidity": pair.get("liquidity", 0)
            }
            for pair in saucer_pairs
        ]
        
        if saucer_pairs:
            pairs_data["protocols"].append("SaucerSwap")
        
        # Get Bonzo Finance opportunities
        saucer_token = self.get_saucerswap_token_by_id(token_id)
        if saucer_token:
            symbol = saucer_token.get("symbol", "")
            bonzo_reserve = self.get_bonzo_reserve(symbol)
            if bonzo_reserve:
                pairs_data["bonzo_opportunities"] = {
                    "lending_available": bonzo_reserve.get("active", False),
                    "borrowing_available": bonzo_reserve.get("variable_borrowing_enabled", False),
                    "supply_apy": bonzo_reserve.get("supply_apy", 0),
                    "borrow_apy": bonzo_reserve.get("variable_borrow_apy", 0),
                    "utilization_rate": bonzo_reserve.get("utilization_rate", 0),
                    "available_liquidity": bonzo_reserve.get("available_liquidity", {}),
                    "ltv": bonzo_reserve.get("ltv", 0)
                }
                pairs_data["protocols"].append("Bonzo Finance")
        
        pairs_data["total_pair_count"] = len(saucer_pairs) + (1 if pairs_data["bonzo_opportunities"] else 0)
        
        return pairs_data
    
    def discover_all_active_tokens(self) -> List[Dict]:
        """Discover all tokens active across both SaucerSwap and Bonzo Finance - OPTIMIZED"""
        print("   🔍 Starting optimized token discovery...")
        start_time = time.time()
        
        all_active_tokens = []
        processed_tokens = set()
        
        # Get all data once at the beginning - NO REPEATED CALLS
        print("   📊 Fetching SaucerSwap tokens (once)...")
        saucer_tokens = self.get_saucerswap_tokens()
        
        print("   🏊 Fetching SaucerSwap pools (once)...")  
        saucer_pools = self.get_saucerswap_pools()
        
        print("   🏦 Fetching Bonzo markets (once)...")
        bonzo_data = self.get_bonzo_markets()
        bonzo_reserves = bonzo_data.get("reserves", [])
        
        # Create lookup maps to avoid repeated searching
        print("   🗺️  Building lookup maps...")
        pools_by_token = {}
        for pool in saucer_pools:
            token_a = pool.get("tokenA", {}).get("id")
            token_b = pool.get("tokenB", {}).get("id")
            if token_a:
                if token_a not in pools_by_token:
                    pools_by_token[token_a] = []
                pools_by_token[token_a].append(pool)
            if token_b:
                if token_b not in pools_by_token:
                    pools_by_token[token_b] = []
                pools_by_token[token_b].append(pool)
        
        bonzo_by_symbol = {r.get("symbol", "").upper(): r for r in bonzo_reserves}
        saucer_by_symbol = {t.get("symbol", "").upper(): t for t in saucer_tokens}
        
        processing_start = time.time()
        print(f"   ⚡ Processing {len(saucer_tokens)} tokens...")
        
        for token in saucer_tokens:
            token_id = token.get("id")
            if token_id and token_id not in processed_tokens:
                processed_tokens.add(token_id)
                
                # Use pre-fetched data instead of making new calls
                token_pairs = pools_by_token.get(token_id, [])
                symbol = token.get("symbol", "").upper()
                bonzo_reserve = bonzo_by_symbol.get(symbol)
                
                # Calculate ecosystem presence without additional calls
                ecosystem_score = 1  # Base score for existing
                protocols = ["SaucerSwap"]
                
                if token.get("inTopPools"):
                    ecosystem_score += 1
                if bonzo_reserve:
                    ecosystem_score += 1
                    protocols.append("Bonzo Finance")
                
                token_data = {
                    "token_id": token_id,
                    "symbol": token.get("symbol", ""),
                    "name": token.get("name", ""),
                    "price_usd": token.get("priceUsd", 0),
                    "protocols_available": protocols,
                    "saucerswap_pairs": len(token_pairs),
                    "bonzo_available": bool(bonzo_reserve),
                    "ecosystem_score": ecosystem_score,
                    "due_diligence": token.get("dueDiligenceComplete", False),
                    "in_top_pools": token.get("inTopPools", False)
                }
                all_active_tokens.append(token_data)
        
        # Check for Bonzo-only tokens
        for reserve in bonzo_reserves:
            symbol = reserve.get("symbol", "").upper()
            if symbol not in saucer_by_symbol:
                # This is a Bonzo-only token
                token_data = {
                    "token_id": "unknown",
                    "symbol": symbol,
                    "name": symbol,
                    "price_usd": 0,
                    "protocols_available": ["Bonzo Finance"],
                    "saucerswap_pairs": 0,
                    "bonzo_available": True,
                    "ecosystem_score": 1,
                    "due_diligence": False,
                    "in_top_pools": False,
                    "bonzo_only": True
                }
                all_active_tokens.append(token_data)
        
        total_time = time.time() - start_time
        processing_time = time.time() - processing_start
        print(f"   ✅ Token discovery completed in {total_time:.2f}s (processing: {processing_time:.2f}s)")
        print(f"   🎯 Found {len(all_active_tokens)} active tokens across both protocols")
        
        return sorted(all_active_tokens, key=lambda t: t["ecosystem_score"], reverse=True)
    
    def get_all_token_images(self) -> Dict:
        """Get all token images/icons from SaucerSwap (PNG URLs)"""
        print(f"   🖼️  Fetching all token images from SaucerSwap...")
        start_time = time.time()
        
        tokens = self.get_saucerswap_tokens()
        
        token_images = {}
        png_count = 0
        
        for token in tokens:
            token_id = token.get("id")
            symbol = token.get("symbol", "")
            icon_url = token.get("icon")
            
            if icon_url and token_id:
                token_images[token_id] = {
                    "symbol": symbol,
                    "name": token.get("name", ""),
                    "icon_url": icon_url,
                    "is_png": icon_url.lower().endswith('.png'),
                    "price_usd": token.get("priceUsd", 0),
                    "in_top_pools": token.get("inTopPools", False)
                }
                
                if icon_url.lower().endswith('.png'):
                    png_count += 1
        
        # Filter to get only PNG images
        png_images = {k: v for k, v in token_images.items() if v["is_png"]}
        
        fetch_time = time.time() - start_time
        print(f"   ✅ Found {len(token_images)} token images ({png_count} PNGs) in {fetch_time:.2f}s")
        
        return {
            "all_images": token_images,
            "png_images": png_images,
            "stats": {
                "total_tokens": len(tokens),
                "tokens_with_images": len(token_images),
                "png_images_count": png_count,
                "other_format_count": len(token_images) - png_count,
                "fetch_time": fetch_time
            }
        }
    
    def get_cross_protocol_liquidity_summary(self) -> Dict:
        """Get summary of liquidity across both protocols"""
        import time
        start_time = time.time()
        
        print(f"   🔄 Starting cross-protocol liquidity summary...")
        
        # SaucerSwap data
        saucer_start = time.time()
        saucer_stats = self.get_saucerswap_stats()
        saucer_pools = self.get_saucerswap_pools()
        saucer_time = time.time() - saucer_start
        print(f"   📊 SaucerSwap data fetched in {saucer_time:.2f}s")
        
        # Bonzo Finance data - fetch once and reuse to avoid duplicate API calls
        bonzo_start = time.time()
        bonzo_data = self.get_bonzo_markets()  # Fetch once instead of calling multiple times
        bonzo_time = time.time() - bonzo_start
        print(f"   💰 Bonzo data fetched in {bonzo_time:.2f}s")
        
        # Extract data from single Bonzo response
        bonzo_totals = {}
        bonzo_reserves = []
        if bonzo_data:
            bonzo_totals = {
                "chain_id": bonzo_data.get("chain_id"),
                "network_name": bonzo_data.get("network_name"),
                "total_market_supplied": bonzo_data.get("total_market_supplied", {}),
                "total_market_borrowed": bonzo_data.get("total_market_borrowed", {}),
                "total_market_liquidity": bonzo_data.get("total_market_liquidity", {}),
                "total_market_reserve": bonzo_data.get("total_market_reserve", {}),
                "timestamp": bonzo_data.get("timestamp"),
                "total_reserves": len(bonzo_data.get("reserves", [])),
            }
            bonzo_reserves = bonzo_data.get("reserves", [])
        
        # Calculate totals
        calc_start = time.time()
        saucer_tvl = saucer_stats.get("tvlUsd", 0)
        bonzo_tvl_str = bonzo_totals.get("total_market_supplied", {}).get("usd_display", "0")
        bonzo_tvl = 0
        if bonzo_tvl_str != "0":
            try:
                bonzo_tvl = float(bonzo_tvl_str.replace("$", "").replace(",", ""))
            except:
                bonzo_tvl = 0
        calc_time = time.time() - calc_start
        
        total_time = time.time() - start_time
        print(f"   ⚡ Cross-protocol summary completed in {total_time:.2f}s")
        
        return {
            "total_liquidity_usd": saucer_tvl + bonzo_tvl,
            "saucerswap": {
                "tvl_usd": saucer_tvl,
                "pool_count": len(saucer_pools),
                "active_pools": len([p for p in saucer_pools if int(p.get("liquidity", 0)) > 0]),
                "protocol_type": "DEX"
            },
            "bonzo_finance": {
                "tvl_usd": bonzo_tvl,
                "reserve_count": len(bonzo_reserves),
                "active_reserves": len([r for r in bonzo_reserves if r.get("active", False)]),
                "protocol_type": "Lending"
            },
            "protocol_distribution": {
                "dex_percentage": (saucer_tvl / (saucer_tvl + bonzo_tvl) * 100) if (saucer_tvl + bonzo_tvl) > 0 else 0,
                "lending_percentage": (bonzo_tvl / (saucer_tvl + bonzo_tvl) * 100) if (saucer_tvl + bonzo_tvl) > 0 else 0
            },
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "total_time": total_time,
                "saucerswap_time": saucer_time,
                "bonzo_time": bonzo_time,
                "calculation_time": calc_time
            }
        }
