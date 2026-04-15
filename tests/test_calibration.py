from __future__ import annotations

import unittest

import numpy as np

from cowvision.calibration import Calibrator


class CalibratorTests(unittest.TestCase):
    def test_calibrate_from_points_calculates_pixels_per_meter(self) -> None:
        image = np.zeros((200, 500, 3), dtype=np.uint8)

        result = Calibrator().calibrate_from_points(
            image=image,
            point_a=(50, 100),
            point_b=(450, 100),
            reference_distance_m=2.0,
        )

        self.assertEqual(result.reference_pixels, 400.0)
        self.assertEqual(result.pixels_per_meter, 200.0)
        self.assertEqual(result.reference_distance_m, 2.0)
        self.assertEqual(result.preview_image.shape, image.shape)

    def test_calibrate_from_points_rejects_invalid_reference_distance(self) -> None:
        image = np.zeros((50, 50, 3), dtype=np.uint8)

        with self.assertRaisesRegex(ValueError, "distancia real"):
            Calibrator().calibrate_from_points(
                image=image,
                point_a=(0, 0),
                point_b=(10, 0),
                reference_distance_m=0,
            )


if __name__ == "__main__":
    unittest.main()
