import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    competitor_url: Mapped[str] = mapped_column(String(500))
    competitor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rank_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_keywords: Mapped[int] = mapped_column(Integer, default=0)
    top_keywords: Mapped[list] = mapped_column(JSON, default=list)
    content_gaps: Mapped[list] = mapped_column(JSON, default=list)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="competitors")
