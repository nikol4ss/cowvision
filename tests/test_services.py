from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from cowvision.kinect import MockKinectCamera
from cowvision.schemas import MeasurementResult
from cowvision.services import MonitoringService
from cowvision.storage import FileStorage


@contextmanager
def fake_session_scope():
    yield MagicMock()


class MonitoringServiceTests(unittest.TestCase):
    @patch("cowvision.services.time.sleep", return_value=None)
    @patch("cowvision.services.session_scope", side_effect=fake_session_scope)
    @patch("cowvision.services.MeasurementRepository")
    def test_capture_once_persists_measurement_artifacts(
        self,
        measurement_repository_cls: MagicMock,
        _session_scope: MagicMock,
        _sleep: MagicMock,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = FileStorage(Path(tmpdir))
            service = MonitoringService(
                camera=MockKinectCamera(),
                storage=storage,
                pixels_per_meter=200,
            )

            result = service.capture_once()

            self.assertIsNotNone(result)
            assert result is not None
            self.assertTrue(result.image_path and result.image_path.exists())
            self.assertTrue(result.depth_path and result.depth_path.exists())
            measurement_repository_cls.return_value.create.assert_called_once()

    @patch("cowvision.services.time.sleep", return_value=None)
    @patch("cowvision.services.session_scope", side_effect=fake_session_scope)
    @patch("cowvision.services.MeasurementRepository")
    def test_monitor_collects_at_least_one_measurement_when_motion_exists(
        self,
        measurement_repository_cls: MagicMock,
        _session_scope: MagicMock,
        _sleep: MagicMock,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = FileStorage(Path(tmpdir))
            service = MonitoringService(
                camera=MockKinectCamera(),
                storage=storage,
                pixels_per_meter=200,
            )

            results = service.monitor(interval_seconds=0, max_frames=3)

            self.assertGreaterEqual(len(results), 1)
            self.assertTrue(all(isinstance(item, MeasurementResult) for item in results))
            self.assertGreaterEqual(measurement_repository_cls.return_value.create.call_count, 1)


if __name__ == "__main__":
    unittest.main()
