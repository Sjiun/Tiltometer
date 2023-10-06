from unittest import TestCase

import numpy as np

from fer.hsemotion.face_detector import FaceDetector
from fer.test.utils import load_file_to_cv2_rgb_array


class FaceDetectorTest(TestCase):

    def test_detect_face(self):
        # Arrange
        input_image = load_file_to_cv2_rgb_array('test_image.png')
        face_detector = FaceDetector()

        # Act
        detected_face = face_detector.detect_face(input_image)

        # Assert
        self.assertIsInstance(detected_face, np.ndarray)
        self.assertEqual(len(detected_face.shape), 3)
        self.assertTrue(0 < detected_face.shape[0] <= input_image.shape[0])
        self.assertTrue(0 < detected_face.shape[1] <= input_image.shape[1])
        self.assertEqual(detected_face.shape[2], 3)
