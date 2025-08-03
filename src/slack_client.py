import requests
import logging
from typing import List, Dict, Any

from .config import Config
from .security import sanitize_text_for_slack

logger = logging.getLogger(__name__)


class SlackClient:
    """Send formatted messages to Slack using Block Kit"""

    def __init__(self) -> None:
        self.webhook_url = Config.SLACK_WEBHOOK_URL

    def send_news_summary(self, article: Dict[str, Any], summary: List[str]) -> bool:
        """Send a news article summary to Slack"""
        # Sanitize all text content
        safe_title = sanitize_text_for_slack(article.get('title', 'No Title'))
        safe_summary = [sanitize_text_for_slack(point) for point in summary]
        safe_feed_name = sanitize_text_for_slack(article.get('feed_name', 'Unknown'))

        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✨ *AI News Summary:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{safe_title}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join([f"• {point}" for point in safe_summary])
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📰 {safe_feed_name} | <{article['url']}|Read More>"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        return self._send_message(blocks=blocks)

    def send_podcast_summary(self, episode: Dict[str, Any], summary: List[str]) -> bool:
        """Send a podcast episode summary to Slack"""
        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎙️ *Podcast Digest:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{episode['title']}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join([f"• {point}" for point in summary])
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🎧 {episode['feed_name']} | <{episode['url']}|Listen Here>"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        return self._send_message(blocks=blocks)

    def send_ai_tip(self, tip: str) -> bool:
        """Send AI Tip of the Day to Slack"""
        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⭐ *AI Tip of the Day!* ⭐"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": tip
                }
            },
            {
                "type": "divider"
            }
        ]

        return self._send_message(blocks=blocks)

    def send_daily_header(self) -> bool:
        """Send a header message for the daily digest"""
        from datetime import datetime
        date_str = datetime.now().strftime("%A, %B %d, %Y")

        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 AI Daily Digest - {date_str}",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Your daily dose of AI news, insights, and tips_"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        return self._send_message(blocks=blocks)

    def send_daily_footer(self, stats: Dict[str, Any]) -> bool:
        """Send a footer with statistics"""
        blocks: List[Dict[str, Any]] = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 _Today's digest: {stats.get('news_count', 0)} news articles, {stats.get('podcast_count', 0)} podcast episodes_"
                    }
                ]
            }
        ]

        return self._send_message(blocks=blocks)

    def send_error_notification(self, error_type: str, error_details: str) -> bool:
        """Send error notification to Slack (for monitoring)"""
        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *AI News Summarizer Error*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Error Type:*\n{error_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Details:*\n{error_details[:100]}..."
                    }
                ]
            }
        ]

        return self._send_message(blocks=blocks)

    def _send_message(self, blocks: List[Dict[str, Any]], text: str = "AI News Update") -> bool:
        """Send message to Slack webhook"""
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return False

        payload = {
            "text": text,  # Fallback text
            "blocks": blocks
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Message sent to Slack successfully")
                return True
            else:
                logger.error(f"Failed to send to Slack: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"Error sending to Slack: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Slack webhook connection"""
        test_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🔧 *Test Message*\nAI News Summarizer webhook test successful!"
                }
            }
        ]

        return self._send_message(blocks=test_blocks, text="Test Message")
