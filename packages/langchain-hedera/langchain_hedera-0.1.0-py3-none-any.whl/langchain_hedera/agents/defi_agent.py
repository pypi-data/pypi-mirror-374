"""
Main Hedera DeFi Agent for comprehensive ecosystem analysis
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
    HederaWhaleTool,
    HederaAccountTool,
    SaucerSwapTool,
    BonzoFinanceTool,
)


class HederaDeFiAgent:
    """
    Intelligent agent for comprehensive Hedera DeFi ecosystem analysis.
    
    This agent can:
    - Analyze protocols, tokens, and market trends
    - Monitor whale transactions and market movements
    - Find arbitrage and yield farming opportunities
    - Provide strategic recommendations for DeFi positions
    - Generate comprehensive market reports and insights
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        enable_whale_monitoring: bool = True,
        enable_arbitrage_detection: bool = True,
        verbose: bool = False,
    ):
        """Initialize the Hedera DeFi Agent.
        
        Args:
            llm: Language model (e.g., ChatOpenAI, ChatAnthropic)
            hedera_client: Optional HederaDeFi client instance
            enable_whale_monitoring: Enable whale transaction monitoring
            enable_arbitrage_detection: Enable arbitrage opportunity detection
            verbose: Enable verbose output
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.verbose = verbose
        
        # Initialize tools
        self.tools = [
            HederaTokenTool(self.client),
            HederaProtocolTool(self.client),
            HederaAccountTool(self.client),
        ]
        
        # Add optional tools based on configuration
        if enable_whale_monitoring:
            self.tools.append(HederaWhaleTool(self.client))
        
        if enable_arbitrage_detection:
            self.tools.extend([
                SaucerSwapTool(self.client),
                BonzoFinanceTool(self.client),
            ])
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with Hedera DeFi tools."""
        
        system_prompt = """
You are an expert Hedera DeFi analyst with deep knowledge of the ecosystem.
You have access to comprehensive tools for analyzing:

1. **Protocols**: SaucerSwap DEX, Bonzo Finance lending, and other DeFi protocols
2. **Tokens**: Price analysis, trading pairs, cross-protocol availability
3. **Accounts**: Portfolio analysis, DeFi positions, risk assessment
4. **Whale Activity**: Large transaction monitoring and market impact analysis
5. **Arbitrage**: Cross-protocol opportunities and yield optimization

**Your capabilities:**
- Provide detailed market analysis and insights
- Find optimal yield farming and lending strategies
- Monitor whale activity and market movements
- Identify arbitrage opportunities across protocols
- Generate strategic recommendations for DeFi investments
- Analyze account portfolios and risk metrics

**Guidelines:**
- Always provide data-driven insights based on real market data
- Explain the reasoning behind your recommendations
- Highlight risks and opportunities clearly
- Use specific numbers and metrics to support your analysis
- Consider both technical and fundamental factors
- Be precise about which protocols and tools you're using

**Format your responses with:**
1. **Summary**: Key findings and recommendations
2. **Analysis**: Detailed breakdown of data and metrics
3. **Opportunities**: Specific actionable opportunities found
4. **Risks**: Important risks and considerations
5. **Strategy**: Recommended next steps or strategies

Use the available tools to gather comprehensive data before providing analysis.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create tool-calling agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=10,
        )
    
    def analyze_ecosystem(self, focus_areas: Optional[List[str]] = None) -> Dict:
        """Perform comprehensive ecosystem analysis."""
        focus_areas = focus_areas or ["protocols", "tokens", "opportunities"]
        
        query_parts = []
        if "protocols" in focus_areas:
            query_parts.append("analyze all DeFi protocols and their performance")
        if "tokens" in focus_areas:
            query_parts.append("identify top tokens and trending assets")
        if "whale_activity" in focus_areas:
            query_parts.append("monitor recent whale transactions and market impact")
        if "opportunities" in focus_areas:
            query_parts.append("find best yield farming and arbitrage opportunities")
        
        query = "Provide a comprehensive Hedera DeFi ecosystem analysis including: " + ", ".join(query_parts)
        
        return self.agent.invoke({"input": query})
    
    def find_opportunities(
        self, 
        min_apy: float = 5.0, 
        max_risk: str = "Medium",
        focus_protocol: Optional[str] = None
    ) -> Dict:
        """Find specific DeFi opportunities based on criteria."""
        
        query = f"""
        Find DeFi opportunities with the following criteria:
        - Minimum APY: {min_apy}%
        - Maximum risk level: {max_risk}
        {f'- Focus on protocol: {focus_protocol}' if focus_protocol else ''}
        
        Analyze both lending opportunities on Bonzo Finance and liquidity provision on SaucerSwap.
        Provide specific recommendations with risk assessments.
        """
        
        return self.agent.invoke({"input": query})
    
    def analyze_account(self, account_id: str, include_recommendations: bool = True) -> Dict:
        """Analyze a specific Hedera account and provide DeFi recommendations."""
        
        query = f"""
        Analyze the Hedera account {account_id} including:
        - Current portfolio composition and values
        - Token holdings and balances
        - Potential DeFi opportunities based on current holdings
        {('- Strategic recommendations for optimizing the portfolio' if include_recommendations else '')}
        
        Focus on actionable insights and specific opportunities.
        """
        
        return self.agent.invoke({"input": query})
    
    def monitor_whale_activity(self, threshold: float = 50000) -> Dict:
        """Monitor and analyze whale transaction activity."""
        
        query = f"""
        Monitor whale transactions above {threshold:,.0f} HBAR and analyze:
        - Recent large transactions and their potential market impact
        - Patterns in whale behavior and trading activity  
        - Market sentiment indicators based on whale movements
        - Potential opportunities or risks from whale activity
        
        Provide insights on market conditions and potential price movements.
        """
        
        return self.agent.invoke({"input": query})
    
    def get_market_report(self, include_predictions: bool = False) -> Dict:
        """Generate comprehensive market report."""
        
        prediction_text = (
            "Include analysis of potential market trends and opportunities based on current data."
            if include_predictions else ""
        )
        
        query = f"""
        Generate a comprehensive Hedera DeFi market report including:
        - Overall ecosystem health and metrics
        - Top performing protocols and their key statistics
        - Best investment opportunities across lending and DEX protocols
        - Risk factors and market considerations
        - Recent whale activity and market impact
        {prediction_text}
        
        Structure the report with clear sections and actionable insights.
        """
        
        return self.agent.invoke({"input": query})