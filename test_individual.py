#!/usr/bin/env python3
"""Test individual components without duplication"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.slack_client import SlackClient
from src.llm_client import LLMClient
from dotenv import load_dotenv

load_dotenv()

def test_ai_tip_only():
    """Test just the AI tip generation"""
    print("🧪 Testing AI Tip Generation Only...")
    
    # Check config
    if not Config.OPENROUTER_API_KEY:
        print("❌ Missing OpenRouter API key!")
        return
        
    llm = LLMClient()
    slack = SlackClient()
    
    # Generate a real AI tip using the LLM
    print("🤖 Generating AI tip with LLM...")
    tip = llm.generate_ai_tip()
    
    if tip:
        print(f"\n💡 Generated tip: {tip}")
        print("\n📤 Posting to Slack...")
        slack.send_ai_tip(tip)
        print("✅ AI tip posted successfully!")
    else:
        print("❌ Failed to generate AI tip")

def test_single_item():
    """Test with a single news/podcast item"""
    print("🧪 Testing Single Item Post...")
    
    slack = SlackClient()
    
    # Sample article for testing
    article = {
        'title': 'Test Article: AI Advances in Healthcare',
        'url': 'https://example.com/test',
        'feed_name': 'Test Feed',
        'feed_type': 'news'
    }
    
    summary = [
        "AI model achieves 95% accuracy in early disease detection",
        "New privacy-preserving techniques protect patient data",
        "Clinical trials show promising results for AI-assisted diagnosis"
    ]
    
    print("📤 Posting single article...")
    slack.send_news_summary(article, summary)
    print("✅ Single article posted!")

def test_formatting():
    """Test Slack message formatting"""
    print("🧪 Testing Message Formatting...")
    
    slack = SlackClient()
    
    # Test a message with various formatting
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🧪 Formatting Test"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bold text* | _Italic text_ | ~Strikethrough~ | `Code`"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "• Bullet point 1\n• Bullet point 2\n• Bullet point 3"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ">This is a blockquote\n>It can span multiple lines"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Test completed successfully ✅"
                }
            ]
        }
    ]
    
    import requests
    response = requests.post(
        Config.SLACK_WEBHOOK_URL,
        json={"blocks": blocks},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("✅ Formatting test posted!")
    else:
        print(f"❌ Failed: {response.status_code}")

def main():
    print("=" * 60)
    print("🧪 AI News Summarizer - Individual Component Testing")
    print("=" * 60)
    
    if not Config.SLACK_WEBHOOK_URL:
        print("❌ ERROR: No Slack webhook URL found!")
        return
    
    print("\nSelect what to test:")
    print("1. AI Tip only (with real LLM generation)")
    print("2. Single news article")
    print("3. Slack formatting test")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_ai_tip_only()
        elif choice == "2":
            test_single_item()
        elif choice == "3":
            test_formatting()
        elif choice == "4":
            print("👋 Exiting...")
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()