"""Comprehensive integration tests with mocked external services"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.main import main_function


class TestFullIntegration(unittest.TestCase):
    """Full integration tests for the AI News Summarizer"""
    
    def setUp(self) -> None:
        """Set up test environment"""
        self.env_patcher = patch.dict(os.environ, {
            'OPENROUTER_API_KEY': 'test-api-key',
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            'GOOGLE_CLOUD_PROJECT': 'test-project',
            'FIRESTORE_COLLECTION': 'test_collection',
            'ENVIRONMENT': 'test'
        })
        self.env_patcher.start()
    
    def tearDown(self) -> None:
        """Clean up test environment"""
        self.env_patcher.stop()
    
    @patch('src.main.RSSParser')
    @patch('src.main.WebScraper')
    @patch('src.main.LLMClient')
    @patch('src.main.FirestoreClient')
    @patch('src.main.SlackClient')
    @patch('src.main.error_reporting.Client')
    @patch('src.main.signal.alarm')
    def test_successful_full_workflow(
        self,
        mock_alarm: Mock,
        mock_error_client: Mock,
        mock_slack: Mock,
        mock_db: Mock,
        mock_llm: Mock,
        mock_scraper: Mock,
        mock_rss: Mock
    ) -> None:
        """Test complete successful workflow with multiple articles and podcasts"""
        
        # Mock RSS feeds with multiple items
        mock_rss_instance = mock_rss.return_value
        mock_rss_instance.fetch_all_feeds.return_value = {
            'news': [
                {
                    'title': 'AI Breakthrough in Healthcare',
                    'url': 'https://example.com/ai-health',
                    'description': 'New AI model improves diagnosis',
                    'feed_name': 'Tech News',
                    'feed_type': 'news'
                },
                {
                    'title': 'Machine Learning Market Growth',
                    'url': 'https://example.com/ml-market',
                    'description': 'ML market reaches new heights',
                    'feed_name': 'Business Tech',
                    'feed_type': 'news'
                }
            ],
            'podcast': [
                {
                    'title': 'Understanding GPT Models',
                    'url': 'https://example.com/gpt-podcast',
                    'description': 'Deep dive into GPT architecture',
                    'feed_name': 'AI Podcast',
                    'feed_type': 'podcast'
                }
            ]
        }
        
        # Mock web scraper
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.fetch_article_content.side_effect = [
            "Detailed content about AI in healthcare...",
            "Analysis of ML market trends..."
        ]
        
        # Mock LLM responses
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.summarize_article.side_effect = [
            ["AI improves diagnosis accuracy by 95%",
             "Reduces healthcare costs significantly",
             "Early detection of diseases enhanced"],
            ["ML market grows 40% year-over-year",
             "Enterprise adoption accelerating",
             "New applications in finance and retail"]
        ]
        mock_llm_instance.summarize_podcast.return_value = [
            "GPT models explained in detail",
            "Architecture and training process",
            "Real-world applications discussed"
        ]
        mock_llm_instance.generate_ai_tip.return_value = (
            "Start with simple AI tools before complex implementations"
        )
        
        # Mock Firestore
        mock_db_instance = mock_db.return_value
        mock_db_instance.is_url_processed.return_value = False
        mock_db_instance.mark_url_processed.return_value = True
        mock_db_instance.initialize_collection = Mock()
        
        # Mock Slack
        mock_slack_instance = mock_slack.return_value
        mock_slack_instance.send_daily_header.return_value = True
        mock_slack_instance.send_news_summary.return_value = True
        mock_slack_instance.send_podcast_summary.return_value = True
        mock_slack_instance.send_ai_tip.return_value = True
        mock_slack_instance.send_daily_footer.return_value = True
        
        # Create cloud event
        from cloudevents.http import CloudEvent
        attributes = {
            "type": "google.cloud.pubsub.topic.v1.messagePublished",
            "source": "test-source",
        }
        data = {"message": {"data": "test-data"}}
        cloud_event = CloudEvent(attributes, data)
        
        # Execute function
        main_function(cloud_event)
        
        # Verify all components were called correctly
        mock_rss_instance.fetch_all_feeds.assert_called_once()
        self.assertEqual(mock_scraper_instance.fetch_article_content.call_count, 2)
        self.assertEqual(mock_llm_instance.summarize_article.call_count, 2)
        self.assertEqual(mock_llm_instance.summarize_podcast.call_count, 1)
        mock_llm_instance.generate_ai_tip.assert_called_once()
        
        # Verify Slack messages sent
        mock_slack_instance.send_daily_header.assert_called_once()
        self.assertEqual(mock_slack_instance.send_news_summary.call_count, 2)
        self.assertEqual(mock_slack_instance.send_podcast_summary.call_count, 1)
        mock_slack_instance.send_ai_tip.assert_called_once()
        
        # Verify footer contains correct stats
        footer_call = mock_slack_instance.send_daily_footer.call_args
        stats = footer_call[0][0]
        self.assertEqual(stats['news_count'], 2)
        self.assertEqual(stats['podcast_count'], 1)
        self.assertEqual(stats['errors'], 0)
    
    @patch('src.main.RSSParser')
    @patch('src.main.WebScraper')
    @patch('src.main.LLMClient')
    @patch('src.main.FirestoreClient')
    @patch('src.main.SlackClient')
    @patch('src.main.error_reporting.Client')
    @patch('src.main.signal.alarm')
    def test_partial_failures_continue_processing(
        self,
        mock_alarm: Mock,
        mock_error_client: Mock,
        mock_slack: Mock,
        mock_db: Mock,
        mock_llm: Mock,
        mock_scraper: Mock,
        mock_rss: Mock
    ) -> None:
        """Test that partial failures don't stop processing of other items"""
        
        # Mock RSS with 3 articles
        mock_rss_instance = mock_rss.return_value
        mock_rss_instance.fetch_all_feeds.return_value = {
            'news': [
                {'title': 'Article 1', 'url': 'https://example.com/1',
                 'feed_name': 'Feed 1', 'feed_type': 'news'},
                {'title': 'Article 2', 'url': 'https://example.com/2',
                 'feed_name': 'Feed 2', 'feed_type': 'news'},
                {'title': 'Article 3', 'url': 'https://example.com/3',
                 'feed_name': 'Feed 3', 'feed_type': 'news'}
            ],
            'podcast': []
        }
        
        # Mock scraper - second article fails
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.fetch_article_content.side_effect = [
            "Content 1",
            None,  # Fail to fetch
            "Content 3"
        ]
        
        # Mock LLM
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.summarize_article.return_value = ["Summary point"]
        mock_llm_instance.generate_ai_tip.return_value = "Test tip"
        
        # Mock other services
        mock_db_instance = mock_db.return_value
        mock_db_instance.is_url_processed.return_value = False
        mock_db_instance.mark_url_processed.return_value = True
        
        mock_slack_instance = mock_slack.return_value
        mock_slack_instance.send_news_summary.return_value = True
        
        # Execute
        from cloudevents.http import CloudEvent
        cloud_event = CloudEvent(
            {"type": "test", "source": "test"},
            {"message": {"data": "test"}}
        )
        main_function(cloud_event)
        
        # Verify processing continued despite failure
        self.assertEqual(mock_scraper_instance.fetch_article_content.call_count, 3)
        self.assertEqual(mock_llm_instance.summarize_article.call_count, 2)  # Only successful fetches
        self.assertEqual(mock_slack_instance.send_news_summary.call_count, 2)
        
        # Check stats reflect the error
        footer_call = mock_slack_instance.send_daily_footer.call_args
        stats = footer_call[0][0]
        self.assertEqual(stats['news_count'], 2)
        self.assertEqual(stats['errors'], 0)  # No errors because scraper returned None
    
    @patch('src.main.RSSParser')
    @patch('src.main.WebScraper')
    @patch('src.main.LLMClient')
    @patch('src.main.FirestoreClient')
    @patch('src.main.SlackClient')
    @patch('src.main.error_reporting.Client')
    @patch('src.main.signal.alarm')
    @patch('src.main.time.time')
    def test_timeout_handling(
        self,
        mock_time: Mock,
        mock_alarm: Mock,
        mock_error_client: Mock,
        mock_slack: Mock,
        mock_db: Mock,
        mock_llm: Mock,
        mock_scraper: Mock,
        mock_rss: Mock
    ) -> None:
        """Test graceful timeout handling"""
        
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 500, 510]  # Start, during, timeout
        
        # Mock basic setup
        mock_rss_instance = mock_rss.return_value
        mock_rss_instance.fetch_all_feeds.return_value = {
            'news': [{'title': 'Test', 'url': 'https://example.com/test',
                     'feed_name': 'Test', 'feed_type': 'news'}],
            'podcast': []
        }
        
        # Simulate timeout during processing
        def timeout_side_effect(*args: Any, **kwargs: Any) -> None:
            raise TimeoutError("Test timeout")
        
        mock_alarm.side_effect = [None, timeout_side_effect]
        
        # Execute - should handle timeout gracefully
        from cloudevents.http import CloudEvent
        cloud_event = CloudEvent(
            {"type": "test", "source": "test"},
            {"message": {"data": "test"}}
        )
        
        # Function should complete without raising
        main_function(cloud_event)
        
        # Verify alarm was set and cancelled
        self.assertEqual(mock_alarm.call_count, 2)


if __name__ == '__main__':
    unittest.main()