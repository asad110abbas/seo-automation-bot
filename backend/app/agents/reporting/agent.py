import os
from datetime import date
from app.agents.base_agent import BaseAgent, AgentResult
from app.agents.reporting.pdf_generator import generate_pdf
from app.config import settings


class ReportingAgent(BaseAgent):
    agent_type = "reporting"

    async def run(self, db=None) -> AgentResult:
        await self.progress("Collecting all agent results...", 10)

        try:
            audit = await self.context.get("audit_result", {})
            keywords = await self.context.get("keyword_result", {})
            competitors = await self.context.get("competitor_result", {})
            gbp = await self.context.get("gbp_result", {})
            content = await self.context.get("content_result", {})
            links = await self.context.get("link_result", {})

            await self.progress("Generating PDF report...", 50)

            report_data = {
                "project_id": self.context.project_id,
                "run_id": self.context.run_id,
                "target_url": self.context.target_url,
                "business_type": self.context.business_type,
                "location": self.context.location,
                "report_month": date.today().isoformat(),
                "audit": audit,
                "keywords": keywords,
                "competitors": competitors,
                "gbp": gbp,
                "content": content,
                "links": links,
            }

            pdf_path = await generate_pdf(report_data)

            summary = {
                "seo_score": audit.get("seo_score", 0),
                "pages_crawled": audit.get("pages_crawled", 0),
                "total_keywords": keywords.get("total_keywords", 0),
                "competitors_found": len(competitors.get("competitors", [])),
                "content_pieces": len(content.get("generated_content", [])),
                "link_opportunities": links.get("total_opportunities", 0),
                "gbp_score": gbp.get("gbp_score", 0),
            }

            result_data = {"pdf_path": pdf_path, "summary": summary}
            await self.context.set("report_result", result_data)
            await self.progress("Report generation complete.", 100)
            return AgentResult(success=True, agent_type=self.agent_type, data=result_data)

        except Exception as e:
            return AgentResult(success=False, agent_type=self.agent_type, error=str(e))
