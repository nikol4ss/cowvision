from __future__ import annotations

"""Modelos ORM persistidos no PostgreSQL."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cowvision.database import Base


class CalibrationRecord(Base):
    """Historico de calibracoes realizadas no sistema.

    Cada registro guarda a relacao pixels/metro obtida a partir de uma
    referencia real conhecida.
    """

    __tablename__ = "calibrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    pixels_per_meter: Mapped[float] = mapped_column(Float, nullable=False)
    reference_distance_m: Mapped[float] = mapped_column(Float, nullable=False)
    reference_pixels: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MeasurementRecord(Base):
    """Registro consolidado de uma medicao automatica."""

    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    width_px: Mapped[float] = mapped_column(Float, nullable=False)
    height_px: Mapped[float] = mapped_column(Float, nullable=False)
    width_m: Mapped[float] = mapped_column(Float, nullable=False)
    height_m: Mapped[float] = mapped_column(Float, nullable=False)
    diameter_m: Mapped[float] = mapped_column(Float, nullable=False)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    depth_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
