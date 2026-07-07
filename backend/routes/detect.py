"""
Phase 8 -- Synchronous detection endpoint for the live camera view.

Unlike POST /detect (which runs in the background and writes to the DB),
this endpoint runs YOLO immediately and returns the bounding boxes right
away -- needed so the live view page can draw boxes on screen in real time.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File
from ultralytics import YOLO

sys.path.append(str(Path(__file__).parent.parent.parent / "cv"))
from shelf_zones import get_zone_for_box  # noqa: E402

router = APIRouter()

WEIGHTS_PATH = Path(__file__).parent.parent.parent / "cv" / "weights" / "best.pt"
_model = None


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(str(WEIGHTS_PATH))
    return _model


@router.post("/detect_live")
async def detect_live(file: UploadFile = File(...)):
    """
    Runs detection on one frame and returns bounding boxes + zone counts
    immediately -- used by the live camera view page, not for DB writes.
    """
    image_bytes = await file.read()
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Could not decode image"}

    model = _get_model()
    results = model(frame)
    boxes = results[0].boxes

    height, width = frame.shape[:2]
    detections = []
    zone_counts: dict[str, int] = {}

    for box in boxes:
        xyxy = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        zone = get_zone_for_box(tuple(xyxy), frame_shape=(height, width))

        detections.append({"bbox": xyxy, "conf": conf, "zone": zone})
        if zone:
            zone_counts[zone] = zone_counts.get(zone, 0) + 1

    return {
        "detections": detections,
        "zone_counts": zone_counts,
        "frame_width": width,
        "frame_height": height,
    }