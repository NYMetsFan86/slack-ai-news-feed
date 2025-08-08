#!/usr/bin/env python3
"""Test the improved AI content filter with problematic articles"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import directly from the module file
import importlib.util
spec = importlib.util.spec_from_file_location("ai_content_filter", os.path.join(parent_dir, "src", "ai_content_filter.py"))
ai_content_filter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_content_filter)
AIContentFilter = ai_content_filter.AIContentFilter


def test_filter():
    # Test cases from the problematic digest
    test_cases = [
        {
            "title": "All the news from Nintendo's August Indie World showcase",
            "description": "Nintendo held an Indie World Showcase on August 7th, 2025, showcasing various indie games coming to the Nintendo Switch consoles later this year.",
            "feed_name": "The Verge",
            "expected": False,
            "reason": "Gaming news, not AI"
        },
        {
            "title": "Meta illegally collected Flo users' menstrual data, jury rules",
            "description": "A California jury found Meta illegally collected sensitive menstrual health data from Flo period-tracking app users, raising concerns about privacy and data protection in AI-driven apps.",
            "feed_name": "The Verge",
            "expected": False,
            "reason": "Privacy lawsuit, not AI focus despite mention"
        },
        {
            "title": "Library of Congress explains how parts of US Constitution vanished from its website",
            "description": "A coding error at the Library of Congress led to the temporary disappearance of key sections of the US Constitution from its official website, causing public concern.",
            "feed_name": "TechCrunch",
            "expected": False,
            "reason": "Website bug, not AI"
        },
        {
            "title": "Hubble Network plans massive satellite upgrade to create global Bluetooth layer",
            "description": "Hubble Network, a startup aiming to provide a global Bluetooth network for enterprises, is planning a massive upgrade to their satellite-powered service.",
            "feed_name": "TechCrunch",
            "expected": False,
            "reason": "Satellite/Bluetooth tech, not AI"
        },
        {
            "title": "Best Tested Walking Pads (2025): Urevo, WalkingPad, Sperax",
            "description": "The article focuses on the best tested walking pads for 2025, including the Urevo CyberPad, WalkingPad C2 Mini Foldable Treadmill, and Egofit Walker Pro M1.",
            "feed_name": "Wired",
            "expected": False,
            "reason": "Product review, not AI"
        },
        {
            "title": "Urevo CyberPad (AI Integration)",
            "description": "The Urevo CyberPad features an AI-powered system that monitors and adapts the treadmill's speed to match the user's walking pace, ensuring a smooth and comfortable experience.",
            "feed_name": "Tool Spotlight",
            "expected": False,
            "reason": "AI mentioned only as minor feature in parentheses"
        },
        # Positive test cases - these SHOULD be included
        {
            "title": "OpenAI releases GPT-5 with breakthrough reasoning capabilities",
            "description": "OpenAI has announced the release of GPT-5, featuring significant improvements in logical reasoning and mathematical problem-solving.",
            "feed_name": "TechCrunch",
            "expected": True,
            "reason": "Clear AI news about OpenAI"
        },
        {
            "title": "Google launches new AI features in Search",
            "description": "Google unveiled AI-powered features in Search that can understand complex queries and provide more nuanced answers using their latest Gemini model.",
            "feed_name": "The Verge",
            "expected": True,
            "reason": "AI feature launch by major tech company"
        },
        {
            "title": "Meta's Llama 3 benchmarks show impressive performance",
            "description": "New benchmarks reveal that Meta's Llama 3 model outperforms competitors in various natural language processing tasks.",
            "feed_name": "TechCrunch",
            "expected": True,
            "reason": "AI model performance news"
        },
        {
            "title": "Anthropic raises $2B for AI safety research",
            "description": "AI startup Anthropic has secured $2 billion in funding to advance their work on creating safe and beneficial artificial intelligence systems.",
            "feed_name": "TechCrunch",
            "expected": True,
            "reason": "AI company funding news"
        }
    ]
    
    print("Testing improved AI content filter...")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        result = AIContentFilter.is_ai_related(test_case)
        expected = test_case["expected"]
        
        if result == expected:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"\nTest {i}: {status}")
        print(f"Title: {test_case['title']}")
        print(f"Expected: {'AI-related' if expected else 'NOT AI-related'}")
        print(f"Got: {'AI-related' if result else 'NOT AI-related'}")
        print(f"Reason: {test_case['reason']}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = test_filter()
    sys.exit(0 if success else 1)