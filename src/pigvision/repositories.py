from __future__ import annotations

import json

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from pigvision.models import CalibrationRecord, MeasurementRecord
from pigvision.schemas import CalibrationResult, MeasurementResult


class CalibrationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, calibration: CalibrationResult, notes: str | None = None) -> CalibrationRecord:
        record = CalibrationRecord(
            name=name,
            pixels_per_meter=calibration.pixels_per_meter,
            reference_distance_m=calibration.reference_distance_m,
            reference_pixels=calibration.reference_pixels,
            notes=notes,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def latest(self) -> CalibrationRecord | None:
        query = select(CalibrationRecord).order_by(desc(CalibrationRecord.created_at)).limit(1)
        return self.session.scalar(query)


class MeasurementRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, measurement: MeasurementResult) -> MeasurementRecord:
        record = MeasurementRecord(
            width_px=measurement.width_px,
            height_px=measurement.height_px,
            width_m=measurement.width_m,
            height_m=measurement.height_m,
            diameter_m=measurement.diameter_m,
            distance_m=measurement.distance_m,
            confidence=measurement.confidence,
            image_path=str(measurement.image_path) if measurement.image_path else "",
            depth_path=str(measurement.depth_path) if measurement.depth_path else None,
            metadata_json=json.dumps(measurement.metadata, ensure_ascii=True),
        )
        self.session.add(record)
        self.session.flush()
        return record
