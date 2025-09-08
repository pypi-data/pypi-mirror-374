import httpx
import asyncio
from urllib.parse import urlencode

from ljobx.utils.logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    """
    Handles all the network requests for the LinkedIn scraper using httpx.
    """
    BASE_LIST_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    BASE_DETAILS_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    def __init__(self, concurrency_limit=5, delay=1):
        self.client = httpx.AsyncClient()
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.delay = delay

    async def get_job_list(self, query_params):
        url = f"{self.BASE_LIST_URL}?{urlencode(query_params)}"
        try:
            logger.debug("Fetching job list for URL: %s", url)
            response = await self.client.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Error fetching job list for URL {url}: {e}")
            return None

    async def get_job_details(self, job_id):
        async with self.semaphore:
            await asyncio.sleep(self.delay)
            url = self.BASE_DETAILS_URL.format(job_id=job_id)
            logger.debug("Fetching job details for URL: %s", url)
            try:
                response = await self.client.get(url, timeout=15)
                response.raise_for_status()
                return response.text
            except httpx.RequestError as e:
                return {"error": f"Request error: {e}"}
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error {e.response.status_code}"}

    async def close(self):
        await self.client.aclose()
