#!/usr/bin/env python3
"""Debug OpenAI client initialization"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("Testing OpenAI client initialization...")

try:
    import openai
    print(f"OpenAI version: {openai.__version__}")
    
    from src.config import Config
    print(f"Base URL: {Config.OPENROUTER_BASE_URL}")
    print(f"API Key present: {bool(Config.OPENROUTER_API_KEY)}")
    
    # Try to initialize the client
    print("\nTrying to create OpenAI client...")
    client = openai.OpenAI(
        base_url=Config.OPENROUTER_BASE_URL,
        api_key=Config.OPENROUTER_API_KEY,
    )
    print("✅ Client created successfully!")
    
    # Check client attributes
    print(f"Client type: {type(client)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()