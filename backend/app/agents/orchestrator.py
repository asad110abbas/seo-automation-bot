import asyncio
from datetime import datetime

from app.agents.base_agent import AgentContext, AgentResult
from app.agents.website_audit.agent import WebsiteAuditAgent
from app.agents.keyword_research.agent import KeywordResearchAgent
from app.agents.competitor_analysis.agent import CompetitorAnalysisAgent
from app.agents.gbp_optimization.agent import GBPOptimizationAgent
from app.agents.content.agent import ContentAgent
from app.agents.link_building.agent import LinkBuildingAgent
from app.agents.reporting.agent import ReportingAgent
from app.core.llm_client import get_claude
from app.core.redis_client import get_redis


async def _stopped(redis, run_id: str) -> bool:
    val = await redis.get(f"run:{run_id}:stop")
    return val is not None


async def _save_usage(db, project_id: str, run_id: str, agent_type: str, claude, serp_calls: int = 0):
    """Persist token usage snapshot for the last agent call."""
    from app.models.usage import UsageLog
    usage = claude.usage
    # SerpAPI: $0.01/call on basic plan
    serp_cost = serp_calls * 0.01
    log = UsageLog(
        project_id=project_id,
        run_id=run_id,
        agent_type=agent_type,
        provider="groq",
        model=claude.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        input_cost_usd=usage.input_cost,
        output_cost_usd=usage.output_cost,
        serp_calls=serp_calls,
        serp_cost_usd=serp_cost,
    )
    db.add(log)
    await db.commit()
    claude.reset_usage()


async def run_full_analysis(
    project_id: str,
    target_url: str,
    business_type: str,
    location: str,
    db,
    run_id: str = None,
) -> dict[str, AgentResult]:
    """
    Entry point for a full multi-agent SEO analysis.

    Execution order:
      Phase 1 (parallel): Audit + Keywords + Competitors
      Phase 2 (parallel): GBP + Link Building
      Phase 3: Content (needs Phase 1 context)
      Phase 4: Reporting (aggregates everything)
    """
    redis = await get_redis()
    claude = get_claude()
    claude.reset_usage()

    context = AgentContext(
        run_id=run_id,
        project_id=project_id,
        target_url=target_url,
        business_type=business_type,
        location=location,
        _redis=redis,
    )

    audit_agent = WebsiteAuditAgent(context, claude)
    keyword_agent = KeywordResearchAgent(context, claude)
    competitor_agent = CompetitorAnalysisAgent(context, claude)
    gbp_agent = GBPOptimizationAgent(context, claude)
    content_agent = ContentAgent(context, claude)
    link_agent = LinkBuildingAgent(context, claude)
    reporting_agent = ReportingAgent(context, claude)

    results: dict[str, AgentResult] = {}

    # Phase 1: independent data gathering — run in parallel
    if await _stopped(redis, run_id):
        return {"run_id": run_id, "results": results}

    phase1 = await asyncio.gather(
        audit_agent.run(url=target_url),
        keyword_agent.run(business_type=business_type, location=location),
        competitor_agent.run(business_type=business_type, location=location),
        return_exceptions=True,
    )
    results["website_audit"] = phase1[0] if not isinstance(phase1[0], Exception) else AgentResult(False, "website_audit", error=str(phase1[0]))
    results["keyword_research"] = phase1[1] if not isinstance(phase1[1], Exception) else AgentResult(False, "keyword_research", error=str(phase1[1]))
    results["competitor_analysis"] = phase1[2] if not isinstance(phase1[2], Exception) else AgentResult(False, "competitor_analysis", error=str(phase1[2]))
    await _save_usage(db, project_id, run_id, "phase1_audit_keywords_competitors", claude)

    # Phase 2: uses Phase 1 context — run in parallel
    if await _stopped(redis, run_id):
        return {"run_id": run_id, "results": results}

    phase2 = await asyncio.gather(
        gbp_agent.run(),
        link_agent.run(),
        return_exceptions=True,
    )
    results["gbp_optimization"] = phase2[0] if not isinstance(phase2[0], Exception) else AgentResult(False, "gbp_optimization", error=str(phase2[0]))
    results["link_building"] = phase2[1] if not isinstance(phase2[1], Exception) else AgentResult(False, "link_building", error=str(phase2[1]))
    await _save_usage(db, project_id, run_id, "phase2_gbp_links", claude)

    # Phase 3: content needs keywords + audit context
    if await _stopped(redis, run_id):
        return {"run_id": run_id, "results": results}

    try:
        results["content"] = await content_agent.run()
    except Exception as e:
        results["content"] = AgentResult(False, "content", error=str(e))
    await _save_usage(db, project_id, run_id, "phase3_content", claude)

    # Phase 4: final report
    if await _stopped(redis, run_id):
        return {"run_id": run_id, "results": results}

    try:
        results["reporting"] = await reporting_agent.run(db=db)
    except Exception as e:
        results["reporting"] = AgentResult(False, "reporting", error=str(e))

    return {"run_id": run_id, "results": results}
