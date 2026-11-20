import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.core.rate_limit import check_run_rate_limit, check_url_safety
from app.core.logging import logger
from app.models.project import Project
from app.models.agent_run import AgentRun
from app.models.usage import UsageLog
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, RunAnalysisRequest
from app.schemas.agent_response import FullRunResponse
from app.agents.orchestrator import run_full_analysis

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(
        id=str(uuid.uuid4()),
        name=data.name,
        website_url=str(data.website_url),
        business_type=data.business_type,
        location=data.location,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/run", response_model=FullRunResponse)
async def run_analysis(
    project_id: str,
    req: RunAnalysisRequest = RunAnalysisRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    """Trigger full multi-agent SEO analysis. Runs in the background."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.website_url:
        raise HTTPException(status_code=400, detail="Project must have a website_url")

    await check_url_safety(project.website_url)
    await check_run_rate_limit(project_id)
    logger.info("analysis_started", project_id=project_id, url=project.website_url)

    run_id = str(uuid.uuid4())

    # Log the run
    agent_run = AgentRun(
        id=run_id,
        project_id=project_id,
        agent_type="orchestrator",
        status="pending",
        started_at=datetime.utcnow(),
    )
    db.add(agent_run)
    await db.commit()

    background_tasks.add_task(
        _run_analysis_bg,
        project_id,
        project.website_url,
        project.business_type or "business",
        project.location or "Pakistan",
        run_id,
    )

    return FullRunResponse(
        run_id=run_id,
        project_id=project_id,
        status="started",
        message="Full SEO analysis started. Connect to WebSocket for real-time progress.",
    )


@router.post("/{project_id}/runs/{run_id}/stop")
async def stop_analysis(project_id: str, run_id: str, db: AsyncSession = Depends(get_db)):
    """Signal the running analysis to stop after the current phase."""
    run = await db.get(AgentRun, run_id)
    if not run or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status not in ("pending", "running"):
        raise HTTPException(status_code=400, detail=f"Run is already {run.status}")

    from app.core.redis_client import get_redis
    redis = await get_redis()
    await redis.set(f"run:{run_id}:stop", "1", ex=3600)

    run.status = "cancelled"
    run.completed_at = datetime.utcnow()
    await db.commit()
    return {"message": "Stop signal sent. Analysis will halt after current phase."}


@router.get("/{project_id}/usage")
async def get_usage(project_id: str, db: AsyncSession = Depends(get_db)):
    """Return aggregated token + cost usage for this project."""
    await db.get(Project, project_id)
    result = await db.execute(
        select(UsageLog).where(UsageLog.project_id == project_id).order_by(UsageLog.created_at.desc())
    )
    logs = result.scalars().all()

    total_input_tokens = sum(l.input_tokens for l in logs)
    total_output_tokens = sum(l.output_tokens for l in logs)
    total_ai_cost = sum(l.input_cost_usd + l.output_cost_usd for l in logs)
    total_serp_calls = sum(l.serp_calls for l in logs)
    total_serp_cost = sum(l.serp_cost_usd for l in logs)

    by_agent: dict = {}
    for l in logs:
        if l.agent_type not in by_agent:
            by_agent[l.agent_type] = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "calls": 0}
        by_agent[l.agent_type]["input_tokens"] += l.input_tokens
        by_agent[l.agent_type]["output_tokens"] += l.output_tokens
        by_agent[l.agent_type]["cost_usd"] += round(l.input_cost_usd + l.output_cost_usd, 6)
        by_agent[l.agent_type]["calls"] += 1

    return {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_ai_cost_usd": round(total_ai_cost, 6),
        "total_serp_calls": total_serp_calls,
        "total_serp_cost_usd": round(total_serp_cost, 6),
        "total_cost_usd": round(total_ai_cost + total_serp_cost, 6),
        "by_agent": by_agent,
        "logs": [
            {
                "agent": l.agent_type,
                "model": l.model,
                "input_tokens": l.input_tokens,
                "output_tokens": l.output_tokens,
                "ai_cost_usd": round(l.input_cost_usd + l.output_cost_usd, 6),
                "serp_calls": l.serp_calls,
                "serp_cost_usd": round(l.serp_cost_usd, 6),
                "timestamp": l.created_at.isoformat(),
            }
            for l in logs
        ],
    }


async def _run_analysis_bg(project_id, url, business_type, location, run_id):
    """Background task that runs the full analysis and persists results to DB."""
    from app.core.database import AsyncSessionLocal
    from app.core.llm_client import get_claude
    from app.models.usage import UsageLog
    async with AsyncSessionLocal() as db:
        try:
            run = await db.get(AgentRun, run_id)
            if run:
                run.status = "running"
                await db.commit()
            output = await run_full_analysis(
                project_id=project_id,
                target_url=url,
                business_type=business_type,
                location=location,
                db=db,
                run_id=run_id,
            )
            await _persist_results(db, project_id, run_id, output.get("results", {}))
            run = await db.get(AgentRun, run_id)
            if run and run.status != "cancelled":
                run.status = "completed"
                run.completed_at = datetime.utcnow()
                await db.commit()
        except Exception as e:
            import traceback
            logger.error("analysis_bg_error", project_id=project_id, run_id=run_id, error=str(e), traceback=traceback.format_exc())
            run = await db.get(AgentRun, run_id)
            if run:
                run.status = "failed"
                run.error_message = str(e)
                await db.commit()
        finally:
            # Save any remaining unsaved tokens (e.g., if stopped mid-phase)
            claude = get_claude()
            if claude.usage.input_tokens > 0 or claude.usage.output_tokens > 0:
                db.add(UsageLog(
                    project_id=project_id,
                    run_id=run_id,
                    agent_type="partial_run",
                    provider="groq",
                    model=claude.model,
                    input_tokens=claude.usage.input_tokens,
                    output_tokens=claude.usage.output_tokens,
                    input_cost_usd=claude.usage.input_cost,
                    output_cost_usd=claude.usage.output_cost,
                ))
                await db.commit()
                claude.reset_usage()


async def _persist_results(db: AsyncSession, project_id: str, run_id: str, results: dict):
    """Save all agent results from Redis-backed AgentResult objects into PostgreSQL."""
    from app.models.audit import AuditResult
    from app.models.keyword import Keyword
    from app.models.competitor import Competitor
    from app.models.gbp import GBPSuggestion
    from app.models.content import GeneratedContent
    from app.models.link import LinkOpportunity
    from sqlalchemy import delete

    logger.info("persist_results_start", project_id=project_id, run_id=run_id, keys=list(results.keys()))
    for key, val in results.items():
        if hasattr(val, 'success'):
            logger.info("agent_result_summary", agent=key, success=val.success, error=val.error, data_keys=list(val.data.keys()) if val.data else [])
        else:
            logger.info("agent_result_raw", agent=key, type=type(val).__name__)

    # ── Website Audit ──────────────────────────────────────────────
    try:
        audit_result = results.get("website_audit")
        if audit_result and audit_result.success:
            d = audit_result.data
            db.add(AuditResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                run_id=run_id,
                seo_score=d.get("seo_score", 0),
                pages_crawled=d.get("pages_crawled", 0),
                issues=d.get("issues", {}),
                recommendations=d.get("recommendations", []),
                raw_data={},
            ))
            await db.flush()
            logger.info("persisted_audit", project_id=project_id, score=d.get("seo_score"))
        else:
            logger.warning("skip_audit", reason="no result or success=False", error=getattr(audit_result, 'error', None))
    except Exception as e:
        logger.error("persist_audit_error", error=str(e))

    # ── Keywords ───────────────────────────────────────────────────
    try:
        kw_result = results.get("keyword_research")
        if kw_result and kw_result.success:
            await db.execute(delete(Keyword).where(Keyword.project_id == project_id))
            d = kw_result.data
            cluster_map: dict[str, str] = {}
            for cluster in d.get("clusters", []):
                for kw in cluster.get("keywords", []):
                    cluster_map[kw] = cluster.get("cluster_name", "")
            quick_win_set = {k.get("keyword") for k in d.get("quick_wins", [])}
            saved_kw = 0
            for kw in d.get("all_keywords", []):
                keyword_str = kw.get("keyword", "")
                if not keyword_str:
                    continue
                db.add(Keyword(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    keyword=keyword_str,
                    search_volume=kw.get("search_volume"),
                    difficulty=kw.get("difficulty"),
                    keyword_type=kw.get("type"),
                    cluster_name=cluster_map.get(keyword_str),
                    is_quick_win=keyword_str in quick_win_set,
                    source=kw.get("source", "mock"),
                ))
                saved_kw += 1
            await db.flush()
            logger.info("persisted_keywords", project_id=project_id, count=saved_kw)
        else:
            logger.warning("skip_keywords", reason="no result or success=False", error=getattr(kw_result, 'error', None))
    except Exception as e:
        logger.error("persist_keywords_error", error=str(e))

    # ── Competitors ────────────────────────────────────────────────
    try:
        comp_result = results.get("competitor_analysis")
        if comp_result and comp_result.success:
            await db.execute(delete(Competitor).where(Competitor.project_id == project_id))
            d = comp_result.data
            content_gaps = d.get("content_gaps", [])
            saved_comp = 0
            for comp in d.get("competitors", []):
                db.add(Competitor(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    competitor_url=comp.get("url", ""),
                    competitor_name=comp.get("title"),
                    rank_position=comp.get("rank"),
                    top_keywords=comp.get("top_keywords", []),
                    content_gaps=content_gaps,
                ))
                saved_comp += 1
            await db.flush()
            logger.info("persisted_competitors", project_id=project_id, count=saved_comp)
        else:
            logger.warning("skip_competitors", reason="no result or success=False", error=getattr(comp_result, 'error', None))
    except Exception as e:
        logger.error("persist_competitors_error", error=str(e))

    # ── GBP Suggestions ────────────────────────────────────────────
    try:
        gbp_result = results.get("gbp_optimization")
        if gbp_result and gbp_result.success:
            await db.execute(delete(GBPSuggestion).where(GBPSuggestion.project_id == project_id))
            saved_gbp = 0
            for sug in gbp_result.data.get("suggestions", []):
                db.add(GBPSuggestion(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    category=sug.get("category", "general"),
                    suggestion=sug.get("suggestion", ""),
                    priority=sug.get("priority", "medium"),
                    status="pending",
                ))
                saved_gbp += 1
            await db.flush()
            logger.info("persisted_gbp", project_id=project_id, count=saved_gbp)
        else:
            logger.warning("skip_gbp", reason="no result or success=False", error=getattr(gbp_result, 'error', None))
    except Exception as e:
        logger.error("persist_gbp_error", error=str(e))

    # ── Generated Content ──────────────────────────────────────────
    try:
        content_result = results.get("content")
        if content_result and content_result.success:
            await db.execute(delete(GeneratedContent).where(GeneratedContent.project_id == project_id))
            saved_content = 0
            for piece in content_result.data.get("generated_content", []):
                db.add(GeneratedContent(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    content_type=piece.get("content_type", "blog_post"),
                    title=piece.get("title", "Untitled"),
                    content=piece.get("content", ""),
                    target_keyword=piece.get("target_keyword"),
                    word_count=piece.get("word_count", 0),
                    seo_score=piece.get("seo_score", 0),
                    status="draft",
                ))
                saved_content += 1
            await db.flush()
            logger.info("persisted_content", project_id=project_id, count=saved_content)
        else:
            logger.warning("skip_content", reason="no result or success=False", error=getattr(content_result, 'error', None))
    except Exception as e:
        logger.error("persist_content_error", error=str(e))

    # ── Link Opportunities ─────────────────────────────────────────
    try:
        link_result = results.get("link_building")
        if link_result and link_result.success:
            await db.execute(delete(LinkOpportunity).where(LinkOpportunity.project_id == project_id))
            saved_links = 0
            for opp in link_result.data.get("opportunities", []):
                db.add(LinkOpportunity(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    directory_name=opp.get("directory_name", ""),
                    directory_url=opp.get("url", opp.get("directory_url", "")),
                    category=opp.get("category"),
                    relevance_score=int(opp.get("relevance_score", 0)),
                    estimated_da=int(opp.get("estimated_da", 0)),
                    submission_type=opp.get("submission_type", "free"),
                    submission_status="not_submitted",
                ))
                saved_links += 1
            await db.flush()
            logger.info("persisted_links", project_id=project_id, count=saved_links)
        else:
            logger.warning("skip_links", reason="no result or success=False", error=getattr(link_result, 'error', None))
    except Exception as e:
        logger.error("persist_links_error", error=str(e))

    await db.commit()
    logger.info("persist_results_done", project_id=project_id)
