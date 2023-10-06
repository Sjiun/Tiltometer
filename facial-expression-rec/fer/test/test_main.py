from pathlib import Path
from unittest import TestCase

from fer import main


class MainTest(TestCase):

    def test_recognize_emotions_from_image(self):
        # Arrange
        base64_image = (Path(__file__).parent / 'test_image_base64.txt').read_text('utf-8')

        # Act
        rgb_image_array = main.decode_image_from_string(base64_image)
        result = main.recognize_emotions_from_image(rgb_image_array)

        # Assert
        self.assertEquals(
            ['angry', 'happy', 'neutral', 'sad', 'surprise'],
            list(result.keys())
        )
        self.assertTrue(all(isinstance(v, float) for v in result.values()))
