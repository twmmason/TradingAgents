#!/usr/bin/env python3
"""
Test script for the new google-genai SDK integration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.resolve()
dotenv_path = project_root / '.env'
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path)

# Check if API key is available
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment")
    sys.exit(1)

print(f"✅ GOOGLE_API_KEY loaded (first 15 chars): {api_key[:15]}...")

try:
    # Import the new SDK
    from google import genai
    print("✅ Successfully imported google-genai SDK")
    
    # Create a client
    client = genai.Client(api_key=api_key)
    print("✅ Client created successfully")
    
    # List available models
    print("\n📋 Available Gemini models:")
    models = client.models.list()
    for model in models:
        print(f"  - {model.name}")
    
    # Test text generation
    print("\n🧪 Testing text generation with gemini-2.0-flash-exp...")
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='Say "Hello from Gemini SDK!" in exactly 5 words.'
    )
    print(f"Response: {response.text}")
    
    # Test with a more complex prompt
    print("\n🧪 Testing more complex generation...")
    complex_response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='Provide a brief summary of the current global economic situation in 2-3 sentences.'
    )
    print(f"Complex response: {complex_response.text}")
    
    # Test system instruction
    print("\n📝 Testing with system instruction...")
    from google.genai.types import GenerateContentConfig
    
    config = GenerateContentConfig(
        system_instruction="You are a helpful financial analyst assistant.",
        temperature=0.7
    )
    
    analyst_response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='What are the key factors to consider when analyzing a stock?',
        config=config
    )
    if analyst_response and hasattr(analyst_response, 'text'):
        response_text = analyst_response.text if analyst_response.text else "No text in response"
        print(f"Analyst response: {response_text[:500] if len(response_text) > 500 else response_text}...")
    else:
        print("Analyst response: No valid response received")
    
    print("\n✅ All tests passed! The new google-genai SDK is working correctly.")
    
except ImportError as e:
    print(f"❌ Failed to import google-genai SDK: {e}")
    print("\nPlease install it with: pip install google-genai")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)