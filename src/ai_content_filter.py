import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class AIContentFilter:
    """Filter content to ensure it's AI-related"""
    
    # Keywords that strongly indicate AI content
    AI_KEYWORDS: Set[str] = {
        # Core AI terms
        'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
        'neural network', 'llm', 'large language model', 'generative ai', 'genai',
        
        # AI companies and products
        'openai', 'chatgpt', 'gpt', 'claude', 'anthropic', 'gemini', 'bard',
        'midjourney', 'stable diffusion', 'dall-e', 'copilot', 'perplexity',
        'hugging face', 'llama', 'mistral', 'cohere', 'ai21', 'meta ai',
        
        # AI concepts
        'transformer', 'prompt engineering', 'fine-tuning', 'embeddings',
        'vector database', 'rag', 'retrieval augmented', 'ai safety',
        'ai ethics', 'ai regulation', 'agi', 'artificial general intelligence',
        'computer vision', 'nlp', 'natural language processing', 'robotics',
        'autonomous', 'ai chip', 'nvidia', 'ai model', 'ai research',
        
        # AI applications
        'ai assistant', 'chatbot', 'ai tool', 'ai platform', 'ai startup',
        'ai powered', 'ai-powered', 'ai based', 'ai-based', 'ai driven',
        'ai generated', 'ai system', 'predictive ai', 'conversational ai'
    }
    
    # Keywords that might appear but don't guarantee AI content
    WEAK_KEYWORDS: Set[str] = {
        'algorithm', 'data science', 'automation', 'bot', 'smart', 'intelligent',
        'cognitive', 'prediction', 'model', 'training', 'inference'
    }
    
    # Keywords that strongly indicate NOT AI content
    EXCLUDE_KEYWORDS: Set[str] = {
        'roku', 'streaming service', 'subscription service', 'cable tv',
        'broadband', 'isp', 'internet service provider', 'gaming console',
        'smartphone review', 'laptop review', 'headphone', 'speaker review',
        'social media platform', 'messaging app', 'vpn service'
    }
    
    @classmethod
    def is_ai_related(cls, item: Dict[str, str]) -> bool:
        """
        Check if an article/podcast is AI-related
        
        Args:
            item: Dictionary with 'title', 'description', and 'feed_name'
            
        Returns:
            bool: True if content is AI-related
        """
        # Combine title and description for checking
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        
        # Some feeds are always AI-related
        ai_specific_feeds = {
            'Science Daily AI', 'Daily AI', 'MarkTechPost', 
            'AI News - Artificial Intelligence News', 'BAIR Blog - Berkeley AI Research',
            'AI Business', 'The AI Daily Brief', 'AI News in 5 Minutes or Less',
            'AI Lawyer Talking Tech', 'The Neuron'
        }
        
        if item.get('feed_name') in ai_specific_feeds:
            return True
        
        # Check for exclude keywords first
        for keyword in cls.EXCLUDE_KEYWORDS:
            if keyword in text:
                logger.debug(f"Excluding '{item.get('title')}' - contains exclude keyword: {keyword}")
                return False
        
        # Check for strong AI keywords
        ai_keyword_count = 0
        found_keywords = []
        
        for keyword in cls.AI_KEYWORDS:
            if keyword in text:
                ai_keyword_count += 1
                found_keywords.append(keyword)
        
        # If we found strong AI keywords, it's AI content
        if ai_keyword_count > 0:
            logger.debug(f"Including '{item.get('title')}' - found AI keywords: {found_keywords}")
            return True
        
        # Check for weak keywords (need multiple to qualify)
        weak_keyword_count = sum(1 for keyword in cls.WEAK_KEYWORDS if keyword in text)
        
        if weak_keyword_count >= 2:
            logger.debug(f"Including '{item.get('title')}' - multiple weak AI keywords")
            return True
        
        # Not AI-related
        logger.debug(f"Excluding '{item.get('title')}' - no AI keywords found")
        return False
    
    @classmethod
    def filter_items(cls, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter a list of items to only include AI-related content"""
        filtered = [item for item in items if cls.is_ai_related(item)]
        
        if len(filtered) < len(items):
            logger.info(f"Filtered {len(items) - len(filtered)} non-AI items, kept {len(filtered)} AI-related items")
        
        return filtered