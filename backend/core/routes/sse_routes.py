"""
SSE Event Broadcaster Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


@router.get("/events")
async def event_stream(request: Request):
    """Broadcaster endpoint streaming live updates to Ink CLI using SSE."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield {
                "event": "ping",
                "data": '{"message": "heartbeat"}'
            }
            await asyncio.sleep(15)

    return EventSourceResponse(event_generator())
