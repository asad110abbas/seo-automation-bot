from datetime import date
from fastapi import HTTPException
from app.core.redis_client import get_redis
from app.config import settings


async def check_run_rate_limit(project_id: str):
    """Allow max N full analysis runs per project per day."""
    redis = await get_redis()
    key = f"rate:runs:{project_id}:{date.today().isoformat()}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 86400)  # expires end of day
    if count > settings.max_runs_per_project_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum {settings.max_runs_per_project_per_day} analysis runs per project per day reached.",
        )


async def check_url_safety(url: str):
    """Basic SSRF protection — block private/internal IP ranges."""
    import ipaddress
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname or ""

    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}
    if host in blocked_hosts:
        raise HTTPException(status_code=400, detail="URL points to a blocked internal host.")

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise HTTPException(status_code=400, detail="URL points to a private/internal IP address.")
    except ValueError:
        pass  # host is a domain name, not an IP — fine
