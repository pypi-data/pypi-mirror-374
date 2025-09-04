"""
DeFi Analysis Chain for comprehensive market analysis
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

from ..tools import (
    HederaTokenTool,
    HederaProtocolTool,
    SaucerSwapTool,
    BonzoFinanceTool,
)


class DeFiAnalysisOutput(BaseModel):
    """Structured output for DeFi analysis."""
    
    ecosystem_health: str = Field(description="Overall ecosystem health: excellent, good, moderate, poor")
    total_tvl_usd: float = Field(description="Total value locked across all protocols")
    top_protocols: List[Dict] = Field(description="Top performing protocols with metrics")
    top_opportunities: List[Dict] = Field(description="Best investment opportunities found")
    market_trends: Dict = Field(description="Market trend analysis and indicators")
    risk_factors: List[str] = Field(description="Key risk factors identified")
    recommendations: List[str] = Field(description="Specific actionable recommendations")


class DeFiAnalysisChain:
    """
    Comprehensive DeFi analysis chain for market research and opportunity identification.
    
    This chain orchestrates multiple tools to provide deep market analysis,
    combining data from Mirror Node, SaucerSwap, and Bonzo Finance.
    """
    
    def __init__(
        self,
        llm: Runnable,
        hedera_client: Optional[Any] = None,
        include_technical_analysis: bool = True,
        include_risk_assessment: bool = True,
    ):
        """Initialize the DeFi Analysis Chain.
        
        Args:
            llm: Language model for analysis
            hedera_client: Optional HederaDeFi client instance
            include_technical_analysis: Include technical trading analysis
            include_risk_assessment: Include comprehensive risk assessment
        """
        if HederaDeFi is None:
            raise ImportError("hedera_defi package is required")
            
        self.client = hedera_client or HederaDeFi()
        self.llm = llm
        self.include_technical_analysis = include_technical_analysis
        self.include_risk_assessment = include_risk_assessment
        
        # Initialize analysis tools
        self.protocol_tool = HederaProtocolTool(self.client)
        self.token_tool = HederaTokenTool(self.client)
        self.saucerswap_tool = SaucerSwapTool(self.client)
        self.bonzo_tool = BonzoFinanceTool(self.client)
        
        # Create the analysis chain
        self.chain = self._create_analysis_chain()
    
    def _create_analysis_chain(self) -> Runnable:
        """Create the comprehensive analysis chain."""
        
        analysis_prompt = ChatPromptTemplate.from_template("""
You are performing comprehensive Hedera DeFi ecosystem analysis. 

Based on the following data, provide a structured analysis:

**Protocol Data:**
{protocol_data}

**SaucerSwap Data:**
{saucerswap_data}

**Bonzo Finance Data:**
{bonzo_data}

**Token Analysis:**
{token_data}

**Analysis Requirements:**
- Assess overall ecosystem health and growth trends
- Identify top performing protocols and their key metrics
- Find best investment and yield opportunities
- Analyze market trends and momentum indicators
- Identify key risk factors and market inefficiencies
- Provide specific, actionable recommendations

**Output Format:**
Provide analysis in the following JSON structure:
{{
    "ecosystem_health": "excellent|good|moderate|poor",
    "total_tvl_usd": <number>,
    "top_protocols": [
        {{
            "name": "<protocol_name>",
            "type": "<protocol_type>", 
            "tvl_usd": <number>,
            "performance_rating": "excellent|good|moderate|poor",
            "key_metrics": {{}}
        }}
    ],
    "top_opportunities": [
        {{
            "type": "lending|trading|liquidity",
            "protocol": "<protocol_name>",
            "asset": "<asset_symbol>",
            "expected_apy": <number>,
            "risk_level": "low|medium|high",
            "capital_required": <number>,
            "reasoning": "<why this is a good opportunity>"
        }}
    ],
    "market_trends": {{
        "overall_direction": "bullish|bearish|neutral|uncertain",
        "volume_trend": "increasing|decreasing|stable", 
        "liquidity_trend": "improving|declining|stable",
        "yield_environment": "attractive|moderate|poor"
    }},
    "risk_factors": [
        "<specific risk factor 1>",
        "<specific risk factor 2>"
    ],
    "recommendations": [
        "<specific actionable recommendation 1>",
        "<specific actionable recommendation 2>"
    ]
}}

