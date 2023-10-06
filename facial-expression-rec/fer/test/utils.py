import base64
from pathlib import Path

import cv2
import numpy as np


def image_file_to_base64(image_path: str) -> None:
    image_path = Path(image_path)
    text_file_path = f'{image_path.stem}_base64.txt'

    base64_encoded = base64.b64encode(image_path.read_bytes()).decode('utf-8')

    with open(text_file_path, 'w') as text_file:
        text_file.write(base64_encoded)


def load_file_to_cv2_rgb_array(image_path: str) -> cv2.typing.MatLike:
    image_bytes = (Path(__file__).parent / image_path).read_bytes()
    image_byte_array = np.frombuffer(image_bytes, np.uint8)
    bgr_image = cv2.imdecode(image_byte_array, cv2.IMREAD_COLOR)
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)


if __name__ == '__main__':
    image_file_to_base64('test_image.png')
