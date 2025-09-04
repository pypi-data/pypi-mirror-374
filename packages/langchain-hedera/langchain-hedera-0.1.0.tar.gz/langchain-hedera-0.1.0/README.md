# LangChain Hedera SDK

Intelligent DeFi agents and tools for Hedera blockchain, built on LangChain.

## 🚀 Features

### 🤖 Intelligent Agents
- **HederaDeFiAgent**: Comprehensive ecosystem analysis and strategic recommendations
- **TradingAnalysisAgent**: DEX trading analysis and arbitrage detection
- **PortfolioAgent**: Portfolio optimization and risk management

### 🛠️ Specialized Tools
- **HederaTokenTool**: Token analysis, price tracking, cross-protocol availability
- **HederaProtocolTool**: Protocol metrics, TVL analysis, performance tracking
- **SaucerSwapTool**: DEX analysis, pool optimization, trading opportunities
- **BonzoFinanceTool**: Lending analysis, yield optimization, risk assessment
- **HederaWhaleTool**: Large transaction monitoring and market impact analysis

### ⛓️ Analysis Chains
- **DeFiAnalysisChain**: Comprehensive market analysis and reporting
- **ArbitrageChain**: Automated arbitrage detection and strategy development

## 📦 Installation

```bash
pip install langchain-hedera
```

## 🔧 Quick Start

### Option 1: OpenRouter (Recommended - Free tier available) ⭐
```python
import os
from langchain_openai import ChatOpenAI
from langchain_hedera import HederaDeFiAgent

# Initialize with OpenRouter (free model)
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="google/gemini-2.5-flash-image-preview:free",  # Free!
    temperature=0.1
)

# Create DeFi agent
agent = HederaDeFiAgent(llm)

# Analyze the ecosystem
analysis = agent.analyze_ecosystem(
    focus_areas=["protocols", "opportunities", "whale_activity"]
)
print(analysis["output"])
```

### Option 2: OpenAI
```python
import os
from langchain_openai import ChatOpenAI
from langchain_hedera import HederaDeFiAgent

# Initialize with OpenAI
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create DeFi agent  
agent = HederaDeFiAgent(llm)

# Find investment opportunities
opportunities = agent.find_opportunities(
    min_apy=8.0,
    max_risk="Medium"
)
print(opportunities["output"])
```

## 📊 Advanced Usage

### Arbitrage Detection
```python
from langchain_hedera import TradingAnalysisAgent

trading_agent = TradingAnalysisAgent(llm)

# Find arbitrage opportunities
arbitrage = trading_agent.find_arbitrage_opportunities(
    min_profit_percent=2.0
)

# Analyze specific trading pairs
pair_analysis = trading_agent.analyze_trading_pair(
    token_a="HBAR",
    token_b="USDC", 
    amount=10000
)
```

### Portfolio Management
```python
from langchain_hedera import PortfolioAgent

portfolio_agent = PortfolioAgent(llm)

# Analyze existing portfolio
analysis = portfolio_agent.analyze_portfolio(
    account_id="0.0.123456",
    include_optimization=True
)

# Create investment strategy
strategy = portfolio_agent.create_investment_strategy(
    investment_amount=50000.0,
    goals=["high_yield", "diversification"]
)
```

### Yield Optimization
```python
from langchain_hedera.chains import DeFiAnalysisChain

analysis_chain = DeFiAnalysisChain(llm)

# Comprehensive yield analysis
yield_analysis = analysis_chain.analyze_market(
    focus_areas=["opportunities"]
)

# Generate yield farming report
report = analysis_chain.generate_market_report(
    report_type="yield_focused"
)
```

## 🔍 Protocol Coverage

### Supported Protocols
- **SaucerSwap**: Leading Hedera DEX with Uniswap V3 architecture
- **Bonzo Finance**: Lending and borrowing protocol
- **HeliSwap**: Additional DEX integration
- **Stader**: Staking protocol integration
- **Mirror Node**: Direct Hedera consensus data

### Data Sources
- **Real-time Prices**: Live price feeds from SaucerSwap
- **TVL Data**: Total value locked across all protocols  
- **Transaction Data**: Whale monitoring via Mirror Node
- **Yield Data**: Lending rates from Bonzo Finance
- **Pool Data**: Liquidity metrics from DEX protocols

