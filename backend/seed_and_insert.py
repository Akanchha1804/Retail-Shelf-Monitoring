"""
Phase 5 -- Insert readings and alerts.

Provides simple functions to:
  1. Seed initial products (one row per shelf area, e.g. Shelf A/B/C)
  2. Insert a new inventory reading (a stock count at a point in time)
  3. Insert a new alert (when stock drops below threshold)

Usage:
    python seed_and_insert.py          # seeds 3 example products
"""

from database import SessionLocal
from models import Product, Inventory, Alert


def seed_products() -> None:
    """Insert example shelf/product rows -- run once to get started."""
    db = SessionLocal()
    try:
        existing = db.query(Product).count()
        if existing > 0:
            print(f"Products table already has {existing} row(s) -- skipping seed.")
            return

        example_products = [
            Product(product_name="Shelf A", minimum_threshold=5, max_capacity=20),
            Product(product_name="Shelf B", minimum_threshold=5, max_capacity=20),
            Product(product_name="Shelf C", minimum_threshold=5, max_capacity=20),
        ]
        db.add_all(example_products)
        db.commit()
        print(f"Seeded {len(example_products)} products.")
    finally:
        db.close()


def insert_reading(product_id: int, quantity: int) -> Inventory:
    """
    Insert one inventory reading for a product/shelf.
    Call this from your detection loop (worker.py) each time you have
    a new smoothed count from occupancy.py.
    """
    db = SessionLocal()
    try:
        reading = Inventory(product_id=product_id, quantity=quantity)
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading
    finally:
        db.close()


def insert_alert(product_id: int, alert_type: str, status: str = "active") -> Alert:
    """
    Insert one alert row.
    Call this from your alerts_engine.py whenever a threshold is crossed.
    """
    db = SessionLocal()
    try:
        alert = Alert(product_id=product_id, alert_type=alert_type, status=status)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()

    # Quick demo: insert one reading and one low-stock alert for Shelf A
    db = SessionLocal()
    shelf_a = db.query(Product).filter(Product.product_name == "Shelf A").first()
    db.close()

    if shelf_a:
        reading = insert_reading(shelf_a.product_id, quantity=4)
        print(f"Inserted reading: product_id={reading.product_id}, quantity={reading.quantity}")

        alert = insert_alert(shelf_a.product_id, alert_type="low_stock")
        print(f"Inserted alert: product_id={alert.product_id}, type={alert.alert_type}, status={alert.status}")