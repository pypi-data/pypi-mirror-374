"""
Arbitrage Detection and Analysis Chain
"""

import json
from typing import Dict, List, Optional, Any
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

try:
    from hedera_defi import HederaDeFi
except ImportError:
    HederaDeFi = None

from ..tools import SaucerSwapTool, BonzoFinanceTool, HederaTokenTool


class ArbitrageOpportunity(BaseModel):
    """Structured arbitrage opportunity output."""
    
    token_id: str = Field(description="Token ID for arbitrage")
    token_symbol: str = Field(description="Token symbol")
    opportunity_type: str = Field(description="Type of arbitrage: price, yield, cross-protocol")
    profit_potential_percent: float = Field(description="Expected profit percentage")
    profit_potential_usd: float = Field(description="Expected profit in USD for reference amount")
    execution_complexity: str = Field(description="Execution complexity: simple, moderate, complex")
    capital_required_usd: float = Field(description="Minimum capital required")
    execution_steps: List[str] = Field(description="Step-by-step execution plan")
    risks: List[str] = Field(description="Key risks and considerations")
    time_sensitivity: str = Field(description="Time sensitivity: immediate, short-term, flexible")


class ArbitrageAnalysisOutput(BaseModel):
    """Complete arbitrage analysis output."""
    
    opportunities: List[ArbitrageOpportunity] = Field(description="Identified arbitrage opportunities")
    market_efficiency: str = Field(description="Market efficiency assessment")
    best_opportunity: Optional[ArbitrageOpportunity] = Field(description="Best overall opportunity")
    execution_priority: List[str] = Field(description="Execution priority order by token symbol")
    total_potential_profit: float = Field(description="Total potential profit across all opportunities")


