"""
Endpoints for reading agent results per project.
All return latest available data from the database.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.project import Project
from app.models.audit import AuditResult
from app.models.keyword import Keyword
from app.models.competitor import Competitor
from app.models.content import GeneratedContent
from app.models.gbp import GBPSuggestion
from app.models.link import LinkOpportunity
from app.models.report import Report
from app.models.agent_run import AgentRun

router = APIRouter(tags=["results"])


async def _check_project(project_id: str, db: AsyncSession):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ── Audit ─────────────────────────────────────────────────
@router.get("/projects/{project_id}/audit")
async def get_audit(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(
        select(AuditResult).where(AuditResult.project_id == project_id).order_by(desc(AuditResult.crawled_at)).limit(1)
    )
    audit = result.scalar_one_or_none()
    if not audit:
        return {"message": "No audit results yet. Run an analysis first."}
    return {"seo_score": audit.seo_score, "pages_crawled": audit.pages_crawled, "issues": audit.issues, "recommendations": audit.recommendations}


# ── Keywords ──────────────────────────────────────────────
@router.get("/projects/{project_id}/keywords")
async def get_keywords(project_id: str, keyword_type: str = None, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    q = select(Keyword).where(Keyword.project_id == project_id)
    if keyword_type:
        q = q.where(Keyword.keyword_type == keyword_type)
    result = await db.execute(q.order_by(desc(Keyword.search_volume)))
    kws = result.scalars().all()
    return [{"id": k.id, "keyword": k.keyword, "search_volume": k.search_volume, "difficulty": k.difficulty, "type": k.keyword_type, "cluster": k.cluster_name, "is_quick_win": k.is_quick_win} for k in kws]


# ── Competitors ───────────────────────────────────────────
@router.get("/projects/{project_id}/competitors")
async def get_competitors(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(select(Competitor).where(Competitor.project_id == project_id).order_by(Competitor.rank_position))
    return result.scalars().all()


@router.get("/projects/{project_id}/competitors/gaps")
async def get_content_gaps(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(select(Competitor).where(Competitor.project_id == project_id))
    competitors = result.scalars().all()
    all_gaps = []
    for c in competitors:
        all_gaps.extend(c.content_gaps or [])
    return {"content_gaps": all_gaps}


# ── GBP ───────────────────────────────────────────────────
@router.get("/projects/{project_id}/gbp/suggestions")
async def get_gbp_suggestions(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(
        select(GBPSuggestion).where(GBPSuggestion.project_id == project_id).order_by(GBPSuggestion.priority)
    )
    return result.scalars().all()


@router.put("/projects/{project_id}/gbp/{suggestion_id}/status")
async def update_gbp_status(project_id: str, suggestion_id: str, status: str, db: AsyncSession = Depends(get_db)):
    sug = await db.get(GBPSuggestion, suggestion_id)
    if not sug or sug.project_id != project_id:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    sug.status = status
    await db.commit()
    return {"id": sug.id, "status": sug.status}


# ── Content ───────────────────────────────────────────────
@router.get("/projects/{project_id}/content")
async def get_content(project_id: str, status: str = None, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    q = select(GeneratedContent).where(GeneratedContent.project_id == project_id)
    if status:
        q = q.where(GeneratedContent.status == status)
    result = await db.execute(q.order_by(desc(GeneratedContent.created_at)))
    items = result.scalars().all()
    return [{"id": c.id, "title": c.title, "content_type": c.content_type, "target_keyword": c.target_keyword, "word_count": c.word_count, "seo_score": c.seo_score, "status": c.status} for c in items]


@router.get("/projects/{project_id}/content/{content_id}")
async def get_content_detail(project_id: str, content_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(GeneratedContent, content_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Content not found")
    return {
        "id": item.id,
        "project_id": item.project_id,
        "content_type": item.content_type,
        "title": item.title,
        "content": item.content,
        "target_keyword": item.target_keyword,
        "word_count": item.word_count,
        "seo_score": item.seo_score,
        "status": item.status,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


# ── Links ─────────────────────────────────────────────────
@router.get("/projects/{project_id}/links")
async def get_links(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(
        select(LinkOpportunity).where(LinkOpportunity.project_id == project_id).order_by(desc(LinkOpportunity.relevance_score))
    )
    return result.scalars().all()


# ── Reports ───────────────────────────────────────────────
@router.get("/projects/{project_id}/reports")
async def list_reports(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(
        select(Report).where(Report.project_id == project_id).order_by(desc(Report.generated_at))
    )
    return result.scalars().all()


@router.get("/projects/{project_id}/reports/{report_id}/pdf")
async def download_report(project_id: str, report_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse
    import os
    report = await db.get(Report, report_id)
    if not report or report.project_id != project_id:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.pdf_path or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=os.path.basename(report.pdf_path))


# ── Agent Runs ────────────────────────────────────────────
@router.get("/projects/{project_id}/runs")
async def list_runs(project_id: str, db: AsyncSession = Depends(get_db)):
    await _check_project(project_id, db)
    result = await db.execute(
        select(AgentRun).where(AgentRun.project_id == project_id).order_by(desc(AgentRun.created_at)).limit(20)
    )
    return result.scalars().all()


@router.get("/projects/{project_id}/runs/{run_id}")
async def get_run(project_id: str, run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(AgentRun, run_id)
    if not run or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
