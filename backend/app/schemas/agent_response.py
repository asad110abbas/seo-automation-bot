from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    agent_type: str
    status: str
    progress: int
    message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class FullRunResponse(BaseModel):
    run_id: str
    project_id: str
    status: str
    message: str
