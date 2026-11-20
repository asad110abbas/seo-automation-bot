from app.core.task_queue import celery_app


@celery_app.task(name="tasks.generate_report", bind=True, max_retries=2)
def generate_report(self, project_id: str, run_id: str):
    import asyncio
    from app.agents.reporting.pdf_generator import generate_pdf

    async def _run():
        return await generate_pdf({"project_id": project_id, "run_id": run_id})

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
