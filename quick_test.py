#!/usr/bin/env python3
"""Quick test to send a sample digest to Slack"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.slack_client import SlackClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_sample_digest():
    """Send a complete sample digest to Slack"""
    
    slack = SlackClient()
    
    if not slack.webhook_url:
        print("❌ No Slack webhook URL found in .env file!")
        print("Please add: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...")
        return
    
    print("📤 Sending sample AI digest to Slack...\n")
    
    # Send header
    slack.send_daily_header()
    
    # Sample news article
    article = {
        'title': 'Google Announces Gemini 2.0 with Multimodal Capabilities',
        'url': 'https://blog.google/technology/ai/gemini-2',
        'feed_name': 'TechCrunch',
        'feed_type': 'news'
    }
    
    news_summary = [
        "Gemini 2.0 introduces native image, audio, and video understanding in a single model",
        "Performance benchmarks show 40% improvement over previous version on complex reasoning tasks",
        "New 'Flash' variant offers 2x faster inference for real-time applications",
        "Enterprise API access begins next month with competitive pricing"
    ]
    
    slack.send_news_summary(article, news_summary)
    
    # Sample podcast
    podcast = {
        'title': 'EP 147: The State of AI Safety Research',
        'url': 'https://example.com/podcast/ep147',
        'feed_name': 'AI News in 5 Minutes or Less',
        'feed_type': 'podcast'
    }
    
    podcast_summary = [
        "Major AI labs announce joint safety initiative with shared evaluation benchmarks",
        "New research shows promise in interpretability methods for large language models",
        "Discussion of the EU AI Act implementation timeline and its global impact",
        "Practical tips for companies implementing AI governance frameworks"
    ]
    
    slack.send_podcast_summary(podcast, podcast_summary)
    
    # AI Tip
    ai_tip = ("💡 Pro Tip: When using AI for data analysis, always verify critical insights with "
              "a second prompt phrased differently. This 'prompt diversity' technique helps catch "
              "potential biases or misunderstandings in the AI's initial response.")
    
    slack.send_ai_tip(ai_tip)
    
    # Footer
    stats = {
        'news_count': 3,
        'podcast_count': 2,
        'errors': 0
    }
    
    slack.send_daily_footer(stats)
    
    print("✅ Sample digest sent successfully!")
    print("\n🎉 Check your Slack channel for the messages!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI News Summarizer - Quick Slack Test")
    print("=" * 60)
    print()
    
    send_sample_digest()