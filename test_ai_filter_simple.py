#!/usr/bin/env python3
"""Simple test of AI filter to demonstrate it's working"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the filter directly
exec(open('src/ai_content_filter.py').read())

# Test cases
test_items = [
    {
        "title": "Best Nintendo Switch 2 Accessories: Controllers, Cases, and More",
        "description": "Major AI news: The article discusses new AI-enhanced features in popular accessories for the Nintendo Switch 2",
        "feed_name": "Wired",
        "expected": False,
        "reason": "Nintendo gaming accessories"
    },
    {
        "title": "Nigerian profitable food delivery Chowdeck lands $9M from Novastar, Y Combinator",
        "description": "Nigerian food delivery startup Chowdeck, known for its profitable operation in a challenging market",
        "feed_name": "TechCrunch",
        "expected": False,
        "reason": "Food delivery startup"
    },
    {
        "title": "Hyundai wants Ioniq 5 owners to pay to fix a keyless entry security hole",
        "description": "Hyundai is offering an optional security upgrade for its Ioniq 5 models",
        "feed_name": "The Verge",
        "expected": False,
        "reason": "Car security issue"
    },
    {
        "title": "OpenAI releases GPT-5 with breakthrough reasoning capabilities",
        "description": "OpenAI has announced GPT-5, featuring significant improvements in logical reasoning",
        "feed_name": "Daily AI",
        "expected": True,
        "reason": "Clear AI news"
    },
    {
        "title": "Google's new Gemini AI model beats GPT-4 on benchmarks",
        "description": "Google's latest Gemini model shows impressive performance across multiple benchmarks",
        "feed_name": "AI News",
        "expected": True,
        "reason": "AI model news"
    }
]

print("Testing AI Content Filter")
print("=" * 60)

filter_instance = AIContentFilter()
passed = 0
failed = 0

for item in test_items:
    result = filter_instance.is_ai_related(item)
    expected = item["expected"]
    
    if result == expected:
        status = "✓ PASS"
        passed += 1
    else:
        status = "✗ FAIL"
        failed += 1
    
    print(f"\n{status}")
    print(f"Title: {item['title'][:60]}...")
    print(f"Expected: {'AI-related' if expected else 'NOT AI-related'}")
    print(f"Got: {'AI-related' if result else 'NOT AI-related'}")
    print(f"Reason: {item['reason']}")

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")

if failed == 0:
    print("\n✅ All tests passed! The filter is working correctly.")
    print("Nintendo, food delivery, and car security content is being filtered out.")
    print("Only genuine AI content is being allowed through.")
else:
    print("\n⚠️ Some tests failed. Please check the filter logic.")