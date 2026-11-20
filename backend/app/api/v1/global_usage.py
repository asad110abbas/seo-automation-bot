from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.usage import UsageLog
from app.models.project import Project

router = APIRouter(tags=["usage"])


@router.get("/usage")
async def get_global_usage(db: AsyncSession = Depends(get_db)):
    """Aggregate usage across ALL projects."""
    logs_result = await db.execute(select(UsageLog).order_by(UsageLog.created_at.desc()))
    logs = logs_result.scalars().all()

    projects_result = await db.execute(select(Project))
    projects = {p.id: p.name for p in projects_result.scalars().all()}

    total_input = sum(l.input_tokens for l in logs)
    total_output = sum(l.output_tokens for l in logs)
    total_ai_cost = sum(l.input_cost_usd + l.output_cost_usd for l in logs)
    total_serp_calls = sum(l.serp_calls for l in logs)
    total_serp_cost = sum(l.serp_cost_usd for l in logs)

    by_project: dict = {}
    for l in logs:
        pid = l.project_id
        if pid not in by_project:
            by_project[pid] = {
                "project_id": pid,
                "project_name": projects.get(pid, "Unknown"),
                "input_tokens": 0,
                "output_tokens": 0,
                "ai_cost_usd": 0.0,
                "serp_calls": 0,
                "serp_cost_usd": 0.0,
                "total_cost_usd": 0.0,
            }
        by_project[pid]["input_tokens"] += l.input_tokens
        by_project[pid]["output_tokens"] += l.output_tokens
        cost = l.input_cost_usd + l.output_cost_usd
        by_project[pid]["ai_cost_usd"] = round(by_project[pid]["ai_cost_usd"] + cost, 6)
        by_project[pid]["serp_calls"] += l.serp_calls
        by_project[pid]["serp_cost_usd"] = round(by_project[pid]["serp_cost_usd"] + l.serp_cost_usd, 6)
        by_project[pid]["total_cost_usd"] = round(
            by_project[pid]["ai_cost_usd"] + by_project[pid]["serp_cost_usd"], 6
        )

    return {
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "total_ai_cost_usd": round(total_ai_cost, 6),
        "total_serp_calls": total_serp_calls,
        "total_serp_cost_usd": round(total_serp_cost, 6),
        "total_cost_usd": round(total_ai_cost + total_serp_cost, 6),
        "by_project": list(by_project.values()),
    }
