"""
Session REST API Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from backend.core.schemas.session import SessionCreate, SessionResponse, SessionStatus

router = APIRouter()

# In-memory session state placeholder for stub
_sessions: dict[str, SessionResponse] = {}


@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate):
    """Initialize a new coding session."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    session_resp = SessionResponse(
        session_id=session_id,
        workspace_path=payload.workspace_path,
        goal_prompt=payload.goal_prompt,
        status=SessionStatus.IDLE,
        created_at=now,
        updated_at=now,
        total_tokens_used=0,
        total_cost_usd=0.0,
    )
    _sessions[session_id] = session_resp
    return session_resp


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Retrieve session details by ID."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return _sessions[session_id]


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session(session_id: str):
    """Close and finalize an active session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    del _sessions[session_id]
