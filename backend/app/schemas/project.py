from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    website_url: str
    business_type: Optional[str] = None
    location: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    business_type: Optional[str] = None
    location: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    website_url: str
    business_type: Optional[str]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RunAnalysisRequest(BaseModel):
    max_pages: int = 30
