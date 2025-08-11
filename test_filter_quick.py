#!/usr/bin/env python3
"""Quick test to verify AI filtering is working correctly"""

import sys
import os

# Add src to path without importing __init__.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_content_filter import AIContentFilter
from rss_parser import RSSParser
from config import Config

def test_filter():
    """Test the AI filter with current feeds"""
    print("Testing AI Filter with Current Feeds")
    print("=" * 50)
    
    parser = RSSParser()
    
    # Test with a few feeds
    test_feeds = [
        {
            "name": "Science Daily AI",
            "url": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
            "type": "news"
        },
        {
            "name": "Daily AI",
            "url": "https://dailyai.com/feed",
            "type": "news"
        }
    ]
    
    all_items = []
    for feed in test_feeds:
        print(f"\nFetching from {feed['name']}...")
        items = parser.parse_feed(feed['url'], feed['name'])
        if items:
            print(f"  Found {len(items)} items")
            for item in items[:3]:  # Show first 3
                item['feed_name'] = feed['name']
                all_items.append(item)
                print(f"  - {item['title'][:80]}...")
    
    print(f"\n\nTotal items before filtering: {len(all_items)}")
    
    # Apply filter
    filtered_items = AIContentFilter.filter_items(all_items)
    
    print(f"Total items after filtering: {len(filtered_items)}")
    print("\nFiltered items:")
    for item in filtered_items:
        print(f"  ✓ {item['title'][:80]}...")
    
    print("\nFilter test complete!")

if __name__ == "__main__":
    test_filter()