from __future__ import annotations

"""Camada de captura para Kinect.

O objetivo deste modulo e esconder a diferenca entre backends de hardware.
O restante do sistema sempre trabalha com um `FrameBundle`.
"""

import time
from abc import ABC, abstractmethod

import cv2
import numpy as np

from cowvision.schemas import FrameBundle


class BaseKinectCamera(ABC):
    """Contrato minimo para qualquer camera suportada pelo projeto."""

    @abstractmethod
    def get_frame(self) -> FrameBundle:
        raise NotImplementedError


class MockKinectCamera(BaseKinectCamera):
    """Camera de simulacao.

    Gera uma elipse deslocando-se horizontalmente para permitir testes do
    pipeline sem Kinect fisico conectado.
    """

    def __init__(self, width: int = 640, height: int = 480) -> None:
        self.width = width
        self.height = height
        self._phase = 0

    def get_frame(self) -> FrameBundle:
        """Retorna frame sintetico colorido + profundidade artificial."""

        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        depth = np.full((self.height, self.width), 1200, dtype=np.uint16)
        center_x = 80 + (self._phase % (self.width - 160))
        center_y = self.height // 2
        axes = (70, 110)
        cv2.ellipse(image, (center_x, center_y), axes, 0, 0, 360, (200, 200, 200), -1)
        cv2.ellipse(depth, (center_x, center_y), axes, 0, 0, 360, 850, -1)
        self._phase += 18
        return FrameBundle(color=image, depth=depth, timestamp=time.time())


class FreenectCamera(BaseKinectCamera):
    """Adaptador para Kinect usando a biblioteca `freenect`."""

    def __init__(self) -> None:
        import freenect  # type: ignore

        self.freenect = freenect

    def get_frame(self) -> FrameBundle:
        """Captura frame RGB e profundidade do Kinect classico."""

        color, _ = self.freenect.sync_get_video()
        depth, _ = self.freenect.sync_get_depth()
        color_bgr = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
        return FrameBundle(color=color_bgr, depth=depth, timestamp=time.time())


class PyKinect2Camera(BaseKinectCamera):
    """Adaptador para Kinect v2 via `pykinect2`."""

    def __init__(self) -> None:
        from pykinect2 import PyKinectRuntime  # type: ignore
        from pykinect2 import PyKinectV2  # type: ignore

        self.runtime = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth
        )

    def get_frame(self) -> FrameBundle:
        """Aguarda novos frames e os converte para arrays do OpenCV."""

        while True:
            if self.runtime.has_new_color_frame() and self.runtime.has_new_depth_frame():
                break

        color_frame = self.runtime.get_last_color_frame()
        depth_frame = self.runtime.get_last_depth_frame()
        color = color_frame.reshape((1080, 1920, 4))[:, :, :3].astype(np.uint8)
        depth = depth_frame.reshape((424, 512)).astype(np.uint16)
        color = cv2.resize(color, (512, 424))
        return FrameBundle(color=color, depth=depth, timestamp=time.time())


def build_camera(backend: str = "auto") -> BaseKinectCamera:
    """Cria a implementacao de camera mais adequada.

    Regras:
    - `mock`: sempre usa simulacao
    - `freenect`: exige freenect
    - `pykinect2`: exige pykinect2
    - `auto`: tenta freenect, depois pykinect2, depois mock
    """

    requested = backend.lower()
    if requested in {"mock", "demo"}:
        return MockKinectCamera()

    if requested in {"auto", "freenect"}:
        try:
            return FreenectCamera()
        except Exception:
            if requested == "freenect":
                raise

    if requested in {"auto", "pykinect2"}:
        try:
            return PyKinect2Camera()
        except Exception:
            if requested == "pykinect2":
                raise

    return MockKinectCamera()
