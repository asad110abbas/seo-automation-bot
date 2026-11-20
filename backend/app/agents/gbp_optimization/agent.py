import json
from app.agents.base_agent import BaseAgent, AgentResult


class GBPOptimizationAgent(BaseAgent):
    agent_type = "gbp_optimization"

    async def run(self) -> AgentResult:
        await self.progress("Analyzing Google Business Profile...", 10)

        try:
            business_type = self.context.business_type
            location = self.context.location
            target_url = self.context.target_url

            await self.progress("Generating GBP optimization suggestions...", 40)
            suggestions = await self._generate_suggestions(business_type, location, target_url)

            gbp_score = max(0, 100 - (len([s for s in suggestions if s["priority"] == "high"]) * 15)
                                    - (len([s for s in suggestions if s["priority"] == "medium"]) * 7))

            result_data = {
                "gbp_score": gbp_score,
                "suggestions": suggestions,
            }

            await self.context.set("gbp_result", result_data)
            await self.progress("GBP optimization analysis complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _generate_suggestions(self, business_type: str, location: str, website: str) -> list[dict]:
        prompt = f"""You are a Google Business Profile (GBP) optimization expert.
Analyze a {business_type} business in {location} (website: {website}) and provide 8-12 specific GBP optimization suggestions.

Cover these categories: categories, photos, description, reviews, posts, Q&A, hours, products/services.

Respond with a JSON array. Each item:
{{"category": "photos", "suggestion": "Add at least 10 interior photos showing your clinic", "priority": "high"}}

Priority: "high" (major impact), "medium" (moderate impact), "low" (nice to have)."""

        raw = self.claude.analyze(
            system_prompt="You are a local SEO and GBP expert. Respond with valid JSON only.",
            user_content=prompt,
        )
        try:
            suggestions = json.loads(raw)
            return suggestions if isinstance(suggestions, list) else []
        except Exception:
            return [
                {"category": "categories", "suggestion": f"Add '{business_type}' as primary category", "priority": "high"},
                {"category": "photos", "suggestion": "Add minimum 10 photos (interior, exterior, team)", "priority": "high"},
                {"category": "reviews", "suggestion": "Respond to all existing reviews", "priority": "medium"},
                {"category": "posts", "suggestion": "Create weekly Google Posts about offers/news", "priority": "medium"},
            ]
