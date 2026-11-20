import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class GBPSuggestion(Base):
    __tablename__ = "gbp_suggestions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    # categories | photos | reviews | posts | description | hours
    category: Mapped[str] = mapped_column(String(100))
    suggestion: Mapped[str] = mapped_column(Text)
    # high | medium | low
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    # pending | implemented
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="gbp_suggestions")
