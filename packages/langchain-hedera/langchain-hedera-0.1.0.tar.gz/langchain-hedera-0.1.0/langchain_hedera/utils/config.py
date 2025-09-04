"""
Configuration utilities for LangChain Hedera integration
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class HederaLLMConfig:
    """Configuration for Hedera DeFi LangChain integration."""
    
    # Hedera DeFi API Configuration
    hedera_endpoint: str = "https://mainnet-public.mirrornode.hedera.com/api/v1"
    bonzo_api: str = "https://mainnet-data.bonzo.finance"
    saucerswap_api: str = "https://server.saucerswap.finance/api/public"
    cache_ttl: int = 60
    timeout: int = 30000
    enable_logging: bool = False
    
    # LangChain Agent Configuration
    max_iterations: int = 10
    handle_parsing_errors: bool = True
    verbose: bool = False
    
    # Analysis Configuration
    default_token_limit: int = 20
    default_pool_limit: int = 15
    whale_threshold_hbar: float = 10000.0
    min_tvl_threshold: float = 1000.0
    
    # Risk Management
    max_risk_score: float = 70.0  # 0-100 scale
    default_risk_tolerance: str = "medium"  # low, medium, high
    
    # Performance Configuration
    enable_caching: bool = True
    batch_requests: bool = True
    optimize_api_calls: bool = True
    
    # Custom Headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Tool Configuration
    enable_whale_monitoring: bool = True
    enable_arbitrage_detection: bool = True
    enable_risk_analysis: bool = True
    enable_yield_optimization: bool = True
    
    @classmethod
    def create_for_production(cls) -> 'HederaLLMConfig':
        """Create production-optimized configuration."""
        return cls(
            cache_ttl=300,  # 5 minutes cache
            timeout=45000,  # 45 seconds timeout
            enable_logging=True,
            max_iterations=15,
            verbose=False,
            optimize_api_calls=True,
            batch_requests=True,
            whale_threshold_hbar=25000.0,  # Higher threshold for production
            min_tvl_threshold=5000.0,  # Higher TVL threshold
        )
    
    @classmethod 
    def create_for_development(cls) -> 'HederaLLMConfig':
        """Create development-friendly configuration."""
        return cls(
            cache_ttl=30,  # Short cache for dev
            timeout=15000,  # Shorter timeout
            enable_logging=True,
            max_iterations=8,
            verbose=True,
            whale_threshold_hbar=5000.0,  # Lower threshold for testing
            min_tvl_threshold=100.0,  # Lower TVL for more results
        )
    
    @classmethod
    def create_for_research(cls) -> 'HederaLLMConfig':
        """Create research-optimized configuration."""
        return cls(
            cache_ttl=900,  # 15 minutes cache
            timeout=60000,  # 1 minute timeout
            enable_logging=True,
            max_iterations=20,
            verbose=True,
            default_token_limit=50,
            default_pool_limit=30,
            optimize_api_calls=True,
            enable_risk_analysis=True,
        )
    
    def get_hedera_client_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for HederaDeFi client."""
        return {
            "endpoint": self.hedera_endpoint,
            "bonzo_api": self.bonzo_api,
            "saucerswap_api": self.saucerswap_api,
            "cache_ttl": self.cache_ttl,
            "custom_headers": self.custom_headers,
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for LangChain agents."""
        return {
            "max_iterations": self.max_iterations,
            "handle_parsing_errors": self.handle_parsing_errors,
            "verbose": self.verbose,
        }
    
    def get_tool_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for tools."""
        return {
            "default_token_limit": self.default_token_limit,
            "default_pool_limit": self.default_pool_limit,
            "whale_threshold_hbar": self.whale_threshold_hbar,
            "min_tvl_threshold": self.min_tvl_threshold,
            "enable_whale_monitoring": self.enable_whale_monitoring,
            "enable_arbitrage_detection": self.enable_arbitrage_detection,
            "enable_risk_analysis": self.enable_risk_analysis,
            "enable_yield_optimization": self.enable_yield_optimization,
        }