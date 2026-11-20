import json
from app.agents.base_agent import BaseAgent, AgentResult
from app.agents.keyword_research.serp_client import fetch_keyword_data
from app.config import settings


class KeywordResearchAgent(BaseAgent):
    agent_type = "keyword_research"

    async def run(self, business_type: str, location: str, language: str = "en") -> AgentResult:
        await self.progress("Generating seed keywords with AI...", 10)

        try:
            seed_keywords = await self._generate_seeds(business_type, location)
            await self.progress(f"Generated {len(seed_keywords)} seed keywords. Fetching SERP data...", 30)

            all_keywords = []
            for i, kw in enumerate(seed_keywords[:15]):  # cap API calls
                pct = 30 + int((i / len(seed_keywords)) * 40)
                await self.progress(f"Researching: {kw}", pct)
                kw_data = await fetch_keyword_data(kw, location)
                all_keywords.extend(kw_data)

            await self.progress("Clustering and scoring keywords...", 75)
            clusters = await self._cluster_keywords(all_keywords, business_type, location)

            quick_wins = [k for k in all_keywords if (k.get("difficulty") or 999) < 40 and (k.get("search_volume") or 0) > 100]

            result_data = {
                "total_keywords": len(all_keywords),
                "clusters": clusters,
                "quick_wins": quick_wins[:20],
                "all_keywords": all_keywords,
            }

            await self.context.set("keyword_result", result_data)
            await self.progress("Keyword research complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _generate_seeds(self, business_type: str, location: str) -> list[str]:
        prompt = f"""Generate 20 SEO seed keywords for a {business_type} business in {location}, Pakistan.
Include: local "near me" keywords, service-specific keywords, informational keywords.
Examples for dental clinic in Lahore: "best dentist lahore", "dental clinic near me lahore", "tooth extraction lahore cost"

Respond with a JSON array of keyword strings only."""

        raw = self.claude.analyze(
            system_prompt="You are a local SEO expert for Pakistan. Respond with valid JSON only.",
            user_content=prompt,
        )
        try:
            return json.loads(raw)
        except Exception:
            return [f"best {business_type} {location}", f"{business_type} near me {location}"]

    async def _cluster_keywords(self, keywords: list[dict], business_type: str, location: str) -> list[dict]:
        if not keywords:
            return []

        kw_list = [k["keyword"] for k in keywords[:50]]
        prompt = f"""Group these keywords for a {business_type} in {location} into 5-8 topic clusters.

Keywords: {json.dumps(kw_list)}

Respond with a JSON array of clusters. Each cluster:
{{"cluster_name": "Emergency Services", "keywords": ["emergency dentist lahore", ...]}}"""

        try:
            raw = self.claude.analyze(
                system_prompt="You are an SEO keyword strategist. Respond with valid JSON only.",
                user_content=prompt,
            )
            return json.loads(raw)
        except Exception:
            return [{"cluster_name": "General", "keywords": kw_list[:10]}]
