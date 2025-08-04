"""Security utilities for input validation and sanitization"""
import re
import html
from urllib.parse import urlparse, urlunparse
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Allowed URL schemes for web scraping
ALLOWED_SCHEMES = ['http', 'https']

# Blocked domains to prevent SSRF attacks
BLOCKED_DOMAINS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '169.254.169.254',  # Cloud metadata endpoint
    '::1',
    '[::1]',
]

# Maximum content length to prevent memory exhaustion
MAX_CONTENT_LENGTH = 1024 * 1024 * 10  # 10MB


def validate_url(url: str) -> Optional[str]:
    """
    Validate and sanitize URL to prevent SSRF attacks

    Args:
        url: URL to validate

    Returns:
        Sanitized URL or None if invalid
    """
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            logger.warning(f"Invalid URL scheme: {parsed.scheme}")
            return None

        # Check for blocked domains
        hostname = parsed.hostname
        if hostname and any(blocked in hostname.lower() for blocked in BLOCKED_DOMAINS):
            logger.warning(f"Blocked domain detected: {hostname}")
            return None

        # Check for IP addresses in domain (basic check)
        if hostname and re.match(r'^(\d{1,3}\.){3}\d{1,3}$', hostname):
            logger.warning(f"Direct IP address not allowed: {hostname}")
            return None

        # Rebuild URL with only allowed components
        clean_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))

        return clean_url

    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return None


def sanitize_text_for_slack(text: str) -> str:
    """
    Sanitize text to prevent Slack injection attacks

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for Slack
    """
    if not text:
        return ""

    # Slack mrkdwn format requires escaping these characters
    # https://api.slack.com/reference/surfaces/formatting#escaping
    slack_special_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;'
    }
    
    # Replace only the characters that Slack requires escaping
    for char, escaped in slack_special_chars.items():
        text = text.replace(char, escaped)

    # Limit length to prevent oversized messages
    max_length = 3000
    if len(text) > max_length:
        text = text[:max_length] + "..."

    # Remove any control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    return text


def sanitize_for_logging(text: str, sensitive_keys: Optional[List[str]] = None) -> str:
    """
    Sanitize text for safe logging, removing sensitive information

    Args:
        text: Text to sanitize
        sensitive_keys: List of sensitive key patterns to redact

    Returns:
        Sanitized text safe for logging
    """
    if not text:
        return ""

    if sensitive_keys is None:
        sensitive_keys = [
            'api_key', 'apikey', 'api-key',
            'password', 'passwd', 'pwd',
            'secret', 'token', 'auth',
            'webhook', 'private'
        ]

    # Redact sensitive patterns
    for key in sensitive_keys:
        # Case-insensitive replacement
        pattern = re.compile(
            rf'({re.escape(key)}["\']?\s*[:=]\s*["\']?)([^"\'\s]+)',
            re.IGNORECASE
        )
        text = pattern.sub(r'\1[REDACTED]', text)

    # Redact URLs with potential credentials
    url_pattern = re.compile(r'(https?://)([^:]+:[^@]+)@')
    text = url_pattern.sub(r'\1[REDACTED]@', text)

    return text


def validate_feed_data(feed_data: dict) -> bool:
    """
    Validate RSS feed data structure

    Args:
        feed_data: Feed data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['title', 'url', 'feed_name', 'feed_type']

    for field in required_fields:
        if field not in feed_data or not feed_data[field]:
            logger.warning(f"Missing required field in feed data: {field}")
            return False

    # Validate URL
    if not validate_url(feed_data['url']):
        return False

    # Validate feed type
    if feed_data['feed_type'] not in ['news', 'podcast']:
        logger.warning(f"Invalid feed type: {feed_data['feed_type']}")
        return False

    return True


def truncate_content(content: str, max_length: int = 5000) -> str:
    """
    Truncate content to prevent token limit issues

    Args:
        content: Content to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated content
    """
    if len(content) <= max_length:
        return content

    # Try to truncate at a sentence boundary
    truncated = content[:max_length]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')

    cut_point = max(last_period, last_newline)
    if cut_point > max_length * 0.8:  # Only use if we're keeping at least 80%
        return truncated[:cut_point + 1] + "..."

    return truncated + "..."
