#!/usr/bin/env python3
"""Preview what would be posted to Slack without actually posting"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.llm_client import LLMClient
from src.rss_parser import RSSParser
from src.web_scraper import WebScraper
from dotenv import load_dotenv
import json

load_dotenv()

def preview_ai_tip():
    """Preview AI tip generation"""
    print("🤖 Generating AI Tip...")
    
    if not Config.OPENROUTER_API_KEY:
        print("❌ Missing OpenRouter API key!")
        return
        
    llm = LLMClient()
    tip = llm.generate_ai_tip()
    
    print("\n💡 AI TIP OF THE DAY:")
    print("-" * 50)
    print(tip if tip else "Failed to generate tip")
    print("-" * 50)
    print(f"Character count: {len(tip) if tip else 0}")
    
def preview_latest_feeds():
    """Preview latest items from RSS feeds"""
    print("\n📡 Checking RSS Feeds...")
    
    rss = RSSParser()
    
    # Check news feeds
    print("\n📰 LATEST NEWS:")
    print("-" * 50)
    for feed_config in Config.NEWS_FEEDS[:2]:  # First 2 feeds only
        print(f"\nFrom {feed_config['name']}:")
        feed = rss.fetch_feed(feed_config['url'], feed_config['name'])
        if feed and feed.entries:
            latest = feed.entries[0]
            print(f"  Title: {latest.get('title', 'No title')}")
            print(f"  Link: {latest.get('link', 'No link')}")
            print(f"  Published: {latest.get('published', 'Unknown date')}")
    
    # Check podcast feeds
    print("\n\n🎙️ LATEST PODCASTS:")
    print("-" * 50)
    for feed_config in Config.PODCAST_FEEDS[:2]:  # First 2 feeds only
        print(f"\nFrom {feed_config['name']}:")
        feed = rss.fetch_feed(feed_config['url'], feed_config['name'])
        if feed and feed.entries:
            latest = feed.entries[0]
            print(f"  Title: {latest.get('title', 'No title')}")
            print(f"  Duration: {latest.get('itunes_duration', 'Unknown')}")
            print(f"  Published: {latest.get('published', 'Unknown date')}")

def preview_summary_generation():
    """Preview how summaries would be generated"""
    print("\n📝 Testing Summary Generation...")
    
    if not Config.OPENROUTER_API_KEY:
        print("❌ Missing OpenRouter API key!")
        return
    
    llm = LLMClient()
    
    # Test article summary
    test_article = """
    OpenAI announced significant improvements to their GPT models today, 
    including better reasoning capabilities and reduced hallucinations. 
    The new models show a 40% improvement in accuracy on complex tasks
    and use 30% less computational resources. This breakthrough comes
    after months of research into more efficient training methods.
    """
    
    print("\nTest Article Summary:")
    summary = llm.summarize_article("OpenAI Announces Model Improvements", test_article)
    if summary:
        for bullet in summary:
            print(f"  • {bullet}")
    else:
        print("  Failed to generate summary")

def main():
    print("=" * 60)
    print("🔍 AI News Summarizer - Preview Mode")
    print("=" * 60)
    print("This will show what would be posted WITHOUT sending to Slack")
    
    print("\nSelect preview option:")
    print("1. Preview AI Tip generation")
    print("2. Preview latest RSS feed items")
    print("3. Preview summary generation")
    print("4. Preview all")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            preview_ai_tip()
        elif choice == "2":
            preview_latest_feeds()
        elif choice == "3":
            preview_summary_generation()
        elif choice == "4":
            preview_ai_tip()
            preview_latest_feeds()
            preview_summary_generation()
        else:
            print("Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Preview cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()