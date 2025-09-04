"""
Basic Usage Examples for LangChain Hedera SDK
"""

import os
from langchain_openai import ChatOpenAI
from langchain_hedera import (
    HederaDeFiAgent,
    TradingAnalysisAgent,
    PortfolioAgent,
    HederaLLMConfig,
)


def main():
    """Demonstrate basic usage of LangChain Hedera tools and agents."""
    
    # Initialize LLM (requires OpenAI API key)
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,  # Low temperature for analytical tasks
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create configuration
    config = HederaLLMConfig.create_for_development()
    
    print("🚀 LangChain Hedera SDK Examples\n")
    
    # Example 1: Basic DeFi Ecosystem Analysis
    print("1️⃣ DeFi Ecosystem Analysis")
    print("-" * 40)
    
    defi_agent = HederaDeFiAgent(llm, verbose=True)
    
    # Analyze the ecosystem
    ecosystem_analysis = defi_agent.analyze_ecosystem(
        focus_areas=["protocols", "opportunities"]
    )
    print("Ecosystem Analysis Result:")
    print(ecosystem_analysis.get("output", "No output"))
    print()
    
    # Example 2: Find Investment Opportunities
    print("2️⃣ Investment Opportunities")
    print("-" * 40)
    
    opportunities = defi_agent.find_opportunities(
        min_apy=5.0,
        max_risk="Medium"
    )
    print("Investment Opportunities:")
    print(opportunities.get("output", "No opportunities found"))
    print()
    
    # Example 3: Trading Analysis
    print("3️⃣ Trading Analysis")
    print("-" * 40)
    
    trading_agent = TradingAnalysisAgent(llm, verbose=True)
    
    # Analyze arbitrage opportunities
    arbitrage_analysis = trading_agent.find_arbitrage_opportunities(
        min_profit_percent=2.0
    )
    print("Arbitrage Analysis:")
    print(arbitrage_analysis.get("output", "No arbitrage found"))
    print()
    
    # Example 4: Portfolio Analysis
    print("4️⃣ Portfolio Analysis")
    print("-" * 40)
    
    portfolio_agent = PortfolioAgent(llm, verbose=True)
    
    # Analyze a sample account (use a real account ID if available)
    sample_account = "0.0.1234567"  # Replace with real account
    try:
        portfolio_analysis = portfolio_agent.analyze_portfolio(
            account_id=sample_account,
            include_optimization=True
        )
        print("Portfolio Analysis:")
        print(portfolio_analysis.get("output", "Analysis failed"))
    except Exception as e:
        print(f"Portfolio analysis skipped (sample account): {e}")
    
    print()
    
    # Example 5: Market Monitoring
    print("5️⃣ Market Monitoring")
    print("-" * 40)
    
    # Monitor whale activity
    whale_activity = defi_agent.monitor_whale_activity(threshold=50000)
    print("Whale Activity Analysis:")
    print(whale_activity.get("output", "No whale activity"))
    print()
    
    # Example 6: Generate Market Report
    print("6️⃣ Market Report")
    print("-" * 40)
    
    market_report = defi_agent.get_market_report(include_predictions=False)
    print("Market Report:")
    print(market_report.get("output", "No report generated"))
    
    print("\n✅ Examples completed!")
    print("\nNext steps:")
    print("- Set up your OpenAI API key in environment")
    print("- Replace sample account with real Hedera account ID") 
    print("- Explore advanced features in other example files")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        print("Continuing with examples (some may fail)...\n")
    
    main()