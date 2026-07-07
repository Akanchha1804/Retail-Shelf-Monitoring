"""
Phase 2 -- Trim the full SKU-110K export down to a manageable subset.

Per the project doc (Section 6.3): don't use all 11,000+ images.
Start with 300-500 total, roughly matching the existing 70/20/10 split ratio.

Usage:
    python cv/data/create_subset.py --total 400

Output:
    Creates cv/data/sku110k_subset/ with train/valid/test folders,
    each containing images/ + labels/, copied (not moved) from the
    original cv/data/sku110k/ folders. Original data is left untouched.
"""

import argparse
import random
import shutil
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "sku110k"
DEST_DIR = Path(__file__).parent / "sku110k_subset"

# Roughly matches your current 70/20/10 split proportions
SPLIT_RATIOS = {"train": 0.7, "valid": 0.2, "test": 0.1}


def trim_split(split_name: str, count: int) -> None:
    src_images = SOURCE_DIR / split_name / "images"
    src_labels = SOURCE_DIR / split_name / "labels"

    dst_images = DEST_DIR / split_name / "images"
    dst_labels = DEST_DIR / split_name / "labels"
    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    all_images = list(src_images.glob("*.jpg")) + list(src_images.glob("*.png"))
    if len(all_images) < count:
        print(f"  Warning: only {len(all_images)} images available in {split_name}, using all of them")
        count = len(all_images)

    chosen = random.sample(all_images, count)

    copied = 0
    skipped = 0
    for img_path in chosen:
        label_path = src_labels / (img_path.stem + ".txt")
        if not label_path.exists():
            skipped += 1
            continue
        shutil.copy2(img_path, dst_images / img_path.name)
        shutil.copy2(label_path, dst_labels / label_path.name)
        copied += 1

    print(f"  {split_name}: copied {copied} image+label pairs (skipped {skipped} missing labels)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trim SKU-110K down to a subset")
    parser.add_argument("--total", type=int, default=400, help="Total images across all splits (default 400)")
    args = parser.parse_args()

    random.seed(42)  # reproducible subset

    print(f"Creating a {args.total}-image subset in {DEST_DIR} ...")
    for split_name, ratio in SPLIT_RATIOS.items():
        split_count = round(args.total * ratio)
        print(f"Processing {split_name} (~{split_count} images)...")
        trim_split(split_name, split_count)

    print("\nDone. Subset saved to:", DEST_DIR)