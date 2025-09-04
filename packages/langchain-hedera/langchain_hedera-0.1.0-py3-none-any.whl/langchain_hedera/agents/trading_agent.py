"""
Specialized Trading Analysis Agent for Hedera DeFi
"""

from typing import Dict, List, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain.agents import create_tool_calling_agent, AgentExecutor

try:
    from hedera_defi import HederaDeFi
except ImportError:
    HederaDeFi = None

from ..tools import SaucerSwapTool, HederaTokenTool


class TradingAnalysisAgent:
    """
    Specialized agent for trading analysis and DEX operations on Hedera.
    
    This agent focuses on:
    - DEX trading analysis and opportunities
    - Price analysis and arbitrage detection
    - Liquidity pool performance assessment
    - Trading strategy recommendations
    - Market timing and entry/exit analysis
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        focus_dex: str = "saucerswap",
        verbose: bool = False,
    ):
        """Initialize the Trading Analysis Agent.
        
        Args:
            llm: Language model for agent reasoning
            hedera_client: Optional HederaDeFi client instance
            focus_dex: Primary DEX to focus on ('saucerswap', 'heliswap', 'all')
            verbose: Enable verbose output
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.focus_dex = focus_dex
        self.verbose = verbose
        
        # Initialize trading-focused tools
        self.tools = [
            SaucerSwapTool(self.client),
            HederaTokenTool(self.client),
        ]
        
        # Create the specialized trading agent
        self.agent = self._create_trading_agent()
    
    def _create_trading_agent(self) -> AgentExecutor:
        """Create specialized trading analysis agent."""
        
        system_prompt = f"""
You are an expert cryptocurrency trading analyst specializing in Hedera DeFi protocols.
Your primary focus is on DEX trading analysis, with expertise in {self.focus_dex.upper()}.

**Your Trading Expertise:**
- **DEX Analysis**: Deep understanding of automated market makers (AMMs) and liquidity pools
- **Price Discovery**: Expert at analyzing price discrepancies and arbitrage opportunities  
- **Market Microstructure**: Knowledge of slippage, fees, and optimal trading routes
- **Risk Management**: Understanding of impermanent loss, liquidity risks, and market volatility
- **Strategy Development**: Creation of data-driven trading and liquidity strategies

**Your Analysis Framework:**
1. **Market Structure Analysis**: Pool liquidity, fee tiers, trading volumes
2. **Price Efficiency**: Cross-pool price comparison and arbitrage identification
3. **Liquidity Analysis**: Depth, utilization, and provider incentives
4. **Risk Assessment**: Impermanent loss potential, concentration risks
5. **Strategy Optimization**: Entry/exit timing, position sizing, risk management

**Key Responsibilities:**
- Find profitable trading opportunities with clear risk/reward ratios
- Identify optimal liquidity provision strategies
- Monitor market conditions for timing recommendations
- Provide specific, actionable trading insights
- Calculate potential profits, losses, and required capital

**Response Format:**
Structure your analysis with:
1. **Market Overview**: Current conditions and key metrics
2. **Trading Opportunities**: Specific trades with entry/exit criteria
3. **Risk Analysis**: Potential losses and risk mitigation strategies
4. **Profit Projections**: Expected returns and timeframes
5. **Execution Plan**: Step-by-step trading strategy

Always use real market data from your tools and provide specific numbers and metrics.
Be precise about fees, slippage, and execution costs in your recommendations.
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
            max_iterations=8,
        )
    
    def find_arbitrage_opportunities(
        self, 
        min_profit_percent: float = 2.0,
        max_gas_cost: float = 100.0
    ) -> Dict:
        """Find arbitrage opportunities across Hedera DEXs."""
        
        query = f"""
        Find arbitrage opportunities with these criteria:
        - Minimum profit: {min_profit_percent}% after fees
        - Maximum execution cost: ${max_gas_cost} USD equivalent
        
        Analyze price differences between SaucerSwap and other protocols.
        Calculate net profit after fees and provide execution strategies.
        Include specific token pairs, amounts, and execution steps.
        """
        
        return self.agent.invoke({"input": query})
    
    def analyze_trading_pair(
        self, 
        token_a: str, 
        token_b: str, 
        amount: Optional[float] = None
    ) -> Dict:
        """Analyze a specific trading pair for optimal execution."""
        
        amount_text = f" for a trade size of {amount}" if amount else ""
        
        query = f"""
        Analyze the {token_a}/{token_b} trading pair{amount_text}:
        
        - Find all available liquidity pools for this pair
        - Calculate optimal routing and slippage estimates
        - Assess market depth and liquidity quality
        - Identify best execution strategy (single pool vs routing)
        - Analyze recent trading activity and volume trends
        - Provide timing recommendations based on market conditions
        
        Include specific pool addresses, fee tiers, and execution costs.
        """
        
        return self.agent.invoke({"input": query})
    
    def optimize_liquidity_strategy(
        self,
        tokens_available: List[str],
        investment_amount: float,
        risk_tolerance: str = "medium"
    ) -> Dict:
        """Optimize liquidity provision strategy for given tokens and capital."""
        
        query = f"""
        Optimize liquidity provision strategy with:
        - Available tokens: {', '.join(tokens_available)}
        - Investment amount: ${investment_amount:,.2f} USD equivalent
        - Risk tolerance: {risk_tolerance}
        
        Analyze:
        - Best pools for liquidity provision with these tokens
        - Expected APY from fees and potential rewards
        - Impermanent loss risks and mitigation strategies
        - Optimal allocation across multiple pools
        - Entry and exit timing recommendations
        
        Provide a specific allocation strategy with expected returns and risks.
        """
        
        return self.agent.invoke({"input": query})
    
    def assess_market_conditions(
        self,
        timeframe: str = "24h",
        include_predictions: bool = False
    ) -> Dict:
        """Assess current market conditions for trading decisions."""
        
        prediction_text = "Include short-term market predictions and trend analysis." if include_predictions else ""
        
        query = f"""
        Assess Hedera DeFi market conditions over the last {timeframe}:
        
        - Overall market trend and momentum indicators
        - Trading volume and liquidity changes
        - Whale activity and its market impact
        - Protocol performance and TVL movements
        - Risk factors and market inefficiencies
        {prediction_text}
        
        Provide trading recommendations based on current market structure.
        Include specific opportunities and risks for the near term.
        """
        
        return self.agent.invoke({"input": query})
    
    def analyze_token_momentum(
        self,
        tokens: List[str],
        analysis_depth: str = "standard"
    ) -> Dict:
        """Analyze momentum and trading signals for specific tokens."""
        
        depth_instructions = {
            "quick": "Provide basic price and volume analysis",
            "standard": "Include price trends, trading pairs, and market position analysis", 
            "deep": "Comprehensive analysis including cross-protocol data, whale activity, and strategic positioning"
        }
        
        query = f"""
        Analyze trading momentum for tokens: {', '.join(tokens)}
        
        Analysis depth: {analysis_depth}
        {depth_instructions.get(analysis_depth, depth_instructions['standard'])}
        
        For each token provide:
        - Current price and recent performance
        - Trading volume and liquidity metrics
        - Available trading pairs and best execution venues
        - Market position and competitive analysis
        - Trading signals and momentum indicators
        - Strategic recommendations (buy/sell/hold/watch)
        
        Rank tokens by trading opportunity and provide reasoning.
        """
        
        return self.agent.invoke({"input": query})


class TradingStrategyAgent:
    """
    Advanced trading strategy development agent for Hedera DeFi.
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        strategy_focus: str = "yield",  # 'yield', 'arbitrage', 'momentum', 'risk'
        verbose: bool = False,
    ):
        """Initialize the Trading Strategy Agent.
        
        Args:
            llm: Language model for strategy development
            hedera_client: Optional HederaDeFi client instance  
            strategy_focus: Primary strategy focus area
            verbose: Enable verbose output
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.strategy_focus = strategy_focus
        self.verbose = verbose
        
        # All tools for comprehensive strategy development
        self.tools = [
            HederaTokenTool(self.client),
            HederaProtocolTool(self.client),
            SaucerSwapTool(self.client),
            BonzoFinanceTool(self.client),
            HederaWhaleTool(self.client),
        ]
        
        self.agent = self._create_strategy_agent()
    
    def _create_strategy_agent(self) -> AgentExecutor:
        """Create strategy development agent."""
        
        strategy_prompts = {
            "yield": "Focus on yield optimization and farming strategies",
            "arbitrage": "Focus on arbitrage detection and execution strategies",
            "momentum": "Focus on momentum trading and trend following",
            "risk": "Focus on risk management and capital preservation"
        }
        
        system_prompt = f"""
