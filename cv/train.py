"""
Phase 3 -- Fine-tune YOLOv8n on the SKU-110K subset.

Per the project doc: fine-tune the existing pretrained YOLOv8n, don't
train one from scratch. YOLOv8 handles augmentation (flips, mixing,
lighting changes) automatically during training -- no extra setup needed.

Usage:
    python cv/train.py
    python cv/train.py --epochs 50 --batch 8

Output:
    Trained weights saved under: runs/detect/train/weights/best.pt
    (Ultralytics creates this automatically -- copy best.pt into
    cv/weights/ once training finishes.)
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

DATASET_YAML = Path(__file__).parent / "dataset.yaml"


def train(epochs: int, batch: int, imgsz: int) -> None:
    # Start from the pretrained COCO checkpoint -- this is the fine-tuning step
    model = YOLO("yolov8n.pt")

    model.train(
        data=str(DATASET_YAML),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        patience=15,   # stop early if no improvement for 15 epochs
        name="shelf_product_detector",
    )

    print("\nTraining complete.")
    print("Best weights saved under: runs/detect/shelf_product_detector/weights/best.pt")
    print("Copy that file into cv/weights/best.pt once you've confirmed it looks good.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8n on SKU-110K subset")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (lower this if you run out of memory)")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    args = parser.parse_args()

    train(args.epochs, args.batch, args.imgsz)