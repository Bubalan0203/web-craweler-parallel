import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    url: str
    title: str
    links: int
    status_code: Optional[int] = None
    error: Optional[str] = None
    response_time: float = 0.0
    success: bool = True


class WebCrawler:
    def __init__(self, timeout: int = 10, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch_sync(self, url: str, session=None) -> CrawlResult:
        import requests

        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'
                }

                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers=headers,
                    allow_redirects=True
                )
                response_time = time.time() - start_time

                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
                links = [a.get('href') for a in soup.find_all('a', href=True)]

                logger.info(f"Successfully crawled {url} - Status: {response.status_code}")

                return CrawlResult(
                    url=url,
                    title=title,
                    links=len(links),
                    status_code=response.status_code,
                    response_time=round(response_time, 3),
                    success=True
                )

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        title="Timeout Error",
                        links=0,
                        error="Request timed out",
                        response_time=round(time.time() - start_time, 3),
                        success=False
                    )

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1} for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        title="Connection Error",
                        links=0,
                        error=f"Connection failed: {str(e)[:50]}",
                        response_time=round(time.time() - start_time, 3),
                        success=False
                    )

            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                return CrawlResult(
                    url=url,
                    title="Error",
                    links=0,
                    error=str(e)[:100],
                    response_time=round(time.time() - start_time, 3),
                    success=False
                )

        return CrawlResult(
            url=url,
            title="Error",
            links=0,
            error="Max retries exceeded",
            response_time=round(time.time() - start_time, 3),
            success=False
        )

    async def fetch_async(self, url: str, session: aiohttp.ClientSession) -> CrawlResult:
        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'
                }

                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers=headers,
                    allow_redirects=True
                ) as response:
                    response_time = time.time() - start_time

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
                    links = [a.get('href') for a in soup.find_all('a', href=True)]

                    logger.info(f"Successfully crawled {url} - Status: {response.status}")

                    return CrawlResult(
                        url=url,
                        title=title,
                        links=len(links),
                        status_code=response.status,
                        response_time=round(response_time, 3),
                        success=True
                    )

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        title="Timeout Error",
                        links=0,
                        error="Request timed out",
                        response_time=round(time.time() - start_time, 3),
                        success=False
                    )
                await asyncio.sleep(0.5)

            except aiohttp.ClientError as e:
                logger.warning(f"Client error on attempt {attempt + 1} for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        title="Connection Error",
                        links=0,
                        error=f"Connection failed: {str(e)[:50]}",
                        response_time=round(time.time() - start_time, 3),
                        success=False
                    )
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                return CrawlResult(
                    url=url,
                    title="Error",
                    links=0,
                    error=str(e)[:100],
                    response_time=round(time.time() - start_time, 3),
                    success=False
                )

        return CrawlResult(
            url=url,
            title="Error",
            links=0,
            error="Max retries exceeded",
            response_time=round(time.time() - start_time, 3),
            success=False
        )

    async def crawl_async(self, urls: List[str], concurrent_limit: int = 50) -> Tuple[List[Dict], float]:
        start_time = time.time()

        connector = aiohttp.TCPConnector(limit=concurrent_limit, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self.fetch_async(url, session) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Unhandled exception: {result}")
                    processed_results.append(CrawlResult(
                        url="unknown",
                        title="Error",
                        links=0,
                        error=str(result)[:100],
                        success=False
                    ))
                else:
                    processed_results.append(result)

        elapsed_time = round(time.time() - start_time, 2)

        result_dicts = [
            {
                "url": r.url,
                "title": r.title,
                "links": r.links,
                "status_code": r.status_code,
                "error": r.error,
                "response_time": r.response_time,
                "success": r.success
            }
            for r in processed_results
        ]

        logger.info(f"Async crawl completed: {len(urls)} URLs in {elapsed_time}s")
        return result_dicts, elapsed_time

    def crawl_threaded(self, urls: List[str], workers: int = 10) -> Tuple[List[Dict], float]:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(self.fetch_sync, urls))

        elapsed_time = round(time.time() - start_time, 2)

        result_dicts = [
            {
                "url": r.url,
                "title": r.title,
                "links": r.links,
                "status_code": r.status_code,
                "error": r.error,
                "response_time": r.response_time,
                "success": r.success
            }
            for r in results
        ]

        logger.info(f"Threaded crawl completed: {len(urls)} URLs in {elapsed_time}s")
        return result_dicts, elapsed_time

    def crawl_sequential(self, urls: List[str]) -> Tuple[List[Dict], float]:
        start_time = time.time()

        results = [self.fetch_sync(url) for url in urls]

        elapsed_time = round(time.time() - start_time, 2)

        result_dicts = [
            {
                "url": r.url,
                "title": r.title,
                "links": r.links,
                "status_code": r.status_code,
                "error": r.error,
                "response_time": r.response_time,
                "success": r.success
            }
            for r in results
        ]

        logger.info(f"Sequential crawl completed: {len(urls)} URLs in {elapsed_time}s")
        return result_dicts, elapsed_time


def crawl_sequential(urls: List[str]) -> Tuple[List[Dict], float]:
    crawler = WebCrawler()
    return crawler.crawl_sequential(urls)


def crawl_parallel(urls: List[str], workers: int = 10) -> Tuple[List[Dict], float]:
    crawler = WebCrawler()
    return crawler.crawl_threaded(urls, workers)


def crawl_async_wrapper(urls: List[str], concurrent_limit: int = 50) -> Tuple[List[Dict], float]:
    crawler = WebCrawler()
    return asyncio.run(crawler.crawl_async(urls, concurrent_limit))
