from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from cowvision import cli
from cowvision.schemas import CalibrationResult, MeasurementResult


class CliTests(unittest.TestCase):
    def test_parse_point(self) -> None:
        self.assertEqual(cli.parse_point("10,20"), (10, 20))

    @patch("cowvision.cli.build_camera")
    def test_command_capture_frame_prints_frame_shapes(self, build_camera_mock: MagicMock) -> None:
        frame = MagicMock()
        frame.color.shape = (480, 640, 3)
        frame.depth.shape = (480, 640)
        build_camera_mock.return_value.get_frame.return_value = frame

        output = io.StringIO()
        with redirect_stdout(output):
            cli.command_capture_frame("mock")

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["color_shape"], [480, 640, 3])
        self.assertEqual(payload["depth_shape"], [480, 640])

    @patch("cowvision.cli.CalibrationService")
    def test_command_calibrate_prints_json_result(self, calibration_service_cls: MagicMock) -> None:
        with TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "reference.png"
            cv2.imwrite(str(image_path), np.zeros((50, 50, 3), dtype=np.uint8))

            calibration_service_cls.return_value.calibrate.return_value = (
                CalibrationResult(
                    pixels_per_meter=200.0,
                    reference_distance_m=2.0,
                    reference_pixels=400.0,
                    preview_image=np.zeros((50, 50, 3), dtype=np.uint8),
                ),
                Path(tmpdir) / "preview.png",
            )

            args = cli.build_parser().parse_args(
                [
                    "calibrate",
                    "--image",
                    str(image_path),
                    "--point-a",
                    "10,10",
                    "--point-b",
                    "30,10",
                    "--distance-m",
                    "2.0",
                ]
            )

            output = io.StringIO()
            with redirect_stdout(output):
                cli.command_calibrate(args)

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["pixels_per_meter"], 200.0)
        self.assertEqual(payload["reference_pixels"], 400.0)

    @patch("cowvision.cli.MonitoringService")
    @patch("cowvision.cli.build_camera")
    def test_command_measure_once_prints_measurement_json(
        self,
        build_camera_mock: MagicMock,
        monitoring_service_cls: MagicMock,
    ) -> None:
        build_camera_mock.return_value = MagicMock()
        monitoring_service_cls.return_value.capture_once.return_value = MeasurementResult(
            width_px=100.0,
            height_px=50.0,
            width_m=0.5,
            height_m=0.25,
            diameter_m=0.375,
            distance_m=1.2,
            confidence=0.8,
            annotated_image=np.zeros((10, 10, 3), dtype=np.uint8),
            depth_visualization=np.zeros((10, 10, 3), dtype=np.uint8),
            metadata={},
            image_path=Path("data/images/out.png"),
            depth_path=Path("data/depth/out.png"),
        )

        output = io.StringIO()
        with redirect_stdout(output):
            cli.command_measure_once("mock")

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["width_m"], 0.5)
        self.assertEqual(payload["depth_path"], "data/depth/out.png")


if __name__ == "__main__":
    unittest.main()
