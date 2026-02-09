import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    name: str
    position: Optional[str]
    company: Optional[str]
    document_path: str
    excerpt: str
    page_number: Optional[int]
    document_date: Optional[str]
    mention_count: int


@dataclass
class ContactMatch:
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str]
    company: Optional[str]
    position: Optional[str]
    connected_on: Optional[str]
    total_mentions: int
    results: List[SearchResult]
    confidence_score: float = 1.0


class EpsteinSearchClient:
    
    API_BASE_URL = "https://analytics.dugganusa.com/api/v1/search"
    PDF_BASE_URL = "https://www.justice.gov/epstein/files/"
    
    def __init__(self, cache_dir: str = "data/cache", timeout: int = 30):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_name(self, full_name: str) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client must be used as async context manager")
            
        logger.info(f"Searching for: {full_name}")
        
        try:
            params = {"query": full_name, "limit": 100}
            async with self.session.get(self.API_BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                results = data.get("results", [])
                logger.info(f"Found {len(results)} results for {full_name}")
                return results
                
        except aiohttp.ClientError as e:
            logger.error(f"Error searching for {full_name}: {e}")
            return []
    
    async def batch_search(
        self, 
        names: List[str], 
        batch_size: int = 10,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            tasks = [self.search_name(name) for name in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for name, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error searching {name}: {result}")
                    results[name] = []
                else:
                    results[name] = result
            
            if progress_callback:
                progress_callback(min(i + batch_size, len(names)), len(names))
            
            await asyncio.sleep(0.5)
        
        return results
    
    def get_pdf_url(self, file_path: str) -> str:
        import urllib.parse
        base_url = self.PDF_BASE_URL.rstrip('/')
        if file_path.startswith('/'):
            return base_url + urllib.parse.quote(file_path, safe='/')
        else:
            return base_url + '/' + urllib.parse.quote(file_path, safe='/')


def search_synchronous(full_name: str, timeout: int = 30) -> List[Dict[str, Any]]:
    params = {"query": full_name, "limit": 100}
    
    try:
        response = requests.get(
            EpsteinSearchClient.API_BASE_URL,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        logger.error(f"Error searching for {full_name}: {e}")
        return []
