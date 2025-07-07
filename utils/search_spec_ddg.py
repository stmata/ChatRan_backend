from duckduckgo_search import DDGS
from starlette.concurrency import run_in_threadpool
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import time

class RateLimitException(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),              # Try up to 3 times
    wait=wait_fixed(3),                      # Wait 3 seconds between retries
    retry=retry_if_exception_type(RateLimitException)
)
def ddg_search_sync(query, num_results):
    with DDGS() as ddgs:
        results = []
        for res in ddgs.text(query, max_results=num_results):
            # DuckDuckGo returns an error dictionary if rate limited
            if "detail" in res and "Ratelimit" in res["detail"]:
                raise RateLimitException("DuckDuckGo Rate Limit hit")
            results.append({
                "snippet": res.get("body", ""),
                "url": res.get("href", ""),
                "title": res.get("title", "")
            })
        return results

async def web_search(query: str, num_results: int = 5) -> list:
    # Use thread pool for sync DDG library
    try:
        results = await run_in_threadpool(ddg_search_sync, query, num_results)
        return results
    except RateLimitException:
        # If even after retries we fail
        return [{
            "snippet": "DuckDuckGo has temporarily rate-limited searches. Please wait a few seconds and try again.",
            "url": "",
            "title": "Rate Limit"
        }]
