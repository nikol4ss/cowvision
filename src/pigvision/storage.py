from __future__ import annotations

"""Utilitarios para persistencia de imagens em disco."""

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from pigvision.config import settings


class FileStorage:
    """Gerencia o salvamento local de imagens do sistema.

    A estrutura gerada fica em:
    - `data/images/`: imagens anotadas de medicao
    - `data/depth/`: visualizacoes de profundidade
    - `data/calibration/`: previews de calibracao
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or settings.storage_dir
        self.images_dir = self.root / "images"
        self.depth_dir = self.root / "depth"
        self.calibration_dir = self.root / "calibration"
        for directory in (self.images_dir, self.depth_dir, self.calibration_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def _timestamped_path(self, directory: Path, prefix: str, suffix: str = ".png") -> Path:
        """Gera um nome de arquivo unico baseado no horario atual."""

        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        return directory / f"{prefix}_{stamp}{suffix}"

    def save_image(self, image: np.ndarray, prefix: str = "measurement") -> Path:
        """Salva uma imagem anotada de medicao."""

        path = self._timestamped_path(self.images_dir, prefix)
        cv2.imwrite(str(path), image)
        return path

    def save_depth(self, image: np.ndarray, prefix: str = "depth") -> Path:
        """Salva a visualizacao colorida do mapa de profundidade."""

        path = self._timestamped_path(self.depth_dir, prefix)
        cv2.imwrite(str(path), image)
        return path

    def save_calibration_preview(self, image: np.ndarray, prefix: str = "calibration") -> Path:
        """Salva a imagem de calibracao com os pontos marcados."""

        path = self._timestamped_path(self.calibration_dir, prefix)
        cv2.imwrite(str(path), image)
        return path
