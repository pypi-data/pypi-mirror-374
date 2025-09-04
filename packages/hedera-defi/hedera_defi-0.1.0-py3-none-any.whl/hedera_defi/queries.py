"""
GraphQL query templates for Hedera
"""


class GraphQLQueries:
    """Collection of GraphQL queries"""
    
    @staticmethod
    def get_protocols_query() -> str:
        """Query to discover DeFi protocols"""
        return """
        query DiscoverProtocols($window: bigint!, $limit: Int!) {
            contracts: contract(
                where: {
                    created_timestamp: {_gte: $window}
                }
                order_by: {created_timestamp: desc}
                limit: $limit
            ) {
                contract_id: id
                created_timestamp
                events: contract_log(
                    distinct_on: topic0
                    limit: 10
                ) {
                    topic0
                }
            }
        }
        """
    
    @staticmethod
    def get_tokens_query(sort_by: str = "tvl") -> str:
        """Query to get top tokens"""
        order_field = {
            "tvl": "total_supply",
            "holders": "token_account_aggregate.count",
            "volume": "total_supply",
            "supply": "total_supply"
        }.get(sort_by, "total_supply")
        
        return f"""
        query GetTopTokens($limit: Int!) {{
            tokens: token(
                order_by: {{{order_field}: desc}}
                limit: $limit
                where: {{type: {{_eq: "FUNGIBLE_COMMON"}}}}
            ) {{
                token_id
                name
                symbol
                decimals
                total_supply
                treasury_account_id
                created_timestamp
            }}
        }}
        """
    
    @staticmethod
    def get_pools_query() -> str:
        """Query to get liquidity pools"""
        return """
        query GetPools($window: bigint!, $minTvl: Float!) {
            pools: contract_log(
                where: {
                    topic0: {_in: [
                        "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
                        "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"
                    ]}
                    timestamp: {_gte: $window}
                }
                distinct_on: contract_id
                limit: 500
            ) {
                pool_id: contract_id
                timestamp
            }
        }
        """
    
    @staticmethod
    def get_whale_transactions_query() -> str:
        """Query to get whale transactions"""
        return """
        query GetWhaleTransactions($window: bigint!, $threshold: bigint!) {
            hbar_transfers: crypto_transfer(
                where: {
                    amount: {_abs: {_gt: $threshold}}
                    consensus_timestamp: {_gte: $window}
                }
                order_by: {consensus_timestamp: desc}
                limit: 100
            ) {
                amount
                consensus_timestamp
                entity_id
                transaction {
                    payer_account_id
                    transaction_hash
                }
            }
            
            token_transfers: token_transfer(
                where: {
                    consensus_timestamp: {_gte: $window}
                }
                order_by: {consensus_timestamp: desc}
                limit: 500
            ) {
                token_id
                account_id
                amount
                consensus_timestamp
            }
        }
        """
    
    @staticmethod
    def get_risk_metrics_query() -> str:
        """Query to calculate risk metrics"""
        return """
        query GetRiskMetrics($protocol: String!, $window: bigint!) {
            protocol_id: _protocol
            
            tvl_data: token_account(
                where: {
                    account_id: {_eq: $protocol}
                    balance: {_gt: 0}
                }
            ) {
                balance
                token {
                    decimals
                }
            }
            
            volume_data: contract_result_aggregate(
                where: {
                    contract_id: {_eq: $protocol}
                    consensus_timestamp: {_gte: $window}
                }
            ) {
                aggregate {
                    count
                }
            }
        }
        """
    
    @staticmethod
    def get_tvl_history_query() -> str:
        """Query to get TVL history"""
        return """
        query GetTVLHistory($start: bigint!, $end: bigint!, $protocol: String) {
            balances: token_account(
                where: {
                    account_id: {_eq: $protocol}
                    balance_timestamp: {_gte: $start, _lt: $end}
                    balance: {_gt: 0}
                }
            ) {
                balance
                decimals: token {
                    decimals
                }
            }
        }
        """