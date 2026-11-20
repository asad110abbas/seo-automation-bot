import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    report_month: Mapped[date] = mapped_column(Date)
    # monthly | quarterly
    report_type: Mapped[str] = mapped_column(String(50), default="monthly")
    # local file path or S3 URL
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # snapshot of key metrics at report time
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="reports")
