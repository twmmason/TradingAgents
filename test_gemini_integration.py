#!/usr/bin/env python3
"""
Test script to verify Google Gemini integration in TradingAgents
"""

import sys
import traceback
from datetime import datetime
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.interface import (
    get_global_news_openai,
    get_fundamentals_openai,
    get_stock_news_openai
)

def test_configuration():
    """Test that configuration is set for Google Gemini"""
    print("=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    
    assert DEFAULT_CONFIG["llm_provider"] == "google", f"Expected 'google', got {DEFAULT_CONFIG['llm_provider']}"
    assert "gemini" in DEFAULT_CONFIG["deep_think_llm"].lower(), f"Expected Gemini model, got {DEFAULT_CONFIG['deep_think_llm']}"
    assert "gemini" in DEFAULT_CONFIG["quick_think_llm"].lower(), f"Expected Gemini model, got {DEFAULT_CONFIG['quick_think_llm']}"
    assert DEFAULT_CONFIG["google_api_key"] is not None, "Google API key not set"
    
    print(f"✅ LLM Provider: {DEFAULT_CONFIG['llm_provider']}")
    print(f"✅ Deep Think LLM: {DEFAULT_CONFIG['deep_think_llm']}")
    print(f"✅ Quick Think LLM: {DEFAULT_CONFIG['quick_think_llm']}")
    print(f"✅ Google API Key: {'Set' if DEFAULT_CONFIG['google_api_key'] else 'Not Set'}")
    print()
    return True

def test_global_news():
    """Test global news function with Gemini"""
    print("=" * 60)
    print("Testing Global News Function")
    print("=" * 60)
    
    try:
        curr_date = datetime.now().strftime("%Y-%m-%d")
        print(f"Fetching global news for date: {curr_date}")
        
        result = get_global_news_openai(curr_date)
        
        if result and len(result) > 0:
            print(f"✅ Successfully fetched global news")
            print(f"   Response length: {len(result)} characters")
            print(f"   Preview: {result[:200]}...")
        else:
            print("⚠️ Function returned empty result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False
    
    print()
    return True

def test_fundamentals():
    """Test fundamentals function with Gemini"""
    print("=" * 60)
    print("Testing Fundamentals Function")
    print("=" * 60)
    
    try:
        ticker = "AAPL"
        curr_date = datetime.now().strftime("%Y-%m-%d")
        print(f"Fetching fundamentals for {ticker} on {curr_date}")
        
        result = get_fundamentals_openai(ticker, curr_date)
        
        if result and len(result) > 0:
            print(f"✅ Successfully fetched fundamentals")
            print(f"   Response length: {len(result)} characters")
            print(f"   Preview: {result[:200]}...")
        else:
            print("⚠️ Function returned empty result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False
    
    print()
    return True

def test_stock_news():
    """Test stock news function with Gemini"""
    print("=" * 60)
    print("Testing Stock News Function")
    print("=" * 60)
    
    try:
        ticker = "AAPL"
        curr_date = datetime.now().strftime("%Y-%m-%d")
        print(f"Fetching stock news for {ticker} on {curr_date}")
        
        result = get_stock_news_openai(ticker, curr_date)
        
        if result and len(result) > 0:
            print(f"✅ Successfully fetched stock news")
            print(f"   Response length: {len(result)} characters")
            print(f"   Preview: {result[:200]}...")
        else:
            print("⚠️ Function returned empty result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False
    
    print()
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TradingAgents Google Gemini Integration Test")
    print("=" * 60 + "\n")
    
    all_passed = True
    
    # Test configuration
    if not test_configuration():
        all_passed = False
        print("❌ Configuration test failed")
    
    # Test functions
    print("\nTesting API Functions (using Google Gemini):\n")
    
    if not test_global_news():
        all_passed = False
    
    if not test_fundamentals():
        all_passed = False
    
    if not test_stock_news():
        all_passed = False
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed! Google Gemini integration is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())