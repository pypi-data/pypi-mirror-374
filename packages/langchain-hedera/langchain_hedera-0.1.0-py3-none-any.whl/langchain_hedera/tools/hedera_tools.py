"""
Core Hedera DeFi Tools for LangChain
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
try:
    from hedera_defi import HederaDeFi
except ImportError:
    # Will be available when package is installed
    HederaDeFi = None


class TokenSearchInput(BaseModel):
    """Input for token search operations."""
    query: str = Field(description="Token symbol, name, or token ID to search for")
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")


class ProtocolSearchInput(BaseModel):
    """Input for protocol search operations."""
    protocol_type: Optional[str] = Field(default=None, description="Filter by protocol type: 'dex', 'lending', 'staking'")
    min_tvl: Optional[float] = Field(default=0, description="Minimum TVL in USD")


class WhaleAlertInput(BaseModel):
    """Input for whale transaction monitoring."""
    threshold: Optional[float] = Field(default=10000, description="Minimum HBAR amount for whale alerts")
    window_minutes: Optional[int] = Field(default=60, description="Time window in minutes to search")


class AccountAnalysisInput(BaseModel):
    """Input for account analysis."""
    account_id: str = Field(description="Hedera account ID (format: 0.0.xxxxx)")


class PoolAnalysisInput(BaseModel):
    """Input for pool analysis."""
    protocol_filter: Optional[str] = Field(default=None, description="Filter by protocol name")
    min_tvl: Optional[float] = Field(default=1000, description="Minimum pool TVL in USD")


class HederaTokenTool(BaseTool):
    """Tool for analyzing Hedera tokens and their metrics."""
    
    name: str = "hedera_token_analyzer"
    description: str = """
    Analyze Hedera tokens including price data, supply, trading activity, and cross-protocol availability.
    Use this tool to:
    - Get detailed token information by symbol or token ID
    - Find tokens with specific characteristics
    - Compare token metrics across protocols
    - Discover new tokens and trending assets
    """
    args_schema: Type[BaseModel] = TokenSearchInput
    
    # Use Pydantic field for client
    client: Any = Field(default=None, exclude=True)
    
    def __init__(self, hedera_client=None, **kwargs):
        super().__init__(**kwargs)
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        # Store client in internal attribute to avoid Pydantic validation
        object.__setattr__(self, '_client', hedera_client or HederaDeFi())
    
    @property
    def client(self):
        return getattr(self, '_client', None)
    
    def _run(self, query: str, limit: Optional[int] = 10) -> str:
        """Search and analyze Hedera tokens."""
        try:
            # If query looks like token ID, get specific token info
            if query.startswith("0.0."):
                token_info = self.client.get_token_info(query)
                if token_info:
                    # Get cross-protocol data
                    multi_data = self.client.get_multi_protocol_token_data(query)
                    
                    result = {
                        "token_info": {
                            "token_id": token_info.token_id,
                            "symbol": token_info.symbol,
                            "name": token_info.name,
                            "decimals": token_info.decimals,
                            "total_supply": token_info.total_supply,
                            "price_usd": token_info.price,
                        },
                        "protocol_availability": {
                            "saucerswap": bool(multi_data.get("saucerswap")),
                            "bonzo_finance": bool(multi_data.get("bonzo_finance")),
                            "trading_pairs": multi_data.get("saucerswap", {}).get("trading_pairs", 0),
                        },
                        "aggregated_price": multi_data.get("aggregated_price", 0),
                    }
                    return json.dumps(result, indent=2)
                else:
                    return f"Token {query} not found"
            
            # Search for tokens by symbol/name
            tokens = self.client.search_tokens(query)
            if not tokens:
                # Try getting top tokens if direct search fails
                all_tokens = self.client.get_top_tokens(limit=50)
                tokens = [t for t in all_tokens if 
                         query.lower() in t.symbol.lower() or 
                         query.lower() in t.name.lower()][:limit]
            
            if not tokens:
                return f"No tokens found matching '{query}'"
            
            results = []
            for token in tokens[:limit]:
                results.append({
                    "token_id": token.token_id,
                    "symbol": token.symbol,
                    "name": token.name,
                    "total_supply": token.total_supply,
                    "price_usd": token.price,
                })
            
            return json.dumps({
                "query": query,
                "found_tokens": len(results),
                "tokens": results
            }, indent=2)
            
        except Exception as e:
            return f"Error analyzing tokens: {str(e)}"


class HederaProtocolTool(BaseTool):
    """Tool for analyzing DeFi protocols on Hedera."""
    
    name: str = "hedera_protocol_analyzer"
    description: str = """
    Analyze DeFi protocols on Hedera including TVL, volume, and protocol metrics.
    Use this tool to:
    - Get comprehensive protocol overview
    - Compare protocol performance and metrics
    - Find protocols by type (DEX, lending, staking)
    - Analyze protocol health and risk metrics
    """
    args_schema: Type[BaseModel] = ProtocolSearchInput
    
    def __init__(self, hedera_client=None, **kwargs):
        super().__init__(**kwargs)
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        object.__setattr__(self, '_client', hedera_client or HederaDeFi())
    
    @property
    def client(self):
        return getattr(self, '_client', None)
    
    def _run(self, protocol_type: Optional[str] = None, min_tvl: Optional[float] = 0) -> str:
        """Analyze Hedera DeFi protocols."""
        try:
            protocols = self.client.get_protocols(
                min_tvl=min_tvl or 0,
                protocol_type=protocol_type
            )
            
            # Get additional data for comprehensive analysis
            combined_overview = self.client.get_combined_defi_overview()
            
            protocol_data = []
            for protocol in protocols:
                protocol_data.append({
                    "name": protocol.name,
                    "type": protocol.type,
                    "contract_id": protocol.contract_id,
                    "tvl_usd": protocol.tvl,
                    "volume_24h": protocol.volume_24h,
                    "users_24h": protocol.users_24h,
                    "token_count": len(protocol.tokens),
                    "created_at": protocol.created_at.isoformat() if protocol.created_at else None,
                })
            
            result = {
                "protocols": protocol_data,
                "ecosystem_overview": {
                    "total_tvl_usd": combined_overview.get("combined_tvl_usd", 0),
                    "saucerswap_tvl": combined_overview.get("saucerswap", {}).get("tvl_usd", 0),
                    "bonzo_tvl": combined_overview.get("bonzo_finance", {}).get("tvl_usd", 0),
                    "protocol_count": len(protocols),
                },
                "filters_applied": {
                    "protocol_type": protocol_type,
                    "min_tvl": min_tvl or 0,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing protocols: {str(e)}"


class HederaWhaleTool(BaseTool):
    """Tool for monitoring whale transactions and large transfers."""
    
    name: str = "hedera_whale_monitor"
    description: str = """
    Monitor whale transactions and large value transfers on Hedera.
    Use this tool to:
    - Track large HBAR transfers above specified thresholds
    - Monitor whale activity and market impact
    - Analyze transaction patterns and trends
    - Get alerts for significant market movements
    """
    args_schema: Type[BaseModel] = WhaleAlertInput
    
    def __init__(self, hedera_client=None, **kwargs):
        super().__init__(**kwargs)
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        object.__setattr__(self, '_client', hedera_client or HederaDeFi())
    
    @property
    def client(self):
        return getattr(self, '_client', None)
    
    def _run(self, threshold: Optional[float] = 10000, window_minutes: Optional[int] = 60) -> str:
        """Monitor whale transactions."""
        try:
            whale_alerts = self.client.get_whale_transactions(
                threshold=threshold or 10000,
                window_minutes=window_minutes or 60
            )
            
            if not whale_alerts:
                return f"No whale transactions found above {threshold:,.0f} HBAR in the last {window_minutes} minutes"
            
            alerts_data = []
            total_value = 0
            
            for alert in whale_alerts[:20]:  # Limit to top 20
                hbar_amount = alert.amount / 100_000_000
                total_value += hbar_amount
                
                alerts_data.append({
                    "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
                    "type": alert.type,
                    "token": alert.token,
                    "amount_hbar": hbar_amount,
                    "from_address": alert.from_address,
                    "transaction_hash": alert.transaction_hash,
                })
            
            result = {
                "whale_alerts": alerts_data,
                "summary": {
                    "total_alerts": len(whale_alerts),
                    "threshold_hbar": threshold,
                    "time_window_minutes": window_minutes,
                    "total_value_hbar": total_value,
                    "largest_transaction_hbar": max([a["amount_hbar"] for a in alerts_data]) if alerts_data else 0,
                },
                "market_impact": {
                    "activity_level": "high" if len(whale_alerts) > 10 else "moderate" if len(whale_alerts) > 5 else "low",
                    "avg_transaction_size": total_value / len(alerts_data) if alerts_data else 0,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error monitoring whale transactions: {str(e)}"


class HederaAccountTool(BaseTool):
    """Tool for analyzing Hedera accounts and their DeFi positions."""
    
    name: str = "hedera_account_analyzer"
    description: str = """
    Analyze Hedera accounts including balances, token holdings, and DeFi positions.
    Use this tool to:
    - Get comprehensive account information
    - Analyze token portfolio and holdings
    - Track DeFi positions across protocols
    - Calculate portfolio values and risk metrics
    """
    args_schema: Type[BaseModel] = AccountAnalysisInput
    
    def __init__(self, hedera_client=None, **kwargs):
        super().__init__(**kwargs)
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        object.__setattr__(self, '_client', hedera_client or HederaDeFi())
    
    @property
    def client(self):
        return getattr(self, '_client', None)
    
    def _run(self, account_id: str) -> str:
        """Analyze Hedera account and DeFi positions."""
        try:
            if not self.client.validate_account_id(account_id):
                return f"Invalid account ID format: {account_id}. Use format: 0.0.xxxxx"
            
            # Get account info and positions
            account_info = self.client.get_account_info(account_id)
            user_positions = self.client.get_user_positions(account_id)
            
            if not account_info:
                return f"Account {account_id} not found or has no data"
            
            # Get token holdings with prices
            token_holdings = []
            total_portfolio_value = user_positions.get("hbar_value", 0)
            
            for token in user_positions.get("tokens", [])[:10]:  # Limit to top 10 tokens
                token_id = token.get("token_id")
                if token_id:
                    # Try to get price data
                    price_data = self.client.get_aggregated_token_price(token_id)
                    token_value = (token.get("balance", 0) / (10 ** token.get("decimals", 8))) * price_data.get("average_price", 0)
                    
                    token_holdings.append({
                        "token_id": token_id,
                        "balance": token.get("balance", 0),
                        "decimals": token.get("decimals", 8),
                        "price_usd": price_data.get("average_price", 0),
                        "value_usd": token_value,
                    })
                    total_portfolio_value += token_value
            
            result = {
                "account_info": {
                    "account_id": account_id,
                    "hbar_balance": user_positions.get("hbar_balance", 0),
                    "token_count": len(user_positions.get("tokens", [])),
                    "created_at": account_info.get("created_at", "").isoformat() if account_info.get("created_at") else None,
                },
                "portfolio": {
                    "total_value_usd": total_portfolio_value,
                    "hbar_value_usd": user_positions.get("hbar_value", 0),
                    "token_holdings": token_holdings,
                },
                "defi_positions": {
                    "protocols_detected": [],  # Would need more analysis
                    "estimated_yield": 0,      # Would need position analysis
                    "risk_level": "unknown",   # Would need risk calculation
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing account: {str(e)}"


class HederaPoolTool(BaseTool):
    """Tool for analyzing liquidity pools and DeFi opportunities."""
    
    name: str = "hedera_pool_analyzer"
    description: str = """
    Analyze liquidity pools and DeFi opportunities across Hedera protocols.
    Use this tool to:
    - Find best yield farming opportunities
    - Analyze pool performance and metrics
    - Compare pools across different protocols
    - Calculate impermanent loss and APY
    """
    args_schema: Type[BaseModel] = PoolAnalysisInput
    
    def __init__(self, hedera_client=None, **kwargs):
        super().__init__(**kwargs)
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        object.__setattr__(self, '_client', hedera_client or HederaDeFi())
    
    @property
    def client(self):
        return getattr(self, '_client', None)
    
    def _run(self, protocol_filter: Optional[str] = None, min_tvl: Optional[float] = 1000) -> str:
        """Analyze liquidity pools and opportunities."""
        try:
            # Get pools from multiple sources
            pools = self.client.get_pools(min_tvl=min_tvl or 1000)
            
            # Get best yields
            best_yields = self.client.get_best_yields(min_apy=1.0, limit=20)
            
            # Get SaucerSwap specific data
            saucer_pools = self.client.get_saucerswap_top_pools(10)
            bonzo_rates = self.client.get_bonzo_best_lending_rates(min_apy=1.0)
            
            pool_data = []
            for pool in pools:
                if not protocol_filter or protocol_filter.lower() in pool.name.lower():
                    pool_data.append({
                        "name": pool.name,
                        "type": pool.type,
                        "tvl_usd": pool.tvl,
                        "volume_24h": pool.volume_24h,
                        "apy": pool.apy,
                        "fee": pool.fee,
                        "tokens": pool.tokens,
                    })
            
            # Process yield opportunities
            yield_opportunities = []
            if not best_yields.empty:
                for _, opportunity in best_yields.head(10).iterrows():
                    yield_opportunities.append({
                        "pool": opportunity.get("pool", ""),
                        "protocol": opportunity.get("protocol", ""),
                        "type": opportunity.get("type", ""),
                        "apy": opportunity.get("apy", 0),
                        "tvl_usd": opportunity.get("tvl", 0),
                        "risk_score": opportunity.get("risk_score", 0),
                        "tokens": opportunity.get("tokens", []),
                    })
            
            result = {
                "pools": pool_data,
                "yield_opportunities": yield_opportunities,
                "saucerswap_top_pools": len(saucer_pools),
                "bonzo_lending_options": len(bonzo_rates),
                "analysis_summary": {
                    "total_pools_found": len(pool_data),
                    "min_tvl_filter": min_tvl or 1000,
                    "protocol_filter": protocol_filter,
                    "best_apy": max([y["apy"] for y in yield_opportunities]) if yield_opportunities else 0,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing pools: {str(e)}"