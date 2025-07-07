from serpapi import GoogleSearch
from starlette.concurrency import run_in_threadpool
from app.core.config import SERPAPI_KEY

def serpapi_search_sync(query: str, num_results: int = 5):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
        "hl": "en"
    }
    search = GoogleSearch(params)
    try:
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        output = []
        for item in organic_results[:num_results]:
            output.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", "")
            })
        return output
    except Exception as e:
        return [{
            "title": "Search Error",
            "snippet": f"SerpAPI error: {e}",
            "url": ""
        }]

async def web_search(query: str, num_results: int = 5) -> list:
    return await run_in_threadpool(serpapi_search_sync, query, num_results)
