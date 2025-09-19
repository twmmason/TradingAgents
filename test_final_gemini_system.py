#!/usr/bin/env python3
"""
Final comprehensive test to verify the system is using Google Gemini only
and all OpenAI references have been removed.
"""

import os
import sys
import traceback
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dotenv_path = Path('.') / '.env'
load_dotenv(dotenv_path)

def test_imports():
    """Test that all imports are working correctly with Google Gemini"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    issues = []
    
    # Test trading graph imports
    try:
        from tradingagents.graph.trading_graph import TradingGraph
        print("✅ TradingGraph imported successfully")
    except ImportError as e:
        issues.append(f"❌ Failed to import TradingGraph: {e}")
    
    # Test agent utils imports
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        print("✅ Toolkit imported successfully")
    except ImportError as e:
        issues.append(f"❌ Failed to import Toolkit: {e}")
    
    # Test agent states imports
    try:
        from tradingagents.agents.utils.agent_states import TradingState
        print("✅ TradingState imported successfully")
    except ImportError as e:
        issues.append(f"❌ Failed to import TradingState: {e}")
    
    # Test interface imports
    try:
        from tradingagents.dataflows import interface
        print("✅ Interface module imported successfully")
    except ImportError as e:
        issues.append(f"❌ Failed to import interface: {e}")
    
    # Check for any remaining OpenAI imports
    try:
        import ast
        import glob
        
        print("\n" + "-"*40)
        print("Checking for OpenAI imports...")
        
        openai_found = False
        for py_file in glob.glob("tradingagents/**/*.py", recursive=True):
            with open(py_file, 'r') as f:
                content = f.read()
                if 'from langchain_openai' in content or 'import openai' in content or 'ChatOpenAI' in content:
                    # Check if it's not in a comment
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if ('from langchain_openai' in line or 'import openai' in line or 'ChatOpenAI' in line) and not line.strip().startswith('#'):
                            issues.append(f"❌ Found OpenAI reference in {py_file}:{i}: {line.strip()}")
                            openai_found = True
        
        if not openai_found:
            print("✅ No OpenAI imports found in codebase")
    except Exception as e:
        issues.append(f"❌ Error checking for OpenAI imports: {e}")
    
    return issues

def test_configuration():
    """Test that configuration is set up for Google Gemini"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    issues = []
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print(f"LLM Provider: {DEFAULT_CONFIG['llm_provider']}")
        print(f"Deep Think LLM: {DEFAULT_CONFIG['deep_think_llm']}")
        print(f"Quick Think LLM: {DEFAULT_CONFIG['quick_think_llm']}")
        
        if DEFAULT_CONFIG['llm_provider'] != 'google':
            issues.append(f"❌ LLM provider is not 'google': {DEFAULT_CONFIG['llm_provider']}")
        else:
            print("✅ LLM provider is set to 'google'")
        
        if 'gpt' in DEFAULT_CONFIG['deep_think_llm'].lower():
            issues.append(f"❌ Deep think LLM contains 'gpt': {DEFAULT_CONFIG['deep_think_llm']}")
        elif 'gemini' in DEFAULT_CONFIG['deep_think_llm'].lower():
            print("✅ Deep think LLM is using Gemini")
        
        if 'gpt' in DEFAULT_CONFIG['quick_think_llm'].lower():
            issues.append(f"❌ Quick think LLM contains 'gpt': {DEFAULT_CONFIG['quick_think_llm']}")
        elif 'gemini' in DEFAULT_CONFIG['quick_think_llm'].lower():
            print("✅ Quick think LLM is using Gemini")
        
        # Check API keys
        if DEFAULT_CONFIG.get('google_api_key'):
            print("✅ Google API key is configured")
        else:
            issues.append("❌ Google API key is not configured")
        
    except Exception as e:
        issues.append(f"❌ Error testing configuration: {e}")
    
    return issues

def test_tool_availability():
    """Test that the correct tools are available"""
    print("\n" + "="*60)
    print("TESTING TOOL AVAILABILITY")
    print("="*60)
    
    issues = []
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Create a Toolkit instance
        toolkit = Toolkit(config=DEFAULT_CONFIG)
        
        # Get available tools (methods that don't start with _)
        tool_names = [method for method in dir(toolkit)
                     if not method.startswith('_') and callable(getattr(toolkit, method))]
        
        print(f"Available tools: {tool_names}")
        
        # Check that OpenAI tools are NOT present
        openai_tools = ['get_global_news_openai', 'get_analyst_recommendations_openai']
        for tool in openai_tools:
            if tool in tool_names:
                issues.append(f"❌ OpenAI tool still present: {tool}")
        
        if not any(issue.startswith("❌ OpenAI tool") for issue in issues):
            print("✅ No OpenAI-specific tools found")
        
        # Check that essential tools ARE present
        essential_tools = [
            'get_YFin_data',  # Provides price/market data
            'get_finnhub_news',  # Provides company news
            'get_stockstats_indicators_report',  # Provides technical indicators
            'get_google_news',  # Provides general news
            'get_reddit_news'  # Provides social sentiment
        ]
        
        for tool in essential_tools:
            if tool in tool_names:
                print(f"✅ Essential tool present: {tool}")
            else:
                issues.append(f"❌ Missing essential tool: {tool}")
        
    except Exception as e:
        issues.append(f"❌ Error testing tools: {e}")
        traceback.print_exc()
    
    return issues

