"""
Test script for Google Search grounding feature in Gemini
Based on the notebook example and Google documentation
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path('.').resolve()
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path)

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key or api_key == 'your_google_api_key_here':
    print("Error: Google API key not configured. Please set GOOGLE_API_KEY in your .env file.")
    exit(1)

print(f"API Key loaded: {api_key[:15]}...")

# Configure the API
genai.configure(api_key=api_key)

print("\n=== Testing Google Search Grounding ===\n")

# Test 1: Basic grounding test with gemini-2.0-flash-exp
print("Test 1: Using gemini-2.0-flash-exp with Google Search grounding")
print("-" * 50)

try:
    # Create model instance
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
    
    # Create prompt that requires current information
    prompt = """What are the latest global economic news and market trends today? 
    Include information about:
    1. Stock market performance
    2. Central bank policies
    3. Major economic indicators
    4. Currency movements
    """
    
    # Generate content with Google Search grounding
    # Using the exact syntax from the notebook
    response = model.generate_content(
        contents=prompt,
        generation_config={"tools": [{"google_search": {}}]}
    )
    
    if response.text:
        print("✅ Response generated successfully!")
        print("\nResponse preview (first 500 chars):")
        print(response.text[:500])
        
        # Try to get grounding metadata
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    metadata = candidate.grounding_metadata
                    print("\n📍 Grounding Metadata:")
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        print(f"  Search Queries: {metadata.web_search_queries}")
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        print(f"  Sources Used: {len(metadata.grounding_chunks)} web pages")
                        for i, chunk in enumerate(metadata.grounding_chunks[:3], 1):
                            if hasattr(chunk, 'web') and hasattr(chunk.web, 'title'):
                                print(f"    {i}. {chunk.web.title}")
        except Exception as e:
            print(f"\nNote: Could not extract grounding metadata: {e}")
    else:
        print("⚠️ No response text generated")
        
except Exception as e:
    print(f"❌ Error with grounding: {e}")
    print("\nAttempting fallback without grounding...")
    
    # Fallback test without grounding
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        if response.text:
            print("✅ Fallback response generated (without grounding)")
            print("\nResponse preview (first 300 chars):")
            print(response.text[:300])
    except Exception as fallback_error:
        print(f"❌ Fallback also failed: {fallback_error}")

print("\n" + "=" * 50)

# Test 2: Test with different model
print("\nTest 2: Testing with gemini-1.5-flash (for comparison)")
print("-" * 50)

try:
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    # Try with grounding (may not be supported)
    try:
        response = model.generate_content(
            contents="What are the latest stock market trends?",
            generation_config={"tools": [{"google_search": {}}]}
        )
        print("✅ Gemini 1.5 Flash supports grounding!")
        if response.text:
            print(f"Response preview: {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Gemini 1.5 Flash doesn't support grounding: {e}")
        
        # Try without grounding
        response = model.generate_content("What are the latest stock market trends?")
        if response.text:
            print("✅ Response without grounding:")
            print(f"Response preview: {response.text[:200]}")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)

# Test the actual function from interface.py
print("\nTest 3: Testing get_global_news_openai function")
print("-" * 50)

try:
    from tradingagents.dataflows.interface import get_global_news_openai
    
    result = get_global_news_openai("2025-09-18")
    print("✅ Function executed successfully!")
    print(f"\nResult type: {type(result)}")
    print(f"Result length: {len(result)} characters")
    print("\nResult preview (first 500 chars):")
    print(result[:500])
    
    # Check if grounding was used
    if "via Google Search" in result:
        print("\n✅ Google Search grounding appears to be active")
    elif "Aggregated" in result or "Analysis" in result:
        print("\n⚠️ Fallback aggregation method was used")
    else:
        print("\n❓ Unclear which method was used")
        
except Exception as e:
    print(f"❌ Error testing function: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("\n✨ Testing complete!")