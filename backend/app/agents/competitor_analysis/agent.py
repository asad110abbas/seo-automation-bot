import json
import asyncio
import httpx
from bs4 import BeautifulSoup
from app.agents.base_agent import BaseAgent, AgentResult
from app.config import settings


class CompetitorAnalysisAgent(BaseAgent):
    agent_type = "competitor_analysis"

    async def run(self, business_type: str, location: str) -> AgentResult:
        await self.progress("Finding top competitors in SERP...", 10)

        try:
            competitors = await self._find_competitors(business_type, location)

            if competitors is None:
                # No SerpAPI key — use full mock data
                await self.progress("Using sample competitor data (no SerpAPI key)...", 40)
                result_data = _mock_competitor_result(business_type, location)
                await self.context.set("competitor_result", result_data)
                await self.progress("Competitor analysis complete.", 100)
                return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

            await self.progress(f"Found {len(competitors)} competitors. Analyzing their content...", 30)

            analyzed = []
            for i, comp in enumerate(competitors[:5]):
                pct = 30 + int((i / 5) * 40)
                await self.progress(f"Analyzing {comp['url']}...", pct)
                details = await self._analyze_competitor(comp)
                analyzed.append(details)

            await self.progress("Identifying content gaps...", 80)
            keyword_result = await self.context.get("keyword_result", {})
            our_keywords = [k["keyword"] for k in keyword_result.get("all_keywords", [])]
            content_gaps = await self._find_gaps(analyzed, our_keywords)

            result_data = {
                "competitors": analyzed,
                "content_gaps": content_gaps,
            }

            await self.context.set("competitor_result", result_data)
            await self.progress("Competitor analysis complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _find_competitors(self, business_type: str, location: str) -> list[dict]:
        if not settings.serpapi_key or settings.serpapi_key == "your_serpapi_key_here":
            return None  # signals full mock mode

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_competitors_sync, business_type, location)

    def _fetch_competitors_sync(self, business_type: str, location: str) -> list[dict]:
        from serpapi import GoogleSearch
        params = {
            "engine": "google",
            "q": f"{business_type} {location}",
            "location": f"{location}, Pakistan",
            "api_key": settings.serpapi_key,
            "num": 10,
        }
        results = GoogleSearch(params).get_dict()
        comps = []
        for i, r in enumerate(results.get("organic_results", [])[:5]):
            comps.append({"url": r.get("link", ""), "rank": i + 1, "title": r.get("title", "")})
        return comps

    async def _analyze_competitor(self, comp: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(comp["url"])
                soup = BeautifulSoup(resp.text, "lxml")
                title = soup.find("title")
                h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
                h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
                text = soup.get_text(" ", strip=True)[:3000]
                word_count = len(soup.get_text().split())
        except Exception:
            return {**comp, "error": "could_not_fetch", "top_keywords": [], "word_count": 0}

        extracted_kws = await self._extract_keywords(text, comp["url"])

        return {
            "url": comp["url"],
            "rank": comp.get("rank", 0),
            "title": title.get_text(strip=True) if title else "",
            "h1": h1s[:3],
            "h2": h2s[:5],
            "word_count": word_count,
            "top_keywords": extracted_kws,
        }

    async def _extract_keywords(self, text: str, url: str) -> list[str]:
        prompt = f"""From this website content from {url}, extract the 10 most important SEO keywords they are targeting.
Content: {text[:2000]}
Respond with a JSON array of keyword strings only."""
        try:
            raw = self.claude.analyze(
                system_prompt="You are an SEO analyst. Respond with valid JSON only.",
                user_content=prompt,
            )
            return json.loads(raw)
        except Exception:
            return []

    async def _find_gaps(self, competitors: list[dict], our_keywords: list[str]) -> list[dict]:
        all_comp_kws: dict[str, int] = {}
        for comp in competitors:
            for kw in comp.get("top_keywords", []):
                all_comp_kws[kw] = all_comp_kws.get(kw, 0) + 1

        gaps = []
        for kw, count in sorted(all_comp_kws.items(), key=lambda x: -x[1]):
            if kw not in our_keywords:
                opportunity = "high" if count >= 3 else "medium" if count == 2 else "low"
                gaps.append({"keyword": kw, "competitors_with_it": count, "opportunity": opportunity})

        return gaps[:30]


def _mock_competitor_result(business_type: str, location: str) -> dict:
    bt = business_type.lower()
    loc = location.lower()
    competitors = [
        {
            "url": f"https://top{bt.replace(' ', '')}{loc}.pk",
            "rank": 1,
            "title": f"Best {business_type} in {location} | Top Rated",
            "h1": [f"#1 {business_type} in {location}"],
            "h2": ["Our Services", "Why Choose Us", "Contact Us"],
            "word_count": 1800,
            "top_keywords": [f"best {bt} {loc}", f"{bt} near me", f"affordable {bt} {loc}"],
        },
        {
            "url": f"https://premium{bt.replace(' ', '')}.pk",
            "rank": 2,
            "title": f"Premium {business_type} Services | {location}",
            "h1": [f"Premium {business_type} Services"],
            "h2": ["Services", "Pricing", "Testimonials", "FAQ"],
            "word_count": 2200,
            "top_keywords": [f"premium {bt}", f"{bt} price {loc}", f"{bt} reviews {loc}"],
        },
        {
            "url": f"https://{bt.replace(' ', '')}experts{loc}.com",
            "rank": 3,
            "title": f"{business_type} Experts | {location} Pakistan",
            "h1": [f"Expert {business_type} in {location}"],
            "h2": ["About Us", "Our Team", "Services", "Book Now"],
            "word_count": 1500,
            "top_keywords": [f"experienced {bt} {loc}", f"{bt} specialists", f"top {bt} pakistan"],
        },
    ]
    content_gaps = [
        {"keyword": f"{bt} cost {loc}", "competitors_with_it": 3, "opportunity": "high"},
        {"keyword": f"{bt} online booking {loc}", "competitors_with_it": 2, "opportunity": "high"},
        {"keyword": f"best {bt} near me", "competitors_with_it": 3, "opportunity": "high"},
        {"keyword": f"{bt} reviews {loc}", "competitors_with_it": 2, "opportunity": "medium"},
        {"keyword": f"affordable {bt} pakistan", "competitors_with_it": 2, "opportunity": "medium"},
        {"keyword": f"{bt} open now {loc}", "competitors_with_it": 1, "opportunity": "low"},
    ]
    return {"competitors": competitors, "content_gaps": content_gaps}
