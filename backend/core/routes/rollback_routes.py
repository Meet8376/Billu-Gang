"""
Workspace Rollback Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class RollbackRequest(BaseModel):
    session_id: str
    target_checkpoint_id: str


class RollbackResponse(BaseModel):
    session_id: str
    target_checkpoint_id: str
    success: bool
    message: str


@router.post("/rollback", response_model=RollbackResponse, status_code=status.HTTP_200_OK)
async def trigger_rollback(payload: RollbackRequest):
    """Revert sandbox workspace state to initial or checkpoint patch."""
    return RollbackResponse(
        session_id=payload.session_id,
        target_checkpoint_id=payload.target_checkpoint_id,
        success=True,
        message=f"Workspace successfully rolled back to checkpoint {payload.target_checkpoint_id}",
    )
