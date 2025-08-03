import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Union
from bs4.element import Tag, PageElement
import time
from urllib.parse import urlparse

from .config import Config
from .security import validate_url, MAX_CONTENT_LENGTH
from .rate_limiter import rate_limit

logger = logging.getLogger(__name__)


class WebScraper:
    """Extract article content from web pages"""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-News-Summarizer/1.0 (Mozilla/5.0 compatible; AI Bot)'
        })

        # Common selectors for article content
        self.content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.article-content',
            '.entry-content',
            '.post-content',
            '.content',
            '#content',
            '.story-body',
            '.article-body',
        ]

        # Tags to remove from content
        self.remove_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside',
                           'form', 'button', 'iframe', 'noscript']

    @rate_limit('web_scraper', calls_per_minute=30)
    def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch and extract main article content from URL"""
        # Validate URL for security
        clean_url = validate_url(url)
        if not clean_url:
            logger.warning(f"Invalid or blocked URL: {url}")
            return None

        for attempt in range(Config.MAX_RETRIES):
            try:
                logger.info(f"Fetching article content from: {clean_url}")
                response = self.session.get(
                    clean_url,
                    timeout=Config.REQUEST_TIMEOUT,
                    stream=True  # Stream to check content length
                )
                response.raise_for_status()

                # Check content length
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > MAX_CONTENT_LENGTH:
                    logger.warning(f"Content too large: {content_length} bytes")
                    return None

                # Read content with size limit
                content = ""
                size = 0
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                    if chunk:
                        size += len(chunk)
                        if size > MAX_CONTENT_LENGTH:
                            logger.warning("Content exceeds maximum allowed size")
                            return None
                        content += chunk

                extracted = self._extract_content(content, clean_url)
                if extracted:
                    return extracted
                else:
                    logger.warning(f"No content extracted from {clean_url}")
                    return None

            except requests.RequestException as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}/{Config.MAX_RETRIES}): {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    return None
            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}")
                return None
        return None

    def _extract_content(self, html: str, url: str) -> Optional[str]:
        """Extract main content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        for tag in self.remove_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Try to find article content using various selectors
        article_content: Optional[Union[Tag, PageElement]] = None

        # First try specific selectors
        for selector in self.content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                article_content = content_elem
                break

        # If no specific content found, try site-specific extraction
        if not article_content:
            article_content = self._site_specific_extraction(soup, url)

        # If still no content, fall back to finding largest text block
        if not article_content:
            article_content = self._find_largest_text_block(soup)

        if article_content:
            # Extract text and clean it
            text = self._clean_text(article_content.get_text())

            # Ensure we have substantial content
            if len(text) > 200:  # Minimum content length
                return text

        return None

    def _site_specific_extraction(self, soup: BeautifulSoup, url: str) -> Optional[Union[Tag, PageElement]]:
        """Handle site-specific content extraction"""
        domain = urlparse(url).netloc.lower()

        # The Verge
        if 'theverge.com' in domain:
            return soup.find('div', class_='c-entry-content')

        # TechCrunch
        elif 'techcrunch.com' in domain:
            return soup.find('div', class_='article-content')

        # NY Times
        elif 'nytimes.com' in domain:
            return soup.find('section', {'name': 'articleBody'})

        # Wired
        elif 'wired.com' in domain:
            return soup.find('div', class_='body__inner-container')

        # Science Daily
        elif 'sciencedaily.com' in domain:
            return soup.find('div', id='text')

        return None

    def _find_largest_text_block(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the largest contiguous text block as fallback"""
        # Find all paragraphs
        paragraphs = soup.find_all('p')

        if not paragraphs:
            return None

        # Group consecutive paragraphs
        groups = []
        current_group = []

        for p in paragraphs:
            if p.get_text(strip=True):
                current_group.append(p)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []

        if current_group:
            groups.append(current_group)

        # Find largest group
        if groups:
            largest_group = max(groups, key=lambda g: sum(len(p.get_text()) for p in g))

            # Create a container with the largest group
            container = soup.new_tag('div')
            for p in largest_group:
                container.append(p)

            return container

        return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)

        # Remove multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')

        # Limit total length to avoid token limits
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        return text.strip()

    def extract_metadata(self, html: str) -> Dict[str, str]:
        """Extract metadata from HTML (title, description, etc.)"""
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)

        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and hasattr(meta_desc, 'get'):
            content = meta_desc.get('content', '')
            metadata['description'] = str(content) if content else ''

        # Open Graph data
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and hasattr(og_title, 'get'):
            content = og_title.get('content', '')
            metadata['og_title'] = str(content) if content else ''

        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and hasattr(og_desc, 'get'):
            content = og_desc.get('content', '')
            metadata['og_description'] = str(content) if content else ''

        return metadata
