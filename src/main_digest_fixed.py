import json
import logging
import time
from typing import Any
import functions_framework
from google.cloud import error_reporting

from .config import Config
from .rss_parser import RSSParser
from .web_scraper import WebScraper
from .llm_client import LLMClient
from .firestore_client import FirestoreClient
from .slack_digest_v2 import SlackDigest
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
    start_time = time.time()
    
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
        
        # Track tool spotlight
        tool_spotlight_found = False
        
        # Fetch all RSS feeds
        logger.info("Fetching RSS feeds")
        all_items = rss_parser.fetch_all_feeds()
        
        # Process news articles
        logger.info(f"Processing {len(all_items['news'])} news items")
        news_processed = 0
        max_news = 5  # Limit to prevent timeout
        
        with ResourceGuard("news_processing", memory_threshold=80.0):
            for article in all_items['news'][:max_news]:
                try:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > 450:  # 7.5 minutes (leaving buffer)
                        logger.warning(f"Approaching timeout after {elapsed:.1f}s, sending partial digest")
                        break
                    
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
                        news_processed += 1
                        
                        # Look for tool mentions if we haven't found one yet
                        if not tool_spotlight_found:
                            tool_info = llm_client.extract_tool_from_article(article['title'], content)
                            if tool_info:
                                digest.set_tool_spotlight(
                                    tool_info['name'],
                                    tool_info['description'],
                                    tool_info['link'] if tool_info['link'] != 'See article' else article['url']
                                )
                                tool_spotlight_found = True
                                logger.info(f"Found tool spotlight: {tool_info['name']}")
                        
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
        podcasts_processed = 0
        max_podcasts = 10  # Increased limit since we're only tracking 2 podcasts
        
        with ResourceGuard("podcast_processing", memory_threshold=80.0):
            for episode in all_items['podcast'][:max_podcasts]:
                try:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > 480:  # 8 minutes (leaving buffer)
                        logger.warning(f"Approaching timeout after {elapsed:.1f}s, sending partial digest")
                        break
                    
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
                            podcasts_processed += 1
                            
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
        
        # If no tool spotlight found in articles, generate one
        if not tool_spotlight_found:
            try:
                logger.info("No tool found in articles, generating tool spotlight")
                tool_info = llm_client.generate_tool_spotlight()
                if tool_info:
                    digest.set_tool_spotlight(
                        tool_info['name'],
                        tool_info['description'],
                        tool_info['link']
                    )
                    logger.info(f"Generated tool spotlight: {tool_info['name']}")
            except Exception as e:
                logger.error(f"Error generating tool spotlight: {e}")
        
        # Send the complete digest
        logger.info(f"Sending daily digest to Slack (news: {news_processed}, podcasts: {podcasts_processed})")
        success = digest.send_digest()
        
        if success:
            logger.info(f"Daily digest sent successfully with {digest.stats}")
        else:
            logger.error("Failed to send daily digest")
        
        # Log final statistics
        elapsed_time = time.time() - start_time
        logger.info(f"Processing complete in {elapsed_time:.1f}s. Stats: {json.dumps(digest.stats)}")
        
    except Exception as e:
        logger.error(f"Cloud Function handler error: {e}")
        
        # Try to send error notification
        try:
            from .slack_client import SlackClient
            slack = SlackClient()
            slack.send_error_notification(
                error_type=type(e).__name__,
                error_details=str(e)
            )
        except Exception:
            pass
        
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