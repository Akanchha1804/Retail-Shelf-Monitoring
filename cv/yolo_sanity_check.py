"""
Phase 1 -- Environment sanity check.

Confirms ultralytics + opencv are installed correctly and that a
pretrained (COCO) YOLOv8n model can run inference on a shelf image.
"""

import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO


def run_sanity_check(image_path: str | None, output_path: str) -> None:
    model = YOLO("yolov8n.pt")

    if image_path is None:
        from ultralytics.utils import ASSETS
        image_path = str(ASSETS / "bus.jpg")
        print(f"No --image given, using bundled sample image: {image_path}")

    if not Path(image_path).exists():
        raise FileNotFoundError(f"Could not find image at: {image_path}")

    frame = cv2.imread(image_path)
    if frame is None:
        raise RuntimeError(f"OpenCV failed to read image at: {image_path}")

    print(f"Loaded image {image_path} with shape {frame.shape}")

    results = model(frame)
    result = results[0]
    boxes = result.boxes

    print(f"\nDetected {len(boxes)} object(s):")
    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        print(f"  - {cls_name:15s} conf={conf:.2f}  bbox={[round(v, 1) for v in xyxy]}")

    annotated = result.plot()
    cv2.imwrite(output_path, annotated)
    print(f"\nAnnotated image saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLOv8 environment sanity check")
    parser.add_argument("--image", type=str, default=None, help="Path to a shelf photo")
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(__file__).parent / "data" / "sanity_check_output.jpg"),
        help="Where to save the annotated output image.",
    )
    args = parser.parse_args()

    run_sanity_check(args.image, args.output)