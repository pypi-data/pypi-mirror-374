"""
Advanced DeFi Analysis Examples using LangChain Hedera SDK
"""

import os
import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_hedera import HederaDeFiAgent, PortfolioAgent
from langchain_hedera.chains import DeFiAnalysisChain
from langchain_hedera.utils import HederaLLMConfig, format_analysis_output


def comprehensive_market_analysis():
    """Perform comprehensive market analysis with custom focus areas."""
    
    print("🔬 Comprehensive Market Analysis")
    print("=" * 50)
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize analysis chain
    analysis_chain = DeFiAnalysisChain(
        llm=llm,
        include_technical_analysis=True,
        include_risk_assessment=True
    )
    
    # Run comprehensive analysis
    print("📊 Running ecosystem-wide analysis...")
    market_analysis = analysis_chain.analyze_market(
        focus_areas=["protocols", "opportunities", "risks"]
    )
    
    # Format and display results
    print("\n📈 MARKET ANALYSIS RESULTS")
    print("-" * 30)
    
    formatted_output = format_analysis_output(
        market_analysis, 
        output_format="markdown",
        include_metadata=True
    )
    print(formatted_output)
    
    # Generate detailed market report
    print("\n📄 Generating detailed market report...")
    market_report = analysis_chain.generate_market_report(
        report_type="comprehensive",
        include_predictions=True
    )
    
    print("\n📋 MARKET REPORT")
    print("-" * 20)
    print(market_report.get("report", "Report generation failed"))
    
    return market_analysis, market_report


def protocol_comparison_analysis():
    """Compare multiple protocols in detail."""
    
    print("\n⚖️ Protocol Comparison Analysis")
    print("=" * 40)
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    analysis_chain = DeFiAnalysisChain(llm=llm)
    
    # Compare major protocols
    protocols_to_compare = ["SaucerSwap", "Bonzo Finance"]
    
    print(f"📊 Comparing protocols: {', '.join(protocols_to_compare)}")
    comparison = analysis_chain.compare_protocols(protocols_to_compare)
    
    print("\n🏆 PROTOCOL COMPARISON")
    print("-" * 25)
    print(comparison.get("comparison_analysis", "Comparison failed"))
    
    return comparison


def yield_farming_strategy_development():
    """Develop comprehensive yield farming strategy."""
    
    print("\n🌾 Yield Farming Strategy Development")  
    print("=" * 45)
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.2,  # Slightly higher for strategy creativity
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize portfolio agent for strategy development
    portfolio_agent = PortfolioAgent(
        llm=llm,
        risk_framework="modern_portfolio_theory"
    )
    
    # Develop yield strategy for different risk profiles
    risk_profiles = ["conservative", "balanced", "aggressive"]
    strategies = {}
    
    for profile in risk_profiles:
        print(f"\n💡 Developing {profile} strategy...")
        
        strategy = portfolio_agent.create_investment_strategy(
            investment_amount=50000.0,  # $50K strategy
            goals=["yield_optimization", "risk_management", "diversification"],
            constraints={"risk_tolerance": profile, "max_protocol_allocation": 0.4}
        )
        
        strategies[profile] = strategy
        
        print(f"✅ {profile.title()} strategy completed")
    
    # Compare strategies
    print(f"\n📊 YIELD FARMING STRATEGIES COMPARISON")
    print("-" * 45)
    
    for profile, strategy in strategies.items():
        print(f"\n🎯 {profile.upper()} STRATEGY:")
        print("-" * 20)
        output = strategy.get("output", "Strategy generation failed")
        # Truncate long outputs for readability
        if len(output) > 1000:
            output = output[:1000] + "... [truncated]"
        print(output)
    
    return strategies


