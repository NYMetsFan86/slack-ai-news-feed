#!/usr/bin/env python3
"""Test the new lighter digest format"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.slack_digest_v2 import SlackDigest
from src.llm_client import LLMClient
import logging

logging.basicConfig(level=logging.INFO)

def test_new_digest():
    """Test the new digest format with sample data"""
    
    # Initialize clients
    digest = SlackDigest()
    llm_client = LLMClient()
    
    # Generate AI tip
    print("Generating AI tip...")
    try:
        ai_tip = llm_client.generate_ai_tip()
        if ai_tip:
            digest.set_ai_tip(ai_tip)
            print(f"✅ AI Tip: {ai_tip}")
        else:
            # Use a sample tip if generation fails
            digest.set_ai_tip("🎯 Try Perplexity's 'Focus' mode for research - it cites sources like Wikipedia or Reddit only. Perfect for fact-checking!")
            print("✅ Using sample AI tip")
    except Exception as e:
        print(f"❌ Error generating AI tip: {e}")
        digest.set_ai_tip("💡 ChatGPT can analyze photos now! Upload a receipt and ask it to create an expense report. Works in the free version!")
    
    # Add sample podcast items
    sample_podcasts = [
        {
            'episode': {
                'title': 'AI Daily Brief: ChatGPT Gets Voice Mode Upgrade',
                'url': 'https://example.com/podcast1',
                'feed_name': 'The AI Daily Brief',
                'description': 'OpenAI releases major voice mode improvements...'
            },
            'summary': [
                'ChatGPT voice mode now supports 50+ languages with natural accents',
                'New emotional intelligence features help detect user mood'
            ]
        },
        {
            'episode': {
                'title': 'Claude 3.5 Sonnet: The New Coding Champion',
                'url': 'https://example.com/podcast2',
                'feed_name': 'AI News in 5 Minutes',
                'description': 'Anthropic launches Claude 3.5 Sonnet...'
            },
            'summary': [
                'Claude 3.5 beats GPT-4 on coding benchmarks by 15%',
                'New artifacts feature lets you run code directly in chat'
            ]
        }
    ]
    
    for item in sample_podcasts[:2]:  # Limit to 2
        digest.add_podcast_item(item['episode'], item['summary'])
        print(f"✅ Added podcast: {item['episode']['title']}")
    
    # Add sample news items
    sample_news = [
        {
            'article': {
                'title': 'Google Adds AI to Gmail Mobile App',
                'url': 'https://example.com/news1',
                'feed_name': 'TechCrunch'
            },
            'summary': [
                'Help Me Write feature now available on iOS and Android',
                'Works offline for basic email drafting tasks'
            ]
        },
        {
            'article': {
                'title': 'Perplexity Launches Pro Search for Free Users',
                'url': 'https://example.com/news2',
                'feed_name': 'The Verge'
            },
            'summary': [
                'Five free Pro searches per day for all users',
                'Includes multi-step reasoning and code execution'
            ]
        }
    ]
    
    for item in sample_news[:2]:  # Limit to 2
        digest.add_news_item(item['article'], item['summary'])
        print(f"✅ Added news: {item['article']['title']}")
    
    # Build and preview the digest
    print("\n📋 Building digest...")
    blocks = digest.build_digest()
    
    # Show a preview of the message structure
    print(f"\n📊 Digest structure:")
    print(f"- Total blocks: {len(blocks)}")
    print(f"- AI Tip: {'Yes' if digest.ai_tip else 'No'}")
    print(f"- Podcasts: {len(digest.podcast_items)}")
    print(f"- News: {len(digest.news_items)}")
    
    # Send the digest
    print("\n📤 Sending digest to Slack...")
    success = digest.send_digest()
    
    if success:
        print("✅ Digest sent successfully!")
    else:
        print("❌ Failed to send digest")
    
    return success

if __name__ == "__main__":
    test_new_digest()