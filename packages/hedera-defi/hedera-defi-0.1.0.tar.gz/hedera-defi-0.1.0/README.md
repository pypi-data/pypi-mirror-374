# Hedera DeFi SDK

Simple Python SDK for accessing Hedera DeFi data via Hgraph GraphQL API.

## Installation

```bash
pip install hedera-defi
```

## Quick Start

```python
from hedera_defi import HederaDeFi

# Initialize client
client = HederaDeFi(api_key="your_hgraph_api_key")

# Get all protocols with >$10k TVL
protocols = client.get_protocols(min_tvl=10000)
for protocol in protocols:
    print(f"{protocol.name}: ${protocol.tvl:,.0f}")

# Get whale transactions
whales = client.get_whale_transactions(threshold=100000)
for whale in whales:
    print(f"${whale.value_usd:,.0f} {whale.token} moved")

# Get best yield opportunities
yields = client.get_best_yields(min_apy=10.0)
print(yields)

# Get complete DeFi overview
overview = client.get_defi_overview()
print(f"Total TVL: ${overview['total_tvl']:,.0f}")
```

## Features

- 🔍 **Protocol Discovery**: Automatically find all DeFi protocols on Hedera
- 🐋 **Whale Tracking**: Monitor large transactions in real-time
- 💰 **Yield Analytics**: Find the best farming opportunities
- 📊 **Risk Metrics**: Assess protocol and pool risks
- 📈 **TVL History**: Track historical TVL data
- 🏊 **Pool Analytics**: Analyze liquidity pools across all protocols

## Main Methods

### Protocol Operations
- `get_protocols(min_tvl, protocol_type, limit)` - Get all protocols
- `search_protocols(query, search_type)` - Search for specific protocols
- `get_risk_metrics(protocol_id)` - Get risk assessment

### Token Operations  
- `get_top_tokens(limit, sort_by)` - Get top tokens by various metrics
- `get_pools(protocol_id, min_tvl, pool_type)` - Get liquidity pools

### Whale Tracking
- `get_whale_transactions(threshold, window_minutes)` - Track whale movements

### Analytics
- `get_tvl_history(protocol_id, days, interval)` - Historical TVL data
- `get_best_yields(min_apy, max_risk)` - Find yield opportunities
- `get_defi_overview()` - Complete ecosystem overview

## Data Models

All methods return typed dataclass objects:

```python
@dataclass
class Protocol:
    contract_id: str
    name: str
    type: str  # 'dex', 'lending', 'staking'
    tvl: float
    volume_24h: float
    users_24h: int
    pools: List[str]
    tokens: List[str]
    created_at: datetime

@dataclass
class WhaleAlert:
    timestamp: datetime
    type: str
    token: str
    amount: int
    value_usd: float
    from_address: str
    to_address: str
    transaction_hash: str
```

## Advanced Usage

### Custom Queries

```python
# Execute custom GraphQL queries
query = """
    query MyQuery($limit: Int!) {
        token(limit: $limit) {
            token_id
            name
            symbol
        }
    }
"""
result = client.query(query, {"limit": 10})
```

### Pandas Integration

```python
import pandas as pd

# Get TVL history as DataFrame
tvl_df = client.get_tvl_history(days=30, interval="daily")

# Get yields as DataFrame
yields_df = client.get_best_yields(min_apy=5.0)

# Export to CSV
yields_df.to_csv("hedera_yields.csv", index=False)
```

### Risk Analysis

```python
# Get comprehensive risk metrics
protocols = client.get_protocols(min_tvl=100000)

for protocol in protocols:
    risk = client.get_risk_metrics(protocol.contract_id)
    if risk.overall_risk == "high":
        print(f"⚠️ {protocol.name} has high risk!")
        print(f"  Concentration: {risk.concentration_risk:.1%}")
        print(f"  Liquidity: {risk.liquidity_risk:.1%}")
```

## Requirements

- Python 3.8+
- requests
- pandas
- numpy

## License

MIT

## Support

For issues and questions, please visit: https://github.com/yourusername/hedera-defi-sdk