"""
Phase 6 -- FastAPI app entrypoint.

Endpoints:
    POST /detect     -- send in a frame, detection runs as a background
                         task so it never blocks the request
    GET  /inventory   -- get the latest stock numbers
    GET  /alerts      -- get the alert history

Run with:
    uvicorn main:app --reload
"""

import uuid

from fastapi import BackgroundTasks, Depends, FastAPI, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Inventory, Alert
from schemas import InventoryOut, AlertOut, DetectResponse
from worker import run_detection_task
from routes.detect import router as detect_live_router

app = FastAPI(title="Retail Shelf Monitoring API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/detect", response_model=DetectResponse)
async def detect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Accepts a frame (image), immediately returns a task_id, and runs
    the actual YOLO detection + DB write in the background -- so slow
    inference never blocks this request.
    """
    task_id = str(uuid.uuid4())
    image_bytes = await file.read()

    background_tasks.add_task(run_detection_task, task_id, image_bytes)

    return DetectResponse(message="Detection started", task_id=task_id)


@app.get("/inventory", response_model=list[InventoryOut])
def get_inventory(limit: int = 50, db: Session = Depends(get_db)):
    """Returns the most recent inventory readings, newest first."""
    readings = (
        db.query(Inventory)
        .order_by(Inventory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return readings

app.include_router(detect_live_router)

@app.get("/alerts", response_model=list[AlertOut])
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    """Returns the most recent alerts, newest first."""
    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc())
        .limit(limit)
        .all()
    )
    return alerts