# src/api/client.py (Modified)
import httpx
import asyncio
import logging
from urllib.parse import urlencode
from typing import Optional, Dict

# Use the logger you've already set up
logger = logging.getLogger(__name__)

class ApiClient:
    """
    Handles all network requests for the LinkedIn scraper using httpx.
    Implements retry logic and robust error handling.
    """
    BASE_LIST_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    BASE_DETAILS_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    def __init__(self, concurrency_limit: int = 5, delay: float = 1.0, retries: int = 3):
        # Rotate user agents to reduce blocking
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        ]
        self.client = httpx.AsyncClient(
            headers={"User-Agent": self.user_agents[0]},
            timeout=20.0,
            follow_redirects=True
        )
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.delay = delay
        self.retries = retries

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        for attempt in range(self.retries):
            try:
                # Rotate user agent per request
                headers = kwargs.pop("headers", {})
                headers["User-Agent"] = self.user_agents[attempt % len(self.user_agents)]

                response = await self.client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retries}): {url} - {e}")
                if attempt + 1 == self.retries:
                    logger.error(f"All {self.retries} retries failed for URL: {url}")
                    return None
                await asyncio.sleep(self.delay * (attempt + 1)) # Exponential backoff
        return None

    async def get_job_list(self, query_params: dict) -> Optional[str]:
        url = f"{self.BASE_LIST_URL}?{urlencode(query_params)}"
        response = await self._request_with_retry("GET", url)
        return response.text if response else None

    async def get_job_details(self, job_id: str) -> Optional[Dict]:
        async with self.semaphore:
            await asyncio.sleep(self.delay)
            url = self.BASE_DETAILS_URL.format(job_id=job_id)
            response = await self._request_with_retry("GET", url)
            if not response:
                return {"error": "Request failed after multiple retries."}
            return response.text

    async def close(self):
        await self.client.aclose()