"""
Phase 5 -- SQLAlchemy models: products, inventory, alerts.

Three tables, properly linked together (per the doc's Section on
database setup):
  - products: what you're tracking, plus min_threshold / max_capacity
  - inventory: stock readings over time (linked to products)
  - alerts: log of alerts that got triggered (linked to products)
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    minimum_threshold = Column(Integer, nullable=False, default=5)
    max_capacity = Column(Integer, nullable=False)

    # One product/shelf area can have many inventory readings and alerts
    inventory_readings = relationship("Inventory", back_populates="product")
    alerts = relationship("Alert", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="inventory_readings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)  # e.g. "low_stock", "empty_shelf"
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, nullable=False, default="active")  # "active" or "resolved"

    product = relationship("Product", back_populates="alerts")