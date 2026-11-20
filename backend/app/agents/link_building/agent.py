import json
import asyncio
from app.agents.base_agent import BaseAgent, AgentResult
from app.config import settings


class LinkBuildingAgent(BaseAgent):
    agent_type = "link_building"

    async def run(self) -> AgentResult:
        await self.progress("Searching for link building opportunities...", 10)

        try:
            business_type = self.context.business_type
            location = self.context.location

            directories = await self._find_directories(business_type, location)
            await self.progress(f"Found {len(directories)} directories. Scoring relevance...", 60)

            scored = await self._score_opportunities(directories, business_type)

            result_data = {
                "total_opportunities": len(scored),
                "opportunities": sorted(scored, key=lambda x: -x.get("relevance_score", 0)),
            }

            await self.context.set("link_result", result_data)
            await self.progress("Link building analysis complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _find_directories(self, business_type: str, location: str) -> list[dict]:
        if not settings.serpapi_key or settings.serpapi_key == "your_serpapi_key_here":
            return _pakistan_directories(business_type)

        queries = [
            f"{business_type} directory Pakistan",
            f"{location} business listings",
            f"Pakistan local business directory",
            f"add {business_type} {location} website",
        ]

        results = []
        loop = asyncio.get_event_loop()
        for q in queries:
            dirs = await loop.run_in_executor(None, self._search_sync, q)
            results.extend(dirs)

        seen = set()
        unique = []
        for d in results:
            if d["url"] not in seen:
                seen.add(d["url"])
                unique.append(d)
        return unique

    def _search_sync(self, query: str) -> list[dict]:
        from serpapi import GoogleSearch
        params = {"engine": "google", "q": query, "api_key": settings.serpapi_key, "num": 5}
        results = GoogleSearch(params).get_dict()
        return [
            {"directory_name": r.get("title", ""), "url": r.get("link", "")}
            for r in results.get("organic_results", [])[:5]
            if r.get("link")
        ]

    async def _score_opportunities(self, directories: list[dict], business_type: str) -> list[dict]:
        if not directories:
            return []

        dirs_json = json.dumps([{"name": d["directory_name"], "url": d["url"]} for d in directories[:20]])
        prompt = f"""Score these directories for a {business_type} business as link building opportunities.

Directories: {dirs_json}

For each, assign:
- relevance_score (0-100): how relevant for this business type
- estimated_da (1-100): estimated domain authority
- category: "business_directory" | "niche_directory" | "local_citation"
- submission_type: "free" | "paid" | "manual"

Respond with a JSON array. Each item must include: url, directory_name, relevance_score, estimated_da, category, submission_type."""

        try:
            raw = self.claude.analyze(
                system_prompt="You are an SEO link building expert. Respond with valid JSON only.",
                user_content=prompt,
            )
            return json.loads(raw)
        except Exception:
            return [{**d, "relevance_score": 50, "estimated_da": 20, "category": "business_directory", "submission_type": "free"} for d in directories]


def _pakistan_directories(business_type: str) -> list[dict]:
    return [
        {"directory_name": "Pakistan Business Directory", "url": "https://www.pakistanbusiness.com"},
        {"directory_name": "Rozee.pk Business", "url": "https://www.rozee.pk"},
        {"directory_name": "OLX Pakistan Business", "url": "https://www.olx.com.pk"},
        {"directory_name": "Fonezone.pk", "url": "https://www.fonezone.pk"},
        {"directory_name": "Daraz Seller", "url": "https://www.daraz.pk"},
        {"directory_name": "Yellow Pages Pakistan", "url": "https://www.yellowpages.com.pk"},
        {"directory_name": "Yelp Pakistan", "url": "https://www.yelp.com"},
        {"directory_name": "Google My Business", "url": "https://business.google.com"},
    ]
