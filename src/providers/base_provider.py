from abc import ABC, abstractmethod
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler

class JobProvider(ABC):
    """Abstract base class for job board providers."""
    
    def __init__(self, crawler: AsyncWebCrawler):
        self.crawler = crawler

    @abstractmethod
    async def search_jobs(self, persona: Dict[str, Any], locations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for jobs matching the persona and locations."""
        pass
