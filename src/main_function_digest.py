import json
import logging
import signal
import time
from typing import Any
import functions_framework
from google.cloud import error_reporting

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


@functions_framework.cloud_event
@monitor_memory(threshold_percent=85.0)
def main_function_digest(cloud_event: Any) -> None:
    """
    Main Cloud Function handler using digest approach
    
    Args:
        cloud_event: Cloud Event from Pub/Sub trigger
        
    Returns:
        None (Cloud Functions don't require return for Pub/Sub triggers)
    """
    # Set up timeout handler
    start_time = time.time()
    timeout_seconds = Config.FUNCTION_TIMEOUT - Config.GRACEFUL_SHUTDOWN_BUFFER
    
    def timeout_handler(signum: int, frame: Any) -> None:
        """Handle timeout signal gracefully"""
        elapsed = time.time() - start_time
        logger.warning(
            f"Function timeout approaching after {elapsed:.1f}s. "
            f"Initiating graceful shutdown..."
        )
        raise TimeoutError("Function timeout - graceful shutdown initiated")
    
    # Set timeout signal
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        logger.info("AI News Summarizer Cloud Function started (Digest Mode)")
        
        # Validate configuration
        if not Config.is_valid():
            validation_results = Config.validate()
            missing = [k for k, v in validation_results.items() if not v]
            raise ValueError(f"Missing required configuration: {missing}")
        
        # Initialize clients
        rss_parser = RSSParser()
        web_scraper = WebScraper()
        llm_client = LLMClient()
        db_client = FirestoreClient()
        digest = SlackDigest()
        
        # Initialize Firestore collection if in development mode
        if Config.ENVIRONMENT == 'development':
            db_client.initialize_collection()
        
        # Generate and add AI Tip of the Day first
        try:
            logger.info("Generating AI Tip of the Day")
            ai_tip = llm_client.generate_ai_tip()
            if ai_tip:
                digest.set_ai_tip(ai_tip)
            else:
                logger.warning("Failed to generate AI tip")
        except Exception as e:
            logger.error(f"Error generating AI tip: {e}")
            digest.increment_errors()
        
        # Fetch all RSS feeds
        logger.info("Fetching RSS feeds")
        all_items = rss_parser.fetch_all_feeds()
        
        # Process news articles
        logger.info(f"Processing {len(all_items['news'])} news items")
        with ResourceGuard("news_processing", memory_threshold=80.0):
            for article in all_items['news']:
                try:
                    # Check if already processed
                    if db_client.is_url_processed(article['url']):
                        logger.info(f"Skipping already processed URL: {article['url']}")
                        continue
                    
                    # Fetch full article content
                    logger.info(f"Fetching article: {article['title']}")
                    content = web_scraper.fetch_article_content(article['url'])
                    
                    if not content:
                        logger.warning(f"No content extracted for: {article['url']}")
                        continue
                    
                    # Generate summary
                    summary = llm_client.summarize_article(article['title'], content)
                    
                    if summary:
                        # Add to digest instead of sending immediately
                        digest.add_news_item(article, summary)
                        
                        # Mark as processed
                        db_client.mark_url_processed(article['url'], {
                            'title': article['title'],
                            'feed_name': article['feed_name'],
                            'feed_type': 'news',
                            'summary_generated': True
                        })
                    else:
                        logger.warning(f"Failed to generate summary for: {article['title']}")
                        
                except Exception as e:
                    logger.error(f"Error processing news article {article['url']}: {e}")
                    digest.increment_errors()
                    continue
        
        # Process podcast episodes
        logger.info(f"Processing {len(all_items['podcast'])} podcast items")
        with ResourceGuard("podcast_processing", memory_threshold=80.0):
            for episode in all_items['podcast']:
                try:
                    # Check if already processed
                    if db_client.is_url_processed(episode['url']):
                        logger.info(f"Skipping already processed podcast: {episode['url']}")
                        continue
                    
                    # Generate summary from description
                    if episode.get('description'):
                        summary = llm_client.summarize_podcast(
                            episode['title'],
                            episode['description']
                        )
                        
                        if summary:
                            # Add to digest instead of sending immediately
                            digest.add_podcast_item(episode, summary)
                            
                            # Mark as processed
                            db_client.mark_url_processed(episode['url'], {
                                'title': episode['title'],
                                'feed_name': episode['feed_name'],
                                'feed_type': 'podcast',
                                'summary_generated': True
                            })
                        else:
                            logger.warning(f"Failed to generate summary for podcast: {episode['title']}")
                    else:
                        logger.warning(f"No description found for podcast: {episode['title']}")
                        
                except Exception as e:
                    logger.error(f"Error processing podcast {episode['url']}: {e}")
                    digest.increment_errors()
                    continue
        
        # Send the complete digest
        logger.info("Sending daily digest to Slack")
        success = digest.send_digest()
        
        if success:
            logger.info(f"Daily digest sent successfully with {digest.stats}")
        else:
            logger.error("Failed to send daily digest")
        
        # Log final statistics
        elapsed_time = time.time() - start_time
        logger.info(f"Processing complete in {elapsed_time:.1f}s. Stats: {json.dumps(digest.stats)}")
        
        # Cancel timeout alarm
        signal.alarm(0)
        
    except TimeoutError as e:
        # Handle graceful timeout
        logger.error(f"Function timeout: {e}")
        elapsed_time = time.time() - start_time
        
        # Try to send partial digest
        try:
            logger.info(f"Attempting to send partial digest before timeout...")
            digest.send_digest()
        except Exception:
            pass
            
        # Cancel alarm and exit gracefully
        signal.alarm(0)
        return
        
    except Exception as e:
        logger.error(f"Cloud Function handler error: {e}")
        
        # Report error to Google Cloud Error Reporting
        error_client = error_reporting.Client()
        error_client.report_exception()
        raise  # Re-raise to mark function execution as failed


# For local testing
if __name__ == "__main__":
    # Mock cloud event for local testing
    from cloudevents.http import CloudEvent
    
    attributes = {
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "source": "local-test",
    }
    data = {"message": {"data": "test"}}
    
    test_event = CloudEvent(attributes, data)
    main_function_digest(test_event)