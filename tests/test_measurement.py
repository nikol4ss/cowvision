from __future__ import annotations

import unittest

from cowvision.kinect import MockKinectCamera
from cowvision.measurement import MeasurementEngine


class MeasurementEngineTests(unittest.TestCase):
    def test_measure_detects_mock_object_and_returns_dimensions(self) -> None:
        engine = MeasurementEngine(pixels_per_meter=200, min_contour_area=1000)
        frame = MockKinectCamera().get_frame()

        result = engine.measure(frame)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertGreater(result.width_px, result.height_px)
        self.assertGreater(result.width_m, 0)
        self.assertGreater(result.diameter_m, 0)
        self.assertIsNotNone(result.distance_m)
        self.assertAlmostEqual(result.distance_m, 0.85, places=2)
        self.assertEqual(result.annotated_image.shape, frame.color.shape)
        self.assertIsNotNone(result.depth_visualization)

    def test_detect_motion_flags_changed_mock_frames(self) -> None:
        camera = MockKinectCamera()
        first = camera.get_frame()
        second = camera.get_frame()
        engine = MeasurementEngine(pixels_per_meter=200, min_contour_area=1000)

        changed = engine.detect_motion(first.color, second.color, threshold=5)

        self.assertTrue(changed)

    def test_measure_returns_none_for_empty_frame(self) -> None:
        camera = MockKinectCamera()
        frame = camera.get_frame()
        frame.color[:] = 0
        frame.depth[:] = 0
        engine = MeasurementEngine(pixels_per_meter=200, min_contour_area=1000)

        result = engine.measure(frame)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
