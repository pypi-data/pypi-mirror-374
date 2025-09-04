"""
LangChain Hedera SDK - Intelligent DeFi Agents and Tools

This package provides LangChain integration for Hedera DeFi protocols,
enabling AI agents to analyze, monitor, and interact with the Hedera ecosystem.
"""

__version__ = "0.1.0"

from .agents import HederaDeFiAgent, TradingAnalysisAgent, PortfolioAgent
from .tools import (
    HederaTokenTool,
    HederaPoolTool,
    HederaWhaleTool,
    HederaProtocolTool,
    SaucerSwapTool,
    BonzoFinanceTool,
)
from .chains import DeFiAnalysisChain, ArbitrageChain
from .utils import HederaLLMConfig

__all__ = [
    # Core agents
    "HederaDeFiAgent",
    "TradingAnalysisAgent", 
    "PortfolioAgent",
    # Tools
    "HederaTokenTool",
    "HederaPoolTool",
    "HederaWhaleTool",
    "HederaProtocolTool",
    "SaucerSwapTool",
    "BonzoFinanceTool",
    # Chains
    "DeFiAnalysisChain",
    "ArbitrageChain",
    # Utils
    "HederaLLMConfig",
]