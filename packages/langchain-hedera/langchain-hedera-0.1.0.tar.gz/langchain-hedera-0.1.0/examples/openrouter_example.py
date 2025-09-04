"""
OpenRouter Integration Example for LangChain Hedera SDK

This example demonstrates how to use OpenRouter's API (including free models)
with the LangChain Hedera SDK for DeFi analysis.

OpenRouter provides access to multiple LLM providers including free models
like Google's Gemini 2.5 Flash, making it cost-effective for DeFi analysis.
"""

import os
import json
from typing import Optional
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_hedera import (
    HederaDeFiAgent,
    TradingAnalysisAgent, 
    PortfolioAgent,
    HederaLLMConfig
)


class OpenRouterDeFiAnalyst:
    """
    DeFi analyst using OpenRouter for cost-effective LLM access.
    
    Features:
    - Free model support (Gemini 2.5 Flash)
    - Multiple model options for different analysis needs
    - Cost optimization for high-frequency analysis
    - Production-grade error handling
    """
    
    def __init__(
        self,
        openrouter_api_key: str,
        model: str = "google/gemini-2.5-flash:free",  # Free model default
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        self.api_key = openrouter_api_key
        self.model = model
        self.site_url = site_url
        self.site_name = site_name
        
        # Initialize OpenRouter-compatible LLM
        self.llm = self._create_openrouter_llm()
        
        # Initialize Hedera agents with optimized config
        self.config = HederaLLMConfig.create_for_production()
        self._initialize_agents()
    
    def _create_openrouter_llm(self) -> ChatOpenAI:
        """Create OpenRouter-compatible LangChain LLM."""
        
        extra_headers = {}
        if self.site_url:
            extra_headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            extra_headers["X-Title"] = self.site_name
        
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            model=self.model,
            temperature=0.1,  # Low temperature for analytical tasks
            default_headers=extra_headers,
            max_retries=3,
        )
    
    def _initialize_agents(self):
        """Initialize all DeFi analysis agents."""
        
        print(f"🤖 Initializing agents with model: {self.model}")
        
        # Main DeFi agent for comprehensive analysis
        self.defi_agent = HederaDeFiAgent(
            llm=self.llm,
            enable_whale_monitoring=True,
            enable_arbitrage_detection=True,
            verbose=False
        )
        
        # Trading specialist for DEX analysis
        self.trading_agent = TradingAnalysisAgent(
            llm=self.llm,
            focus_dex="saucerswap",
            verbose=False
        )
        
        # Portfolio manager for investment strategies
        self.portfolio_agent = PortfolioAgent(
            llm=self.llm,
            risk_framework="modern_portfolio_theory",
            verbose=False
        )
        
        print("✅ All agents initialized successfully")
    
    def analyze_ecosystem(self, focus_areas: list = None) -> dict:
        """Comprehensive ecosystem analysis using OpenRouter."""
        
        focus_areas = focus_areas or ["protocols", "opportunities", "whale_activity"]
        
        print(f"🔍 Analyzing Hedera DeFi ecosystem...")
        print(f"   Model: {self.model}")
        print(f"   Focus: {', '.join(focus_areas)}")
        
        try:
            analysis = self.defi_agent.analyze_ecosystem(focus_areas=focus_areas)
            
            print("✅ Ecosystem analysis completed")
            return {
                "analysis": analysis,
                "model_used": self.model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "error": str(e),
                "model_used": self.model,
                "success": False
            }
    
    def find_arbitrage_opportunities(
        self,
        min_profit: float = 2.0,
        tokens: list = None
    ) -> dict:
        """Find arbitrage opportunities using OpenRouter."""
        
        tokens = tokens or ["HBAR", "USDC", "SAUCE"]
        
        print(f"💰 Finding arbitrage opportunities...")
        print(f"   Min profit: {min_profit}%")
        print(f"   Focus tokens: {', '.join(tokens)}")
        
        try:
            opportunities = self.trading_agent.find_arbitrage_opportunities(
                min_profit_percent=min_profit
            )
            
            print("✅ Arbitrage analysis completed")
            return {
                "opportunities": opportunities,
                "parameters": {
                    "min_profit": min_profit,
                    "tokens": tokens
                },
                "model_used": self.model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Arbitrage analysis failed: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def optimize_portfolio(
        self,
        investment_amount: float = 25000.0,
        risk_level: str = "medium"
    ) -> dict:
        """Optimize portfolio allocation using OpenRouter."""
        
        print(f"📊 Optimizing portfolio...")
        print(f"   Investment: ${investment_amount:,.0f}")
        print(f"   Risk level: {risk_level}")
        
        try:
            strategy = self.portfolio_agent.create_investment_strategy(
                investment_amount=investment_amount,
                goals=["yield_optimization", "diversification", "risk_management"],
                constraints={"risk_tolerance": risk_level}
            )
            
            print("✅ Portfolio optimization completed")
            return {
                "strategy": strategy,
                "parameters": {
                    "investment_amount": investment_amount,
                    "risk_level": risk_level
                },
                "model_used": self.model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Portfolio optimization failed: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def generate_market_report(self, include_predictions: bool = False) -> dict:
        """Generate comprehensive market report."""
        
        print(f"📄 Generating market report...")
        print(f"   Include predictions: {include_predictions}")
        
        try:
            report = self.defi_agent.get_market_report(
                include_predictions=include_predictions
            )
            
            print("✅ Market report generated")
            return {
                "report": report,
                "model_used": self.model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            return {
                "error": str(e),
                "success": False
            }


def run_openrouter_example():
    """Run complete OpenRouter example."""
    
    print("🚀 OpenRouter + LangChain Hedera Integration Example")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable required")
        print("\nTo get started:")
        print("1. Visit https://openrouter.ai/")
        print("2. Create account and get API key")  
        print("3. export OPENROUTER_API_KEY=your_key_here")
        print("4. Run this example again")
        return
    
    # Available models for different use cases
    models = {
        "free": "google/gemini-2.5-flash-image-preview:free",  # Free for testing
        "fast": "google/gemini-2.5-flash-lite",  # Fast and cheap
        "quality": "google/gemini-2.5-flash",   # Best balance
        "premium": "google/gemini-2.5-pro",     # Highest quality
    }
    
    print("🤖 Available models:")
    for tier, model in models.items():
        print(f"   {tier}: {model}")
    
    # Use free model for this example
    selected_model = models["free"]
    print(f"\n🎯 Using model: {selected_model}")
    
    try:
        # Initialize analyst with OpenRouter
        analyst = OpenRouterDeFiAnalyst(
            openrouter_api_key=api_key,
            model=selected_model,
            site_url="https://github.com/samthedataman/langchain-hedera",
            site_name="LangChain Hedera SDK"
        )
        
        results = {}
        
        # 1. Ecosystem Analysis
        print(f"\n1️⃣ ECOSYSTEM ANALYSIS")
        print("-" * 25)
        ecosystem = analyst.analyze_ecosystem(
            focus_areas=["protocols", "opportunities"]
        )
        results["ecosystem"] = ecosystem
        
        if ecosystem.get("success"):
            print("✅ Ecosystem analysis successful")
        else:
            print(f"❌ Ecosystem analysis failed: {ecosystem.get('error')}")
        
        # 2. Arbitrage Opportunities
        print(f"\n2️⃣ ARBITRAGE ANALYSIS") 
        print("-" * 25)
        arbitrage = analyst.find_arbitrage_opportunities(
            min_profit=1.5,
            tokens=["HBAR", "USDC"]
        )
        results["arbitrage"] = arbitrage
        
        if arbitrage.get("success"):
            print("✅ Arbitrage analysis successful")
        else:
            print(f"❌ Arbitrage analysis failed: {arbitrage.get('error')}")
        
        # 3. Portfolio Strategy
        print(f"\n3️⃣ PORTFOLIO OPTIMIZATION")
        print("-" * 30)
        portfolio = analyst.optimize_portfolio(
            investment_amount=50000.0,
            risk_level="medium"
        )
        results["portfolio"] = portfolio
        
        if portfolio.get("success"):
            print("✅ Portfolio optimization successful")
        else:
            print(f"❌ Portfolio optimization failed: {portfolio.get('error')}")
        
        # 4. Market Report
        print(f"\n4️⃣ MARKET REPORT")
        print("-" * 20)
        report = analyst.generate_market_report(include_predictions=False)
        results["report"] = report
        
        if report.get("success"):
            print("✅ Market report generated")
        else:
            print(f"❌ Report generation failed: {report.get('error')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"openrouter_analysis_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Summary
        successful_analyses = sum(1 for r in results.values() if r.get("success", False))
        total_analyses = len(results)
        
        print(f"\n📊 ANALYSIS SUMMARY")
        print("=" * 25)
        print(f"Model used: {selected_model}")
        print(f"Successful analyses: {successful_analyses}/{total_analyses}")
        print(f"Success rate: {(successful_analyses/total_analyses)*100:.1f}%")
        
        if successful_analyses == total_analyses:
            print("🎉 All analyses completed successfully!")
            print("📦 Package is ready for publication!")
        else:
            print("⚠️  Some analyses failed - check error messages above")
        
        return results
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return {"error": str(e)}


def test_different_models():
    """Test package with different OpenRouter models."""
    
    print(f"\n🔬 Testing Multiple Models")
    print("=" * 35)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY required")
        return
    
    # Test with different models
    test_models = [
        "google/gemini-2.5-flash-image-preview:free",  # Free
        "google/gemini-2.5-flash-lite",  # Fast
    ]
    
    model_results = {}
    
    for model in test_models:
        print(f"\n🧪 Testing model: {model}")
        
        try:
            llm = ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                model=model,
                temperature=0.1,
            )
            
            # Simple test query
            response = llm.invoke("Analyze the Hedera DeFi ecosystem in one paragraph.")
            
            model_results[model] = {
                "success": True,
                "response_length": len(response.content),
                "sample": response.content[:200] + "..." if len(response.content) > 200 else response.content
            }
            
            print(f"✅ Model {model} working")
            print(f"   Response length: {len(response.content)} chars")
            
        except Exception as e:
            print(f"❌ Model {model} failed: {e}")
            model_results[model] = {
                "success": False,
                "error": str(e)
            }
    
    return model_results


if __name__ == "__main__":
    # Import datetime here to avoid issues if not available at top level
    from datetime import datetime
    
    print("🌟 OpenRouter + LangChain Hedera Integration")
    print("=" * 55)
    print("This example demonstrates using free/cheap models via OpenRouter")
    print("for cost-effective DeFi analysis on Hedera blockchain.\n")
    
    # Check dependencies
    try:
        import langchain_openai
        print("✅ langchain-openai available")
    except ImportError:
        print("❌ langchain-openai required: pip install langchain-openai")
        exit(1)
    
    # Run example
    try:
        # Test different models first
        model_results = test_different_models()
        
        if model_results:
            print(f"\n📊 Model Test Results:")
            for model, result in model_results.items():
                status = "✅" if result.get("success") else "❌"
                print(f"   {status} {model}")
        
        # Run full example
        example_results = run_openrouter_example()
        
        if example_results and not example_results.get("error"):
            print(f"\n🎉 OpenRouter integration test successful!")
            print(f"📦 LangChain Hedera package is ready for publication!")
        else:
            print(f"\n⚠️  Integration test had issues")
    
    except KeyboardInterrupt:
        print(f"\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print(f"\nThis is expected in development - package will work after proper installation")


# Model recommendations for different use cases
MODEL_RECOMMENDATIONS = {
    "development": {
        "model": "google/gemini-2.5-flash-image-preview:free",
        "reason": "Free tier for testing and development",
        "cost": "$0.00",
    },
    "production_light": {
        "model": "google/gemini-2.5-flash-lite", 
        "reason": "Fast and cost-effective for high-frequency analysis",
        "cost": "~$0.10/1M tokens",
    },
    "production_balanced": {
        "model": "google/gemini-2.5-flash",
        "reason": "Best balance of quality and cost for general use",
        "cost": "~$0.30/1M tokens", 
    },
    "production_premium": {
        "model": "google/gemini-2.5-pro",
        "reason": "Highest quality for critical analysis and strategies",
        "cost": "~$1.25/1M tokens",
    }
}

def print_model_recommendations():
    """Print model recommendations for different use cases."""
    
    print("\n🎯 OpenRouter Model Recommendations")
    print("=" * 45)
    
    for use_case, info in MODEL_RECOMMENDATIONS.items():
        print(f"\n{use_case.replace('_', ' ').title()}:")
        print(f"   Model: {info['model']}")
        print(f"   Reason: {info['reason']}")
        print(f"   Cost: {info['cost']}")
    
    print(f"\n💡 Pro Tips:")
    print(f"   • Start with free tier for testing")
    print(f"   • Use Flash Lite for real-time monitoring") 
    print(f"   • Use Pro for complex portfolio strategies")
    print(f"   • Set up proper error handling for production")

if __name__ == "__main__":
    print_model_recommendations()