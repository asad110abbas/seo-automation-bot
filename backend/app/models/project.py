import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str] = mapped_column(String(500), nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    audit_results: Mapped[list["AuditResult"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    keywords: Mapped[list["Keyword"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    generated_content: Mapped[list["GeneratedContent"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    gbp_suggestions: Mapped[list["GBPSuggestion"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    link_opportunities: Mapped[list["LinkOpportunity"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="project", cascade="all, delete-orphan")
