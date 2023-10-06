import asyncio
import base64
import json
import re
import socket
from typing import Dict, Optional

import cv2
import numpy as np
from websockets import connect

from fer.hsemotion.face_detector import FaceDetector
from fer.hsemotion.hsemotion_recognizer import HSEmotionRecognizer

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
facial_expression_recognizer = HSEmotionRecognizer()


def decode_image_from_string(base_64_image: str) -> np.ndarray:
    """
    :param base_64_image: base64 string that encodes an image
    :return: numpy array of shape (height, width, channels)
    """
    base_64_image_without_metadata = re.sub('^data:image/.+;base64,', '', base_64_image)
    image_bytes = base64.b64decode(base_64_image_without_metadata)
    image_byte_array = np.frombuffer(image_bytes, np.uint8)
    bgr_image = cv2.imdecode(image_byte_array, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    return rgb_image


def recognize_emotions_from_image(image: np.ndarray) -> Dict[str, float]:
    """
    :param image: numpy array of shape (height, width, channels)
    :return: dictionary containing probabilities for the emotions: angry, happy, neutral, sad and surprise.
    """
    scores = facial_expression_recognizer.predict_emotions(image)
    return {
        "angry": scores[0],
        "happy": scores[3],
        "neutral": scores[4],
        "sad": scores[5],
        "surprise": scores[6],
    }


def get_fer_result_from_server_message(msg_content: str) -> Optional[Dict[str, float]]:
    image_to_recognize = decode_image_from_string(msg_content)
    face_image = face_detector.detect_face(image_to_recognize)

    if face_image is None:
        return None

    return recognize_emotions_from_image(face_image)


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
