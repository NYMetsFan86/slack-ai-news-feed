import unittest
import os
from unittest.mock import patch

from src.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration module"""

    def test_config_defaults(self):
        """Test default configuration values"""
        self.assertEqual(Config.OPENROUTER_BASE_URL, "https://openrouter.ai/api/v1")
        self.assertEqual(Config.OPENROUTER_MODEL, "meta-llama/llama-3.1-8b-instruct:free")
        self.assertEqual(Config.MAX_ARTICLES_PER_FEED, 3)
        self.assertEqual(Config.MAX_RETRIES, 3)

    def test_feed_configuration(self):
        """Test RSS feed configuration"""
        news_feeds = Config.NEWS_FEEDS
        podcast_feeds = Config.PODCAST_FEEDS

        # Check news feeds
        self.assertEqual(len(news_feeds), 5)
        self.assertTrue(all('name' in feed and 'url' in feed and 'type' in feed for feed in news_feeds))
        self.assertTrue(all(feed['type'] == 'news' for feed in news_feeds))

        # Check podcast feeds
        self.assertEqual(len(podcast_feeds), 3)
        self.assertTrue(all('name' in feed and 'url' in feed and 'type' in feed for feed in podcast_feeds))
        self.assertTrue(all(feed['type'] == 'podcast' for feed in podcast_feeds))

    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key',
        'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
        'GOOGLE_CLOUD_PROJECT': 'test-project',
        'FIRESTORE_COLLECTION': 'test_processed_items'
    })
    def test_config_validation_success(self):
        """Test configuration validation with all required values"""
        validation_results = Config.validate()
        self.assertTrue(all(validation_results.values()))
        self.assertTrue(Config.is_valid())

    @patch.dict(os.environ, {}, clear=True)
    def test_config_validation_failure(self):
        """Test configuration validation with missing values"""
        validation_results = Config.validate()
        self.assertFalse(validation_results['openrouter_api_key'])
        self.assertFalse(validation_results['slack_webhook_url'])
        self.assertFalse(Config.is_valid())

    def test_get_all_feeds(self):
        """Test getting all configured feeds"""
        all_feeds = Config.get_all_feeds()
        self.assertEqual(len(all_feeds), 8)  # 5 news + 3 podcasts
        self.assertTrue(all(isinstance(feed, dict) for feed in all_feeds))


if __name__ == '__main__':
    unittest.main()
