import json
from app.agents.base_agent import BaseAgent, AgentResult
from app.agents.website_audit.crawler import crawl_website


class WebsiteAuditAgent(BaseAgent):
    agent_type = "website_audit"

    async def run(self, url: str, max_pages: int = 30) -> AgentResult:
        await self.progress("Starting website crawl...", 5)

        try:
            pages = await crawl_website(url, max_pages=max_pages)
            await self.progress(f"Crawled {len(pages)} pages. Analyzing issues...", 50)

            all_issues = []
            for page in pages:
                for issue in page.get("issues", []):
                    issue["url"] = page["url"]
                    all_issues.append(issue)

            critical = [i for i in all_issues if i.get("severity") == "critical"]
            warnings = [i for i in all_issues if i.get("severity") == "warning"]
            info = [i for i in all_issues if i.get("severity") == "info"]

            # Score: start at 100, deduct points per issue
            score = max(0, 100 - (len(critical) * 10) - (len(warnings) * 3) - (len(info) * 1))

            await self.progress("Generating AI recommendations...", 75)

            recommendations = await self._get_recommendations(critical, warnings, url)

            result_data = {
                "seo_score": score,
                "pages_crawled": len(pages),
                "issues": {
                    "critical": critical,
                    "warning": warnings,
                    "info": info,
                },
                "recommendations": recommendations,
                "raw_pages": pages,
            }

            await self.context.set("audit_result", result_data)
            await self.progress("Website audit complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))

    async def _get_recommendations(self, critical: list, warnings: list, url: str) -> list[str]:
        if not critical and not warnings:
            return ["No major SEO issues found. Keep maintaining your site."]

        issues_summary = json.dumps(critical[:10] + warnings[:10], indent=2)
        prompt = f"""You are an expert SEO consultant. Analyze these SEO issues found on {url} and provide 5-8 actionable recommendations, prioritized by impact. Be specific and practical.

Issues found:
{issues_summary}

Respond with a JSON array of recommendation strings. Example:
["Fix missing meta descriptions on 3 pages starting with /services", "Add H1 tags to all pages"]"""

        try:
            raw = self.claude.analyze(
                system_prompt="You are a senior SEO expert. Always respond with valid JSON only.",
                user_content=prompt,
            )
            parsed = json.loads(raw)
            # Normalize: Groq sometimes returns [{recommendation: "..."}, ...] instead of ["..."]
            result = []
            for item in parsed:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(item.get("recommendation") or item.get("text") or item.get("suggestion") or str(item))
            return result
        except Exception:
            return [f"Fix {len(critical)} critical issues and {len(warnings)} warnings found during the audit."]
