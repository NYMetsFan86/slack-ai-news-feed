#!/usr/bin/env python3
"""Test script to verify RSS feed URLs are working"""

import feedparser
import requests
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def test_rss_feed(feed_url: str, feed_name: str) -> bool:
    """Test if an RSS feed is accessible and valid"""
    print(f"\n🔍 Testing RSS feed: {feed_name}")
    print(f"   URL: {feed_url}")

    try:
        # First try with requests to check accessibility
        response = requests.get(feed_url, timeout=10, headers={
            'User-Agent': 'AI-News-Summarizer/1.0'
        })
        response.raise_for_status()
        print(f"   ✅ Feed is accessible (Status: {response.status_code})")

        # Parse the feed
        feed = feedparser.parse(response.content)

        if feed.bozo:
            print(f"   ⚠️  Feed parsing warning: {feed.bozo_exception}")
            return False

        # Check feed details
        feed_title = feed.feed.get('title', 'Unknown')
        print(f"   📰 Feed Title: {feed_title}")

        # Check entries
        entry_count = len(feed.entries)
        print(f"   📊 Number of episodes/articles: {entry_count}")

        if entry_count > 0:
            # Show latest entry
            latest = feed.entries[0]
            print(f"\n   📌 Latest Episode:")
            print(f"      Title: {latest.get('title', 'No title')}")

            # Try to get publication date
            pub_date = None
            if hasattr(latest, 'published_parsed') and latest.published_parsed:
                pub_date = datetime.fromtimestamp(latest.published_parsed[0])
            elif hasattr(latest, 'updated_parsed') and latest.updated_parsed:
                pub_date = datetime.fromtimestamp(latest.updated_parsed[0])

            if pub_date:
                print(f"      Published: {pub_date.strftime('%Y-%m-%d %H:%M')}")

            # Check description
            description = latest.get('summary', latest.get('description', ''))
            if description:
                print(f"      Description: {description[:100]}...")

            print(f"      Link: {latest.get('link', 'No link')}")

        return True

    except requests.RequestException as e:
        print(f"   ❌ Error fetching feed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def main():
    """Test all configured RSS feeds"""
    print("=" * 60)
    print("🧪 RSS Feed Testing Tool")
    print("=" * 60)

    all_feeds = Config.NEWS_FEEDS + Config.PODCAST_FEEDS

    success_count = 0
    failed_feeds = []

    for feed in all_feeds:
        if test_rss_feed(feed['url'], feed['name']):
            success_count += 1
        else:
            failed_feeds.append(feed['name'])

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Total feeds tested: {len(all_feeds)}")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {len(failed_feeds)}")

    if failed_feeds:
        print(f"\n   Failed feeds:")
        for feed in failed_feeds:
            print(f"      - {feed}")

    # Special test for the new podcast
    print("\n" + "=" * 60)
    print("🎯 Special Test: AI News in 5 Minutes or Less")
    test_rss_feed(
        "https://feeds.transistor.fm/ai-news-in-5-minutes-or-less",
        "AI News in 5 Minutes or Less (Direct Test)"
    )

    return len(failed_feeds) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
