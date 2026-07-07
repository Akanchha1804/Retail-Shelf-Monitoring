"""
Phase 4 -- Fixed shelf zone definitions.

Per the project doc: mark out rough shelf areas (Shelf A/B/C) using
fixed coordinates in the frame. Zones are defined as FRACTIONS of the
frame (0.0 to 1.0), then converted to actual pixels based on whatever
frame size comes in -- this way it works regardless of your camera's
resolution or the input image size.
"""

# Each zone is a fraction of the frame: (x1_frac, y1_frac, x2_frac, y2_frac)
SHELF_ZONES_FRACTIONAL = {
    "Shelf A": (0.0, 0.0, 1.0, 0.33),     # top third
    "Shelf B": (0.0, 0.33, 1.0, 0.66),    # middle third
    "Shelf C": (0.0, 0.66, 1.0, 1.0),     # bottom third
}

MAX_CAPACITY = {
    "Shelf A": 20,
    "Shelf B": 20,
    "Shelf C": 20,
}

# Kept for backward compatibility with any code expecting pixel zones
# at a default 640x640 -- prefer get_zone_for_box() with frame_shape instead.
SHELF_ZONES = {
    name: (fx1 * 640, fy1 * 640, fx2 * 640, fy2 * 640)
    for name, (fx1, fy1, fx2, fy2) in SHELF_ZONES_FRACTIONAL.items()
}


def get_zone_for_box(
    box_xyxy: tuple[float, float, float, float],
    frame_shape: tuple[int, int] | None = None,
) -> str | None:
    """
    Given a detection's bounding box (x1, y1, x2, y2) and the actual
    frame's (height, width), figure out which shelf zone its center
    point falls into.

    If frame_shape is not given, falls back to assuming a 640x640 frame
    (kept for backward compatibility with existing tests).
    """
    x1, y1, x2, y2 = box_xyxy
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    if frame_shape is not None:
        height, width = frame_shape
    else:
        height, width = 640, 640

    for zone_name, (fx1, fy1, fx2, fy2) in SHELF_ZONES_FRACTIONAL.items():
        zx1, zy1, zx2, zy2 = fx1 * width, fy1 * height, fx2 * width, fy2 * height
        if zx1 <= center_x <= zx2 and zy1 <= center_y <= zy2:
            return zone_name

    return None