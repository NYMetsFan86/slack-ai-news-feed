#!/usr/bin/env python3
"""Test the full digest with tool spotlight"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.slack_digest_v2 import SlackDigest
from src.llm_client import LLMClient
import logging

logging.basicConfig(level=logging.INFO)

def test_full_digest():
    """Test the complete digest with all features"""
    
    # Initialize clients
    digest = SlackDigest()
    llm_client = LLMClient()
    
    print("🚀 Testing Full AI Daily Digest with Tool Spotlight")
    print("=" * 50)
    
    # 1. Generate AI tip
    print("\n1️⃣ Generating AI Tip...")
    try:
        ai_tip = llm_client.generate_ai_tip()
        if ai_tip:
            digest.set_ai_tip(ai_tip)
            print(f"✅ AI Tip: {ai_tip}")
    except Exception as e:
        print(f"⚠️ Using fallback tip: {e}")
        digest.set_ai_tip("💡 Did you know? Claude can now analyze screenshots! Just paste an image and ask questions about it.")
    
    # 2. Generate tool spotlight
    print("\n2️⃣ Generating Tool Spotlight...")
    try:
        tool = llm_client.generate_tool_spotlight()
        if tool:
            digest.set_tool_spotlight(tool['name'], tool['description'], tool['link'])
            print(f"✅ Tool: {tool['name']}")
            print(f"   {tool['description']}")
    except Exception as e:
        print(f"⚠️ Using fallback tool: {e}")
        digest.set_tool_spotlight(
            "Perplexity Pages",
            "Create beautiful, shareable research pages with AI. Just ask a question and Perplexity generates a comprehensive, well-formatted article with sources. Free to create and share!",
            "https://perplexity.ai/pages"
        )
    
    # 3. Add sample podcasts
    print("\n3️⃣ Adding Podcast Episodes...")
    sample_podcasts = [
        {
            'title': 'AI Daily Brief: OpenAI Announces GPT-4 Turbo Price Drop',
            'url': 'https://example.com/podcast1',
            'feed_name': 'The AI Daily Brief',
            'description': 'Major price reduction makes advanced AI more accessible'
        },
        {
            'title': 'Google Gemini 1.5 Pro Now Available to Everyone',
            'url': 'https://example.com/podcast2',
            'feed_name': 'AI News in 5 Minutes',
            'description': 'Google opens up access to their most powerful model'
        }
    ]
    
    for ep in sample_podcasts:
        summary = [
            f"{ep['feed_name']} discusses latest developments",
            "Key insights on how this impacts AI adoption"
        ]
        digest.add_podcast_item(ep, summary)
        print(f"✅ Added: {ep['title']}")
    
    # 4. Add sample news
    print("\n4️⃣ Adding News Articles...")
    sample_news = [
        {
            'title': 'Microsoft Copilot Gets Major Upgrade with GPT-4 Turbo',
            'url': 'https://example.com/news1',
            'feed_name': 'TechCrunch'
        },
        {
            'title': 'Anthropic Launches Claude Pro Team Plan for Businesses',
            'url': 'https://example.com/news2',
            'feed_name': 'The Verge'
        }
    ]
    
    for article in sample_news:
        summary = [
            "New features enable better collaboration",
            "Pricing remains competitive with other solutions"
        ]
        digest.add_news_item(article, summary)
        print(f"✅ Added: {article['title']}")
    
    # 5. Send digest
    print("\n5️⃣ Sending Complete Digest to Slack...")
    print("=" * 50)
    
    success = digest.send_digest()
    
    if success:
        print("\n✅ SUCCESS! Full digest sent to Slack")
        print(f"📊 Stats: {digest.stats}")
    else:
        print("\n❌ Failed to send digest")
    
    return success

if __name__ == "__main__":
    test_full_digest()