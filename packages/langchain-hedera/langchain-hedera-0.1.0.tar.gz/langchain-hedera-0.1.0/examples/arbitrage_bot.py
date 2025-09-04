"""
Advanced Arbitrage Detection Bot Example
"""

import os
import time
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_hedera import HederaDeFiAgent
from langchain_hedera.chains import ArbitrageChain
from langchain_hedera.utils import HederaLLMConfig, format_analysis_output


class ArbitrageBot:
    """
    Automated arbitrage detection bot for Hedera DeFi.
    
    Features:
    - Continuous monitoring for arbitrage opportunities
    - Real-time profit calculations and risk assessment
    - Automated execution planning and validation
    - Performance tracking and reporting
    """
    
    def __init__(
        self,
        api_key: str,
        min_profit_percent: float = 2.0,
        max_execution_cost: float = 100.0,
        monitoring_interval: int = 300,  # 5 minutes
    ):
        self.min_profit = min_profit_percent
        self.max_cost = max_execution_cost
        self.monitoring_interval = monitoring_interval
        
        # Initialize LLM and configuration
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
        
        self.config = HederaLLMConfig.create_for_production()
        
        # Initialize agents and chains
        self.defi_agent = HederaDeFiAgent(self.llm, verbose=False)
        self.arbitrage_chain = ArbitrageChain(
            llm=self.llm,
            min_profit_threshold=self.min_profit,
            max_execution_cost=self.max_cost
        )
        
        # Tracking
        self.opportunities_found = 0
        self.total_potential_profit = 0.0
        self.start_time = datetime.now()
    
    def scan_for_opportunities(self, focus_tokens: list = None) -> dict:
        """Scan for arbitrage opportunities."""
        print(f"🔍 Scanning for arbitrage opportunities... ({datetime.now().strftime('%H:%M:%S')})")
        
        try:
            # Detect opportunities using the arbitrage chain
            opportunities = self.arbitrage_chain.detect_opportunities(
                focus_tokens=focus_tokens,
                capital_amount=10000.0  # Reference amount for calculations
            )
            
            # Process and validate opportunities
            valid_opportunities = []
            for opp in opportunities.get("opportunities", []):
                profit_percent = opp.get("profit_potential_percent", 0)
                execution_cost = opp.get("capital_required_usd", 0)
                
                if profit_percent >= self.min_profit and execution_cost <= self.max_cost:
                    valid_opportunities.append(opp)
                    self.opportunities_found += 1
                    self.total_potential_profit += opp.get("profit_potential_usd", 0)
            
            if valid_opportunities:
                print(f"✅ Found {len(valid_opportunities)} arbitrage opportunities!")
                
                # Show best opportunity
                best = max(valid_opportunities, key=lambda x: x.get("profit_potential_percent", 0))
                print(f"🎯 Best opportunity: {best.get('token_symbol')} - {best.get('profit_potential_percent', 0):.2f}% profit")
                
                return {
                    "opportunities": valid_opportunities,
                    "best_opportunity": best,
                    "scan_successful": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print("❌ No profitable opportunities found meeting criteria")
                return {
                    "opportunities": [],
                    "scan_successful": True,
                    "message": "No opportunities meeting minimum criteria",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error during opportunity scan: {e}")
            return {
                "opportunities": [],
                "scan_successful": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_monitoring_cycle(self, focus_tokens: list = None, cycles: int = 5) -> list:
        """Execute multiple monitoring cycles."""
        print(f"🤖 Starting arbitrage monitoring bot")
        print(f"   Min profit: {self.min_profit}%")
        print(f"   Max execution cost: ${self.max_cost}")
        print(f"   Monitoring interval: {self.monitoring_interval}s")
        print(f"   Cycles to run: {cycles}")
        print(f"   Focus tokens: {focus_tokens or 'All available'}")
        print("-" * 60)
        
        results = []
        
        for cycle in range(cycles):
            print(f"\n📊 Cycle {cycle + 1}/{cycles}")
            
            # Scan for opportunities
            scan_result = self.scan_for_opportunities(focus_tokens)
            results.append(scan_result)
            
            # Show statistics
            opportunities = scan_result.get("opportunities", [])
            if opportunities:
                total_profit = sum(opp.get("profit_potential_usd", 0) for opp in opportunities)
                avg_profit = sum(opp.get("profit_potential_percent", 0) for opp in opportunities) / len(opportunities)
                
                print(f"💰 Potential profit this cycle: ${total_profit:,.2f}")
                print(f"📈 Average profit margin: {avg_profit:.2f}%")
                
                # Show top 3 opportunities
                top_opportunities = sorted(opportunities, key=lambda x: x.get("profit_potential_percent", 0), reverse=True)[:3]
                print("\n🏆 Top 3 opportunities:")
                for i, opp in enumerate(top_opportunities, 1):
                    print(f"   {i}. {opp.get('token_symbol')} - {opp.get('profit_potential_percent', 0):.2f}% profit")
                    print(f"      Type: {opp.get('opportunity_type')}, Risk: {opp.get('execution_complexity')}")
            
            # Wait before next cycle (skip wait on last cycle)
            if cycle < cycles - 1:
                print(f"\n⏰ Waiting {self.monitoring_interval}s until next scan...")
                time.sleep(self.monitoring_interval)
        
        # Generate summary
        self._print_session_summary(results)
        return results
    
    def _print_session_summary(self, results: list):
        """Print summary of monitoring session."""
        print("\n" + "=" * 60)
        print("📈 ARBITRAGE MONITORING SESSION SUMMARY")
        print("=" * 60)
        
        total_opportunities = sum(len(r.get("opportunities", [])) for r in results)
        successful_scans = len([r for r in results if r.get("scan_successful", False)])
        
        runtime = datetime.now() - self.start_time
        
        print(f"🕐 Session runtime: {runtime}")
        print(f"✅ Successful scans: {successful_scans}/{len(results)}")
        print(f"🎯 Total opportunities found: {total_opportunities}")
        print(f"💰 Total potential profit: ${self.total_potential_profit:,.2f}")
        
        if total_opportunities > 0:
            # Find best overall opportunity
            all_opportunities = []
            for result in results:
                all_opportunities.extend(result.get("opportunities", []))
            
            if all_opportunities:
                best_overall = max(all_opportunities, key=lambda x: x.get("profit_potential_percent", 0))
                print(f"🏆 Best opportunity found: {best_overall.get('token_symbol')} ({best_overall.get('profit_potential_percent', 0):.2f}%)")
                
                # Show execution plan for best opportunity
                print(f"\n📋 Execution plan for {best_overall.get('token_symbol')}:")
                for step in best_overall.get("execution_steps", []):
                    print(f"   • {step}")
        else:
            print("❌ No profitable opportunities found in this session")
        
        print("\n💡 Recommendations:")
        if total_opportunities == 0:
            print("   • Lower minimum profit threshold")
            print("   • Increase monitoring frequency") 
            print("   • Expand token watch list")
        else:
            print("   • Consider automated execution for high-confidence opportunities")
            print("   • Implement position sizing based on available capital")
            print("   • Set up alerts for immediate opportunity notification")


def run_basic_arbitrage_example():
    """Run basic arbitrage detection example."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        return
    
    # Initialize bot
    bot = ArbitrageBot(
        api_key=api_key,
        min_profit_percent=1.5,  # 1.5% minimum profit
        max_execution_cost=200.0,  # $200 max execution cost
        monitoring_interval=60,    # 1 minute intervals
    )
    
    # Focus on major tokens for this example
    focus_tokens = ["HBAR", "USDC", "SAUCE", "ETH"]
    
    # Run monitoring cycles
    results = bot.execute_monitoring_cycle(
        focus_tokens=focus_tokens,
        cycles=3  # 3 monitoring cycles
    )
    
    # Save results
    import json
    with open("arbitrage_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to arbitrage_results.json")


def run_yield_optimization_example():
    """Run yield optimization example."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key required")
        return
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=api_key)
    
    print("💰 Yield Optimization Example")
    print("-" * 40)
    
    # Initialize DeFi agent
    agent = HederaDeFiAgent(llm)
    
    # Find best yields
    yield_opportunities = agent.find_opportunities(
        min_apy=8.0,  # 8% minimum APY
        max_risk="Medium"
    )
    
    print("Best yield opportunities found:")
    print(yield_opportunities.get("output", "No yields found"))


def run_portfolio_analysis_example():
    """Run portfolio analysis example."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key required")
        return
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=api_key)
    
    print("📊 Portfolio Analysis Example")
    print("-" * 40)
    
    # Initialize portfolio agent
    portfolio_agent = PortfolioAgent(llm)
    
    # Create investment strategy
    strategy = portfolio_agent.create_investment_strategy(
        investment_amount=25000.0,
        goals=["high_yield", "diversification", "risk_management"]
    )
    
    print("Investment strategy:")
    print(strategy.get("output", "No strategy generated"))


if __name__ == "__main__":
    print("Choose example to run:")
    print("1. Basic arbitrage detection")
    print("2. Yield optimization")  
    print("3. Portfolio analysis")
    print("4. All examples")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        run_basic_arbitrage_example()
    elif choice == "2":
        run_yield_optimization_example()
    elif choice == "3":
        run_portfolio_analysis_example()
    elif choice == "4":
        run_basic_arbitrage_example()
        print("\n" + "="*60 + "\n")
        run_yield_optimization_example()
        print("\n" + "="*60 + "\n") 
        run_portfolio_analysis_example()
    else:
        print("Invalid choice. Running basic arbitrage example...")
        run_basic_arbitrage_example()