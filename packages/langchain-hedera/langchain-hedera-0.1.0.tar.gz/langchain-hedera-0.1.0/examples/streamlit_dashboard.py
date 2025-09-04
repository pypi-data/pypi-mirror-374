"""
Streamlit Dashboard Example using OpenRouter + LangChain Hedera

Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Only import if available
try:
    from openai import OpenAI
    from langchain_openai import ChatOpenAI
    from langchain_hedera import HederaDeFiAgent, TradingAnalysisAgent
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


def main():
    """Main Streamlit dashboard."""
    
    st.set_page_config(
        page_title="Hedera DeFi Analysis Dashboard",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Hedera DeFi Analysis Dashboard")
    st.markdown("*Powered by LangChain Hedera SDK + OpenRouter*")
    
    if not DEPS_AVAILABLE:
        st.error("Missing dependencies. Install with: pip install langchain-hedera[examples]")
        st.stop()
    
    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "OpenRouter API Key",
        type="password",
        value=os.getenv("OPENROUTER_API_KEY", ""),
        help="Get your free API key from https://openrouter.ai"
    )
    
    # Model selection
    models = {
        "Free (Gemini 2.5 Flash)": "google/gemini-2.5-flash-image-preview:free",
        "Fast (Gemini 2.5 Flash Lite)": "google/gemini-2.5-flash-lite", 
        "Balanced (Gemini 2.5 Flash)": "google/gemini-2.5-flash",
        "Premium (Gemini 2.5 Pro)": "google/gemini-2.5-pro",
    }
    
    selected_model_name = st.sidebar.selectbox(
        "Select Model",
        list(models.keys()),
        index=0
    )
    selected_model = models[selected_model_name]
    
    # Analysis parameters
    st.sidebar.subheader("📊 Analysis Parameters")
    
    whale_threshold = st.sidebar.number_input(
        "Whale Threshold (HBAR)",
        min_value=1000,
        max_value=1000000,
        value=50000,
        step=5000
    )
    
    min_apy = st.sidebar.slider(
        "Minimum APY (%)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.5
    )
    
    if not api_key:
        st.warning("🔑 Please enter your OpenRouter API key in the sidebar to begin analysis")
        st.info("Get a free API key at https://openrouter.ai")
        st.stop()
    
    # Initialize LLM and agents
    @st.cache_resource
    def get_agents(api_key, model):
        """Initialize agents with caching."""
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model,
            temperature=0.1,
        )
        
        defi_agent = HederaDeFiAgent(llm, verbose=False)
        trading_agent = TradingAnalysisAgent(llm, verbose=False)
        
        return defi_agent, trading_agent
    
    try:
        defi_agent, trading_agent = get_agents(api_key, selected_model)
        st.sidebar.success(f"✅ Agents initialized with {selected_model_name}")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to initialize: {e}")
        st.stop()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Ecosystem Overview", 
        "💰 Arbitrage Opportunities", 
        "🐋 Whale Monitoring",
        "📊 Custom Analysis"
    ])
    
    with tab1:
        st.header("🌍 Hedera DeFi Ecosystem Overview")
        
        if st.button("🔍 Analyze Ecosystem", key="ecosystem_btn"):
            with st.spinner("Analyzing Hedera DeFi ecosystem..."):
                try:
                    analysis = defi_agent.analyze_ecosystem(
                        focus_areas=["protocols", "opportunities"]
                    )
                    
                    output = analysis.get("output", "No analysis available")
                    st.success("✅ Analysis completed")
                    st.markdown(output)
                    
                    # Show raw data in expander
                    with st.expander("📄 Raw Analysis Data"):
                        st.json(analysis)
                        
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
    
    with tab2:
        st.header("💰 Arbitrage Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            arb_min_profit = st.number_input(
                "Minimum Profit (%)",
                min_value=0.1,
                max_value=10.0,
                value=2.0,
                step=0.1
            )
        
        with col2:
            focus_tokens = st.multiselect(
                "Focus Tokens",
                ["HBAR", "USDC", "SAUCE", "ETH", "BTC"],
                default=["HBAR", "USDC"]
            )
        
        if st.button("🔍 Find Arbitrage", key="arbitrage_btn"):
            with st.spinner("Searching for arbitrage opportunities..."):
                try:
                    opportunities = trading_agent.find_arbitrage_opportunities(
                        min_profit_percent=arb_min_profit
                    )
                    
                    output = opportunities.get("output", "No opportunities found")
                    st.success("✅ Arbitrage analysis completed")
                    st.markdown(output)
                    
                    with st.expander("📄 Raw Opportunity Data"):
                        st.json(opportunities)
                        
                except Exception as e:
                    st.error(f"❌ Arbitrage analysis failed: {e}")
    
    with tab3:
        st.header("🐋 Whale Transaction Monitoring")
        
        if st.button("🔍 Monitor Whales", key="whale_btn"):
            with st.spinner(f"Monitoring whale transactions above {whale_threshold:,.0f} HBAR..."):
                try:
                    whale_activity = defi_agent.monitor_whale_activity(
                        threshold=whale_threshold
                    )
                    
                    output = whale_activity.get("output", "No whale activity detected")
                    st.success("✅ Whale monitoring completed")
                    st.markdown(output)
                    
                    with st.expander("📄 Raw Whale Data"):
                        st.json(whale_activity)
                        
                except Exception as e:
                    st.error(f"❌ Whale monitoring failed: {e}")
    
    with tab4:
        st.header("📊 Custom Analysis")
        
        analysis_type = st.selectbox(
            "Analysis Type",
            [
                "Market Report",
                "Protocol Comparison", 
                "Yield Opportunities",
                "Risk Assessment"
            ]
        )
        
        custom_query = st.text_area(
            "Custom Analysis Query",
            placeholder="Enter your custom DeFi analysis question...",
            height=100
        )
        
        if st.button("🔍 Run Analysis", key="custom_btn"):
            if custom_query:
                with st.spinner(f"Running {analysis_type.lower()}..."):
                    try:
                        if analysis_type == "Market Report":
                            result = defi_agent.get_market_report(include_predictions=True)
                        else:
                            # Use the custom query directly
                            result = defi_agent.agent.invoke({"input": custom_query})
                        
                        output = result.get("output", str(result))
                        st.success("✅ Custom analysis completed")
                        st.markdown(output)
                        
                        with st.expander("📄 Raw Analysis Data"):
                            st.json(result)
                            
                    except Exception as e:
                        st.error(f"❌ Custom analysis failed: {e}")
            else:
                st.warning("Please enter a custom query")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🛠️ **Built with:** LangChain Hedera SDK | "
        "🤖 **Powered by:** OpenRouter API | "
        "⛓️ **Data from:** Hedera Mirror Node, SaucerSwap, Bonzo Finance"
    )


if __name__ == "__main__":
    main()