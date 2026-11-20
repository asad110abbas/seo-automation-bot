import asyncio
from urllib.parse import urljoin, urlparse
from typing import Any

import httpx
from bs4 import BeautifulSoup


async def crawl_website(base_url: str, max_pages: int = 50) -> list[dict[str, Any]]:
    """Crawl up to max_pages pages starting from base_url and return page data."""
    visited: set[str] = set()
    queue: list[str] = [base_url]
    pages: list[dict[str, Any]] = []
    domain = urlparse(base_url).netloc

    headers = {
        "User-Agent": "SEOAutomationBot/1.0 (SEO Audit)",
        "Accept": "text/html,application/xhtml+xml",
    }

    async with httpx.AsyncClient(headers=headers, timeout=15, follow_redirects=True) as client:
        while queue and len(pages) < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                resp = await client.get(url)
                content_type = resp.headers.get("content-type", "")
                if "text/html" not in content_type:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                page_data = _extract_page_data(url, resp, soup)
                pages.append(page_data)

                # Queue internal links
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, a["href"])
                    parsed = urlparse(href)
                    if parsed.netloc == domain and href not in visited:
                        queue.append(href)

            except (httpx.RequestError, httpx.HTTPStatusError):
                pages.append({"url": url, "error": "fetch_failed", "status_code": 0})

    return pages


def _extract_page_data(url: str, resp: httpx.Response, soup: BeautifulSoup) -> dict[str, Any]:
    title_tag = soup.find("title")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", rel="canonical")
    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
    images = soup.find_all("img")
    images_missing_alt = sum(1 for img in images if not img.get("alt", "").strip())
    internal_links = [a["href"] for a in soup.find_all("a", href=True)]
    has_schema = bool(soup.find("script", type="application/ld+json"))
    viewport_meta = soup.find("meta", attrs={"name": "viewport"})

    title = title_tag.get_text(strip=True) if title_tag else ""
    description = meta_desc.get("content", "").strip() if meta_desc else ""

    issues = []
    if not title:
        issues.append({"type": "missing_title", "severity": "critical"})
    elif len(title) < 30 or len(title) > 60:
        issues.append({"type": "title_length", "severity": "warning", "length": len(title)})
    if not description:
        issues.append({"type": "missing_meta_description", "severity": "critical"})
    elif len(description) < 120 or len(description) > 160:
        issues.append({"type": "meta_description_length", "severity": "warning", "length": len(description)})
    if len(h1_tags) == 0:
        issues.append({"type": "missing_h1", "severity": "critical"})
    elif len(h1_tags) > 1:
        issues.append({"type": "multiple_h1", "severity": "warning", "count": len(h1_tags)})
    if images_missing_alt > 0:
        issues.append({"type": "images_missing_alt", "severity": "warning", "count": images_missing_alt})
    if not has_schema:
        issues.append({"type": "missing_schema_markup", "severity": "info"})
    if not viewport_meta:
        issues.append({"type": "missing_viewport_meta", "severity": "warning"})

    return {
        "url": url,
        "status_code": resp.status_code,
        "title": title,
        "meta_description": description,
        "canonical": canonical.get("href", "") if canonical else "",
        "h1_tags": h1_tags,
        "h2_tags": h2_tags[:10],
        "images_missing_alt": images_missing_alt,
        "has_schema": has_schema,
        "internal_links_count": len(internal_links),
        "issues": issues,
        "word_count": len(soup.get_text().split()),
    }
