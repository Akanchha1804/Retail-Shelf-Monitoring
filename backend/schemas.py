"""
Phase 6 -- Pydantic request/response schemas for the FastAPI backend.
"""

from datetime import datetime

from pydantic import BaseModel


class InventoryOut(BaseModel):
    id: int
    timestamp: datetime
    product_id: int
    quantity: int

    class Config:
        from_attributes = True  # lets Pydantic read SQLAlchemy model objects directly


class AlertOut(BaseModel):
    id: int
    alert_type: str
    product_id: int
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True


class DetectResponse(BaseModel):
    """Returned immediately by POST /detect -- detection runs in the background."""
    message: str
    task_id: str