def risk_assessment_analysis():
    """Perform comprehensive risk assessment across protocols."""
    
    print("\n⚠️ Risk Assessment Analysis")
    print("=" * 35)
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize agents for risk analysis
    defi_agent = HederaDeFiAgent(llm, verbose=False)
    portfolio_agent = PortfolioAgent(llm)
    
    print("🔍 Analyzing ecosystem risks...")
    
    # Get ecosystem overview with risk focus
    ecosystem_analysis = defi_agent.analyze_ecosystem(
        focus_areas=["protocols", "whale_activity", "risks"]
    )
    
    print("✅ Ecosystem risk analysis completed")
    
    # Stress test scenarios
    print("\n🧪 Running stress test scenarios...")
    
    stress_scenarios = [
        "Major protocol exploit or hack",
        "30% market crash across crypto markets", 
        "Regulatory restrictions on DeFi protocols",
        "Hedera network congestion or outage",
        "Liquidity crisis in major pools"
    ]
    
    # Note: This would need a real account ID for actual stress testing
    sample_portfolio = {
        "hbar_allocation": 0.4,
        "defi_allocation": 0.6,
        "protocols": ["SaucerSwap", "Bonzo Finance"],
        "total_value_usd": 100000
    }
    
    risk_analysis = {
        "ecosystem_risks": ecosystem_analysis.get("output", ""),
        "stress_scenarios": stress_scenarios,
        "sample_portfolio": sample_portfolio,
        "risk_mitigation": [
            "Diversify across multiple protocols",
            "Maintain adequate HBAR reserves",
            "Set stop-loss levels for volatile positions",
            "Monitor protocol health indicators",
            "Keep some assets in liquid form"
        ]
    }
    
    print("\n⚠️ RISK ASSESSMENT RESULTS")
    print("-" * 30)
    print(f"Ecosystem Analysis: {ecosystem_analysis.get('output', '')[:500]}...")
    print("\n🛡️ Risk Mitigation Strategies:")
    for strategy in risk_analysis["risk_mitigation"]:
        print(f"   • {strategy}")
    
    return risk_analysis


def real_time_monitoring_setup():
    """Set up real-time monitoring dashboard."""
    
    print("\n📡 Real-Time Monitoring Setup")
    print("=" * 35)
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize monitoring components
    defi_agent = HederaDeFiAgent(llm)
    
    # Define monitoring parameters
    monitoring_config = {
        "whale_threshold": 100000,  # $100K+ transactions
        "price_change_threshold": 5.0,  # 5%+ price movements
        "tvl_change_threshold": 10.0,   # 10%+ TVL changes
        "new_opportunity_threshold": 3.0,  # 3%+ profit opportunities
    }
    
    print("⚙️ Monitoring configuration:")
    for key, value in monitoring_config.items():
        print(f"   {key}: {value}")
    
    # Simulate monitoring cycle
    print(f"\n🔄 Running monitoring cycle...")
    
    # Get baseline metrics
    baseline = defi_agent.analyze_ecosystem()
    
    # Monitor whale activity
    whale_activity = defi_agent.monitor_whale_activity(
        threshold=monitoring_config["whale_threshold"]
    )
    
    monitoring_summary = {
        "configuration": monitoring_config,
        "baseline_metrics": baseline.get("output", ""),
        "whale_activity": whale_activity.get("output", ""),
        "monitoring_active": True,
        "last_update": datetime.now().isoformat(),
    }
    
    print("✅ Monitoring setup completed")
    print("📊 Use this configuration for continuous monitoring")
    
    return monitoring_summary


def main():
    """Run all advanced analysis examples."""
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        return
    
    print("🚀 Advanced LangChain Hedera Analysis Examples")
    print("=" * 55)
    
    results = {}
    
    try:
        # 1. Comprehensive market analysis
        market_analysis, market_report = comprehensive_market_analysis()
        results["market_analysis"] = market_analysis
        results["market_report"] = market_report
        
        # 2. Protocol comparison
        protocol_comparison = protocol_comparison_analysis()
        results["protocol_comparison"] = protocol_comparison
        
        # 3. Yield farming strategies
        yield_strategies = yield_farming_strategy_development()
        results["yield_strategies"] = yield_strategies
        
        # 4. Risk assessment
        risk_assessment = risk_assessment_analysis()
        results["risk_assessment"] = risk_assessment
        
        # 5. Monitoring setup
        monitoring_setup = real_time_monitoring_setup()
        results["monitoring_setup"] = monitoring_setup
        
        # Save complete analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hedera_defi_analysis_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Complete analysis saved to {filename}")
        print("\n✅ All advanced examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        return
    
    # Print summary
    print(f"\n📋 ANALYSIS SUMMARY")
    print("-" * 20)
    print(f"Market analysis: {'✅' if 'market_analysis' in results else '❌'}")
    print(f"Protocol comparison: {'✅' if 'protocol_comparison' in results else '❌'}")
    print(f"Yield strategies: {'✅' if 'yield_strategies' in results else '❌'}")
    print(f"Risk assessment: {'✅' if 'risk_assessment' in results else '❌'}")
    print(f"Monitoring setup: {'✅' if 'monitoring_setup' in results else '❌'}")


if __name__ == "__main__":
    main()