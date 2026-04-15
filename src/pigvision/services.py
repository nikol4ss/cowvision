from __future__ import annotations

"""Servicos de alto nivel do projeto.

Aqui ficam os fluxos completos que combinam:
- captura
- calibracao ou medicao
- armazenamento de imagem
- persistencia em banco
"""

import time
from pathlib import Path

from pigvision.calibration import Calibrator
from pigvision.config import settings
from pigvision.database import session_scope
from pigvision.kinect import BaseKinectCamera, build_camera
from pigvision.measurement import MeasurementEngine
from pigvision.repositories import CalibrationRepository, MeasurementRepository
from pigvision.schemas import CalibrationResult, FrameBundle, MeasurementResult
from pigvision.storage import FileStorage


class CalibrationService:
    """Orquestra o fluxo de calibracao e persistencia do resultado."""

    def __init__(self, storage: FileStorage | None = None) -> None:
        self.storage = storage or FileStorage()
        self.calibrator = Calibrator()

    def calibrate(
        self,
        image,
        point_a: tuple[int, int],
        point_b: tuple[int, int],
        reference_distance_m: float,
        name: str = "default",
        notes: str | None = None,
    ) -> tuple[CalibrationResult, Path]:
        """Calcula calibracao, salva imagem de preview e registra no banco."""

        result = self.calibrator.calibrate_from_points(image, point_a, point_b, reference_distance_m)
        preview_path = self.storage.save_calibration_preview(result.preview_image)
        with session_scope() as session:
            CalibrationRepository(session).create(name=name, calibration=result, notes=notes)
        return result, preview_path

    def latest_pixels_per_meter(self) -> float:
        """Busca o fator de calibracao atual.

        Prioridade:
        1. valor fixo no `.env`
        2. ultima calibracao gravada no banco
        """

        if settings.pixels_per_meter > 0:
            return settings.pixels_per_meter
        with session_scope() as session:
            latest = CalibrationRepository(session).latest()
            if latest is None:
                raise RuntimeError("Nenhuma calibracao encontrada. Execute o comando de calibracao primeiro.")
            return latest.pixels_per_meter


class MonitoringService:
    """Executa o fluxo automatico de deteccao e medicao."""

    def __init__(
        self,
        camera: BaseKinectCamera | None = None,
        storage: FileStorage | None = None,
        pixels_per_meter: float | None = None,
    ) -> None:
        self.camera = camera or build_camera(settings.kinect_backend)
        self.storage = storage or FileStorage()
        ppm = pixels_per_meter or CalibrationService(self.storage).latest_pixels_per_meter()
        self.engine = MeasurementEngine(ppm, min_contour_area=settings.min_contour_area)

    def capture_once(self) -> MeasurementResult | None:
        """Captura um frame e tenta medir imediatamente o objeto presente."""

        frame = self.camera.get_frame()
        measurement = self.engine.measure(frame)
        if measurement is None:
            return None
        return self._persist_measurement(measurement)

    def monitor(self, interval_seconds: float = 0.3, max_frames: int | None = None) -> list[MeasurementResult]:
        """Monitora continuamente a cena.

        O gatilho atual e:
        - compara o frame atual com o anterior
        - se houve movimento suficiente, tenta medir
        - apos uma medicao valida, aguarda 1 segundo para evitar duplicatas
        """

        previous: FrameBundle | None = None
        measurements: list[MeasurementResult] = []
        processed = 0
        while max_frames is None or processed < max_frames:
            current = self.camera.get_frame()
            if previous is not None and self.engine.detect_motion(
                previous.color, current.color, threshold=settings.motion_threshold
            ):
                result = self.engine.measure(current)
                if result is not None:
                    measurements.append(self._persist_measurement(result))
                    time.sleep(1.0)
            previous = current
            processed += 1
            time.sleep(interval_seconds)
        return measurements

    def _persist_measurement(self, measurement: MeasurementResult) -> MeasurementResult:
        """Salva artefatos da medicao e registra os dados no banco."""

        measurement.image_path = self.storage.save_image(measurement.annotated_image)
        if measurement.depth_visualization is not None:
            measurement.depth_path = self.storage.save_depth(measurement.depth_visualization)
        with session_scope() as session:
            MeasurementRepository(session).create(measurement)
        return measurement
