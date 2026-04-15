from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(slots=True)
class FrameBundle:
    color: np.ndarray
    depth: np.ndarray | None = None
    timestamp: float | None = None


@dataclass(slots=True)
class CalibrationResult:
    pixels_per_meter: float
    reference_distance_m: float
    reference_pixels: float
    preview_image: np.ndarray


@dataclass(slots=True)
class MeasurementResult:
    width_px: float
    height_px: float
    width_m: float
    height_m: float
    diameter_m: float
    distance_m: float | None
    confidence: float
    annotated_image: np.ndarray
    depth_visualization: np.ndarray | None
    metadata: dict
    image_path: Path | None = None
    depth_path: Path | None = None