Focus on providing actionable insights with specific numbers and clear reasoning.
""")
        
        # Create parser for structured output
        parser = JsonOutputParser(pydantic_object=DeFiAnalysisOutput)
        
        # Chain: gather data -> analyze -> parse output
        chain = (
            {
                "protocol_data": lambda _: self._gather_protocol_data(),
                "saucerswap_data": lambda _: self._gather_saucerswap_data(),
                "bonzo_data": lambda _: self._gather_bonzo_data(),
                "token_data": lambda _: self._gather_token_data(),
            }
            | analysis_prompt
            | self.llm
            | parser
        )
        
        return chain
    
    def _gather_protocol_data(self) -> str:
        """Gather comprehensive protocol data."""
        try:
            return self.protocol_tool._run()
        except Exception as e:
            return f"Error gathering protocol data: {str(e)}"
    
    def _gather_saucerswap_data(self) -> str:
        """Gather SaucerSwap DEX data."""
        try:
            return self.saucerswap_tool._run(analysis_type="overview")
        except Exception as e:
            return f"Error gathering SaucerSwap data: {str(e)}"
    
    def _gather_bonzo_data(self) -> str:
        """Gather Bonzo Finance lending data."""
        try:
            return self.bonzo_tool._run(analysis_type="overview")
        except Exception as e:
            return f"Error gathering Bonzo data: {str(e)}"
    
    def _gather_token_data(self) -> str:
        """Gather top token data and analysis."""
        try:
            # Analyze top tokens by different criteria
            results = []
            
            # Top tokens by supply
            supply_tokens = self.token_tool._run("", limit=20)
            results.append(f"Top tokens by supply: {supply_tokens}")
            
            # Active trading tokens from SaucerSwap
            trading_tokens = self.saucerswap_tool._run(analysis_type="tokens", limit=15)
            results.append(f"Active trading tokens: {trading_tokens}")
            
            return "\n".join(results)
        except Exception as e:
            return f"Error gathering token data: {str(e)}"
    
    def analyze_market(self, focus_areas: Optional[List[str]] = None) -> Dict:
        """Perform comprehensive market analysis."""
        try:
            # Run the analysis chain
            analysis_result = self.chain.invoke({})
            
            # Add focus area filtering if specified
            if focus_areas:
                filtered_result = self._filter_by_focus_areas(analysis_result, focus_areas)
                return filtered_result
            
            return analysis_result
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "ecosystem_health": "unknown",
                "total_tvl_usd": 0,
                "top_protocols": [],
                "top_opportunities": [],
                "market_trends": {},
                "risk_factors": ["Analysis error occurred"],
                "recommendations": ["Retry analysis with different parameters"]
            }
    
    def _filter_by_focus_areas(self, analysis: Dict, focus_areas: List[str]) -> Dict:
        """Filter analysis results by specified focus areas."""
        filtered = analysis.copy()
        
        if "protocols" not in focus_areas:
            filtered["top_protocols"] = filtered["top_protocols"][:3]
        
        if "opportunities" not in focus_areas:
            filtered["top_opportunities"] = filtered["top_opportunities"][:3]
        
        if "risks" not in focus_areas:
            filtered["risk_factors"] = filtered["risk_factors"][:3]
        
        return filtered
    
    def compare_protocols(self, protocol_names: List[str]) -> Dict:
        """Compare specific protocols in detail."""
        try:
            comparison_data = {}
            
            for protocol_name in protocol_names:
                if protocol_name.lower() == "saucerswap":
                    data = self.saucerswap_tool._run(analysis_type="overview")
                    comparison_data[protocol_name] = json.loads(data) if isinstance(data, str) else data
                elif protocol_name.lower() in ["bonzo", "bonzo finance"]:
                    data = self.bonzo_tool._run(analysis_type="overview")
                    comparison_data[protocol_name] = json.loads(data) if isinstance(data, str) else data
            
            # Use LLM to analyze and compare
            comparison_prompt = f"""
            Compare the following Hedera DeFi protocols:
            
            {json.dumps(comparison_data, indent=2)}
            
            Provide a detailed comparison including:
            - TVL and volume comparisons
            - Yield opportunities in each protocol
            - Risk profiles and security considerations
            - User experience and accessibility
            - Growth trends and market position
            - Recommendations for different user types
            
            Structure as a comprehensive comparison report.
            """
            
            result = self.llm.invoke(comparison_prompt)
            return {"comparison_analysis": result.content if hasattr(result, 'content') else str(result)}
            
        except Exception as e:
            return {"error": f"Protocol comparison failed: {str(e)}"}
    
    def generate_market_report(
        self,
        report_type: str = "weekly",
        include_predictions: bool = False
    ) -> Dict:
        """Generate formatted market report."""
        try:
            # Get comprehensive analysis
            analysis = self.analyze_market()
            
            # Create report based on type and requirements
            report_prompt = f"""
            Create a {report_type} Hedera DeFi market report based on this analysis:
            
            {json.dumps(analysis, indent=2)}
            
            Report requirements:
            - Executive summary with key highlights
            - Protocol performance breakdown
            - Top investment opportunities with specific metrics
            - Risk analysis and market considerations
            - Strategic recommendations for different investor types
            {'- Market predictions and trend analysis' if include_predictions else ''}
            
            Format as a professional market research report with clear sections and actionable insights.
            Use specific numbers, percentages, and metrics throughout.
            """
            
            report = self.llm.invoke(report_prompt)
            
            return {
                "report": report.content if hasattr(report, 'content') else str(report),
                "analysis_data": analysis,
                "report_metadata": {
                    "type": report_type,
                    "includes_predictions": include_predictions,
                    "generated_at": analysis.get("timestamp"),
                    "protocols_analyzed": len(analysis.get("top_protocols", [])),
                    "opportunities_found": len(analysis.get("top_opportunities", [])),
                }
            }
            
        except Exception as e:
            return {"error": f"Report generation failed: {str(e)}"}