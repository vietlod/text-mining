import requests
from bs4 import BeautifulSoup
from app.utils.logger import setup_logger

logger = setup_logger("WebSearch")

class WebSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_url(self, url):
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""

    def search_and_extract(self, query, num_results=5):
        logger.warning("Search API not configured. Returning empty results.")
        return []

    def process_website_list(self, urls):
        results = {}
        for url in urls:
            if url.strip():
                text = self.fetch_url(url.strip())
                if text:
                    results[url] = text
        return results
