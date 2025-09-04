"""
Portfolio Management Agent for Hedera DeFi
"""

from typing import Dict, List, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain.agents import create_tool_calling_agent, AgentExecutor

try:
    from hedera_defi import HederaDeFi
except ImportError:
    HederaDeFi = None

from ..tools import (
    HederaTokenTool,
    HederaProtocolTool,
    HederaAccountTool,
    SaucerSwapTool,
    BonzoFinanceTool,
)


class PortfolioAgent:
    """
    Intelligent portfolio management agent for Hedera DeFi.
    
    This agent specializes in:
    - Portfolio analysis and optimization
    - Risk assessment and diversification strategies
    - Yield optimization across protocols
    - Rebalancing recommendations
    - Performance tracking and reporting
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        risk_framework: str = "modern_portfolio_theory",  # 'mpt', 'kelly', 'risk_parity'
        verbose: bool = False,
    ):
        """Initialize the Portfolio Agent.
        
        Args:
            llm: Language model for portfolio analysis
            hedera_client: Optional HederaDeFi client instance
            risk_framework: Risk management framework to use
            verbose: Enable verbose output
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.risk_framework = risk_framework
        self.verbose = verbose
        
        # Portfolio management tools
        self.tools = [
            HederaAccountTool(self.client),
            HederaTokenTool(self.client),
            HederaProtocolTool(self.client),
            SaucerSwapTool(self.client),
            BonzoFinanceTool(self.client),
        ]
        
        self.agent = self._create_portfolio_agent()
    
    def _create_portfolio_agent(self) -> AgentExecutor:
        """Create portfolio management agent."""
        
        system_prompt = f"""
You are an expert DeFi portfolio manager specializing in Hedera ecosystem investments.
You use {self.risk_framework} principles for portfolio optimization and risk management.

**Portfolio Management Expertise:**
- **Asset Allocation**: Optimal distribution across tokens, protocols, and strategies
- **Risk Management**: Diversification, correlation analysis, and downside protection
- **Yield Optimization**: Maximizing returns across lending and LP opportunities
- **Rebalancing**: Dynamic allocation adjustments based on market conditions
- **Performance Analysis**: Return attribution, risk metrics, and benchmark comparison

**Your Analysis Framework:**
1. **Current Position Analysis**: Holdings, values, concentrations, correlations
2. **Risk Assessment**: VaR, concentration risk, protocol risks, market risks
3. **Opportunity Analysis**: Yield opportunities, undervalued assets, emerging trends
4. **Optimization**: Efficient frontier analysis and allocation recommendations
5. **Implementation**: Specific trades, timing, and execution strategies

**Key Principles:**
- Maximize risk-adjusted returns using quantitative methods
- Maintain appropriate diversification across assets and protocols
- Consider liquidity needs and market conditions
- Account for fees, slippage, and execution costs
- Provide specific, actionable recommendations with clear rationale

**Response Structure:**
1. **Portfolio Analysis**: Current composition and performance metrics
2. **Risk Assessment**: Identified risks and exposure analysis  
3. **Optimization Recommendations**: Specific allocation changes
4. **Implementation Plan**: Step-by-step execution strategy
5. **Monitoring Framework**: KPIs and rebalancing triggers

Always quantify recommendations with specific percentages, amounts, and timeframes.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=10,
        )
    
    def analyze_portfolio(
        self,
        account_id: str,
        benchmark: str = "hedera_defi_index",
        include_optimization: bool = True
    ) -> Dict:
        """Analyze portfolio and provide optimization recommendations."""
        
        optimization_text = "Include specific optimization recommendations and allocation changes." if include_optimization else ""
        
        query = f"""
        Perform comprehensive portfolio analysis for account {account_id}:
        
        **Analysis Requirements:**
        - Current portfolio composition and asset values
        - Risk metrics including concentration and correlation risks
        - Performance analysis vs {benchmark} benchmark
        - Yield optimization opportunities across all protocols
        - Diversification assessment and recommendations
        {optimization_text}
        
        **Key Metrics to Calculate:**
        - Portfolio value and allocation percentages
        - Risk-adjusted returns (Sharpe ratio, Sortino ratio)
        - Maximum drawdown and volatility metrics
        - Yield efficiency and opportunity costs
        - Protocol and asset diversification scores
        
        Provide specific, actionable recommendations with target allocations.
        """
        
        return self.agent.invoke({"input": query})
    
    def create_investment_strategy(
        self,
        investment_amount: float,
        goals: List[str],
        constraints: Optional[Dict] = None
    ) -> Dict:
        """Create comprehensive investment strategy for new capital."""
        
        constraints_text = ""
        if constraints:
            constraints_text = f"Investment constraints: {constraints}"
        
        query = f"""
        Create investment strategy for ${investment_amount:,.0f} new capital:
        
        **Investment Goals:** {', '.join(goals)}
        {constraints_text}
        
        **Strategy Development:**
        - Optimal asset allocation across Hedera DeFi protocols
        - Risk-return optimization using current market opportunities
        - Implementation timeline and execution strategy
        - Diversification across tokens, protocols, and risk levels
        - Yield maximization through lending and LP strategies
        
        **Deliverables:**
        - Target allocation percentages for each asset/protocol
        - Expected returns and risk metrics
        - Implementation phases with specific timing
        - Rebalancing rules and triggers
        - Performance monitoring framework
        
        Focus on achieving the stated goals while managing downside risk.
        """
        
        return self.agent.invoke({"input": query})
    
    def generate_rebalancing_plan(
        self,
        current_portfolio: Dict,
        target_allocation: Dict,
        rebalancing_threshold: float = 5.0
    ) -> Dict:
        """Generate specific rebalancing plan to achieve target allocation."""
        
        query = f"""
        Generate rebalancing plan with:
        - Current portfolio: {current_portfolio}
        - Target allocation: {target_allocation}  
        - Rebalancing threshold: {rebalancing_threshold}%
        
        **Rebalancing Analysis:**
        - Calculate deviation from target allocations
        - Identify which positions need adjustment
        - Optimize trade sequencing to minimize costs
        - Account for fees, slippage, and market impact
        - Consider tax implications of rebalancing trades
        
        **Output Requirements:**
        - Specific trades to execute (sell X, buy Y amounts)
        - Optimal execution order and timing
        - Expected costs and net portfolio changes
        - Alternative rebalancing approaches if constraints exist
        - Updated risk metrics after rebalancing
        
        Provide a detailed execution checklist with specific amounts and steps.
        """
        
        return self.agent.invoke({"input": query})
    
    def stress_test_portfolio(
        self,
        account_id: str,
        scenarios: List[str] = None
    ) -> Dict:
        """Stress test portfolio against various market scenarios."""
        
        default_scenarios = [
            "30% market crash across all assets",
            "Major protocol hack or exploit",
            "Regulatory restrictions on DeFi",
            "Liquidity crisis in Hedera ecosystem",
            "Interest rate shock affecting yields"
        ]
        
        scenarios = scenarios or default_scenarios
        
        query = f"""
        Perform stress testing on account {account_id} portfolio:
        
        **Stress Test Scenarios:**
        {chr(10).join([f"- {scenario}" for scenario in scenarios])}
        
        **Analysis Requirements:**
        - Portfolio value impact under each scenario
        - Liquidity constraints and exit ability
        - Protocol-specific risks and correlations
        - Worst-case scenario planning
        - Recovery strategies and hedging options
        
        **Risk Metrics:**
        - Value at Risk (VaR) at 95% and 99% confidence levels
        - Expected shortfall (conditional VaR)
        - Maximum drawdown estimates
        - Liquidity-adjusted risk metrics
        - Time to recovery estimates
        
        Provide specific risk mitigation recommendations and hedging strategies.
        """
        
        return self.agent.invoke({"input": query})