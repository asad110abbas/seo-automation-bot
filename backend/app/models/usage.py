import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(20), default="groq")
    model: Mapped[str] = mapped_column(String(100))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    # Cost in USD
    input_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    output_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    serp_calls: Mapped[int] = mapped_column(Integer, default=0)
    serp_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="usage_logs")
