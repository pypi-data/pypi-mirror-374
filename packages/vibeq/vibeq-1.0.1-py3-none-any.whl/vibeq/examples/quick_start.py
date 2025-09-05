#!/usr/bin/env python3
"""
VibeQ Example: Quick Start
Your first VibeQ automation script

Copy this file and modify for your own website!
"""
from vibeq import VibeQ
import time

def main():
    print("🚀 VibeQ Quick Start Example")
    print("This script shows basic VibeQ usage patterns\n")
    
    # Initialize VibeQ with flexible AI provider options
    vq = VibeQ(
        ai_provider="auto",      # Auto-detect from environment or use "openai", "anthropic", "grok", "local"
        headless=False           # Show browser for learning
    )
    
    # Alternative configurations:
    # vq = VibeQ(ai_provider="openai")        # Use OpenAI GPT-4
    # vq = VibeQ(ai_provider="anthropic")     # Use Claude
    # vq = VibeQ(ai_provider="grok")          # Use Grok
    # vq = VibeQ(ai_provider="local")         # Use local model (Ollama/LM Studio)
    # vq = VibeQ(ai_provider="custom", ai_endpoint="http://localhost:1234/v1")  # Custom endpoint
    
    # Launch browser
    vq.launch_browser()
    
    try:
        # Example 1: Basic Navigation and Form Filling
        print("📋 Example 1: Form Automation")
        vq.go_to("https://www.saucedemo.com/")
        
        # Use natural language - VibeQ figures out the selectors
        vq.do("type standard_user in username field")
        vq.do("type secret_sauce in password field")
        vq.do("click login button")
        
        # Verify success
        if vq.check("inventory page loaded successfully"):
            print("✅ Login successful!")
        
        time.sleep(2)  # Pause to see results
        
        # Example 2: E-commerce Workflow
        print("\n📋 Example 2: Shopping Workflow")
        vq.do("click add to cart for first product")
        vq.do("click shopping cart icon")
        
        # Verify cart has items
        if vq.check("cart contains items"):
            print("✅ Product added to cart!")
        
        print("\n🎉 Examples completed successfully!")
        print("Modify this script for your own websites!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your API key and internet connection")
        
    finally:
        vq.close()
        print("🧹 Browser closed")

if __name__ == "__main__":
    main()
