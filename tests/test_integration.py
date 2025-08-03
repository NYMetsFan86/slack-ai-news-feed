import unittest
from unittest.mock import Mock, patch
import os

from src.main import main_function


class TestIntegration(unittest.TestCase):
    """Integration tests for the Cloud Function handler"""

    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key',
        'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
        'GOOGLE_CLOUD_PROJECT': 'test-project',
        'FIRESTORE_COLLECTION': 'test_processed_items',
        'ENVIRONMENT': 'development'
    })
    @patch('src.main.RSSParser')
    @patch('src.main.WebScraper')
    @patch('src.main.LLMClient')
    @patch('src.main.FirestoreClient')
    @patch('src.main.SlackClient')
    def test_main_function_success(self, mock_slack, mock_db, mock_llm, mock_scraper, mock_rss):
        """Test successful Cloud Function execution"""

        # Mock RSS parser
        mock_rss_instance = mock_rss.return_value
        mock_rss_instance.fetch_all_feeds.return_value = {
            'news': [
                {
                    'title': 'Test Article',
                    'url': 'http://test.com/article',
                    'description': 'Test description',
                    'feed_name': 'Test Feed',
                    'feed_type': 'news'
                }
            ],
            'podcast': []
        }

        # Mock web scraper
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.fetch_article_content.return_value = "Article content about AI"

        # Mock LLM client
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.summarize_article.return_value = [
            "AI is transforming businesses",
            "New developments in machine learning",
            "Important for digital transformation"
        ]
        mock_llm_instance.generate_ai_tip.return_value = "Use AI to automate repetitive tasks"

        # Mock Firestore client
        mock_db_instance = mock_db.return_value
        mock_db_instance.is_url_processed.return_value = False
        mock_db_instance.mark_url_processed.return_value = True
        mock_db_instance.initialize_collection = Mock()

        # Mock Slack client
        mock_slack_instance = mock_slack.return_value
        mock_slack_instance.send_daily_header.return_value = True
        mock_slack_instance.send_news_summary.return_value = True
        mock_slack_instance.send_ai_tip.return_value = True
        mock_slack_instance.send_daily_footer.return_value = True

        # Execute Cloud Function
        from cloudevents.http import CloudEvent

        attributes = {
            "type": "google.cloud.pubsub.topic.v1.messagePublished",
            "source": "test",
        }
        data = {"message": {"data": "test"}}

        cloud_event = CloudEvent(attributes, data)

        # Cloud Functions don't return values for Pub/Sub triggers
        main_function(cloud_event)

        # Verify calls
        mock_rss_instance.fetch_all_feeds.assert_called_once()
        mock_scraper_instance.fetch_article_content.assert_called_once()
        mock_llm_instance.summarize_article.assert_called_once()
        mock_llm_instance.generate_ai_tip.assert_called_once()
        mock_db_instance.mark_url_processed.assert_called_once()
        mock_slack_instance.send_news_summary.assert_called_once()

    @patch.dict(os.environ, {})
    def test_main_function_missing_config(self):
        """Test Cloud Function execution with missing configuration"""
        from cloudevents.http import CloudEvent

        attributes = {
            "type": "google.cloud.pubsub.topic.v1.messagePublished",
            "source": "test",
        }
        data = {"message": {"data": "test"}}

        cloud_event = CloudEvent(attributes, data)

        # Should raise an exception with missing config
        with self.assertRaises(ValueError):
            main_function(cloud_event)


if __name__ == '__main__':
    unittest.main()
