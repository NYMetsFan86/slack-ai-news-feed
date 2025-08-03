import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for the AI News Summarizer"""

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

    # Slack Configuration
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

    # Google Cloud Configuration
    GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "processed_items")

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

    # RSS Feeds
    NEWS_FEEDS = [
        {
            "name": "The Verge",
            "url": "https://www.theverge.com/rss/index.xml",
            "type": "news"
        },
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "type": "news"
        },
        {
            "name": "NY Times Technology",
            "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "type": "news"
        },
        {
            "name": "Wired",
            "url": "https://www.wired.com/feed/",
            "type": "news"
        },
        {
            "name": "Science Daily AI",
            "url": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
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
        }
    ]

    # Processing Configuration
    MAX_ARTICLES_PER_FEED = 3  # Limit articles per feed to avoid overwhelming
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    REQUEST_TIMEOUT = 30  # seconds

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
