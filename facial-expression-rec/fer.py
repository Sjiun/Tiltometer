import asyncio
import base64
import json
import re
import socket
from io import BytesIO

import numpy as np
from PIL import Image
from typing import Dict, Optional
from websockets import connect

from face_detector import FaceDetector
from hs_emotion_recognizer import HSEmotionRecognizer

# Address of the WebSocket server, which is expected run at the docker host machine.
# The code below should work on Windows with Docker Desktop.
# For linux you may use your machine's IPv4 address.
URI = f'ws://{socket.gethostbyname("host.docker.internal")}:5000'

MSG_CODE = {
    'CONNECT': 0,
    'AUDIO_INPUT': 1,
    'SER_INPUT': 2,
    'SER_RESULT': 3,
    'IMAGE_INPUT': 4,
    'FER_INPUT': 5,
    'FER_RESULT': 6,
    'PULSE_INPUT': 7,
    'PULSE_DATA': 8,
    'CSV_EXPORT': 9,
}

face_detector = FaceDetector()
facial_expression_recognizer = HSEmotionRecognizer(model_name='enet_b2_7')


def decode_image_from_string(base_64_image: str) -> np.ndarray:
    """
    :param base_64_image: base64 string that encodes an image
    :return: numpy array of shape (height, width, channels)
    """
    base_64_image_without_metadata = re.sub('^data:image/.+;base64,', '', base_64_image)
    decoded_image = Image.open(BytesIO(base64.b64decode(base_64_image_without_metadata)))
    decoded_rgb_image = decoded_image.convert('RGB')
    return np.array(decoded_rgb_image)


def recognize_emotions_from_image(image: np.ndarray) -> Dict[str, float]:
    """
    :param image: numpy array of shape (height, width, channels)
    :return: dictionary containing probabilities for the emotions: angry, happy, neutral, sad and surprise.
    """
    scores = facial_expression_recognizer.predict_emotions(image)
    if '_7' in facial_expression_recognizer.model_name:
        indices = [0, 3, 4, 5, 6]
    else:
        indices = [0, 4, 5, 6, 7]
    return {
        "angry": scores[indices[0]],
        "happy": scores[indices[1]],
        "neutral": scores[indices[2]],
        "sad": scores[indices[3]],
        "surprise": scores[indices[4]],
    }


def get_fer_result_from_server_message(msg_content: str) -> Optional[Dict[str, float]]:
    image_to_recognize = decode_image_from_string(msg_content)
    face_image = face_detector.detect_face(image_to_recognize)
    if face_image is None:
        return None
    fer_result = recognize_emotions_from_image(face_image)
    return fer_result


async def handle_incoming_message_from_websocket(msg_content: str, msg_time, websocket):
    fer_result = get_fer_result_from_server_message(msg_content)
    if fer_result is not None:
        print('---')
        print('FER result: ', fer_result)
        fer_res_string = json.dumps(fer_result)
        # send the FER result back to the server (as a string)
        fer_result_message = json.dumps(
            [MSG_CODE['FER_RESULT'], fer_res_string, msg_time])
        print(fer_result_message)
        print('---')
        await websocket.send(fer_result_message)


async def websocket_handler():
    async with connect(URI) as websocket:
        await websocket.send(json.dumps([MSG_CODE['CONNECT'], 'FER CONTAINER IS UP AND CONNECTED']))
        # keep websocket open
        while True:
            message = await websocket.recv()
            msg_json = json.loads(message)
            msg_code = msg_json[0]
            msg_content = msg_json[1]
            msg_time = msg_json[2]
            # only handle FER input messages
            if msg_code == MSG_CODE['FER_INPUT']:
                await handle_incoming_message_from_websocket(msg_content, msg_time, websocket)


if __name__ == "__main__":
    asyncio.run(websocket_handler())
