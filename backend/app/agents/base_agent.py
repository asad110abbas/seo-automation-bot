import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import redis.asyncio as aioredis

from app.core.llm_client import ClaudeClient
from app.config import settings


@dataclass
class AgentContext:
    """Shared state for a single analysis run, backed by Redis."""
    run_id: str
    project_id: str
    target_url: str
    business_type: str
    location: str
    data: dict = field(default_factory=dict)
    _redis: Any = field(default=None, repr=False)

    async def set(self, key: str, value: Any):
        self.data[key] = value
        if self._redis:
            await self._redis.hset(f"run:{self.run_id}:ctx", key, json.dumps(value))

    async def get(self, key: str, default=None) -> Any:
        if key in self.data:
            return self.data[key]
        if self._redis:
            raw = await self._redis.hget(f"run:{self.run_id}:ctx", key)
            if raw:
                return json.loads(raw)
        return default

    async def publish_progress(self, agent_name: str, message: str, pct: int):
        if self._redis:
            payload = json.dumps({
                "agent": agent_name,
                "message": message,
                "progress": pct,
                "timestamp": datetime.utcnow().isoformat(),
            })
            await self._redis.publish(f"run:{self.run_id}:progress", payload)


@dataclass
class AgentResult:
    success: bool
    agent_type: str
    data: dict = field(default_factory=dict)
    error: str | None = None


class BaseAgent(ABC):
    agent_type: str = "base"

    def __init__(self, context: AgentContext, claude: ClaudeClient):
        self.context = context
        self.claude = claude

    @abstractmethod
    async def run(self, **kwargs) -> AgentResult:
        pass

    async def progress(self, message: str, pct: int):
        await self.context.publish_progress(self.agent_type, message, pct)
