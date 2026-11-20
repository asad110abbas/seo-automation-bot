import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LinkOpportunity(Base):
    __tablename__ = "link_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    directory_name: Mapped[str] = mapped_column(String(255))
    directory_url: Mapped[str] = mapped_column(String(500))
    # business_directory | niche_directory | local_citation
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    relevance_score: Mapped[int] = mapped_column(Integer, default=0)
    estimated_da: Mapped[int] = mapped_column(Integer, default=0)
    # free | paid | manual
    submission_type: Mapped[str] = mapped_column(String(20), default="free")
    # not_submitted | submitted | approved | rejected
    submission_status: Mapped[str] = mapped_column(String(20), default="not_submitted")
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="link_opportunities")
