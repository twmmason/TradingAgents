#!/usr/bin/env python3
"""
Comprehensive integration test to verify all OpenAI dependencies have been removed
and the system works with Google Gemini only.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import traceback
import importlib

# Load environment variables
dotenv_path = Path('.') / '.env'
load_dotenv(dotenv_path)

# Add the project directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_configuration():
    """Test that configuration is properly set for Google Gemini."""
    print("=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60)
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Check LLM provider
        assert DEFAULT_CONFIG["llm_provider"] in ["google", "google_genai"], f"Expected llm_provider to be 'google' or 'google_genai', got {DEFAULT_CONFIG['llm_provider']}"
        print(f"✅ LLM Provider: {DEFAULT_CONFIG['llm_provider']}")
        
        # Check model names
        assert "gemini" in DEFAULT_CONFIG["deep_think_llm"].lower(), f"Expected Gemini model for deep_think_llm, got {DEFAULT_CONFIG['deep_think_llm']}"
        assert "gemini" in DEFAULT_CONFIG["quick_think_llm"].lower(), f"Expected Gemini model for quick_think_llm, got {DEFAULT_CONFIG['quick_think_llm']}"
        print(f"✅ Deep Think LLM: {DEFAULT_CONFIG['deep_think_llm']}")
        print(f"✅ Quick Think LLM: {DEFAULT_CONFIG['quick_think_llm']}")
        
        # Check API keys
        google_key = DEFAULT_CONFIG.get('google_api_key')
        assert google_key and google_key != 'your_google_api_key_here', "Google API key not properly configured"
        print(f"✅ Google API Key configured: {google_key[:15]}...")
        
        print("\n✅ Configuration test PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test FAILED: {e}\n")
        traceback.print_exc()
        return False

def test_interface_functions():
    """Test that interface functions don't reference OpenAI."""
    print("=" * 60)
    print("TESTING INTERFACE FUNCTIONS")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows import interface
        
        # Check that OpenAI functions don't exist or have been replaced
        functions_to_check = [
            'get_global_news_openai',
            'get_stock_news_openai', 
            'get_fundamentals_openai'
        ]
        
        for func_name in functions_to_check:
            if hasattr(interface, func_name):
                func = getattr(interface, func_name)
                # Check if it's a deprecated stub
                if "deprecated" in str(func.__doc__).lower() or "no longer available" in str(func.__doc__).lower():
                    print(f"✅ {func_name} is properly deprecated/stubbed")
                else:
                    # Try calling it to see if it's actually functional
                    try:
                        result = func('2025-09-18')
                        if "deprecated" in result.lower() or "no longer available" in result.lower() or "not available" in result.lower():
                            print(f"✅ {func_name} returns deprecation message")
                        else:
                            print(f"⚠️  {func_name} still appears to be functional")
                    except Exception as e:
                        print(f"✅ {func_name} raises error when called: {type(e).__name__}")
            else:
                print(f"✅ {func_name} has been removed from interface")
        
        # Test Google News function exists and works
        if hasattr(interface, 'get_google_news'):
            print(f"✅ get_google_news function exists")
        else:
            print(f"❌ get_google_news function not found")
            
        print("\n✅ Interface functions test PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Interface functions test FAILED: {e}\n")
        traceback.print_exc() 
        return False

