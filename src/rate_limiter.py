"""Rate limiting utilities for external API calls"""
import time
import logging
from typing import Dict, Optional, Callable, Any
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60) -> None:
        """
        Initialize rate limiter
        
        Args:
            calls_per_minute: Maximum allowed calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.interval = 60.0 / calls_per_minute  # seconds between calls
        self.last_call_times: Dict[str, float] = defaultdict(float)
        self.call_counts: Dict[str, int] = defaultdict(int)
        self.reset_times: Dict[str, datetime] = defaultdict(
            lambda: datetime.now() + timedelta(minutes=1)
        )
    
    def wait_if_needed(self, key: str = "default") -> None:
        """
        Wait if necessary to respect rate limits
        
        Args:
            key: Identifier for the rate limit bucket
        """
        current_time = time.time()
        last_call = self.last_call_times[key]
        
        # Reset counter if minute has passed
        if datetime.now() >= self.reset_times[key]:
            self.call_counts[key] = 0
            self.reset_times[key] = datetime.now() + timedelta(minutes=1)
        
        # Check if we've hit the limit
        if self.call_counts[key] >= self.calls_per_minute:
            sleep_time = (self.reset_times[key] - datetime.now()).total_seconds()
            if sleep_time > 0:
                logger.warning(
                    f"Rate limit reached for {key}. Sleeping for {sleep_time:.2f}s"
                )
                time.sleep(sleep_time)
                # Reset after sleep
                self.call_counts[key] = 0
                self.reset_times[key] = datetime.now() + timedelta(minutes=1)
        
        # Ensure minimum interval between calls
        time_since_last = current_time - last_call
        if time_since_last < self.interval:
            sleep_time = self.interval - time_since_last
            logger.debug(f"Rate limiting {key}: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        # Update tracking
        self.last_call_times[key] = time.time()
        self.call_counts[key] += 1


# Global rate limiters for different services
RATE_LIMITERS = {
    'openrouter': RateLimiter(calls_per_minute=30),  # OpenRouter free tier
    'rss': RateLimiter(calls_per_minute=60),  # RSS feeds
    'web_scraper': RateLimiter(calls_per_minute=30),  # Web scraping
}


def rate_limit(service: str = 'default', calls_per_minute: Optional[int] = None) -> Callable:
    """
    Decorator to rate limit function calls
    
    Args:
        service: Service identifier for rate limiting
        calls_per_minute: Override default rate limit
    
    Returns:
        Decorated function with rate limiting
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get or create rate limiter
            if service not in RATE_LIMITERS:
                RATE_LIMITERS[service] = RateLimiter(
                    calls_per_minute=calls_per_minute or 60
                )
            elif calls_per_minute:
                # Update existing rate limiter
                RATE_LIMITERS[service].calls_per_minute = calls_per_minute
                RATE_LIMITERS[service].interval = 60.0 / calls_per_minute
            
            # Apply rate limiting
            RATE_LIMITERS[service].wait_if_needed(service)
            
            # Call the function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts based on error responses
    """
    
    def __init__(self, calls_per_minute: int = 60) -> None:
        super().__init__(calls_per_minute)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.backoff_multipliers: Dict[str, float] = defaultdict(lambda: 1.0)
    
    def record_error(self, key: str = "default") -> None:
        """Record an error and increase backoff"""
        self.error_counts[key] += 1
        # Exponential backoff on errors
        self.backoff_multipliers[key] = min(
            self.backoff_multipliers[key] * 2, 8.0
        )
        logger.warning(
            f"Error recorded for {key}. Backoff multiplier: "
            f"{self.backoff_multipliers[key]}"
        )
    
    def record_success(self, key: str = "default") -> None:
        """Record a success and decrease backoff"""
        self.error_counts[key] = 0
        # Gradually reduce backoff on success
        self.backoff_multipliers[key] = max(
            self.backoff_multipliers[key] * 0.9, 1.0
        )
    
    def wait_if_needed(self, key: str = "default") -> None:
        """Wait with adaptive backoff based on errors"""
        # Apply backoff multiplier to interval
        original_interval = self.interval
        self.interval = original_interval * self.backoff_multipliers[key]
        
        try:
            super().wait_if_needed(key)
        finally:
            # Restore original interval
            self.interval = original_interval