#!/usr/bin/env python3
"""
Test script for TradingAgents system with Google Gemini
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_trading_system():
    """Test the TradingAgents system with Google Gemini"""
    
    print("=" * 60)
    print("Testing TradingAgents System with Google Gemini")
    print("=" * 60)
    
    # Import after path is set
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    
    # Display configuration
    print("\n📋 Configuration:")
    print(f"  LLM Provider: {DEFAULT_CONFIG['llm_provider']}")
    print(f"  Deep Think Model: {DEFAULT_CONFIG['deep_think_llm']}")
    print(f"  Quick Think Model: {DEFAULT_CONFIG['quick_think_llm']}")
    
    # Check API keys
    google_key = os.getenv('GOOGLE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    print("\n🔑 API Keys Status:")
    print(f"  GOOGLE_API_KEY: {'✅ Loaded' if google_key else '❌ Not found'}")
    print(f"  FINNHUB_API_KEY: {'✅ Loaded' if finnhub_key else '❌ Not found'}")
    
    if not google_key:
        print("\n❌ Error: GOOGLE_API_KEY not found in environment!")
        print("Please ensure your .env file contains GOOGLE_API_KEY")
        return
    
    # Test parameters
    stock_symbol = "AAPL"  # Apple Inc.
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    initial_capital = 100000
    
    print(f"\n📊 Test Parameters:")
    print(f"  Stock Symbol: {stock_symbol}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Initial Capital: ${initial_capital:,}")
    
    try:
        # Initialize the trading graph
        print("\n🚀 Initializing TradingAgents Graph...")
        
        # Use a minimal set of analysts for testing
        selected_analysts = ["market", "news"]  # Start with just market and news
        
        trading_graph = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=True,  # Enable debug mode for more output
            config=DEFAULT_CONFIG
        )
        
        print("✅ Graph initialized successfully!")
        
        # Run the analysis
        print(f"\n🔄 Running analysis for {stock_symbol}...")
        print("(This may take a few minutes...)\n")
        
        # The propagate method takes company_name and trade_date
        # Use end_date as the trade date for analysis
        result, processed_signal = trading_graph.propagate(
            company_name=stock_symbol,
            trade_date=end_date
        )
        
        print("\n✅ Analysis completed successfully!")
        
        # Display results
        print("\n📈 Results:")
        print(f"  Processed Signal: {processed_signal}")
        
        # Check for various possible result keys
        if result:
            print(f"\n  Available keys in result: {list(result.keys())[:10]}")
            
            # Try to display final trade decision
            if "final_trade_decision" in result:
                print(f"\n  Final Trade Decision (preview):")
                decision_text = str(result["final_trade_decision"])
                print(f"    {decision_text[:300]}..." if len(decision_text) > 300 else f"    {decision_text}")
            
            # Try to display investment plan
            if "investment_plan" in result:
                print(f"\n  Investment Plan (preview):")
                plan_text = str(result["investment_plan"])
                print(f"    {plan_text[:300]}..." if len(plan_text) > 300 else f"    {plan_text}")
        
        # Check if reports were generated
        reports_dir = Path(f"results/{stock_symbol}/{datetime.now().strftime('%Y-%m-%d')}/reports")
        if reports_dir.exists():
            print(f"\n📁 Reports generated in: {reports_dir}")
            for report_file in reports_dir.glob("*.md"):
                print(f"  - {report_file.name}")
        
        print("\n✅ Test completed successfully!")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Please ensure all required packages are installed")
        print("Run: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Additional debugging info
        print("\n🔍 Debug Information:")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")

if __name__ == "__main__":
    test_trading_system()