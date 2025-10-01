import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    """Fetch title + link count from a URL."""
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return {"url": url, "title": title, "links": len(links)}
    except Exception:
        return {"url": url, "title": "Error", "links": 0}

def crawl_sequential(urls):
    """Crawl sequentially."""
    start = time.time()
    results = [fetch(u) for u in urls]
    return results, round(time.time() - start, 2)

def crawl_parallel(urls, workers=10):
    """Crawl in parallel using ThreadPoolExecutor."""
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(fetch, urls))
    return results, round(time.time() - start, 2)