You are a quantitative trading strategist specializing in Hedera DeFi protocols.
Your primary focus is {strategy_prompts.get(self.strategy_focus, 'comprehensive strategy development')}.

**Strategy Development Framework:**
1. **Market Analysis**: Analyze current market structure and conditions
2. **Opportunity Identification**: Find specific trading/investment opportunities
3. **Risk Assessment**: Quantify risks and develop mitigation strategies
4. **Capital Allocation**: Optimize position sizing and portfolio allocation
5. **Execution Planning**: Create step-by-step implementation plans
6. **Performance Monitoring**: Define success metrics and exit criteria

**Your Strategy Expertise:**
- **Yield Strategies**: LP provision, lending optimization, reward farming
- **Arbitrage Strategies**: Cross-protocol, cross-pool, and temporal arbitrage
- **Risk Management**: Position sizing, diversification, hedging strategies
- **Market Making**: Liquidity provision optimization and fee earning

**Response Requirements:**
Always provide:
- Specific entry/exit criteria with numerical thresholds
- Risk metrics and maximum acceptable losses
- Expected returns with realistic timeframes
- Capital requirements and allocation recommendations
- Step-by-step execution instructions
- Performance monitoring guidelines

Use real market data and provide concrete, actionable strategies.
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
            max_iterations=12,
        )
    
    def develop_yield_strategy(
        self,
        capital_usd: float,
        risk_level: str = "medium",
        time_horizon: str = "medium"  # short, medium, long
    ) -> Dict:
        """Develop comprehensive yield farming strategy."""
        
        query = f"""
        Develop a yield farming strategy for ${capital_usd:,.0f} with:
        - Risk level: {risk_level}
        - Time horizon: {time_horizon} term
        
        Create a comprehensive strategy including:
        - Optimal allocation across Bonzo lending and SaucerSwap LP
        - Expected APY and risk-adjusted returns
        - Rebalancing triggers and frequency
        - Exit strategies and stop-loss levels
        - Tax optimization considerations
        
        Provide specific percentages, amounts, and execution steps.
        """
        
        return self.agent.invoke({"input": query})
    
    def create_arbitrage_system(
        self,
        monitoring_tokens: List[str],
        min_profit_threshold: float = 1.0
    ) -> Dict:
        """Create systematic arbitrage detection and execution system."""
        
        query = f"""
        Create an arbitrage system for monitoring {', '.join(monitoring_tokens)} with:
        - Minimum profit threshold: {min_profit_threshold}%
        - Real-time monitoring requirements
        
        Design system including:
        - Price monitoring across all available protocols
        - Automated opportunity detection algorithms
        - Execution cost calculation and profit validation
        - Risk controls and position limits
        - Performance tracking and optimization metrics
        
        Provide implementation specifications and monitoring parameters.
        """
        
        return self.agent.invoke({"input": query})