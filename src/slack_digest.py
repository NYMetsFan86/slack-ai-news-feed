import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import Config
from .security import sanitize_text_for_slack

logger = logging.getLogger(__name__)


class SlackDigest:
    """Collect all daily content and send as a single digest message"""
    
    def __init__(self) -> None:
        self.webhook_url = Config.SLACK_WEBHOOK_URL
        self.blocks: List[Dict[str, Any]] = []
        self.news_items: List[Dict[str, Any]] = []
        self.podcast_items: List[Dict[str, Any]] = []
        self.ai_tip: Optional[str] = None
        self.stats: Dict[str, int] = {'news_count': 0, 'podcast_count': 0, 'errors': 0}
    
    def add_news_item(self, article: Dict[str, Any], summary: List[str]) -> None:
        """Add a news item to the digest"""
        self.news_items.append({
            'article': article,
            'summary': summary
        })
        self.stats['news_count'] += 1
    
    def add_podcast_item(self, episode: Dict[str, Any], summary: List[str]) -> None:
        """Add a podcast episode to the digest"""
        self.podcast_items.append({
            'episode': episode,
            'summary': summary
        })
        self.stats['podcast_count'] += 1
    
    def set_ai_tip(self, tip: str) -> None:
        """Set the AI tip of the day"""
        self.ai_tip = tip
    
    def increment_errors(self) -> None:
        """Track error count"""
        self.stats['errors'] += 1
    
    def build_digest(self) -> List[Dict[str, Any]]:
        """Build the complete digest message blocks"""
        blocks = []
        
        # Header
        blocks.extend([
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 AI Daily Digest - {datetime.now().strftime('%B %d, %Y')}",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Your daily AI news roundup • {self.stats['news_count']} articles • {self.stats['podcast_count']} podcasts"
                    }
                ]
            },
            {"type": "divider"}
        ])
        
        # AI Tip of the Day (at the top for visibility)
        if self.ai_tip:
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"💡 *AI Tip of the Day*\n{sanitize_text_for_slack(self.ai_tip)}"
                    }
                },
                {"type": "divider"}
            ])
        
        # News Articles
        if self.news_items:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📰 *Today's AI News*"
                }
            })
            
            for item in self.news_items[:5]:  # Limit to top 5
                article = item['article']
                summary = item['summary']
                
                safe_title = sanitize_text_for_slack(article.get('title', 'No Title'))
                safe_summary = [sanitize_text_for_slack(point) for point in summary]
                safe_feed = sanitize_text_for_slack(article.get('feed_name', 'Unknown'))
                
                blocks.extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{article.get('url', '#')}|{safe_title}>*\n_{safe_feed}_"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\n".join([f"• {point}" for point in safe_summary])
                        }
                    }
                ])
            
            blocks.append({"type": "divider"})
        
        # Podcasts
        if self.podcast_items:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🎙️ *Today's AI Podcasts*"
                }
            })
            
            for item in self.podcast_items[:6]:  # Show up to 6 episodes (weekend catch-up)
                episode = item['episode']
                summary = item['summary']
                
                safe_title = sanitize_text_for_slack(episode.get('title', 'No Title'))
                safe_summary = [sanitize_text_for_slack(point) for point in summary]
                safe_feed = sanitize_text_for_slack(episode.get('feed_name', 'Unknown'))
                duration = episode.get('duration', '')
                
                blocks.extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{episode.get('url', '#')}|{safe_title}>*\n_{safe_feed}_ {f'• {duration}' if duration else ''}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\n".join([f"• {point}" for point in safe_summary])
                        }
                    }
                ])
            
            blocks.append({"type": "divider"})
        
        # Footer
        blocks.extend([
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 Processed: {self.stats['news_count']} news articles, {self.stats['podcast_count']} podcasts • ⚠️ Errors: {self.stats['errors']}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 _Powered by AI News Summarizer_ • <https://github.com/NYMetsFan86/slack-ai-news-feed|View on GitHub>"
                    }
                ]
            }
        ])
        
        return blocks  # type: ignore[return-value]
    
    def send_digest(self) -> bool:
        """Send the complete digest to Slack"""
        if not self.news_items and not self.podcast_items and not self.ai_tip:
            logger.warning("No content to send in digest")
            return False
        
        blocks = self.build_digest()
        
        # Slack has a limit of 50 blocks per message
        if len(blocks) > 50:
            logger.warning(f"Digest has {len(blocks)} blocks, truncating to 50")
            blocks = blocks[:49] + [blocks[-1]]  # Keep footer
        
        payload = {
            "blocks": blocks,
            "text": f"AI Daily Digest - {self.stats['news_count']} articles, {self.stats['podcast_count']} podcasts"  # Fallback text
        }
        
        try:
            if not self.webhook_url:
                logger.error("No webhook URL configured")
                return False
                
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Daily digest sent to Slack successfully")
                return True
            else:
                logger.error(f"Failed to send digest to Slack: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending digest to Slack: {e}")
            return False