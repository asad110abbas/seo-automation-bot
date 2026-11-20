from app.core.task_queue import celery_app


@celery_app.task(name="tasks.run_website_audit", bind=True, max_retries=3)
def run_website_audit(self, project_id: str, url: str, run_id: str):
    """Celery task for running website audit asynchronously."""
    import asyncio
    from app.agents.website_audit.crawler import crawl_website

    async def _run():
        return await crawl_website(url, max_pages=30)

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
