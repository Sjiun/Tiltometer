import asyncio
from websockets import connect
import json
import socket

import numpy as np
from PIL import Image
import mediapipe as mp

from io import BytesIO
import base64
import re

from facial_emotions import HSEmotionRecognizer


# local machine's IP goes here.
# use ipconfig command and the first IPv4 Address listed
# Port corresponds to where websocket server is running (`./server/server.js`)
#uri = "ws://192.168.178.31:5000"
#uri = "ws://192.168.178.38:5000"
uri = f'ws://{socket.gethostbyname("host.docker.internal")}:5000'

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


def decode_image_from_string(string: str):
    # das hier ist nur ein Platzhalter. Das tatsächliche Decoding kommt hier herein
    # sobald wir wissen, welches Decoding/Encoding wir benutzen wollen
    # frontend schickt vrmtl. meta data des bildes mit
    img_data_no_meta = re.sub('^data:image/.+;base64,', '', string)
    image = Image.open(BytesIO(base64.b64decode(img_data_no_meta)))
    image = image.convert('RGB')
    # Resizing to 48x48 because we trained the model with this image size.
    #image = image.resize((48, 48))
    img_array = np.array(image)
    print(f'image_array: {img_array.shape}')
    # Our keras model used a 4D tensor, (images x height x width x channel)
    # So changing dimension 128x128x3 into 1x128x128x3
    # img_array = np.expand_dims(img_array, axis=0)

    return img_array

def detect_face(image: np.ndarray):
    print(image.shape)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True,min_detection_confidence=0.5,min_tracking_confidence=0.5)
    results = face_mesh.process(image)
    if not results.multi_face_landmarks:
        return image
    face_landmarks = results.multi_face_landmarks[0]
    height,width,_=image.shape
    x1 = y1 = 1
    x2 = y2 = 0
    for id, lm in enumerate(face_landmarks.landmark):
        cx, cy = lm.x, lm.y
        if cx<x1:
            x1=cx
        if cy<y1:
            y1=cy
        if cx>x2:
            x2=cx
        if cy>y2:
            y2=cy
    if x1<0:
        x1=0
    if y1<0:
        y1=0
    x1,x2=int(x1*width),int(x2*width)
    y1,y2=int(y1*height),int(y2*height)
    return image[y1:y2,x1:x2,:]
        

def recognize_emotions_from_image(image):
    # ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']
    model_name = 'enet_b2_7'
    fer = HSEmotionRecognizer(model_name)
    scores=fer.predict_emotions(image)    
    if '_7' in model_name:
        indices = [0,3,4,5,6]
    else:
        indices = [0,4,5,6,7]
    prediction = {
        "angry": scores[indices[0]],
        "happy": scores[indices[1]],
        "neutral": scores[indices[2]],
        "sad": scores[indices[3]],
        "surprise": scores[indices[4]],
    }
    return prediction


def get_fer_result_from_server_message(msg_content: str, websocket):
    # get the image object from message string
    image_to_recognize = decode_image_from_string(msg_content)
    
    face_image = detect_face(image_to_recognize)
    # calculate the FER values from speech with the Keras model
    fer_result = recognize_emotions_from_image(face_image)
    return fer_result


async def handle_incoming_message_from_websocket(msg_content, msg_time, websocket):
    fer_result = get_fer_result_from_server_message(msg_content, websocket)
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
    async with connect(uri) as websocket:
        await websocket.send(json.dumps([MSG_CODE['CONNECT'], 'FER CONTAINER IS UP AND CONNECTED']))
        # keep websocket open
        while True:
            message = await websocket.recv()
            msg_json = json.loads(message)
            msg_code = msg_json[0]
            msg_content = msg_json[1]
            msg_time = msg_json[2]
            # only handle FER input messages
            if (msg_code == MSG_CODE['FER_INPUT']):
                await handle_incoming_message_from_websocket(msg_content, msg_time, websocket)

if __name__ == "__main__":
    asyncio.run(websocket_handler())