def test_llm_initialization():
    """Test that LLMs can be initialized with Google Gemini"""
    print("\n" + "="*60)
    print("TESTING LLM INITIALIZATION")
    print("="*60)
    
    issues = []
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Test deep thinking LLM
        try:
            deep_llm = ChatGoogleGenerativeAI(
                model=DEFAULT_CONFIG["deep_think_llm"],
                google_api_key=DEFAULT_CONFIG.get("google_api_key")
            )
            print(f"✅ Deep thinking LLM initialized: {DEFAULT_CONFIG['deep_think_llm']}")
        except Exception as e:
            issues.append(f"❌ Failed to initialize deep thinking LLM: {e}")
        
        # Test quick thinking LLM
        try:
            quick_llm = ChatGoogleGenerativeAI(
                model=DEFAULT_CONFIG["quick_think_llm"],
                google_api_key=DEFAULT_CONFIG.get("google_api_key")
            )
            print(f"✅ Quick thinking LLM initialized: {DEFAULT_CONFIG['quick_think_llm']}")
        except Exception as e:
            issues.append(f"❌ Failed to initialize quick thinking LLM: {e}")
        
        # Test a simple generation if API key is available
        if DEFAULT_CONFIG.get("google_api_key") and DEFAULT_CONFIG["google_api_key"] != "your_google_api_key_here":
            try:
                from langchain_core.messages import HumanMessage
                response = quick_llm.invoke([HumanMessage(content="Say 'Google Gemini is working' in 5 words or less")])
                print(f"✅ LLM generation successful: {response.content[:50]}...")
            except Exception as e:
                issues.append(f"❌ Failed to generate with LLM: {e}")
        
    except ImportError as e:
        issues.append(f"❌ Failed to import ChatGoogleGenerativeAI: {e}")
    except Exception as e:
        issues.append(f"❌ Error testing LLM initialization: {e}")
        traceback.print_exc()
    
    return issues

def test_trading_graph():
    """Test that TradingGraph can be initialized"""
    print("\n" + "="*60)
    print("TESTING TRADING GRAPH")
    print("="*60)
    
    issues = []
    
    try:
        from tradingagents.graph.trading_graph import TradingGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Try to create a TradingGraph instance
        try:
            graph = TradingGraph(config=DEFAULT_CONFIG)
            print("✅ TradingGraph initialized successfully")
            
            # Check that it's using the right LLM provider
            if hasattr(graph, 'deep_thinking_llm'):
                llm_class = type(graph.deep_thinking_llm).__name__
                if 'ChatGoogleGenerativeAI' in llm_class:
                    print(f"✅ Using Google Gemini LLM: {llm_class}")
                elif 'OpenAI' in llm_class:
                    issues.append(f"❌ Still using OpenAI LLM: {llm_class}")
                else:
                    print(f"⚠️  Using LLM: {llm_class}")
            
        except Exception as e:
            issues.append(f"❌ Failed to initialize TradingGraph: {e}")
            traceback.print_exc()
        
    except ImportError as e:
        issues.append(f"❌ Failed to import TradingGraph: {e}")
    except Exception as e:
        issues.append(f"❌ Error testing TradingGraph: {e}")
        traceback.print_exc()
    
    return issues

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("FINAL GOOGLE GEMINI MIGRATION TEST")
    print("="*80)
    
    all_issues = []
    
    # Run all test suites
    all_issues.extend(test_imports())
    all_issues.extend(test_configuration())
    all_issues.extend(test_tool_availability())
    all_issues.extend(test_llm_initialization())
    all_issues.extend(test_trading_graph())
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issue(s):\n")
        for issue in all_issues:
            print(f"  {issue}")
        print("\n⚠️  The system may not be fully migrated to Google Gemini")
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("✅ The system has been successfully migrated to Google Gemini")
        print("✅ No OpenAI references found")
        print("✅ Configuration is correct")
        print("✅ Tools are properly configured")
        print("✅ LLMs can be initialized")
        print("\n🎉 Migration complete!")
    
    print("\n" + "="*80)
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)