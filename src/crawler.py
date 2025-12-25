import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, start_urls: List[str], max_depth: int = 2):
        self.start_urls = start_urls
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.content: Dict[str, str] = {}
        self.base_domains = {urlparse(url).netloc for url in start_urls}

    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc in self.base_domains

    def crawl(self):
        for url in self.start_urls:
            self._crawl_recursive(url, 0)

    def _crawl_recursive(self, url: str, depth: int):
        if depth > self.max_depth or url in self.visited:
            return

        self.visited.add(url)
        logger.info(f"Crawling: {url} (Depth: {depth})")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text content
            # Try multiple selectors to find the main content
            selectors = [
                ('main', {}),
                ('article', {}),
                ('div', {'role': 'main'}),
                ('div', {'class': 'content'}),
                ('div', {'class': 'main-content'}),
                ('div', {'id': 'content'}),
                ('div', {'id': 'main'}),
                ('body', {}) # Fallback
            ]
            
            main_content = None
            for tag, attrs in selectors:
                main_content = soup.find(tag, attrs)
                if main_content:
                    break
            
            if main_content:
                # Remove navigation and footer elements within the main content
                for tag in main_content.find_all(['nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                    
                text = main_content.get_text(separator='\n', strip=True)
                # Basic cleaning
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                cleaned_text = '\n'.join(lines)
                
                if len(cleaned_text) > 100: # Only save if we got meaningful content
                    self.content[url] = cleaned_text
                    logger.info(f"Extracted {len(cleaned_text)} chars from {url}")
                else:
                    logger.warning(f"Content too short for {url}")

            # Find links
            if depth < self.max_depth:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    # Remove fragments
                    full_url = full_url.split('#')[0]
                    
                    if self.is_valid_url(full_url):
                        self._crawl_recursive(full_url, depth + 1)
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")

    def get_content(self) -> Dict[str, str]:
        return self.content