class ArbitrageChain:
    """
    Specialized chain for detecting and analyzing arbitrage opportunities across Hedera DeFi.
    
    This chain systematically:
    1. Scans for price discrepancies across protocols
    2. Analyzes yield arbitrage opportunities  
    3. Calculates execution costs and net profits
    4. Ranks opportunities by risk-adjusted returns
    5. Provides detailed execution strategies
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        min_profit_threshold: float = 1.0,
        max_execution_cost: float = 50.0,
    ):
        """Initialize the Arbitrage Chain.
        
        Args:
            llm: Language model for arbitrage analysis
            hedera_client: Optional HederaDeFi client instance
            min_profit_threshold: Minimum profit percentage to consider
            max_execution_cost: Maximum execution cost in USD
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.min_profit_threshold = min_profit_threshold
        self.max_execution_cost = max_execution_cost
        
        # Initialize arbitrage detection tools
        self.saucerswap_tool = SaucerSwapTool(self.client)
        self.bonzo_tool = BonzoFinanceTool(self.client)
        self.token_tool = HederaTokenTool(self.client)
        
        # Create the arbitrage detection chain
        self.chain = self._create_arbitrage_chain()
    
    def _create_arbitrage_chain(self) -> Runnable:
        """Create arbitrage detection and analysis chain."""
        
        arbitrage_prompt = ChatPromptTemplate.from_template("""
You are an expert arbitrage trader analyzing Hedera DeFi protocols for profit opportunities.

**Available Data:**
Price Data: {price_data}
SaucerSwap Pools: {saucerswap_pools}
Bonzo Finance Rates: {bonzo_rates}
Cross-Protocol Comparison: {cross_protocol_data}

**Analysis Criteria:**
- Minimum profit threshold: {min_profit_percent}%
- Maximum execution cost: ${max_execution_cost}
- Focus on opportunities with clear execution paths

**Arbitrage Types to Analyze:**
1. **Price Arbitrage**: Same token trading at different prices across venues
2. **Yield Arbitrage**: Borrow on one protocol, lend on another for profit
3. **Cross-Protocol**: Opportunities between SaucerSwap trading and Bonzo lending
4. **Temporal Arbitrage**: Rate changes creating temporary profit windows

**Required Analysis:**
For each opportunity found:
- Calculate net profit after all fees and costs
- Assess execution complexity and time requirements
- Identify specific steps for implementation
- Evaluate risks including liquidity, timing, and protocol risks
- Determine optimal capital allocation

**Output Requirements:**
Return a JSON object with the exact structure specified in the schema.
Include only profitable opportunities that meet the minimum criteria.
Rank opportunities by risk-adjusted profit potential.

Be specific about:
- Exact profit calculations with fees included
- Step-by-step execution instructions
- Capital requirements and timing considerations
- Risk mitigation strategies
""")
        
        # Create parser for structured output
        parser = JsonOutputParser(pydantic_object=ArbitrageAnalysisOutput)
        
        # Chain: gather data -> analyze -> parse structured output
        chain = (
            {
                "price_data": lambda _: self._gather_price_data(),
                "saucerswap_pools": lambda _: self._gather_saucerswap_data(),
                "bonzo_rates": lambda _: self._gather_bonzo_rates(),
                "cross_protocol_data": lambda _: self._gather_cross_protocol_data(),
                "min_profit_percent": lambda _: self.min_profit_threshold,
                "max_execution_cost": lambda _: self.max_execution_cost,
            }
            | arbitrage_prompt
            | self.llm
            | parser
        )
        
        return chain
    
    def _gather_price_data(self) -> str:
        """Gather price data across protocols."""
        try:
            # Get price comparison for active tokens
            active_tokens = self.saucerswap_tool._get_token_analysis(20)
            return active_tokens
        except Exception as e:
            return f"Error gathering price data: {str(e)}"
    
    def _gather_saucerswap_data(self) -> str:
        """Gather SaucerSwap pool and trading data."""
        try:
            pools_data = self.saucerswap_tool._get_top_pools(15)
            return pools_data
        except Exception as e:
            return f"Error gathering SaucerSwap data: {str(e)}"
    
    def _gather_bonzo_rates(self) -> str:
        """Gather Bonzo Finance lending rates."""
        try:
            rates_data = self.bonzo_tool._get_lending_opportunities(0)  # All rates
            return rates_data
        except Exception as e:
            return f"Error gathering Bonzo rates: {str(e)}"
    
    def _gather_cross_protocol_data(self) -> str:
        """Gather cross-protocol comparison data."""
        try:
            # Find tokens available in both protocols for arbitrage
            arbitrage_data = self.saucerswap_tool._find_arbitrage_opportunities()
            return arbitrage_data
        except Exception as e:
            return f"Error gathering cross-protocol data: {str(e)}"
    
    def detect_opportunities(
        self,
        focus_tokens: Optional[List[str]] = None,
        capital_amount: float = 10000.0
    ) -> Dict:
        """Detect arbitrage opportunities with specified parameters."""
        try:
            # Run the arbitrage detection chain
            result = self.chain.invoke({})
            
            # Filter and enhance results based on parameters
            if focus_tokens:
                filtered_opportunities = [
                    opp for opp in result.get("opportunities", [])
                    if opp.get("token_symbol", "").upper() in [t.upper() for t in focus_tokens]
                ]
                result["opportunities"] = filtered_opportunities
                result["filtered_by_tokens"] = focus_tokens
            
            # Calculate position sizing for given capital
            for opportunity in result.get("opportunities", []):
                max_position = min(capital_amount, opportunity.get("capital_required_usd", 0) * 2)
                opportunity["recommended_position_usd"] = max_position
                opportunity["expected_profit_usd"] = max_position * (opportunity.get("profit_potential_percent", 0) / 100)
            
            # Update best opportunity based on capital
            if result.get("opportunities"):
                best_opp = max(
                    result["opportunities"],
                    key=lambda x: x.get("expected_profit_usd", 0)
                )
                result["best_opportunity"] = best_opp
            
            result["analysis_parameters"] = {
                "capital_amount": capital_amount,
                "min_profit_threshold": self.min_profit_threshold,
                "max_execution_cost": self.max_execution_cost,
                "focus_tokens": focus_tokens,
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Arbitrage detection failed: {str(e)}",
                "opportunities": [],
                "market_efficiency": "unknown",
                "analysis_parameters": {
                    "capital_amount": capital_amount,
                    "error": str(e)
                }
            }
    
    def monitor_opportunities(
        self,
        watch_list: List[str],
        check_interval_minutes: int = 15
    ) -> Dict:
        """Monitor specific opportunities for execution timing."""
        
        query = f"""
        Set up monitoring for arbitrage opportunities:
        
        **Watch List:** {', '.join(watch_list)}
        **Check Interval:** Every {check_interval_minutes} minutes
        
        Create monitoring strategy including:
        - Key metrics to track for each opportunity
        - Alert conditions for immediate execution
        - Automated checks for profit threshold maintenance
        - Risk monitoring and stop-loss triggers
        - Market condition assessments
        
        Provide monitoring framework with specific thresholds and actions.
        """
        
        try:
            # Analyze current opportunities for watch list
            current_analysis = self.detect_opportunities(focus_tokens=watch_list)
            
            monitoring_prompt = ChatPromptTemplate.from_template("""
            Based on current arbitrage analysis:
            {current_analysis}
            
            Create monitoring strategy for: {watch_list}
            Check interval: {check_interval} minutes
            
            Provide monitoring framework including:
            - Alert thresholds for each opportunity
            - Execution triggers and stop conditions  
            - Risk monitoring parameters
            - Performance tracking metrics
            
            Return as structured monitoring plan.
            """)
            
            monitoring_analysis = (
                monitoring_prompt
                | self.llm
            ).invoke({
                "current_analysis": json.dumps(current_analysis, indent=2),
                "watch_list": watch_list,
                "check_interval": check_interval_minutes,
            })
            
            return {
                "monitoring_plan": monitoring_analysis.content if hasattr(monitoring_analysis, 'content') else str(monitoring_analysis),
                "current_opportunities": current_analysis,
                "watch_list": watch_list,
                "check_interval_minutes": check_interval_minutes,
            }
            
        except Exception as e:
            return {"error": f"Monitoring setup failed: {str(e)}"}