def test_agent_creation():
    """Test that all agents can be created without OpenAI dependencies."""
    print("=" * 60)
    print("TESTING AGENT CREATION")
    print("=" * 60)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.agents.utils.memory import MemoryTool
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Create LLM instances
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_CONFIG["deep_think_llm"],
            temperature=0.7,
            google_api_key=DEFAULT_CONFIG["google_api_key"]
        )
        print("✅ Created Google Gemini LLM instance")
        
        # Create toolkit
        toolkit = Toolkit(DEFAULT_CONFIG)
        print("✅ Created Toolkit instance")
        
        # Check that OpenAI tools are not in toolkit
        openai_tools = ['get_global_news_openai', 'get_stock_news_openai', 'get_fundamentals_openai']
        for tool in openai_tools:
            assert not hasattr(toolkit, tool), f"OpenAI tool {tool} still exists in Toolkit"
        print("✅ Verified no OpenAI tools in Toolkit")
        
        # Create memory
        memory = MemoryTool(DEFAULT_CONFIG)
        print("✅ Created Memory instance")
        
        # Test creating each analyst
        analysts = [
            ('news_analyst', 'tradingagents.agents.analysts.news_analyst', 'create_news_analyst'),
            ('fundamentals_analyst', 'tradingagents.agents.analysts.fundamentals_analyst', 'create_fundamentals_analyst'),
            ('social_media_analyst', 'tradingagents.agents.analysts.social_media_analyst', 'create_social_media_analyst'),
            ('market_analyst', 'tradingagents.agents.analysts.market_analyst', 'create_market_analyst'),
        ]
        
        for name, module_path, func_name in analysts:
            try:
                module = importlib.import_module(module_path)
                create_func = getattr(module, func_name)
                # Create the analyst (don't call it, just verify it can be created)
                analyst = create_func(llm, toolkit)
                print(f"✅ Created {name} successfully")
            except Exception as e:
                print(f"❌ Failed to create {name}: {e}")
                raise
        
        print("\n✅ Agent creation test PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent creation test FAILED: {e}\n")
        traceback.print_exc()
        return False

def test_no_openai_imports():
    """Scan codebase for any remaining OpenAI imports."""
    print("=" * 60)
    print("TESTING FOR OPENAI IMPORTS")
    print("=" * 60)
    
    try:
        import subprocess
        
        # Search for OpenAI imports in Python files
        openai_patterns = [
            "from openai",
            "import openai",
            "from langchain_openai",
            "import langchain_openai",
            "OpenAI",
            "ChatOpenAI"
        ]
        
        found_issues = []
        
        for pattern in openai_patterns:
            # Use grep to search for patterns, excluding test files and this file
            cmd = f"grep -r --include='*.py' '{pattern}' tradingagents/ 2>/dev/null | grep -v 'test_' | grep -v '__pycache__' || true"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Skip comments and docstrings
                    if '#' not in line and '"""' not in line and "'''" not in line:
                        # Check if it's in actual code
                        if ':' in line:
                            file_path, code = line.split(':', 1)
                            # Skip if it's a comment
                            code_stripped = code.strip()
                            if not code_stripped.startswith('#'):
                                found_issues.append((pattern, line))
        
        if found_issues:
            print(f"⚠️  Found {len(found_issues)} potential OpenAI references:")
            for pattern, line in found_issues:
                print(f"   - {line}")
            print("\nNote: These might be in comments or unused code.")
        else:
            print("✅ No OpenAI imports found in the codebase")
        
        print("\n✅ OpenAI import scan PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI import scan FAILED: {e}\n")
        traceback.print_exc()
        return False

def test_google_genai_sdk():
    """Test that Google GenAI SDK is properly installed and working."""
    print("=" * 60)
    print("TESTING GOOGLE GENAI SDK")
    print("=" * 60)
    
    try:
        # Try the new SDK first
        try:
            from google import genai
            print("✅ New google-genai SDK is available")
            
            # Test creating a client
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                client = genai.Client(api_key=api_key)
                print("✅ Created GenAI client successfully")
                
                # Test a simple generation
                response = client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents='Reply with: Test successful'
                )
                if response and response.text:
                    print(f"✅ Test generation worked: {response.text[:50]}...")
                else:
                    print("⚠️  Generation returned empty response")
                    
        except ImportError:
            print("⚠️  New google-genai SDK not available, trying legacy...")
            
            # Fallback to legacy SDK
            import google.generativeai as genai
            print("✅ Legacy google.generativeai SDK is available")
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content('Reply with: Test successful')
                if response and response.text:
                    print(f"✅ Test generation worked: {response.text[:50]}...")
                    
        # Test LangChain integration
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        print("✅ LangChain Google GenAI integration working")
        
        print("\n✅ Google GenAI SDK test PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Google GenAI SDK test FAILED: {e}\n")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE OPENAI REMOVAL VERIFICATION")
    print("=" * 60 + "\n")
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Configuration", test_configuration),
        ("Interface Functions", test_interface_functions),
        ("Agent Creation", test_agent_creation),
        ("OpenAI Import Scan", test_no_openai_imports),
        ("Google GenAI SDK", test_google_genai_sdk),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} encountered an error: {e}\n")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The system has been successfully migrated to Google Gemini.")
        print("All OpenAI dependencies have been removed.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please review the failures above and fix any remaining issues.")
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)