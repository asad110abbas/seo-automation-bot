import json
from app.agents.base_agent import BaseAgent, AgentResult


class ContentAgent(BaseAgent):
    agent_type = "content"

    async def run(self) -> AgentResult:
        await self.progress("Loading keyword and audit context...", 10)

        try:
            keyword_result = await self.context.get("keyword_result", {})
            audit_result = await self.context.get("audit_result", {})

            quick_wins = keyword_result.get("quick_wins", [])
            top_keywords = quick_wins[:3] if quick_wins else []

            if not top_keywords:
                clusters = keyword_result.get("clusters", [])
                if clusters and clusters[0].get("keywords"):
                    top_keywords = [{"keyword": clusters[0]["keywords"][0]}]

            generated = []
            for i, kw_data in enumerate(top_keywords[:3]):
                kw = kw_data.get("keyword", "") if isinstance(kw_data, dict) else str(kw_data)
                await self.progress(f"Writing content for: {kw}", 20 + i * 25)
                content_piece = await self._generate_blog_post(kw)
                generated.append(content_piece)

            # Generate optimized service page for main service
            await self.progress("Writing service page...", 85)
            service_page = await self._generate_service_page(
                self.context.business_type,
                self.context.location,
            )
            generated.append(service_page)

            result_data = {"generated_content": generated}
            await self.context.set("content_result", result_data)
            await self.progress("Content generation complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _generate_blog_post(self, target_keyword: str) -> dict:
        prompt = f"""Write a comprehensive SEO-optimized blog post targeting the keyword: "{target_keyword}"

Requirements:
- 800-1000 words
- Includes H2 and H3 subheadings
- Naturally uses the target keyword 3-5 times
- Includes a clear introduction and conclusion
- Written for a Pakistani audience
- Professional but friendly tone
- Include a meta description (150-160 chars) at the top as: META: [description]

Write the full blog post in Markdown format."""

        content = self.claude.analyze(
            system_prompt=f"You are an expert SEO content writer for {self.context.business_type} businesses in Pakistan.",
            user_content=prompt,
            max_tokens=2000,
        )

        word_count = len(content.split())
        return {
            "content_type": "blog_post",
            "title": f"Complete Guide: {target_keyword.title()}",
            "content": content,
            "target_keyword": target_keyword,
            "word_count": word_count,
            "seo_score": min(100, 60 + (word_count // 20)),
        }

    async def _generate_service_page(self, business_type: str, location: str) -> dict:
        prompt = f"""Write an SEO-optimized service page for a {business_type} in {location}, Pakistan.

Requirements:
- 500-700 words
- Clear H1 with main keyword
- Benefits section with bullet points
- Call-to-action paragraph
- Targets: "best {business_type} {location}" and "{business_type} near me {location}"
- Include meta description at the top as: META: [description]

Write in Markdown format."""

        content = self.claude.analyze(
            system_prompt="You are an expert SEO copywriter for local Pakistani businesses.",
            user_content=prompt,
            max_tokens=1500,
        )

        return {
            "content_type": "service_page",
            "title": f"Best {business_type.title()} in {location}",
            "content": content,
            "target_keyword": f"best {business_type} {location}",
            "word_count": len(content.split()),
            "seo_score": 82,
        }
