import re
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class AIContentFilter:
    """Filter content to ensure it's AI-related"""
    
    # Primary AI keywords - must be in title or first 200 chars of description
    PRIMARY_AI_KEYWORDS: Set[str] = {
        # Core AI terms
        'artificial intelligence', ' ai ', 'machine learning', ' ml ', 'deep learning',
        'neural network', 'llm', 'large language model', 'generative ai', 'genai',
        
        # AI companies and products (as primary subjects)
        'openai', 'chatgpt', 'gpt-', 'claude', 'anthropic', 'gemini ai', 'google ai',
        'midjourney', 'stable diffusion', 'dall-e', 'github copilot', 'perplexity ai',
        'hugging face', 'meta llama', 'mistral ai', 'cohere', 'ai21',
        
        # AI concepts as main topics
        'transformer model', 'prompt engineering', 'fine-tuning', 'ai safety',
        'ai ethics', 'ai regulation', 'agi', 'artificial general intelligence',
        'computer vision', 'natural language processing', 'ai research',
        'foundation model', 'multimodal ai', 'ai alignment', 'responsible ai'
    }
    
    # Secondary AI terms - need multiple matches or context
    SECONDARY_AI_KEYWORDS: Set[str] = {
        'ai tool', 'ai platform', 'ai startup', 'ai company', 'ai service',
        'ai-powered', 'ai-based', 'ai-driven', 'ai-enabled', 'ai application',
        'ai generated', 'ai system', 'predictive ai', 'conversational ai',
        'ai assistant', 'chatbot', 'ai model', 'ai training', 'ai deployment',
        'ai breakthrough', 'ai innovation', 'ai development', 'ai technology'
    }
    
    # Context keywords that strengthen AI relevance
    CONTEXT_KEYWORDS: Set[str] = {
        'launches ai', 'unveils ai', 'introduces ai', 'releases ai', 'develops ai',
        'ai announcement', 'ai update', 'ai feature', 'ai capability', 'ai integration',
        'ai partnership', 'ai acquisition', 'ai investment', 'ai funding', 'ai valuation'
    }
    
    # Strong exclusion patterns - definitely not AI content
    EXCLUDE_PATTERNS: List[Tuple[str, str]] = [
        # Gaming and entertainment
        ('nintendo', 'showcase'), ('gaming', 'console'), ('video game', 'release'),
        ('streaming', 'service'), ('netflix', 'show'), ('disney', 'content'),
        
        # Hardware reviews (unless AI-specific)
        ('laptop', 'review'), ('smartphone', 'review'), ('headphone', 'review'),
        ('speaker', 'review'), ('monitor', 'review'), ('keyboard', 'review'),
        ('walking pad', 'review'), ('treadmill', 'review'), ('fitness', 'equipment'),
        
        # General tech infrastructure
        ('broadband', 'provider'), ('internet', 'outage'), ('wifi', 'router'),
        ('5g', 'network'), ('satellite', 'internet'), ('bluetooth', 'network'),
        
        # Social media and apps (unless AI features)
        ('instagram', 'feature'), ('twitter', 'update'), ('facebook', 'change'),
        ('whatsapp', 'update'), ('tiktok', 'trend'), ('snapchat', 'filter'),
        
        # Legal/regulatory (unless AI-specific)
        ('privacy', 'lawsuit'), ('data', 'breach'), ('antitrust', 'case'),
        ('patent', 'dispute'), ('copyright', 'claim'), ('trademark', 'filing'),
        ('illegally', 'collected'), ('jury', 'rules'), ('menstrual', 'data'),
        
        # Other non-AI tech
        ('cryptocurrency', 'price'), ('bitcoin', 'mining'), ('blockchain', 'network'),
        ('nft', 'collection'), ('metaverse', 'platform'), ('vr', 'headset'),
        ('website', 'error'), ('coding', 'bug'), ('server', 'outage')
    ]
    
    # Topics that need very specific AI context
    REQUIRES_STRONG_CONTEXT: Set[str] = {
        'meta', 'google', 'microsoft', 'amazon', 'apple', 'nvidia',
        'data collection', 'privacy', 'regulation', 'ethics', 'safety',
        'research', 'development', 'innovation', 'technology'
    }
    
    @classmethod
    def is_ai_related(cls, item: Dict[str, str]) -> bool:
        """
        Check if an article/podcast is AI-related using multi-stage filtering
        
        Args:
            item: Dictionary with 'title', 'description', and 'feed_name'
            
        Returns:
            bool: True if content is AI-related
        """
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        full_text = f"{title} {description}"
        
        # Priority check: Some feeds are always AI-related
        ai_specific_feeds = {
            'Science Daily AI', 'Daily AI', 'MarkTechPost',
            'AI News - Artificial Intelligence News',
            'BAIR Blog - Berkeley AI Research', 'AI Business',
            'The AI Daily Brief', 'AI News in 5 Minutes or Less',
            'AI Lawyer Talking Tech', 'The Neuron',
            'Analytics India Magazine'
        }
        
        if item.get('feed_name') in ai_specific_feeds:
            logger.debug(f"Including '{item.get('title')}' - from AI-specific feed")
            return True
        
        # Stage 1: Check exclusion patterns first
        for pattern1, pattern2 in cls.EXCLUDE_PATTERNS:
            if pattern1 in full_text and pattern2 in full_text:
                logger.debug(f"Excluding '{item.get('title')}' - matches exclusion pattern: {pattern1} + {pattern2}")
                return False
        
        # Additional check: If "AI" appears only in parentheses or as a minor feature, skip
        if re.search(r'\(ai[^)]*\)', title) and not any(kw in title for kw in cls.PRIMARY_AI_KEYWORDS):
            logger.debug(f"Excluding '{item.get('title')}' - AI only mentioned as minor feature")
            return False
        
        # Check if it's primarily about legal/privacy issues with only passing AI mention
        legal_privacy_keywords = {
            'lawsuit', 'jury', 'illegally', 'privacy violation',
            'data breach', 'court rules', 'legal battle',
            'privacy concerns'
        }
        if any(kw in title.lower() for kw in legal_privacy_keywords):
            # If title is about legal issues, require stronger AI presence
            if not any(kw in title for kw in cls.PRIMARY_AI_KEYWORDS):
                logger.debug(
                    f"Excluding '{item.get('title')}' - "
                    "primarily legal/privacy news with weak AI connection"
                )
                return False
        
        # Stage 2: Check for primary AI keywords in title or early description
        title_and_early_desc = title + " " + description[:200]
        
        primary_matches = []
        for keyword in cls.PRIMARY_AI_KEYWORDS:
            if keyword in title_and_early_desc:
                primary_matches.append(keyword)
        
        if primary_matches:
            logger.debug(f"Including '{item.get('title')}' - primary AI keywords in title/early desc: {primary_matches}")
            return True
        
        # Stage 3: Check for strong context phrases
        context_matches = []
        for phrase in cls.CONTEXT_KEYWORDS:
            if phrase in full_text:
                context_matches.append(phrase)
        
        if context_matches:
            logger.debug(f"Including '{item.get('title')}' - strong AI context: {context_matches}")
            return True
        
        # Stage 4: Check secondary keywords (need multiple or with context)
        secondary_matches = []
        for keyword in cls.SECONDARY_AI_KEYWORDS:
            if keyword in full_text:
                secondary_matches.append(keyword)
        
        # Need at least 2 secondary keywords
        if len(secondary_matches) >= 2:
            logger.debug(f"Including '{item.get('title')}' - multiple secondary AI keywords: {secondary_matches}")
            return True
        
        # Stage 5: Check if topics that require strong context have AI mentions
        has_context_topic = any(topic in full_text for topic in cls.REQUIRES_STRONG_CONTEXT)
        if has_context_topic and secondary_matches:
            # Has a context-requiring topic AND at least one AI keyword
            logger.debug(f"Including '{item.get('title')}' - context topic with AI keyword: {secondary_matches}")
            return True
        
        # Stage 6: Special case - check for AI company/product as main subject
        ai_companies = {
            'openai', 'anthropic', 'deepmind', 'stability ai',
            'midjourney', 'character.ai', 'inflection ai',
            'adept ai', 'cohere', 'ai21 labs'
        }
        
        # Check if AI company is in title (strong signal)
        for company in ai_companies:
            if company in title:
                logger.debug(f"Including '{item.get('title')}' - AI company in title: {company}")
                return True
        
        # Not AI-related
        logger.debug(f"Excluding '{item.get('title')}' - failed all AI relevance checks")
        return False
    
    @classmethod
    def filter_items(cls, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter a list of items to only include AI-related content
        
        Args:
            items: List of dictionaries containing article/podcast information
            
        Returns:
            List[Dict[str, str]]: Filtered list containing only AI-related items
        """
        filtered = [item for item in items if cls.is_ai_related(item)]
        
        if len(filtered) < len(items):
            logger.info(f"Filtered {len(items) - len(filtered)} non-AI items, kept {len(filtered)} AI-related items")
        
        return filtered