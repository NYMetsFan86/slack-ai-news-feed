import openai
import logging
import time
from typing import Optional, List, Dict

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

        system_prompt = """You are an AI news curator with a focus on consumer-facing AI tools and practical applications.

PRIORITIZE content about:
- Updates to ChatGPT, Claude, Gemini, Perplexity, or other major AI assistants
- New AI features in popular apps (Microsoft, Google, Apple, etc.)
- Practical AI tools regular people can use today
- Business implications that affect everyday users

SKIP or briefly mention:
- Technical chip announcements (unless game-changing)
- Academic research papers
- Infrastructure/backend updates
- Developer-only tools

Create 2-3 punchy bullet points that answer "Why should I care?" 
Keep it conversational and exciting - think "The Neuron" newsletter style.
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
            "new free AI tools or websites to try",
            "ChatGPT/Claude/Gemini productivity hacks",
            "AI features in apps you already use",
            "quick AI tricks that save time",
            "comparing different AI assistants",
            "AI prompts that actually work",
            "free alternatives to paid AI tools",
            "AI features most people don't know about",
            "practical AI uses for everyday tasks",
            "AI tools for creative projects",
            "AI browser extensions that boost productivity",
            "AI meeting assistants and note-takers",
            "AI tools for social media content",
            "AI-powered research and fact-checking tools",
            "AI writing assistants beyond ChatGPT",
            "AI tools for data analysis without coding",
            "AI image and video editing shortcuts",
            "AI tools for learning new skills",
            "team collaboration AI tools",
            "AI automation for repetitive tasks"
        ]

        # Rotate through topics based on current day
        import random
        random.seed()  # Use current time for randomness
        topic = random.choice(topics)

        system_prompt = f"""You are writing practical AI tips for people who want to get more out of AI tools.
Create an exciting, actionable tip about: {topic}

Requirements:
- 1-2 sentences max (under 200 characters)
- Name a specific tool, feature, or technique
- Make it something they can try RIGHT NOW
- Use casual, enthusiastic language
- Focus on "wow factor" or time-saving potential

Good examples:
"🎯 Try Perplexity's 'Focus' mode for research - it cites sources like Wikipedia or Reddit only. Perfect for fact-checking!"
"💡 ChatGPT can analyze photos now! Upload a receipt and ask it to create an expense report. Works in the free version!"
"🚀 Google Docs has AI now: Type '@' to summarize, rewrite, or brainstorm. Hidden in plain sight!"

Bad example: "AI can help improve your productivity in various ways."""

        user_prompt = "Generate today's AI tip for business professionals."

        response = self._make_request(system_prompt, user_prompt, parse_bullets=False)
        return response[0] if response else None

    def extract_tool_from_article(self, title: str, content: str) -> Optional[Dict[str, str]]:
        """Extract AI tool mention from article if present"""
        system_prompt = """You are analyzing tech news articles to identify new AI tool launches or updates.

If the article mentions a NEW AI tool, app, or feature that readers can actually use, extract it.

ONLY extract if:
- It's a consumer-facing AI tool (not infrastructure/chips/research)
- It has a clear name and purpose
- Users can actually try it (launched/available, not "coming soon")

Return NOTHING if the article is about:
- AI policy, regulation, or ethics
- Company earnings or business news
- Technical infrastructure
- Research papers
- Vague AI initiatives

Format EXACTLY:
TOOL_NAME: [exact tool name]
DESCRIPTION: [1-2 sentences about what it does and why users should care]
LINK: [tool's website if mentioned, otherwise 'See article']"""

        user_prompt = f"""Article Title: {title}

Content: {content[:2000]}

Extract any new AI tool if this article announces one."""

        response = self._make_request(system_prompt, user_prompt, parse_bullets=False)
        
        if response and response[0] and "TOOL_NAME:" in response[0]:
            lines = response[0].strip().split('\n')
            tool_data = {}
            
            for line in lines:
                if line.startswith('TOOL_NAME:'):
                    tool_data['name'] = line.replace('TOOL_NAME:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    tool_data['description'] = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('LINK:'):
                    tool_data['link'] = line.replace('LINK:', '').strip()
            
            if all(k in tool_data for k in ['name', 'description', 'link']):
                return tool_data
        
        return None

    def generate_tool_spotlight(self) -> Optional[Dict[str, str]]:
        """Generate a featured AI tool recommendation"""
        categories = [
            "AI writing assistants",
            "AI image generators",
            "AI productivity tools",
            "AI research tools",
            "AI meeting assistants",
            "AI design tools",
            "AI coding assistants",
            "AI data analysis tools",
            "AI marketing tools",
            "AI learning platforms"
        ]
        
        import random
        category = random.choice(categories)
        
        system_prompt = f"""You are recommending useful AI tools for business professionals.
        
Generate a tool spotlight for the category: {category}

Requirements:
- Focus on tools that are FREE or have generous free tiers
- Must be something people can start using TODAY
- Include practical use cases
- Make it exciting but factual

Format your response EXACTLY like this:
TOOL_NAME: [name of the tool]
DESCRIPTION: [2-3 sentence description of what it does and why it's useful]
LINK: [actual website URL]

Example:
TOOL_NAME: Gamma
DESCRIPTION: Create beautiful presentations in minutes using AI. Just type what you want to present, and Gamma generates professional slides with design, images, and content. Perfect for last-minute presentations!
LINK: https://gamma.app"""

        user_prompt = "Generate today's AI tool spotlight."
        
        response = self._make_request(system_prompt, user_prompt, parse_bullets=False)
        
        if response and response[0]:
            # Parse the response
            lines = response[0].strip().split('\n')
            tool_data = {}
            
            for line in lines:
                if line.startswith('TOOL_NAME:'):
                    tool_data['name'] = line.replace('TOOL_NAME:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    tool_data['description'] = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('LINK:'):
                    tool_data['link'] = line.replace('LINK:', '').strip()
            
            if all(k in tool_data for k in ['name', 'description', 'link']):
                return tool_data
        
        return None

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
