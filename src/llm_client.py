import openai
import logging
import time
from typing import Optional, List

from .config import Config
from .rate_limiter import rate_limit
from .circuit_breaker import circuit_breaker

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenRouter LLM client for content summarization and AI tip generation"""

    def __init__(self) -> None:
        self.client = openai.OpenAI(
            base_url=Config.OPENROUTER_BASE_URL,
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.model = Config.OPENROUTER_MODEL

    def summarize_article(self, title: str, content: str) -> Optional[List[str]]:
        """Summarize article content into bullet points focusing on AI relevance"""
        if not content:
            return None

        system_prompt = """You are an AI news summarizer for a business audience. Your task is to:
1. Identify and highlight AI-related content within the provided article
2. Create 3-5 concise bullet points summarizing the key information
3. Focus on practical implications, business relevance, and why it matters
4. Avoid highly technical jargon unless necessary
5. If the article is not related to AI, still summarize but note the general tech relevance

Format: Return ONLY bullet points, one per line, starting with "• "."""

        user_prompt = f"""Article Title: {title}

Article Content:
{content[:4000]}  # Limit content to avoid token limits

Please summarize this article in 3-5 bullet points, focusing on AI-related aspects and business relevance."""

        result = self._make_request(system_prompt, user_prompt, parse_bullets=True)
        return result  # type: ignore[no-any-return]

    def summarize_podcast(self, title: str, description: str) -> Optional[List[str]]:
        """Summarize podcast description into bullet points"""
        if not description:
            return None

        system_prompt = """You are an AI podcast summarizer. Your task is to:
1. Extract key topics and themes from the podcast description
2. Create 3-5 concise bullet points highlighting what listeners will learn
3. Focus on AI insights, practical applications, and key takeaways
4. Make it compelling for a business audience

Format: Return ONLY bullet points, one per line, starting with "• "."""

        user_prompt = f"""Podcast Episode: {title}

Description:
{description[:3000]}

Please summarize this podcast episode in 3-5 bullet points, focusing on key AI insights and takeaways."""

        result = self._make_request(system_prompt, user_prompt, parse_bullets=True)
        return result  # type: ignore[no-any-return]

    def generate_ai_tip(self) -> Optional[str]:
        """Generate an AI Tip of the Day"""
        topics = [
            "practical AI usage in daily work",
            "prompt engineering best practices",
            "understanding AI capabilities and limitations",
            "AI ethics and responsible use",
            "AI tools for productivity",
            "demystifying AI concepts",
            "AI in business decision-making",
            "future of work with AI",
            "AI collaboration strategies",
            "data privacy and AI"
        ]

        # Rotate through topics based on current day
        import random
        random.seed()  # Use current time for randomness
        topic = random.choice(topics)

        system_prompt = f"""You are an AI educator creating daily tips for business professionals.
Create a clear, practical, and engaging AI tip about: {topic}

Requirements:
- Keep it between 150-300 characters (1-2 sentences)
- Make it immediately actionable with a specific technique or tool
- Use simple, clear language without jargon
- Include a concrete example or specific use case
- Focus on practical value for everyday work
- Be encouraging and positive about AI adoption

Good example: "Try the '5W1H' prompt technique: Start your AI requests with Who, What, When, Where, Why, or How for clearer responses. Example: 'What are the key benefits of cloud computing for small businesses?'"
Bad example: "AI can help with many tasks in various ways across different domains."""

        user_prompt = "Generate today's AI tip for business professionals."

        response = self._make_request(system_prompt, user_prompt, parse_bullets=False)
        return response[0] if response else None

    @rate_limit('openrouter', calls_per_minute=30)
    @circuit_breaker(failure_threshold=3, recovery_timeout=120, expected_exception=openai.APIError)
    def _make_request(self, system_prompt: str, user_prompt: str,
                     parse_bullets: bool = False) -> Optional[List[str]]:
        """Make API request with retry logic"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                logger.info(f"Making LLM request (attempt {attempt + 1}/{Config.MAX_RETRIES})")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/yourusername/ai-slack-news",
                        "X-Title": "AI News Summarizer"
                    }
                )

                message_content = response.choices[0].message.content
                if message_content is None:
                    logger.warning("Received None content from API")
                    return None
                content = message_content.strip()

                if parse_bullets:
                    # Parse bullet points
                    bullets = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                            # Clean up the bullet point
                            bullet = line.lstrip('•-* ').strip()
                            if bullet:
                                bullets.append(bullet)
                    return bullets if bullets else None
                else:
                    return [content] if content else None

            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit: {e}")
                wait_time = min(2 ** attempt * 5, 60)  # Exponential backoff
                time.sleep(wait_time)

            except openai.APIError as e:
                logger.error(f"OpenRouter API error: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    return None

            except Exception as e:
                logger.error(f"Unexpected error in LLM request: {e}")
                return None

        return None

    def test_connection(self) -> bool:
        """Test the connection to OpenRouter"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
