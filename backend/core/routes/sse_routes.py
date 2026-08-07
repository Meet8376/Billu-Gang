"""
SSE Event Broadcaster Route Handlers & Queue Manager.
Member 2 — Backend Core & Model Adapter Lead
"""

import asyncio
import json
from typing import List
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from backend.core.schemas.sse_events import SSEEvent, EventType

router = APIRouter()


class SSEBroadcaster:
    """PubSub Event Broadcaster using asyncio Queues for live CLI streaming."""

    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def publish(self, event: SSEEvent):
        """Publish an SSEEvent to all active streaming subscribers."""
        event_dict = event.model_dump(mode="json")
        for queue in self.subscribers:
            await queue.put(event_dict)


broadcaster = SSEBroadcaster()


@router.get("/events")
async def event_stream(request: Request):
    """Broadcaster endpoint streaming live updates to Ink CLI using SSE."""
    queue = broadcaster.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Wait for next published event with timeout for heartbeat ping
                    event_data = await asyncio.wait_for(queue.get(), timeout=10.0)
                    yield {
                        "event": event_data.get("event_type", "message"),
                        "data": json.dumps(event_data)
                    }
                except asyncio.TimeoutError:
                    # Send heartbeat ping if no event published within timeout
                    yield {
                        "event": "ping",
                        "data": json.dumps({"message": "heartbeat"})
                    }
        finally:
            broadcaster.unsubscribe(queue)

    return EventSourceResponse(event_generator())
