import feedparser
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

from .config import Config
from .rate_limiter import rate_limit

logger = logging.getLogger(__name__)


class RSSParser:
    """Parse RSS feeds and extract relevant content"""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-News-Summarizer/1.0 (+https://github.com/yourusername/ai-slack-news)'
        })

    @rate_limit('rss', calls_per_minute=60)
    def fetch_feed(self, feed_url: str, feed_name: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse an RSS feed with retry logic"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                logger.info(f"Fetching RSS feed: {feed_name} ({feed_url})")
                response = self.session.get(feed_url, timeout=Config.REQUEST_TIMEOUT)
                response.raise_for_status()

                feed = feedparser.parse(response.content)
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_name}: {feed.bozo_exception}")

                return feed

            except requests.RequestException as e:
                logger.error(f"Error fetching {feed_name} (attempt {attempt + 1}/{Config.MAX_RETRIES}): {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    return None
            except Exception as e:
                logger.error(f"Unexpected error parsing {feed_name}: {e}")
                return None
        return None

    def extract_feed_items(self, feed: feedparser.FeedParserDict, feed_config: Dict[str, str],
                          hours_back: int = 24) -> List[Dict[str, str]]:
        """Extract relevant items from feed published within the specified time window"""
        items = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        for entry in feed.entries[:Config.MAX_ARTICLES_PER_FEED]:
            try:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))

                # Skip old items
                if pub_date and pub_date < cutoff_time:
                    continue

                # Extract item data
                item = {
                    'title': entry.get('title', 'No Title'),
                    'url': entry.get('link', ''),
                    'description': self._clean_description(entry.get('summary', '')),
                    'published': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                    'feed_name': feed_config['name'],
                    'feed_type': feed_config['type']
                }

                # For podcasts, try to get more detailed description
                if feed_config['type'] == 'podcast':
                    if hasattr(entry, 'content') and entry.content:
                        item['description'] = self._clean_description(entry.content[0].get('value', ''))

                # Only add items with valid URLs
                if item['url']:
                    items.append(item)

            except Exception as e:
                logger.error(f"Error processing feed entry in {feed_config['name']}: {e}")
                continue

        return items

    def _clean_description(self, description: str) -> str:
        """Clean HTML and excessive whitespace from descriptions"""
        if not description:
            return ""

        # Remove HTML tags using BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()

        # Clean whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return ' '.join(lines)

    def fetch_all_feeds(self) -> Dict[str, List[Dict[str, str]]]:
        """Fetch all configured feeds and return categorized items"""
        all_items: Dict[str, List[Dict[str, str]]] = {
            'news': [],
            'podcast': []
        }

        for feed_config in Config.get_all_feeds():
            feed = self.fetch_feed(feed_config['url'], feed_config['name'])
            if feed:
                # Use 72 hours for podcasts to catch weekend releases
                hours_back = 72 if feed_config['type'] == 'podcast' else 24
                items = self.extract_feed_items(feed, feed_config, hours_back=hours_back)
                all_items[feed_config['type']].extend(items)
                logger.info(f"Extracted {len(items)} items from {feed_config['name']} (last {hours_back} hours)")
            else:
                logger.warning(f"Failed to fetch feed: {feed_config['name']}")

        return all_items
