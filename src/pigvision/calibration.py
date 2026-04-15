from __future__ import annotations

"""Rotinas para transformar distancia em pixels em distancia real."""

import cv2
import numpy as np

from pigvision.schemas import CalibrationResult


class Calibrator:
    """Calcula a relacao entre mundo real e imagem.

    O fluxo implementado aqui e o mais simples possivel:
    - o usuario informa dois pontos na imagem
    - informa a distancia real entre eles
    - o sistema calcula quantos pixels equivalem a um metro
    """

    def calibrate_from_points(
        self,
        image: np.ndarray,
        point_a: tuple[int, int],
        point_b: tuple[int, int],
        reference_distance_m: float,
    ) -> CalibrationResult:
        """Executa calibracao baseada em dois pontos visiveis na imagem."""

        pixel_distance = float(np.linalg.norm(np.array(point_a) - np.array(point_b)))
        if reference_distance_m <= 0:
            raise ValueError("A distancia real de referencia deve ser maior que zero.")
        if pixel_distance <= 0:
            raise ValueError("A distancia em pixels deve ser maior que zero.")

        pixels_per_meter = pixel_distance / reference_distance_m
        preview = image.copy()
        cv2.line(preview, point_a, point_b, (0, 255, 0), 2)
        cv2.circle(preview, point_a, 5, (0, 0, 255), -1)
        cv2.circle(preview, point_b, 5, (255, 0, 0), -1)
        cv2.putText(
            preview,
            f"{reference_distance_m:.2f}m = {pixel_distance:.1f}px",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )
        return CalibrationResult(
            pixels_per_meter=pixels_per_meter,
            reference_distance_m=reference_distance_m,
            reference_pixels=pixel_distance,
            preview_image=preview,
        )
