import asyncio
import json
from typing import Any
from app.config import settings


async def fetch_keyword_data(keyword: str, location: str) -> list[dict[str, Any]]:
    """Fetch keyword metrics from SerpAPI. Caches in Redis for 24h. Falls back to mock data."""
    if not settings.serpapi_key or settings.serpapi_key == "your_serpapi_key_here":
        return _mock_keyword_data(keyword)

    # Check Redis cache first
    try:
        from app.core.redis_client import get_redis
        redis = await get_redis()
        cache_key = f"serp:{keyword}:{location}"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _fetch_sync, keyword, location)
        # Cache for 24 hours to reduce SerpAPI costs
        try:
            await redis.setex(cache_key, 86400, json.dumps(result))
        except Exception:
            pass
        return result
    except Exception:
        return _mock_keyword_data(keyword)


def _fetch_sync(keyword: str, location: str) -> list[dict]:
    from serpapi import GoogleSearch

    params = {
        "engine": "google",
        "q": keyword,
        "location": f"{location}, Pakistan",
        "api_key": settings.serpapi_key,
        "num": 10,
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    keywords = [{"keyword": keyword, "search_volume": None, "difficulty": None, "source": "serpapi"}]

    # Extract related searches
    for related in results.get("related_searches", [])[:5]:
        keywords.append({
            "keyword": related.get("query", ""),
            "search_volume": None,
            "difficulty": None,
            "source": "serpapi_related",
        })

    return [k for k in keywords if k["keyword"]]


def _mock_keyword_data(keyword: str) -> list[dict]:
    """Return plausible mock data when SerpAPI key is not set."""
    import random
    base = [
        {"keyword": keyword, "search_volume": random.randint(100, 2000), "difficulty": random.randint(10, 70), "source": "mock"},
        {"keyword": f"{keyword} near me", "search_volume": random.randint(50, 800), "difficulty": random.randint(5, 50), "source": "mock"},
        {"keyword": f"best {keyword}", "search_volume": random.randint(80, 1200), "difficulty": random.randint(20, 65), "source": "mock"},
    ]
    return base
