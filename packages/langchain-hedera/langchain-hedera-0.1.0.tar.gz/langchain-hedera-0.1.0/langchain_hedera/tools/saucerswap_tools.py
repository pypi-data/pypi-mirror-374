"""
SaucerSwap DEX Tools for LangChain
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
try:
    from hedera_defi import HederaDeFi
except ImportError:
    HederaDeFi = None


class SaucerSwapAnalysisInput(BaseModel):
    """Input for SaucerSwap analysis operations."""
    analysis_type: str = Field(
        description="Type of analysis: 'overview', 'pools', 'tokens', 'arbitrage'",
        default="overview"
    )
    limit: Optional[int] = Field(default=10, description="Maximum number of results")


class TokenPairInput(BaseModel):
    """Input for token pair analysis."""
    token_id: str = Field(description="Token ID to find trading pairs for")


class PriceComparisonInput(BaseModel):
    """Input for cross-protocol price comparison."""
    token_ids: List[str] = Field(description="List of token IDs to compare prices")


class SaucerSwapTool(BaseTool):
    """Comprehensive SaucerSwap DEX analysis tool."""
    
    name: str = "saucerswap_analyzer"
    description: str = """
    Comprehensive analysis tool for SaucerSwap DEX on Hedera.
    Use this tool to:
    - Get SaucerSwap protocol overview and statistics
    - Analyze top liquidity pools and trading pairs
    - Find token trading opportunities and liquidity
    - Compare prices and find arbitrage opportunities
    - Monitor DEX metrics and trading activity
    """
    args_schema: Type[BaseModel] = SaucerSwapAnalysisInput
    
    def __init__(self, hedera_client=None):
        super().__init__()
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        self.client = hedera_client or HederaDeFi()
    
    def _run(self, analysis_type: str = "overview", limit: Optional[int] = 10) -> str:
        """Analyze SaucerSwap DEX data."""
        try:
            if analysis_type == "overview":
                return self._get_saucerswap_overview()
            elif analysis_type == "pools":
                return self._get_top_pools(limit or 10)
            elif analysis_type == "tokens":
                return self._get_token_analysis(limit or 10)
            elif analysis_type == "arbitrage":
                return self._find_arbitrage_opportunities()
            else:
                return json.dumps({
                    "error": "Invalid analysis_type",
                    "valid_types": ["overview", "pools", "tokens", "arbitrage"]
                })
                
        except Exception as e:
            return f"Error analyzing SaucerSwap: {str(e)}"
    
    def _get_saucerswap_overview(self) -> str:
        """Get comprehensive SaucerSwap overview."""
        try:
            stats = self.client.get_saucerswap_stats()
            analytics = self.client.get_saucerswap_analytics()
            
            overview = {
                "protocol_stats": {
                    "total_tvl_usd": stats.get("tvlUsd", 0),
                    "total_volume_usd": stats.get("volumeTotalUsd", 0),
                    "daily_volume_estimate": stats.get("volumeTotalUsd", 0) / 365,  # Rough estimate
                    "total_swaps": stats.get("swapTotal", 0),
                    "circulating_sauce": stats.get("circulatingSauce", 0),
                },
                "pool_analytics": {
                    "total_pools": analytics.get("total_pools", 0),
                    "active_pools": analytics.get("active_pools", 0),
                    "pool_utilization": (analytics.get("active_pools", 0) / analytics.get("total_pools", 1)) * 100,
                },
                "token_analytics": {
                    "total_tokens": analytics.get("total_tokens", 0),
                    "tokens_with_prices": analytics.get("tokens_with_prices", 0),
                    "price_coverage": (analytics.get("tokens_with_prices", 0) / analytics.get("total_tokens", 1)) * 100,
                },
                "performance_metrics": analytics.get("performance", {}),
                "timestamp": analytics.get("timestamp"),
            }
            
            return json.dumps(overview, indent=2)
            
        except Exception as e:
            return f"Error getting SaucerSwap overview: {str(e)}"
    
    def _get_top_pools(self, limit: int) -> str:
        """Get top SaucerSwap pools by TVL."""
        try:
            top_pools = self.client.get_saucerswap_top_pools(limit)
            
            pools_data = []
            for pool in top_pools:
                token_a = pool.get("tokenA", {})
                token_b = pool.get("tokenB", {})
                
                pools_data.append({
                    "pool_id": pool.get("id"),
                    "contract_id": pool.get("contractId"),
                    "token_pair": f"{token_a.get('symbol', 'Unknown')}/{token_b.get('symbol', 'Unknown')}",
                    "tvl_usd": pool.get("tvl_usd", 0),
                    "fee_tier": pool.get("fee", 0),
                    "liquidity": pool.get("liquidity", 0),
                    "token_a": {
                        "id": token_a.get("id"),
                        "symbol": token_a.get("symbol"),
                        "amount": pool.get("amountA", 0),
                        "value_usd": pool.get("value_a_usd", 0),
                    },
                    "token_b": {
                        "id": token_b.get("id"),
                        "symbol": token_b.get("symbol"),
                        "amount": pool.get("amountB", 0),
                        "value_usd": pool.get("value_b_usd", 0),
                    },
                })
            
            total_tvl = sum(pool["tvl_usd"] for pool in pools_data)
            
            result = {
                "top_pools": pools_data,
                "summary": {
                    "total_pools_analyzed": len(pools_data),
                    "combined_tvl_usd": total_tvl,
                    "average_tvl_usd": total_tvl / len(pools_data) if pools_data else 0,
                    "largest_pool_tvl": max(pool["tvl_usd"] for pool in pools_data) if pools_data else 0,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error getting top pools: {str(e)}"
    
    def _get_token_analysis(self, limit: int) -> str:
        """Analyze SaucerSwap tokens and trading activity."""
        try:
            tokens = self.client.discover_tokens_by_trading_activity(min_pairs=1)
            token_images = self.client.get_all_token_images()
            
            active_tokens = []
            for token in tokens[:limit]:
                token_id = token.get("token_id")
                
                # Get image if available
                image_data = token_images.get("all_images", {}).get(token_id, {})
                
                active_tokens.append({
                    "token_id": token_id,
                    "symbol": token.get("symbol"),
                    "name": token.get("name"),
                    "price_usd": token.get("price_usd", 0),
                    "trading_pairs": token.get("trading_pairs_count", 0),
                    "in_top_pools": token.get("in_top_pools", False),
                    "due_diligence_complete": token.get("due_diligence", False),
                    "icon_url": image_data.get("icon_url"),
                    "has_png_icon": image_data.get("is_png", False),
                })
            
            result = {
                "active_tokens": active_tokens,
                "token_statistics": {
                    "total_active_tokens": len(tokens),
                    "tokens_with_icons": len(token_images.get("all_images", {})),
                    "png_icons_available": len(token_images.get("png_images", {})),
                    "tokens_in_top_pools": len([t for t in active_tokens if t["in_top_pools"]]),
                    "due_diligence_complete": len([t for t in active_tokens if t["due_diligence_complete"]]),
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing tokens: {str(e)}"
    
    def _find_arbitrage_opportunities(self) -> str:
        """Find arbitrage opportunities using real price data."""
        try:
            opportunities = self.client.find_arbitrage_opportunities_real_data()
            
            if not opportunities:
                return json.dumps({
                    "arbitrage_opportunities": [],
                    "message": "No arbitrage opportunities found with current data"
                })
            
            arb_data = []
            for opp in opportunities[:10]:  # Top 10 opportunities
                arb_data.append({
                    "token_id": opp.get("token_id"),
                    "symbol": opp.get("symbol"),
                    "saucerswap_price": opp.get("saucerswap_price", 0),
                    "bonzo_available": opp.get("bonzo_available", False),
                    "bonzo_supply_apy": opp.get("bonzo_supply_apy", 0),
                    "bonzo_borrow_apy": opp.get("bonzo_borrow_apy", 0),
                    "opportunity_type": opp.get("opportunity_type"),
                    "potential_yield": opp.get("potential_yield", 0),
                    "strategy": "Lend on Bonzo while trading on SaucerSwap" if opp.get("bonzo_available") else "Price arbitrage"
                })
            
            result = {
                "arbitrage_opportunities": arb_data,
                "analysis": {
                    "total_opportunities": len(opportunities),
                    "best_yield": max(opp["potential_yield"] for opp in arb_data) if arb_data else 0,
                    "cross_protocol_count": len([o for o in arb_data if o["bonzo_available"]]),
                    "recommendation": "Focus on tokens available in both protocols for maximum yield potential"
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error finding arbitrage opportunities: {str(e)}"


class SaucerSwapTokenPairTool(BaseTool):
    """Tool for analyzing token trading pairs on SaucerSwap."""
    
    name: str = "saucerswap_token_pairs"
    description: str = """
    Find and analyze trading pairs for specific tokens on SaucerSwap.
    Use this tool to:
    - Find all trading pairs for a specific token
    - Analyze liquidity and trading activity for pairs
    - Get detailed pool information for token pairs
    - Find the best liquidity pools for trading
    """
    args_schema: Type[BaseModel] = TokenPairInput
    
    def __init__(self, hedera_client=None):
        super().__init__()
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        self.client = hedera_client or HederaDeFi()
    
    def _run(self, token_id: str) -> str:
        """Find trading pairs for a specific token."""
        try:
            # Get all token pairs across protocols
            all_pairs = self.client.get_all_token_pairs(token_id)
            
            # Get SaucerSwap-specific data
            saucer_pairs = self.client.get_saucerswap_token_pairs(token_id)
            
            # Calculate TVL for pairs
            pairs_with_tvl = []
            for pair in saucer_pairs[:10]:  # Limit to top 10
                pool_tvl = self.client.get_saucerswap_pool_tvl(pair.get("id", 0))
                
                token_a = pair.get("tokenA", {})
                token_b = pair.get("tokenB", {})
                
                pairs_with_tvl.append({
                    "pool_id": pair.get("id"),
                    "contract_id": pair.get("contractId"),
                    "pair_name": f"{token_a.get('symbol', 'Unknown')}/{token_b.get('symbol', 'Unknown')}",
                    "tvl_usd": pool_tvl,
                    "fee_tier": pair.get("fee", 0),
                    "liquidity": pair.get("liquidity", 0),
                    "paired_token": {
                        "id": token_b.get("id") if token_a.get("id") == token_id else token_a.get("id"),
                        "symbol": token_b.get("symbol") if token_a.get("id") == token_id else token_a.get("symbol"),
                        "name": token_b.get("name") if token_a.get("id") == token_id else token_a.get("name"),
                    }
                })
            
            # Sort by TVL
            pairs_with_tvl.sort(key=lambda x: x["tvl_usd"], reverse=True)
            
            result = {
                "token_id": token_id,
                "trading_pairs": pairs_with_tvl,
                "cross_protocol_data": all_pairs,
                "summary": {
                    "total_saucerswap_pairs": len(saucer_pairs),
                    "total_cross_protocol_pairs": all_pairs.get("total_pair_count", 0),
                    "available_protocols": all_pairs.get("protocols", []),
                    "best_liquidity_pool": pairs_with_tvl[0] if pairs_with_tvl else None,
                    "total_liquidity_usd": sum(pair["tvl_usd"] for pair in pairs_with_tvl),
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing token pairs: {str(e)}"


class SaucerSwapPriceComparisonTool(BaseTool):
    """Tool for comparing token prices across protocols."""
    
    name: str = "saucerswap_price_comparison"
    description: str = """
    Compare token prices between SaucerSwap and other protocols.
    Use this tool to:
    - Compare prices across multiple protocols
    - Find price discrepancies and arbitrage opportunities
    - Get aggregated price data from multiple sources
    - Analyze price consistency and market efficiency
    """
    args_schema: Type[BaseModel] = PriceComparisonInput
    
    def __init__(self, hedera_client=None):
        super().__init__()
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required. Install with: pip install hedera-defi")
        self.client = hedera_client or HederaDeFi()
    
    def _run(self, token_ids: List[str]) -> str:
        """Compare token prices across protocols."""
        try:
            comparisons = self.client.compare_token_prices_across_protocols(token_ids)
            
            comparison_results = []
            price_discrepancies = []
            
            for comparison in comparisons:
                token_id = comparison.get("token_id")
                price_data = comparison.get("price_data", {})
                protocol_availability = comparison.get("protocol_availability", {})
                
                # Calculate price discrepancy if multiple sources
                prices = price_data.get("prices", {})
                price_values = [p for p in prices.values() if isinstance(p, (int, float)) and p > 0]
                
                discrepancy = 0
                if len(price_values) > 1:
                    discrepancy = (max(price_values) - min(price_values)) / min(price_values) * 100
                    if discrepancy > 5:  # More than 5% discrepancy
                        price_discrepancies.append({
                            "token_id": token_id,
                            "symbol": comparison.get("symbol"),
                            "discrepancy_percent": discrepancy,
                            "min_price": min(price_values),
                            "max_price": max(price_values),
                        })
                
                comparison_results.append({
                    "token_id": token_id,
                    "symbol": comparison.get("symbol"),
                    "name": comparison.get("name"),
                    "prices": prices,
                    "average_price": price_data.get("average_price", 0),
                    "source_count": price_data.get("source_count", 0),
                    "protocol_availability": protocol_availability,
                    "price_discrepancy_percent": discrepancy,
                })
            
            result = {
                "price_comparisons": comparison_results,
                "arbitrage_alerts": price_discrepancies,
                "analysis_summary": {
                    "tokens_analyzed": len(token_ids),
                    "tokens_with_prices": len([c for c in comparison_results if c["average_price"] > 0]),
                    "price_discrepancies_found": len(price_discrepancies),
                    "best_arbitrage_opportunity": max(price_discrepancies, key=lambda x: x["discrepancy_percent"]) if price_discrepancies else None,
                    "market_efficiency": "High" if len(price_discrepancies) == 0 else "Medium" if len(price_discrepancies) < 3 else "Low"
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error comparing prices: {str(e)}"