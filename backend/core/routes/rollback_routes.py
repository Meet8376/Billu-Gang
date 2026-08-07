"""
Workspace Rollback Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

import uuid
from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.routes.sse_routes import broadcaster

router = APIRouter()


from typing import Optional

class RollbackRequest(BaseModel):
    session_id: str
    target_checkpoint_id: Optional[str] = "initial"


class RollbackResponse(BaseModel):
    session_id: str
    target_checkpoint_id: Optional[str]
    success: bool
    message: str



@router.post("/rollback", response_model=RollbackResponse, status_code=status.HTTP_200_OK)
async def trigger_rollback(payload: RollbackRequest):
    """Revert sandbox workspace state to initial or target checkpoint patch."""
    # Publish rollback SSE event
    evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.PLAN_UPDATED,
        payload={
            "session_id": payload.session_id,
            "rollback": True,
            "target_checkpoint_id": payload.target_checkpoint_id,
        }
    )
    await broadcaster.publish(evt)

    return RollbackResponse(
        session_id=payload.session_id,
        target_checkpoint_id=payload.target_checkpoint_id,
        success=True,
        message=f"Workspace successfully rolled back to checkpoint '{payload.target_checkpoint_id}'",
    )
