import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.config import settings


async def generate_pdf(report_data: dict) -> str:
    """Render Jinja2 template and convert to PDF. Returns file path."""
    os.makedirs(settings.reports_dir, exist_ok=True)

    # Render HTML
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("monthly_report.html")
    html_content = template.render(**report_data, generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

    # Convert to PDF
    filename = f"seo_report_{report_data['project_id']}_{report_data['report_month']}.pdf"
    pdf_path = os.path.join(settings.reports_dir, filename)

    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(pdf_path)
    except ImportError:
        # WeasyPrint not available — save HTML instead
        pdf_path = pdf_path.replace(".pdf", ".html")
        with open(pdf_path, "w") as f:
            f.write(html_content)

    return pdf_path
