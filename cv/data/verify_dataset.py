"""
Phase 2 -- Verify that images and labels actually match up.

Checks the trimmed subset (cv/data/sku110k_subset/) for:
  - every image has a corresponding .txt label file
  - every label file has a corresponding image
  - no empty/corrupt label files (a heads-up, not necessarily an error --
    an empty label just means "no objects in this image")

Usage:
    python cv/data/verify_dataset.py
"""

from pathlib import Path

SUBSET_DIR = Path(__file__).parent / "sku110k_subset"
SPLITS = ["train", "valid", "test"]


def verify_split(split_name: str) -> None:
    images_dir = SUBSET_DIR / split_name / "images"
    labels_dir = SUBSET_DIR / split_name / "labels"

    if not images_dir.exists() or not labels_dir.exists():
        print(f"  {split_name}: MISSING images/ or labels/ folder -- skipping")
        return

    image_stems = {p.stem for p in images_dir.glob("*.jpg")} | {p.stem for p in images_dir.glob("*.png")}
    label_stems = {p.stem for p in labels_dir.glob("*.txt")}

    images_without_labels = image_stems - label_stems
    labels_without_images = label_stems - image_stems

    empty_labels = []
    for stem in label_stems:
        label_path = labels_dir / f"{stem}.txt"
        if label_path.stat().st_size == 0:
            empty_labels.append(stem)

    print(f"\n{split_name}:")
    print(f"  Images: {len(image_stems)}   Labels: {len(label_stems)}")

    if images_without_labels:
        print(f"  WARNING: {len(images_without_labels)} images have no matching label file")
        for s in list(images_without_labels)[:5]:
            print(f"    - {s}")
    else:
        print("  OK: every image has a matching label file")

    if labels_without_images:
        print(f"  WARNING: {len(labels_without_images)} label files have no matching image")
        for s in list(labels_without_images)[:5]:
            print(f"    - {s}")
    else:
        print("  OK: every label file has a matching image")

    if empty_labels:
        print(f"  Note: {len(empty_labels)} label files are empty (no objects annotated in those images)")


if __name__ == "__main__":
    print(f"Verifying dataset at: {SUBSET_DIR}")
    for split in SPLITS:
        verify_split(split)