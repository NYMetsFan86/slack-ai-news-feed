#!/usr/bin/env python3
"""Test the digest format by sending a sample digest to Slack"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.slack_digest import SlackDigest
from src.config import Config
from src.llm_client import LLMClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def test_real_digest_format():
    """Send a real digest with actual LLM-generated content"""
    print("🧪 Testing Real Digest Format...")
    
    if not Config.SLACK_WEBHOOK_URL:
        print("❌ Missing Slack webhook URL!")
        return
    
    digest = SlackDigest()
    
    # Generate real AI tip if API key available
    if Config.OPENROUTER_API_KEY:
        print("🤖 Generating real AI tip...")
        llm = LLMClient()
        ai_tip = llm.generate_ai_tip()
        if ai_tip:
            digest.set_ai_tip(ai_tip)
        else:
            digest.set_ai_tip("When using AI for research, always verify important facts from primary sources. AI is a powerful starting point, not the final authority.")
    else:
        digest.set_ai_tip("When using AI for research, always verify important facts from primary sources. AI is a powerful starting point, not the final authority.")
    
    # Add sample news items
    news_items = [
        {
            'article': {
                'title': 'OpenAI Announces GPT-5 with Advanced Reasoning Capabilities',
                'url': 'https://example.com/gpt5-announcement',
                'feed_name': 'AI News Daily',
                'published': datetime.now().isoformat()
            },
            'summary': [
                "GPT-5 demonstrates 10x improvement in complex reasoning tasks",
                "New model can solve multi-step problems with 95% accuracy",
                "Available through API starting next month at competitive pricing"
            ]
        },
        {
            'article': {
                'title': 'Google DeepMind Achieves Breakthrough in Scientific Discovery',
                'url': 'https://example.com/deepmind-science',
                'feed_name': 'TechCrunch',
                'published': datetime.now().isoformat()
            },
            'summary': [
                "AI system discovers new materials for renewable energy storage",
                "Reduces research time from years to weeks using novel approach",
                "Open-sourcing the model to accelerate scientific progress"
            ]
        },
        {
            'article': {
                'title': 'Microsoft Integrates AI Copilot Across Enterprise Suite',
                'url': 'https://example.com/microsoft-copilot',
                'feed_name': 'The Verge',
                'published': datetime.now().isoformat()
            },
            'summary': [
                "AI assistant now available in Excel, PowerPoint, and Teams",
                "Early adopters report 40% productivity improvement",
                "Enhanced privacy controls address enterprise security concerns"
            ]
        }
    ]
    
    # Add news to digest
    for item in news_items:
        digest.add_news_item(item['article'], item['summary'])
    
    # Add sample podcast items
    podcast_items = [
        {
            'episode': {
                'title': 'The Future of AGI: A Conversation with Leading Researchers',
                'url': 'https://example.com/podcast-agi',
                'feed_name': 'AI Explained',
                'duration': '45 min',
                'published': datetime.now().isoformat()
            },
            'summary': [
                "Timeline predictions range from 5-20 years for AGI development",
                "Key challenges include alignment, safety, and computational limits",
                "Researchers emphasize importance of international cooperation"
            ]
        },
        {
            'episode': {
                'title': 'AI in Healthcare: Real-World Success Stories',
                'url': 'https://example.com/podcast-health',
                'feed_name': 'AI News in 5 Minutes or Less',
                'duration': '5 min',
                'published': datetime.now().isoformat()
            },
            'summary': [
                "AI diagnostics reducing cancer detection time by 70%",
                "Machine learning models predicting patient outcomes with high accuracy",
                "Privacy-preserving techniques enabling secure data sharing"
            ]
        }
    ]
    
    # Add podcasts to digest
    for item in podcast_items:
        digest.add_podcast_item(item['episode'], item['summary'])
    
    # Send the digest
    print("\n📤 Sending test digest to Slack...")
    success = digest.send_digest()
    
    if success:
        print("✅ Test digest sent successfully!")
        print(f"\n📊 Stats: {digest.stats}")
    else:
        print("❌ Failed to send digest")


def test_minimal_digest():
    """Send a minimal digest with just one item of each type"""
    print("🧪 Testing Minimal Digest Format...")
    
    digest = SlackDigest()
    
    # Simple AI tip
    digest.set_ai_tip("Use 'Act as a [role]' at the start of your prompts to get more focused responses. Example: 'Act as a data analyst and help me interpret these sales figures.'")
    
    # One news item
    digest.add_news_item(
        {
            'title': 'Quick Test: AI News Update',
            'url': 'https://example.com/test',
            'feed_name': 'Test Feed'
        },
        [
            "This is the first key point from the article",
            "This is the second important takeaway",
            "This is the final summary point"
        ]
    )
    
    # One podcast
    digest.add_podcast_item(
        {
            'title': 'Quick Test: AI Podcast Episode',
            'url': 'https://example.com/podcast-test',
            'feed_name': 'Test Podcast',
            'duration': '20 min'
        },
        [
            "Key discussion point from the podcast",
            "Important insight shared by the guest",
            "Actionable advice for listeners"
        ]
    )
    
    print("\n📤 Sending minimal test digest...")
    success = digest.send_digest()
    
    if success:
        print("✅ Minimal digest sent successfully!")
    else:
        print("❌ Failed to send digest")


def preview_digest_blocks():
    """Preview the digest structure without sending"""
    print("🔍 Preview Digest Structure (not sending)...")
    
    digest = SlackDigest()
    digest.set_ai_tip("This is a test AI tip")
    digest.add_news_item({'title': 'Test', 'url': '#', 'feed_name': 'Test'}, ['Point 1'])
    
    blocks = digest.build_digest()
    
    print(f"\n📋 Digest will contain {len(blocks)} blocks")
    print("Block types:")
    for i, block in enumerate(blocks):
        print(f"  {i+1}. {block.get('type')} - {block.get('text', {}).get('text', '')[:50]}...")


def main():
    print("=" * 60)
    print("🧪 Slack Digest Format Tester")
    print("=" * 60)
    
    if not Config.SLACK_WEBHOOK_URL:
        print("❌ ERROR: No Slack webhook URL found!")
        return
    
    print("\nSelect test option:")
    print("1. Send REAL digest format (3 news, 2 podcasts, AI tip)")
    print("2. Send MINIMAL digest (1 of each type)")
    print("3. Preview structure only (no sending)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_real_digest_format()
        elif choice == "2":
            test_minimal_digest()
        elif choice == "3":
            preview_digest_blocks()
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()