from app.core.task_queue import celery_app


@celery_app.task(name="tasks.run_keyword_research", bind=True, max_retries=3)
def run_keyword_research(self, project_id: str, business_type: str, location: str, run_id: str):
    import asyncio
    from app.agents.keyword_research.serp_client import fetch_keyword_data

    async def _run():
        return await fetch_keyword_data(f"{business_type} {location}", location)

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
