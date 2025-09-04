"""
Bonzo Finance Lending Tools for LangChain
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
try:
    from hedera_defi import HederaDeFi
except ImportError:
    # Fallback for development
    HederaDeFi = None


class BonzoAnalysisInput(BaseModel):
    """Input for Bonzo Finance analysis operations."""
    analysis_type: str = Field(
        description="Type of analysis: 'overview', 'markets', 'lending', 'borrowing'",
        default="overview"
    )
    min_apy: Optional[float] = Field(default=0, description="Minimum APY for filtering opportunities")


class LendingOpportunityInput(BaseModel):
    """Input for finding lending opportunities."""
    min_apy: Optional[float] = Field(default=5.0, description="Minimum supply APY")
    risk_level: Optional[str] = Field(default=None, description="Risk level filter: 'Low', 'Medium', 'High'")


class BorrowingAnalysisInput(BaseModel):
    """Input for borrowing analysis."""
    max_apy: Optional[float] = Field(default=20.0, description="Maximum acceptable borrow APY")
    min_ltv: Optional[float] = Field(default=0.5, description="Minimum loan-to-value ratio")


class BonzoFinanceTool(BaseTool):
    """Comprehensive Bonzo Finance lending protocol analysis tool."""
    
    name: str = "bonzo_finance_analyzer"
    description: str = """
    Comprehensive analysis tool for Bonzo Finance lending protocol on Hedera.
    Use this tool to:
    - Get Bonzo Finance protocol overview and market statistics
    - Find best lending opportunities with competitive APY rates
    - Analyze borrowing options and rates across all assets
    - Calculate lending/borrowing strategies and risk assessments
    - Monitor protocol utilization and liquidity metrics
    """
    args_schema: Type[BaseModel] = BonzoAnalysisInput
    
    def __init__(self, hedera_client=None):
        super().__init__()
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
        self.client = hedera_client or HederaDeFi()
    
    def _run(self, analysis_type: str = "overview", min_apy: Optional[float] = 0) -> str:
        """Analyze Bonzo Finance lending protocol."""
        try:
            if analysis_type == "overview":
                return self._get_bonzo_overview()
            elif analysis_type == "markets":
                return self._get_market_analysis()
            elif analysis_type == "lending":
                return self._get_lending_opportunities(min_apy or 0)
            elif analysis_type == "borrowing":
                return self._get_borrowing_analysis()
            else:
                return json.dumps({
                    "error": "Invalid analysis_type",
                    "valid_types": ["overview", "markets", "lending", "borrowing"]
                })
                
        except Exception as e:
            return f"Error analyzing Bonzo Finance: {str(e)}"
    
    def _get_bonzo_overview(self) -> str:
        """Get comprehensive Bonzo Finance protocol overview."""
        try:
            # Get data efficiently with single API call
            bonzo_data = self.client.get_bonzo_markets()
            totals = self.client.get_bonzo_total_markets(bonzo_data)
            reserves = self.client.get_bonzo_reserves(bonzo_data)
            
            # Calculate key metrics
            active_reserves = [r for r in reserves if r.get("active", False)]
            total_apy = sum(r.get("supply_apy", 0) for r in active_reserves)
            avg_apy = total_apy / len(active_reserves) if active_reserves else 0
            
            # Risk assessment
            high_util_reserves = [r for r in active_reserves if r.get("utilization_rate", 0) > 80]
            
            overview = {
                "protocol_metrics": {
                    "network": totals.get("network_name", "Hedera"),
                    "chain_id": totals.get("chain_id"),
                    "total_reserves": totals.get("total_reserves", 0),
                    "active_reserves": len(active_reserves),
                    "timestamp": totals.get("timestamp"),
                },
                "financial_metrics": {
                    "total_supplied": totals.get("total_market_supplied", {}),
                    "total_borrowed": totals.get("total_market_borrowed", {}),
                    "total_liquidity": totals.get("total_market_liquidity", {}),
                    "total_reserves_amount": totals.get("total_market_reserve", {}),
                },
                "yield_metrics": {
                    "average_supply_apy": avg_apy,
                    "highest_apy": max([r.get("supply_apy", 0) for r in active_reserves]) if active_reserves else 0,
                    "best_lending_asset": max(active_reserves, key=lambda x: x.get("supply_apy", 0)).get("symbol") if active_reserves else None,
                },
                "risk_metrics": {
                    "high_utilization_count": len(high_util_reserves),
                    "high_utilization_assets": [r.get("symbol") for r in high_util_reserves],
                    "protocol_health": "Good" if len(high_util_reserves) < 3 else "Moderate" if len(high_util_reserves) < 5 else "High Risk",
                }
            }
            
            return json.dumps(overview, indent=2)
            
        except Exception as e:
            return f"Error getting Bonzo overview: {str(e)}"
    
    def _get_market_analysis(self) -> str:
        """Get detailed market analysis for all Bonzo reserves."""
        try:
            reserves = self.client.get_bonzo_reserves()
            
            markets_data = []
            for reserve in reserves:
                if reserve.get("active", False):
                    risk_level = self.client._assess_bonzo_risk(reserve)
                    
                    markets_data.append({
                        "symbol": reserve.get("symbol"),
                        "supply_apy": reserve.get("supply_apy", 0),
                        "variable_borrow_apy": reserve.get("variable_borrow_apy", 0),
                        "stable_borrow_apy": reserve.get("stable_borrow_apy", 0),
                        "utilization_rate": reserve.get("utilization_rate", 0),
                        "ltv": reserve.get("ltv", 0),
                        "liquidation_threshold": reserve.get("liquidation_threshold", 0),
                        "liquidation_bonus": reserve.get("liquidation_bonus", 0),
                        "risk_level": risk_level,
                        "lending_enabled": reserve.get("active", False),
                        "borrowing_enabled": reserve.get("variable_borrowing_enabled", False),
                        "available_liquidity": reserve.get("available_liquidity", {}),
                        "total_supplied": reserve.get("total_supplied", {}),
                        "total_borrowed": reserve.get("total_borrowed", {}),
                    })
            
            # Sort by supply APY
            markets_data.sort(key=lambda x: x["supply_apy"], reverse=True)
            
            result = {
                "active_markets": markets_data,
                "market_summary": {
                    "total_active_markets": len(markets_data),
                    "lending_markets": len([m for m in markets_data if m["lending_enabled"]]),
                    "borrowing_markets": len([m for m in markets_data if m["borrowing_enabled"]]),
                    "high_yield_markets": len([m for m in markets_data if m["supply_apy"] > 10]),
                    "low_risk_markets": len([m for m in markets_data if m["risk_level"] == "Low"]),
                    "best_yield": max([m["supply_apy"] for m in markets_data]) if markets_data else 0,
                    "lowest_borrow_rate": min([m["variable_borrow_apy"] for m in markets_data if m["borrowing_enabled"]]) if markets_data else 0,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing markets: {str(e)}"
    
    def _get_lending_opportunities(self, min_apy: float) -> str:
        """Find best lending opportunities."""
        try:
            lending_rates = self.client.get_bonzo_best_lending_rates(min_apy=min_apy)
            
            opportunities = []
            for rate in lending_rates:
                opportunities.append({
                    "asset": rate.get("token"),
                    "supply_apy": rate.get("supply_apy", 0),
                    "available_liquidity": rate.get("available_liquidity", "0"),
                    "utilization_rate": rate.get("utilization_rate", 0),
                    "risk_level": rate.get("risk_level", "Unknown"),
                    "ltv": rate.get("ltv", 0),
                    "liquidation_threshold": rate.get("liquidation_threshold", 0),
                    "strategy_notes": self._generate_lending_strategy(rate),
                })
            
            # Calculate portfolio recommendations
            low_risk_assets = [o for o in opportunities if o["risk_level"] == "Low"]
            high_yield_assets = [o for o in opportunities if o["supply_apy"] > 15]
            
            result = {
                "lending_opportunities": opportunities,
                "portfolio_recommendations": {
                    "conservative_portfolio": low_risk_assets[:3],
                    "aggressive_portfolio": high_yield_assets[:3],
                    "balanced_portfolio": opportunities[:5],  # Mix of best overall
                },
                "market_insights": {
                    "total_opportunities": len(opportunities),
                    "best_apy": max([o["supply_apy"] for o in opportunities]) if opportunities else 0,
                    "average_apy": sum([o["supply_apy"] for o in opportunities]) / len(opportunities) if opportunities else 0,
                    "low_risk_count": len(low_risk_assets),
                    "high_yield_count": len(high_yield_assets),
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error finding lending opportunities: {str(e)}"
    
    def _get_borrowing_analysis(self) -> str:
        """Analyze borrowing options and rates."""
        try:
            borrowing_rates = self.client.get_bonzo_borrowing_rates()
            
            borrowing_options = []
            for option in borrowing_rates:
                borrowing_options.append({
                    "asset": option.get("token"),
                    "variable_borrow_apy": option.get("variable_borrow_apy", 0),
                    "stable_borrow_apy": option.get("stable_borrow_apy", 0),
                    "recommended_rate": "variable" if option.get("variable_borrow_apy", 0) < option.get("stable_borrow_apy", 0) else "stable",
                    "utilization_rate": option.get("utilization_rate", 0),
                    "ltv": option.get("ltv", 0),
                    "liquidation_threshold": option.get("liquidation_threshold", 0),
                    "liquidation_bonus": option.get("liquidation_bonus", 0),
                    "available_to_borrow": option.get("available_to_borrow", "0"),
                    "borrowing_strategy": self._generate_borrowing_strategy(option),
                })
            
            # Find best opportunities
            cheapest_rates = sorted(borrowing_options, key=lambda x: x["variable_borrow_apy"])[:5]
            high_ltv_options = [o for o in borrowing_options if o["ltv"] > 0.7]
            
            result = {
                "borrowing_options": borrowing_options,
                "recommended_strategies": {
                    "cheapest_borrowing": cheapest_rates,
                    "high_leverage_options": high_ltv_options,
                    "short_term_borrowing": [o for o in cheapest_rates if o["recommended_rate"] == "variable"],
                    "long_term_borrowing": [o for o in borrowing_options if o["recommended_rate"] == "stable"],
                },
                "borrowing_insights": {
                    "total_assets_available": len(borrowing_options),
                    "cheapest_rate": min([o["variable_borrow_apy"] for o in borrowing_options]) if borrowing_options else 0,
                    "average_borrow_rate": sum([o["variable_borrow_apy"] for o in borrowing_options]) / len(borrowing_options) if borrowing_options else 0,
                    "high_ltv_assets": len(high_ltv_options),
                    "best_leverage_asset": max(high_ltv_options, key=lambda x: x["ltv"])["asset"] if high_ltv_options else None,
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing borrowing options: {str(e)}"
    
    def _generate_lending_strategy(self, rate_data: Dict) -> str:
        """Generate lending strategy recommendations."""
        apy = rate_data.get("supply_apy", 0)
        risk = rate_data.get("risk_level", "Unknown")
        utilization = rate_data.get("utilization_rate", 0)
        
        if risk == "Low" and apy > 10:
            return "Excellent opportunity - Low risk with high yield"
        elif risk == "Low":
            return "Safe option for conservative portfolios"
        elif apy > 20:
            return "High yield opportunity - Monitor risk closely"
        elif utilization > 90:
            return "High utilization - Potential for rate volatility"
        else:
            return "Standard lending opportunity"
    
    def _generate_borrowing_strategy(self, option_data: Dict) -> str:
        """Generate borrowing strategy recommendations."""
        var_rate = option_data.get("variable_borrow_apy", 0)
        stable_rate = option_data.get("stable_borrow_apy", 0)
        ltv = option_data.get("ltv", 0)
        utilization = option_data.get("utilization_rate", 0)
        
        if var_rate < 5:
            return "Excellent borrowing rates - Consider for leverage strategies"
        elif ltv > 0.8:
            return "High leverage available - Use with caution"
        elif utilization > 85:
            return "High utilization - Rates may increase soon"
        elif stable_rate < var_rate * 1.2:
            return "Consider stable rate for rate certainty"
        else:
            return "Variable rate recommended for flexibility"


class BonzoLendingOpportunityTool(BaseTool):
    """Specialized tool for finding optimal lending opportunities on Bonzo Finance."""
    
    name: str = "bonzo_lending_opportunities"
    description: str = """
    Find optimal lending opportunities on Bonzo Finance based on APY and risk preferences.
    Use this tool to:
    - Find lending opportunities above specified APY thresholds
    - Filter opportunities by risk level (Low, Medium, High)
    - Get detailed analysis of lending strategies
    - Compare risk-adjusted returns across assets
    """
    args_schema: Type[BaseModel] = LendingOpportunityInput
    
    def __init__(self, hedera_client=None):
        super().__init__()
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
        self.client = hedera_client or HederaDeFi()
    
    def _run(self, min_apy: Optional[float] = 5.0, risk_level: Optional[str] = None) -> str:
        """Find optimal lending opportunities."""
        try:
            lending_rates = self.client.get_bonzo_best_lending_rates(min_apy=min_apy or 5.0)
            
            # Filter by risk level if specified
            if risk_level:
                lending_rates = [r for r in lending_rates if r.get("risk_level") == risk_level]
            
            if not lending_rates:
                return json.dumps({
                    "message": f"No lending opportunities found with APY >= {min_apy}%" + 
                              (f" and risk level {risk_level}" if risk_level else ""),
                    "suggestions": [
                        "Try lowering the minimum APY requirement",
                        "Consider different risk levels",
                        "Check back later as rates change frequently"
                    ]
                })
            
            opportunities = []
            for rate in lending_rates:
                apy = rate.get("supply_apy", 0)
                risk = rate.get("risk_level", "Unknown")
                
                # Calculate risk-adjusted return
                risk_multiplier = {"Low": 1.0, "Medium": 0.8, "High": 0.6}.get(risk, 0.7)
                risk_adjusted_apy = apy * risk_multiplier
                
                opportunities.append({
                    "asset": rate.get("token"),
                    "supply_apy": apy,
                    "risk_level": risk,
                    "risk_adjusted_apy": risk_adjusted_apy,
                    "utilization_rate": rate.get("utilization_rate", 0),
                    "available_liquidity": rate.get("available_liquidity", "0"),
                    "ltv": rate.get("ltv", 0),
                    "liquidation_threshold": rate.get("liquidation_threshold", 0),
                    "recommendation_score": self._calculate_recommendation_score(rate),
                    "strategy": self._generate_detailed_strategy(rate),
                })
            
            # Sort by recommendation score
            opportunities.sort(key=lambda x: x["recommendation_score"], reverse=True)
            
            result = {
                "lending_opportunities": opportunities,
                "top_recommendations": opportunities[:3],
                "analysis": {
                    "opportunities_found": len(opportunities),
                    "filters_applied": {
                        "min_apy": min_apy,
                        "risk_level": risk_level,
                    },
                    "best_raw_apy": max([o["supply_apy"] for o in opportunities]) if opportunities else 0,
                    "best_risk_adjusted": max([o["risk_adjusted_apy"] for o in opportunities]) if opportunities else 0,
                    "risk_distribution": {
                        "low_risk": len([o for o in opportunities if o["risk_level"] == "Low"]),
                        "medium_risk": len([o for o in opportunities if o["risk_level"] == "Medium"]),
                        "high_risk": len([o for o in opportunities if o["risk_level"] == "High"]),
                    }
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error finding lending opportunities: {str(e)}"
    
    def _calculate_recommendation_score(self, rate_data: Dict) -> float:
        """Calculate a recommendation score (0-100) based on multiple factors."""
        apy = rate_data.get("supply_apy", 0)
        risk = rate_data.get("risk_level", "High")
        utilization = rate_data.get("utilization_rate", 0)
        ltv = rate_data.get("ltv", 0)
        
        # Base score from APY (0-40 points)
        apy_score = min(apy * 2, 40)
        
        # Risk score (0-30 points) - lower risk is better
        risk_scores = {"Low": 30, "Medium": 20, "High": 10}
        risk_score = risk_scores.get(risk, 5)
        
        # Utilization score (0-20 points) - moderate utilization is best
        if 50 <= utilization <= 80:
            util_score = 20
        elif 30 <= utilization < 50 or 80 < utilization <= 90:
            util_score = 15
        elif utilization < 30:
            util_score = 10
        else:  # > 90%
            util_score = 5
        
        # LTV score (0-10 points) - higher LTV is better for collateral
        ltv_score = ltv * 10
        
        return apy_score + risk_score + util_score + ltv_score
    
    def _generate_detailed_strategy(self, rate_data: Dict) -> Dict:
        """Generate detailed lending strategy."""
        apy = rate_data.get("supply_apy", 0)
        risk = rate_data.get("risk_level", "Unknown")
        utilization = rate_data.get("utilization_rate", 0)
        ltv = rate_data.get("ltv", 0)
        
        strategy = {
            "recommended_allocation": "High" if risk == "Low" and apy > 10 else "Medium" if risk == "Low" or apy > 15 else "Low",
            "time_horizon": "Long-term" if risk == "Low" else "Medium-term" if risk == "Medium" else "Short-term",
            "monitoring_frequency": "Weekly" if risk == "Low" else "Daily" if risk == "High" else "Bi-weekly",
            "exit_conditions": [
                f"APY drops below {apy * 0.7:.1f}%",
                f"Utilization exceeds 95%" if utilization < 90 else "Monitor liquidations closely",
                "Risk level increases" if risk == "Low" else "Market conditions deteriorate"
            ],
            "complementary_assets": "Consider diversifying with other low-risk assets" if risk == "Low" else "Balance with conservative options",
        }
        
        return strategy