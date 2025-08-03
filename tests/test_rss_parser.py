import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import feedparser

from src.rss_parser import RSSParser


class TestRSSParser(unittest.TestCase):
    """Test RSS parser module"""

    def setUp(self):
        self.parser = RSSParser()

    @patch('src.rss_parser.requests.Session')
    def test_fetch_feed_success(self, mock_session):
        """Test successful feed fetching"""
        # Mock response
        mock_response = Mock()
        mock_response.content = b'<rss><channel><title>Test Feed</title></channel></rss>'
        mock_response.raise_for_status = Mock()

        mock_session.return_value.get.return_value = mock_response

        # Test fetch
        result = self.parser.fetch_feed('http://test.com/feed', 'Test Feed')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, feedparser.FeedParserDict)

    @patch('src.rss_parser.requests.Session')
    def test_fetch_feed_retry_on_error(self, mock_session):
        """Test retry logic on network error"""
        # Mock failed requests
        mock_session.return_value.get.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            Mock(content=b'<rss></rss>', raise_for_status=Mock())
        ]

        with patch('time.sleep'):  # Speed up test by mocking sleep
            result = self.parser.fetch_feed('http://test.com/feed', 'Test Feed')

        self.assertIsNotNone(result)
        self.assertEqual(mock_session.return_value.get.call_count, 3)

    def test_extract_feed_items(self):
        """Test extracting items from parsed feed"""
        # Create mock feed
        mock_feed = feedparser.FeedParserDict()
        mock_feed.entries = []

        # Add recent entry
        recent_entry = feedparser.FeedParserDict()
        recent_entry.title = "Recent Article"
        recent_entry.link = "http://test.com/recent"
        recent_entry.summary = "This is a recent article"
        recent_entry.published_parsed = (datetime.now() - timedelta(hours=1)).timetuple()
        mock_feed.entries.append(recent_entry)

        # Add old entry
        old_entry = feedparser.FeedParserDict()
        old_entry.title = "Old Article"
        old_entry.link = "http://test.com/old"
        old_entry.summary = "This is an old article"
        old_entry.published_parsed = (datetime.now() - timedelta(days=2)).timetuple()
        mock_feed.entries.append(old_entry)

        feed_config = {'name': 'Test Feed', 'type': 'news'}
        items = self.parser.extract_feed_items(mock_feed, feed_config, hours_back=24)

        # Should only get recent article
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], "Recent Article")
        self.assertEqual(items[0]['feed_name'], "Test Feed")

    def test_clean_description(self):
        """Test HTML cleaning from descriptions"""
        html_description = """
        <p>This is a <strong>test</strong> description.</p>
        <div>With multiple lines</div>
        <script>alert('bad')</script>
        """

        cleaned = self.parser._clean_description(html_description)

        self.assertNotIn('<p>', cleaned)
        self.assertNotIn('<strong>', cleaned)
        self.assertNotIn('<script>', cleaned)
        self.assertIn('This is a test description.', cleaned)
        self.assertIn('With multiple lines', cleaned)

    @patch.object(RSSParser, 'fetch_feed')
    @patch.object(RSSParser, 'extract_feed_items')
    def test_fetch_all_feeds(self, mock_extract, mock_fetch):
        """Test fetching all configured feeds"""
        # Mock feed responses
        mock_feed = feedparser.FeedParserDict()
        mock_fetch.return_value = mock_feed

        # Mock extracted items
        mock_extract.side_effect = [
            [{'title': 'News 1', 'url': 'http://news1.com'}],  # First news feed
            [{'title': 'News 2', 'url': 'http://news2.com'}],  # Second news feed
            [],  # Empty feed
            [],  # Empty feed
            [],  # Empty feed
            [{'title': 'Podcast 1', 'url': 'http://podcast1.com'}],  # First podcast
            [],  # Empty feed
            []   # Empty feed
        ]

        result = self.parser.fetch_all_feeds()

        self.assertEqual(len(result['news']), 2)
        self.assertEqual(len(result['podcast']), 1)
        self.assertEqual(result['news'][0]['title'], 'News 1')
        self.assertEqual(result['podcast'][0]['title'], 'Podcast 1')


if __name__ == '__main__':
    unittest.main()
