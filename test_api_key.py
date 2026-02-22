#!/usr/bin/env python3
"""Test that the DeepSeek API key is properly loaded and LLM client can be initialized."""

import sys
import os
sys.path.insert(0, '.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("Testing DeepSeek API key loading...")
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"Key starts with: {api_key[:10]}...")
    print(f"Key length: {len(api_key)} characters")
    
    # Check if it's still the placeholder
    if api_key == "your_deepseek_api_key_here":
        print("WARNING: API key is still the placeholder!")
    else:
        print("API key appears to be a real key (not placeholder).")

# Test initializing an AgentBrain with LLM
print("\nTesting AgentBrain LLM initialization...")
try:
    from red_dust.agents.personas import create_all_personas
    from red_dust.agents.brain import AgentBrain
    
    personas = create_all_personas()
    if personas:
        persona = personas[0]  # Take first persona
        print(f"Testing with persona: {persona.name}")
        
        # Initialize brain with LLM enabled
        brain = AgentBrain(persona, use_llm=True)
        
        print(f"Brain.use_llm: {brain.use_llm}")
        print(f"Brain.llm_client is not None: {brain.llm_client is not None}")
        
        if brain.llm_client:
            print("SUCCESS: LLM client initialized!")
            # Optional: test a simple non-API call to verify client configuration
            print(f"Client base_url: {brain.llm_client.base_url}")
        else:
            print("FAILED: LLM client not initialized.")
            print("This could be due to:")
            print("  - Missing openai package (pip install openai)")
            print("  - Invalid API key format")
            print("  - Network issues")
            
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required packages:")
    print("  pip install openai python-dotenv")
except Exception as e:
    print(f"Error during testing: {type(e).__name__}: {e}")

print("\nTest completed.")