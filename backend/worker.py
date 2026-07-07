"""
Phase 6 -- Background detection worker.

This runs OUTSIDE the request/response cycle (called via FastAPI's
BackgroundTasks from main.py's /detect endpoint), so slow YOLO inference
never blocks the API from responding quickly.

Flow:
    1. Decode the uploaded frame
    2. Run YOLO detection
    3. Aggregate into shelf zone counts + occupancy % (via cv/occupancy.py)
    4. Write a new Inventory row per shelf zone
    5. Check thresholds and write an Alert row if needed
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

# Let this file import from the cv/ folder (shelf_zones.py, occupancy.py)
sys.path.append(str(Path(__file__).parent.parent / "cv"))
from occupancy import ShelfOccupancyTracker  # noqa: E402
from shelf_zones import MAX_CAPACITY  # noqa: E402

from database import SessionLocal
from models import Product, Inventory, Alert

WEIGHTS_PATH = Path(__file__).parent.parent / "cv" / "weights" / "best.pt"

# One shared tracker across requests, so the rolling window persists
# between frames (matches how a real live camera loop would behave)
_model = None

_tracker = ShelfOccupancyTracker()


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(str(WEIGHTS_PATH))
    return _model


def run_detection_task(task_id: str, image_bytes: bytes) -> None:
    """
    The actual background job. Runs detection on one frame, updates
    occupancy tracking, and writes results to the database.
    """
    print(f"[{task_id}] Starting detection...")

    # Decode the uploaded image bytes into an OpenCV frame
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if frame is None:
        print(f"[{task_id}] ERROR: could not decode image")
        return

    model = _get_model()
    results = model(frame)
    boxes = results[0].boxes

    detections = [{"bbox": tuple(box.xyxy[0].tolist()), "conf": float(box.conf[0])} for box in boxes]

    zone_results = _tracker.process_frame(detections, frame_shape=frame.shape[:2])

    db = SessionLocal()
    try:
        for zone_name, info in zone_results.items():
            product = db.query(Product).filter(Product.product_name == zone_name).first()
            if product is None:
                print(f"[{task_id}] WARNING: no product row for '{zone_name}', skipping")
                continue

            # Write the smoothed count as an inventory reading
            reading = Inventory(product_id=product.product_id, quantity=int(info["smoothed_count"]))
            db.add(reading)

            # Fire an alert if this zone is flagged low stock
            if info["low_stock"]:
                alert = Alert(
                    product_id=product.product_id,
                    alert_type="low_stock",
                    status="active",
                )
                db.add(alert)
                print(f"[{task_id}] ALERT: {zone_name} is low stock ({info['occupancy_pct']}%)")

        db.commit()
        print(f"[{task_id}] Detection complete, DB updated.")
    finally:
        db.close()