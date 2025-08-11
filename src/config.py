import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for the AI News Summarizer"""

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"  # Updated to available free model

    # Slack Configuration
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

    # Google Cloud Configuration
    GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "processed_items")

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

    # RSS Feeds - Expanded list for more content
    NEWS_FEEDS = [
        # Primary AI news sources
        {
            "name": "MarkTechPost",
            "url": "https://www.marktechpost.com/feed/",
            "type": "news"
        },
        {
            "name": "Analytics India Magazine",
            "url": "https://analyticsindiamag.com/feed/",
            "type": "news"
        },
        {
            "name": "TechRepublic AI",
            "url": "https://www.techrepublic.com/rssfeeds/topic/artificial-intelligence/",
            "type": "news"
        },
        {
            "name": "VentureBeat AI",
            "url": "https://feeds.feedburner.com/venturebeat/SZYF",
            "type": "news"
        },
        {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "type": "news"
        },
        {
            "name": "AI Business",
            "url": "https://aibusiness.com/rss.xml",
            "type": "news"
        },
        {
            "name": "Daily AI",
            "url": "https://dailyai.com/feed",
            "type": "news"
        },
        # Additional sources for more content
        {
            "name": "MIT Technology Review AI",
            "url": "https://www.technologyreview.com/feed/",
            "type": "news"
        },
        {
            "name": "The Information",
            "url": "https://www.theinformation.com/feed",
            "type": "news"
        },
        {
            "name": "Axios AI",
            "url": "https://www.axios.com/technology/artificial-intelligence/feed",
            "type": "news"
        },
        {
            "name": "AI News",
            "url": "https://artificialintelligence-news.com/feed/",
            "type": "news"
        }
    ]

    PODCAST_FEEDS = [
        {
            "name": "The AI Daily Brief",
            "url": "https://anchor.fm/s/f7cac464/podcast/rss",
            "type": "podcast"
        },
        {
            "name": "AI News in 5 Minutes or Less",
            "url": "https://feeds.transistor.fm/ai-news-in-5-minutes-or-less",
            "type": "podcast"
        },
        {
            "name": "AI Lawyer Talking Tech",
            "url": "https://anchor.fm/s/d9c4eb70/podcast/rss",
            "type": "podcast"
        },
        {
            "name": "The Neuron",
            "url": "https://anchor.fm/s/f51d3fd0/podcast/rss",
            "type": "podcast"
        }
    ]

    # Processing Configuration - Balanced for content and speed
    MAX_ARTICLES_PER_FEED = 2  # 2 articles per feed for more content
    MAX_NEWS_ITEMS = 8  # Maximum news items in digest
    MAX_PODCAST_ITEMS = 3  # Maximum podcast items in digest
    MAX_RETRIES = 2  # Reduced retries for faster execution
    RETRY_DELAY = 1  # seconds
    REQUEST_TIMEOUT = 15  # seconds (balanced timeout)

    # Summarization Configuration
    SUMMARY_BULLET_POINTS = 5  # Number of bullet points for summaries
    AI_TIP_MAX_LENGTH = 300  # Maximum characters for AI tip
    
    # Cloud Function Configuration
    FUNCTION_TIMEOUT = 540  # 9 minutes (max for HTTP functions)
    FUNCTION_MEMORY_MB = 512  # Memory allocation in MB
    GRACEFUL_SHUTDOWN_BUFFER = 30  # Seconds before timeout to stop processing

    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Validate required configuration values"""
        validation_results = {
            "openrouter_api_key": bool(cls.OPENROUTER_API_KEY),
            "slack_webhook_url": bool(cls.SLACK_WEBHOOK_URL),
            "gcp_project": bool(cls.GCP_PROJECT_ID),
            "firestore_collection": bool(cls.FIRESTORE_COLLECTION)
        }
        return validation_results

    @classmethod
    def is_valid(cls) -> bool:
        """Check if all required configuration is present"""
        results = cls.validate()
        return all(results.values())

    @classmethod
    def get_all_feeds(cls) -> List[Dict[str, str]]:
        """Get all configured RSS feeds"""
        return cls.NEWS_FEEDS + cls.PODCAST_FEEDS