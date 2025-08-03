import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import functions_framework
from google.cloud import error_reporting, firestore

from .config import Config
from .rss_parser import RSSParser
from .web_scraper import WebScraper
from .llm_client import LLMClient
from .firestore_client import FirestoreClient
from .slack_digest import SlackDigest
from .logging_config import configure_logging
from .monitoring import ResourceGuard, monitor_memory

# Configure secure logging
configure_logging(level="INFO")
logger = logging.getLogger(__name__)


class EventDrivenSummarizer:
    """Event-driven summarizer that triggers on new content"""
    
    def __init__(self) -> None:
        self.rss_parser = RSSParser()
        self.web_scraper = WebScraper()
        self.llm_client = LLMClient()
        self.db_client = FirestoreClient()
        self.digest = SlackDigest()
        
    def check_for_new_episodes(self) -> List[Dict[str, Any]]:
        """Check podcast feeds for new episodes"""
        new_episodes = []
        
        for feed_config in Config.PODCAST_FEEDS:
            try:
                feed = self.rss_parser.fetch_feed(feed_config['url'], feed_config['name'])
                if feed and feed.entries:
                    # Extract items from the feed (get just the most recent)
                    items = self.rss_parser.extract_feed_items(feed, feed_config, hours_back=24)
                    
                    if items and not self.db_client.is_url_processed(items[0]['url']):
                        new_episodes.append(items[0])
                        logger.info(f"Found new episode: {items[0]['title']} from {feed_config['name']}")
                        
            except Exception as e:
                logger.error(f"Error checking feed {feed_config['name']}: {e}")
                
        return new_episodes
    
    def should_send_digest(self) -> bool:
        """Check if we should send a digest based on various triggers"""
        # Check if we've already sent a digest today
        today = datetime.now().strftime('%Y-%m-%d')
        digest_doc = self.db_client.db.collection('digest_history').document(today).get()
        
        if digest_doc.exists:
            last_sent = digest_doc.to_dict().get('sent_at')
            if last_sent:
                # Already sent today, check if enough time has passed (e.g., 12 hours for bi-daily)
                time_since = datetime.now() - last_sent
                if time_since < timedelta(hours=12):
                    logger.info(f"Digest already sent {time_since.total_seconds()/3600:.1f} hours ago")
                    return False
        
        # Check for new episodes
        new_episodes = self.check_for_new_episodes()
        
        # Trigger conditions:
        # 1. New podcast episode(s) found
        # 2. It's past our preferred time window (e.g., 7 AM - 9 AM)
        # 3. We have accumulated enough content
        
        current_hour = datetime.now().hour
        is_preferred_time = 7 <= current_hour <= 9  # 7 AM - 9 AM
        
        if new_episodes:
            logger.info(f"Trigger: Found {len(new_episodes)} new podcast episodes")
            return True
        elif is_preferred_time and not digest_doc.exists:
            logger.info("Trigger: Preferred time window and no digest sent today")
            return True
        else:
            logger.info("No trigger conditions met")
            return False
    
    def process_all_content(self) -> Dict[str, int]:
        """Process all new content and build digest"""
        stats = {'news': 0, 'podcasts': 0, 'errors': 0}
        
        # Fetch all RSS feeds
        all_items = self.rss_parser.fetch_all_feeds()
        
        # Process news articles (limit to most recent to avoid overwhelming)
        recent_news = sorted(all_items['news'], 
                           key=lambda x: x.get('published_parsed', time.gmtime(0)), 
                           reverse=True)[:10]  # Top 10 most recent
        
        logger.info(f"Processing {len(recent_news)} recent news items")
        for article in recent_news:
            try:
                if self.db_client.is_url_processed(article['url']):
                    continue
                    
                content = self.web_scraper.fetch_article_content(article['url'])
                if not content:
                    continue
                    
                summary = self.llm_client.summarize_article(article['title'], content)
                if summary:
                    self.digest.add_news_item(article, summary)
                    self.db_client.mark_url_processed(article['url'], {
                        'title': article['title'],
                        'feed_name': article['feed_name'],
                        'feed_type': 'news',
                        'summary_generated': True
                    })
                    stats['news'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing news {article['url']}: {e}")
                stats['errors'] += 1
        
        # Process podcast episodes
        recent_podcasts = sorted(all_items['podcast'], 
                               key=lambda x: x.get('published_parsed', time.gmtime(0)), 
                               reverse=True)[:5]  # Top 5 most recent
        
        logger.info(f"Processing {len(recent_podcasts)} recent podcast items")
        for episode in recent_podcasts:
            try:
                if self.db_client.is_url_processed(episode['url']):
                    continue
                    
                if episode.get('description'):
                    summary = self.llm_client.summarize_podcast(
                        episode['title'],
                        episode['description']
                    )
                    
                    if summary:
                        self.digest.add_podcast_item(episode, summary)
                        self.db_client.mark_url_processed(episode['url'], {
                            'title': episode['title'],
                            'feed_name': episode['feed_name'],
                            'feed_type': 'podcast',
                            'summary_generated': True
                        })
                        stats['podcasts'] += 1
                        
            except Exception as e:
                logger.error(f"Error processing podcast {episode['url']}: {e}")
                stats['errors'] += 1
        
        # Generate AI tip
        try:
            ai_tip = self.llm_client.generate_ai_tip()
            if ai_tip:
                self.digest.set_ai_tip(ai_tip)
        except Exception as e:
            logger.error(f"Error generating AI tip: {e}")
        
        return stats
    
    def record_digest_sent(self) -> None:
        """Record that a digest was sent today"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.db_client.db.collection('digest_history').document(today).set({
            'sent_at': datetime.now(),
            'stats': self.digest.stats,
            'trigger': 'event_driven'
        })


@functions_framework.cloud_event
@monitor_memory(threshold_percent=85.0)
def event_driven_function(cloud_event: Any) -> None:
    """
    Event-driven Cloud Function that checks for new content
    Can be triggered frequently (e.g., every 30 minutes) with minimal cost
    """
    start_time = time.time()
    
    try:
        logger.info("Event-driven check started")
        
        # Validate configuration
        if not Config.is_valid():
            validation_results = Config.validate()
            missing = [k for k, v in validation_results.items() if not v]
            raise ValueError(f"Missing required configuration: {missing}")
        
        # Initialize summarizer
        summarizer = EventDrivenSummarizer()
        
        # Check if we should send a digest
        if summarizer.should_send_digest():
            logger.info("Digest trigger conditions met, processing content...")
            
            # Process all new content
            with ResourceGuard("content_processing", memory_threshold=80.0):
                stats = summarizer.process_all_content()
            
            # Send digest if we have content
            if summarizer.digest.news_items or summarizer.digest.podcast_items:
                success = summarizer.digest.send_digest()
                
                if success:
                    logger.info(f"Digest sent successfully: {stats}")
                    summarizer.record_digest_sent()
                else:
                    logger.error("Failed to send digest")
            else:
                logger.info("No new content to send")
        else:
            logger.info("No digest needed at this time")
        
        elapsed = time.time() - start_time
        logger.info(f"Event-driven check completed in {elapsed:.1f}s")
        
    except Exception as e:
        logger.error(f"Event-driven function error: {e}")
        error_client = error_reporting.Client()
        error_client.report_exception()
        raise


@functions_framework.cloud_event
def podcast_check_function(cloud_event: Any) -> None:
    """
    Lightweight function that just checks for new podcasts
    Can run very frequently (every 15-30 minutes) at minimal cost
    """
    try:
        logger.info("Checking for new podcast episodes...")
        
        parser = RSSParser()
        db_client = FirestoreClient()
        new_episodes_found = False
        
        for feed_config in Config.PODCAST_FEEDS:
            try:
                feed = parser.fetch_feed(feed_config['url'], feed_config['name'])
                if feed and feed.entries:
                    latest = feed.entries[0]
                    episode_url = latest.get('link', '')
                    
                    if episode_url and not db_client.is_url_processed(episode_url):
                        logger.info(f"New episode found: {latest.get('title')} from {feed_config['name']}")
                        new_episodes_found = True
                        
                        # Trigger the main digest function
                        # In GCP, you would publish to a Pub/Sub topic here
                        # For now, just log it
                        logger.info("Would trigger digest generation now")
                        
            except Exception as e:
                logger.error(f"Error checking {feed_config['name']}: {e}")
        
        if not new_episodes_found:
            logger.info("No new episodes found")
            
    except Exception as e:
        logger.error(f"Podcast check error: {e}")


# For local testing
if __name__ == "__main__":
    # Test the event-driven function
    from cloudevents.http import CloudEvent
    
    attributes = {
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "source": "local-test",
    }
    data = {"message": {"data": "test"}}
    
    test_event = CloudEvent(attributes, data)
    event_driven_function(test_event)