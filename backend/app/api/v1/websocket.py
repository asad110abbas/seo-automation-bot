import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.redis_client import get_redis

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/projects/{project_id}/runs/{run_id}")
async def agent_progress_ws(websocket: WebSocket, project_id: str, run_id: str):
    """
    WebSocket endpoint for real-time agent progress.
    Subscribes to Redis pub/sub channel for the given run.
    """
    await websocket.accept()
    redis = await get_redis()
    pubsub = redis.pubsub()
    channel = f"run:{run_id}:progress"

    await pubsub.subscribe(channel)
    try:
        while True:
            message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=30)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
            else:
                # Send heartbeat so client knows connection is alive
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