## ⚙️ Configuration

```python
from langchain_hedera.utils import HederaLLMConfig

# Production configuration
config = HederaLLMConfig.create_for_production()

# Development configuration  
config = HederaLLMConfig.create_for_development()

# Custom configuration
config = HederaLLMConfig(
    whale_threshold_hbar=25000,
    min_tvl_threshold=5000,
    enable_arbitrage_detection=True,
    verbose=True
)
```

## 📈 Examples

### Basic Ecosystem Analysis
```python
# Get comprehensive ecosystem overview
overview = agent.analyze_ecosystem()

# Monitor whale activity
whales = agent.monitor_whale_activity(threshold=50000)

# Generate market report
report = agent.get_market_report(include_predictions=True)
```

### Advanced Arbitrage Bot
```python
from langchain_hedera.chains import ArbitrageChain

arbitrage_chain = ArbitrageChain(
    llm=llm,
    min_profit_threshold=2.0
)

# Detect opportunities
opportunities = arbitrage_chain.detect_opportunities(
    focus_tokens=["HBAR", "USDC", "SAUCE"],
    capital_amount=10000
)

# Set up monitoring
monitoring = arbitrage_chain.monitor_opportunities(
    watch_list=["HBAR", "USDC"],
    check_interval_minutes=15
)
```

## 🔧 Tool Reference

### HederaTokenTool
```python
from langchain_hedera.tools import HederaTokenTool

token_tool = HederaTokenTool()
result = token_tool._run("SAUCE", limit=5)  # Search for SAUCE token
```

### SaucerSwapTool  
```python
from langchain_hedera.tools import SaucerSwapTool

saucer_tool = SaucerSwapTool()
pools = saucer_tool._run("pools", limit=10)  # Get top pools
```

### BonzoFinanceTool
```python
from langchain_hedera.tools import BonzoFinanceTool

bonzo_tool = BonzoFinanceTool()
lending = bonzo_tool._run("lending", min_apy=5.0)  # Find lending opportunities
```

## 🧪 Running Examples

### OpenRouter Examples (Free tier available)
```bash
# Set up free OpenRouter API key
export OPENROUTER_API_KEY="your_key_here"

# OpenRouter integration example
python examples/openrouter_example.py

# Interactive Streamlit dashboard
pip install streamlit plotly
streamlit run examples/streamlit_dashboard.py
```

### OpenAI Examples
```bash  
# Set up OpenAI API key
export OPENAI_API_KEY="your_key_here"

# Basic usage examples
python examples/basic_usage.py

# Advanced arbitrage bot
python examples/arbitrage_bot.py

# Comprehensive analysis  
python examples/advanced_analysis.py
```

## 📋 Requirements

- Python 3.8+
- LangChain 0.1.0+
- OpenAI API key (or other LLM provider)
- hedera-defi SDK

## 🔑 Environment Setup

### OpenRouter Setup (Recommended - Free tier available)
```bash
# 1. Get free API key from https://openrouter.ai
export OPENROUTER_API_KEY="your_openrouter_key_here"

# 2. Install with OpenRouter support
pip install langchain-hedera[examples]
```

### OpenAI Setup
```bash
export OPENAI_API_KEY="your_openai_key_here"
```

### Custom Hedera Endpoints (Optional)
```bash
export HEDERA_ENDPOINT="https://mainnet-public.mirrornode.hedera.com/api/v1"
export BONZO_API="https://mainnet-data.bonzo.finance" 
export SAUCERSWAP_API="https://server.saucerswap.finance/api/public"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Documentation: [Coming Soon]
- Issues: [GitHub Issues](https://github.com/samthedataman/langchain-hedera/issues)
- Community: [Discord/Telegram] 

## 🔗 Related Projects

- [hedera-defi-sdk](https://github.com/samthedataman/hedera-defi-sdk) - Core Python SDK
- [hedera-defi-js](https://github.com/samthedataman/hedera-defi-sdk-js) - TypeScript/JavaScript SDK
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework

---

**Built with ❤️ for the Hedera DeFi ecosystem**