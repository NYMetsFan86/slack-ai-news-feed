#!/usr/bin/env python3
"""Test script to manually post to Slack channel"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.slack_client import SlackClient
from src.rss_parser import RSSParser
from src.llm_client import LLMClient
from src.web_scraper import WebScraper
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_basic_slack_post():
    """Test basic Slack connectivity"""
    print("🧪 Testing basic Slack post...")
    
    slack = SlackClient()
    
    # Test connection with a simple message
    success = slack.test_connection()
    
    if success:
        print("✅ Successfully posted test message to Slack!")
    else:
        print("❌ Failed to post to Slack. Check your webhook URL.")
    
    return success


def test_full_workflow():
    """Test the full workflow with real data"""
    print("\n🧪 Testing full workflow...")
    
    # Initialize clients
    slack = SlackClient()
    rss = RSSParser()
    llm = LLMClient()
    scraper = WebScraper()
    
    # Send header
    print("📤 Sending daily header...")
    slack.send_daily_header()
    
    # Test with a sample article
    print("\n📰 Testing news summary...")
    sample_article = {
        'title': 'OpenAI Announces New AI Model with Advanced Reasoning',
        'url': 'https://example.com/article',
        'feed_name': 'TechCrunch',
        'feed_type': 'news'
    }
    
    sample_summary = [
        "New model demonstrates 10x improvement in complex problem solving",
        "Features advanced reasoning capabilities for multi-step tasks",
        "Available through API starting next month"
    ]
    
    slack.send_news_summary(sample_article, sample_summary)
    
    # Test with a podcast
    print("\n🎙️ Testing podcast summary...")
    sample_podcast = {
        'title': 'AI Safety and the Future of AGI',
        'url': 'https://example.com/podcast',
        'feed_name': 'AI News in 5 Minutes or Less',
        'feed_type': 'podcast'
    }
    
    podcast_summary = [
        "Discussion on current AI safety measures in major labs",
        "Timeline predictions for AGI development",
        "Practical implications for businesses and society"
    ]
    
    slack.send_podcast_summary(sample_podcast, podcast_summary)
    
    # Test AI tip
    print("\n💡 Testing AI tip...")
    ai_tip = "When prompting AI for creative tasks, provide examples of the style and tone you want. This 'few-shot learning' approach significantly improves output quality."
    
    slack.send_ai_tip(ai_tip)
    
    # Send footer
    print("\n📊 Sending footer...")
    stats = {
        'news_count': 1,
        'podcast_count': 1,
        'errors': 0
    }
    slack.send_daily_footer(stats)
    
    print("\n✅ Full workflow test completed!")


def test_with_live_data():
    """Test with actual RSS feed data"""
    print("\n🧪 Testing with live RSS data...")
    
    # Check configuration
    if not Config.is_valid():
        print("❌ Missing required configuration!")
        print("   Please ensure .env file has:")
        print("   - OPENROUTER_API_KEY")
        print("   - SLACK_WEBHOOK_URL")
        return
    
    # Initialize clients
    slack = SlackClient()
    rss = RSSParser()
    
    # Fetch one item from the new podcast feed
    print("\n📡 Fetching from 'AI News in 5 Minutes or Less'...")
    
    podcast_feed = {
        "name": "AI News in 5 Minutes or Less",
        "url": "https://feeds.transistor.fm/ai-news-in-5-minutes-or-less",
        "type": "podcast"
    }
    
    feed = rss.fetch_feed(podcast_feed['url'], podcast_feed['name'])
    
    if feed and feed.entries:
        # Get the latest episode
        latest = feed.entries[0]
        
        item = {
            'title': latest.get('title', 'No Title'),
            'url': latest.get('link', ''),
            'description': rss._clean_description(latest.get('summary', '')),
            'feed_name': podcast_feed['name'],
            'feed_type': 'podcast'
        }
        
        print(f"\n📌 Found episode: {item['title']}")
        print(f"   Description preview: {item['description'][:100]}...")
        
        # Create a mock summary (since we're not calling the LLM)
        mock_summary = [
            "Latest AI developments and breakthroughs",
            "Key insights for business professionals",
            "Practical applications discussed"
        ]
        
        # Send to Slack
        print("\n📤 Posting to Slack...")
        success = slack.send_podcast_summary(item, mock_summary)
        
        if success:
            print("✅ Successfully posted real podcast data to Slack!")
        else:
            print("❌ Failed to post to Slack")
    else:
        print("❌ Could not fetch podcast feed")


def main():
    """Main test menu"""
    print("=" * 60)
    print("🧪 AI News Summarizer - Slack Testing Tool")
    print("=" * 60)
    
    # Check for webhook URL
    if not Config.SLACK_WEBHOOK_URL:
        print("❌ ERROR: No Slack webhook URL found!")
        print("\n📝 Please set up your .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Slack webhook URL")
        print("   3. Add your OpenRouter API key")
        return
    
    print("\nSelect a test option:")
    print("1. Test basic Slack connection")
    print("2. Test full workflow with sample data")
    print("3. Test with live RSS data (no LLM)")
    print("4. Run all tests")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_basic_slack_post()
        elif choice == "2":
            test_full_workflow()
        elif choice == "3":
            test_with_live_data()
        elif choice == "4":
            test_basic_slack_post()
            test_full_workflow()
            test_with_live_data()
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()