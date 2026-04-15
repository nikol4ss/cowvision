from __future__ import annotations

"""Motor de deteccao e medicao.

Este modulo concentra a parte de visao computacional:
1. detectar mudanca entre frames
2. segmentar o maior objeto da cena
3. medir dimensoes com base na calibracao
4. estimar distancia usando o mapa de profundidade
"""

import cv2
import numpy as np

from cowvision.schemas import FrameBundle, MeasurementResult


class MeasurementEngine:
    """Executa o pipeline de medicao de um frame de vaca.

    A abordagem foi mantida simples de proposito:
    - aplica blur e threshold
    - remove pequenos ruidos com operacoes morfologicas
    - pega o maior contorno como objeto principal
    - usa `minAreaRect` para obter largura/altura orientadas
    """

    def __init__(self, pixels_per_meter: float, min_contour_area: int = 8000) -> None:
        if pixels_per_meter <= 0:
            raise ValueError("pixels_per_meter deve ser maior que zero. Execute a calibracao antes.")
        self.pixels_per_meter = pixels_per_meter
        self.min_contour_area = min_contour_area

    def detect_motion(self, previous_frame: np.ndarray, current_frame: np.ndarray, threshold: int = 25) -> bool:
        """Detecta se houve mudanca suficiente entre dois frames.

        A regra atual conta quantos pixels mudaram acima de um limiar.
        Ela funciona bem como gatilho simples para comecar a medicao.
        """

        gray_prev = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        gray_curr = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_prev, gray_curr)
        _, mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        changed_pixels = int(cv2.countNonZero(mask))
        return changed_pixels > 5000

    def measure(self, frame: FrameBundle) -> MeasurementResult | None:
        """Segmenta e mede o objeto principal do frame.

        Retorna `None` quando nao encontra um objeto suficientemente grande.
        """

        color = frame.color.copy()
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        # Remove pequenos ruidos claros e depois fecha pequenos buracos
        # no objeto principal para estabilizar o contorno.
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        if area < self.min_contour_area:
            return None

        rect = cv2.minAreaRect(contour)
        (center_x, center_y), (width_px, height_px), angle = rect
        box = cv2.boxPoints(rect).astype(int)
        # `minAreaRect` retorna a menor caixa rotacionada que contem o contorno.
        # O maior lado representa a extensao principal da vaca no frame.
        major_px = max(width_px, height_px)
        minor_px = min(width_px, height_px)
        width_m = major_px / self.pixels_per_meter
        height_m = minor_px / self.pixels_per_meter
        diameter_m = (major_px + minor_px) / 2 / self.pixels_per_meter

        distance_m = self._estimate_distance(frame.depth, contour)
        confidence = min(0.99, max(0.25, area / (color.shape[0] * color.shape[1])))

        cv2.drawContours(color, [box], 0, (0, 255, 0), 2)
        cv2.circle(color, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)
        cv2.putText(color, f"Largura: {width_m:.3f} m", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(color, f"Diametro: {diameter_m:.3f} m", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if distance_m is not None:
            cv2.putText(
                color,
                f"Distancia: {distance_m:.3f} m",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        depth_visualization = self._visualize_depth(frame.depth)
        return MeasurementResult(
            width_px=float(major_px),
            height_px=float(minor_px),
            width_m=float(width_m),
            height_m=float(height_m),
            diameter_m=float(diameter_m),
            distance_m=distance_m,
            confidence=float(confidence),
            annotated_image=color,
            depth_visualization=depth_visualization,
            metadata={
                "center": [float(center_x), float(center_y)],
                "angle": float(angle),
                "contour_area": float(area),
            },
        )

    def _estimate_distance(self, depth: np.ndarray | None, contour: np.ndarray) -> float | None:
        """Estima a distancia pela mediana dos pixels de profundidade do objeto."""

        if depth is None:
            return None
        mask = np.zeros(depth.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, thickness=-1)
        values = depth[mask == 255]
        valid = values[values > 0]
        if valid.size == 0:
            return None
        return float(np.median(valid) / 1000.0)

    def _visualize_depth(self, depth: np.ndarray | None) -> np.ndarray | None:
        """Converte profundidade bruta em imagem colorida para inspeção visual."""

        if depth is None:
            return None
        normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
