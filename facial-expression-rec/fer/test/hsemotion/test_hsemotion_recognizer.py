from unittest import TestCase

from fer.hsemotion.face_detector import FaceDetector
from fer.hsemotion.hsemotion_recognizer import HSEmotionRecognizer
from fer.test.utils import load_file_to_cv2_rgb_array


class HSEmotionRecognizerTest(TestCase):

    def test_predict_emotions(self):
        # Arrange
        rgb_image = load_file_to_cv2_rgb_array('test_image.png')
        cropped_image = FaceDetector().detect_face(rgb_image)
        emotion_recognizer = HSEmotionRecognizer()

        # Act
        recognized_emotions = emotion_recognizer.predict_emotions(cropped_image)

        # Assert
        self.assertTrue(len(recognized_emotions) == 7)
        for re in recognized_emotions:
            self.assertIsInstance(re, float)
