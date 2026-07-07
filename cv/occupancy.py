"""
Phase 4 -- Counting + occupancy logic.

Takes YOLO detections per frame, aggregates them into shelf-area counts,
calculates occupancy % against a stored max_capacity, and averages counts
over the last 10-20 frames before flagging low stock -- so a single noisy
frame doesn't trigger a false alarm.
"""

from collections import deque

from shelf_zones import SHELF_ZONES, MAX_CAPACITY, get_zone_for_box

# How many recent frames to average over before trusting a count.
# Per the doc: 10-20 frames smooths out detection noise (e.g. 20, 18, 22
# for the same shelf, just from momentary misdetection).
ROLLING_WINDOW_SIZE = 15

# Below this % occupancy, a shelf is considered "low stock"
LOW_STOCK_THRESHOLD_PCT = 25.0


class ShelfOccupancyTracker:
    """
    Keeps a rolling history of detection counts per shelf zone, and
    computes smoothed occupancy % + low-stock flags.
    """

    def __init__(self, window_size: int = ROLLING_WINDOW_SIZE):
        self.window_size = window_size
        # One rolling deque of raw counts per shelf zone
        self._history = {
            zone_name: deque(maxlen=window_size) for zone_name in SHELF_ZONES
        }

    def process_frame(self, detections: list[dict], frame_shape: tuple[int, int] | None = None) -> dict:
        """
        detections: list of dicts like {"bbox": (x1, y1, x2, y2), "conf": 0.87}
                    (this is exactly what yolo_sanity_check.py / a live
                    inference loop would produce per frame)

        Returns a dict per shelf zone with:
            raw_count       -- count found in THIS frame only
            smoothed_count  -- rolling average over the last N frames
            occupancy_pct   -- smoothed_count / max_capacity * 100
            low_stock       -- True if occupancy_pct < threshold
        """
        # Count raw detections per zone for this single frame
        raw_counts = {zone_name: 0 for zone_name in SHELF_ZONES}
        for det in detections:
            zone = get_zone_for_box(det["bbox"], frame_shape=frame_shape)
            if zone is not None:
                raw_counts[zone] += 1

        # Push this frame's counts into the rolling history
        for zone_name, count in raw_counts.items():
            self._history[zone_name].append(count)

        # Build the result per zone
        results = {}
        for zone_name in SHELF_ZONES:
            history = self._history[zone_name]
            smoothed_count = sum(history) / len(history) if history else 0

            max_cap = MAX_CAPACITY[zone_name]
            occupancy_pct = (smoothed_count / max_cap) * 100 if max_cap > 0 else 0

            results[zone_name] = {
                "raw_count": raw_counts[zone_name],
                "smoothed_count": round(smoothed_count, 1),
                "occupancy_pct": round(occupancy_pct, 1),
                "low_stock": occupancy_pct < LOW_STOCK_THRESHOLD_PCT,
                "frames_in_window": len(history),
            }

        return results


if __name__ == "__main__":
    # Quick manual test with fake detections, using the REAL rolling
    # window size (15 frames, matching the doc's 10-20 frame recommendation)
    tracker = ShelfOccupancyTracker(window_size=ROLLING_WINDOW_SIZE)

    # Simulate 20 frames for Shelf A: starts full (~20), then gradually
    # drops off to simulate stock being sold, with some frame-to-frame
    # noise mixed in (detection wobble)
    fake_counts = [20, 19, 20, 18, 17, 16, 15, 14, 12, 10, 9, 8, 6, 5, 4, 3, 5, 3, 2, 1]

    for i, count in enumerate(fake_counts, start=1):
        frame_detections = [{"bbox": (100, 50, 150, 100), "conf": 0.8}] * count
        results = tracker.process_frame(frame_detections)
        shelf_a = results["Shelf A"]
        print(
            f"Frame {i:2d}: raw={shelf_a['raw_count']:2d}  "
            f"smoothed={shelf_a['smoothed_count']:5.1f}  "
            f"occupancy={shelf_a['occupancy_pct']:5.1f}%  "
            f"low_stock={shelf_a['low_stock']}  "
            f"(window={shelf_a['frames_in_window']})"
        )

