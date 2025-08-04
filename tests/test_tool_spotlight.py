#!/usr/bin/env python3
"""Test the tool spotlight feature"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm_client import LLMClient
import logging

logging.basicConfig(level=logging.INFO)

def test_tool_extraction():
    """Test extracting tools from articles"""
    llm_client = LLMClient()
    
    # Test article about a new AI tool
    test_article = {
        'title': 'Google Launches NotebookLM Plus with Advanced Features',
        'content': '''Google has announced NotebookLM Plus, an upgraded version of its AI-powered research assistant. 
        The new version includes real-time collaboration features, support for audio files, and the ability to 
        generate study guides from uploaded documents. Users can now share notebooks with team members and work 
        together on research projects. The tool uses Gemini Pro to analyze documents and answer questions. 
        NotebookLM Plus is available now at notebooklm.google.com with a free tier that includes 50 sources per month.'''
    }
    
    print("🔍 Testing tool extraction from article...")
    tool_info = llm_client.extract_tool_from_article(test_article['title'], test_article['content'])
    
    if tool_info:
        print(f"✅ Found tool: {tool_info['name']}")
        print(f"   Description: {tool_info['description']}")
        print(f"   Link: {tool_info['link']}")
    else:
        print("❌ No tool found in article")
    
    # Test generating a tool spotlight
    print("\n🔧 Testing tool spotlight generation...")
    generated_tool = llm_client.generate_tool_spotlight()
    
    if generated_tool:
        print(f"✅ Generated tool: {generated_tool['name']}")
        print(f"   Description: {generated_tool['description']}")
        print(f"   Link: {generated_tool['link']}")
    else:
        print("❌ Failed to generate tool spotlight")

if __name__ == "__main__":
    test_tool_extraction()