"""
Phase 3 -- Run `yolo val` on the fine-tuned model to get real
precision, recall, and mAP@50 numbers.

Per the project doc (Section 9): use these real numbers in your report,
don't leave placeholder values. 60-70% mAP@50 is a perfectly fine,
honest number for a student project.

Usage:
    python cv/validate.py
    python cv/validate.py --weights cv/weights/best.pt
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

DATASET_YAML = Path(__file__).parent / "dataset.yaml"
DEFAULT_WEIGHTS = Path(__file__).parent / "weights" / "best.pt"


def validate(weights_path: str) -> None:
    if not Path(weights_path).exists():
        raise FileNotFoundError(
            f"Could not find weights at: {weights_path}\n"
            "Run cv/train.py first, then copy runs/detect/shelf_product_detector/weights/best.pt "
            "into cv/weights/best.pt"
        )

    model = YOLO(weights_path)

    metrics = model.val(data=str(DATASET_YAML))

    print("\n=== Validation Results ===")
    print(f"Precision:  {metrics.box.mp:.4f}")
    print(f"Recall:     {metrics.box.mr:.4f}")
    print(f"mAP@50:     {metrics.box.map50:.4f}")
    print(f"mAP@50-95:  {metrics.box.map:.4f}")

    print("\nCopy these real numbers into your project report (Section 9 of the doc).")
    print("60-70% mAP@50 is a perfectly fine, honest number for a student project.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate fine-tuned YOLOv8 model")
    parser.add_argument(
        "--weights",
        type=str,
        default=str(DEFAULT_WEIGHTS),
        help="Path to trained weights (default: cv/weights/best.pt)",
    )
    args = parser.parse_args()

    validate(args.weights)