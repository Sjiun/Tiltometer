import asyncio
from websockets import connect
import json

import numpy as np
from PIL import Image
from keras import models

from io import BytesIO
import base64
import re


# local machine's IP goes here.
# Port corresponds to where websocket server is running (`./server/server.js`)
uri = "ws://192.168.178.31:5000"

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

model = models.load_model('model.h5')


def decode_image_from_string(string: str):
    # das hier ist nur ein Platzhalter. Das tatsächliche Decoding kommt hier herein
    # sobald wir wissen, welches Decoding/Encoding wir benutzen wollen
    # frontend schickt vrmtl. meta data des bildes mit
    img_data_no_meta = re.sub('^data:image/.+;base64,', '', string)
    image = Image.open(BytesIO(base64.b64decode(img_data_no_meta)))
    image = image.convert('L')
    # Resizing to 48x48 because we trained the model with this image size.
    image = image.resize((48, 48))
    img_array = np.array(image)
    # Our keras model used a 4D tensor, (images x height x width x channel)
    # So changing dimension 128x128x3 into 1x128x128x3
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def recognize_emotions_from_image(image):
    # ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']
    prediction_ndarray = model.predict(image)[0]
    prediction_array = prediction_ndarray.tolist()
    prediction = {
        "angry": prediction_array[0],
        "happy": prediction_array[1],
        "neutral": prediction_array[2],
        "sad": prediction_array[3],
        "surprise": prediction_array[4],
    }
    return prediction


def get_fer_result_from_server_message(msg_content: str, websocket):
    # get the image object from message string
    image_to_recognize = decode_image_from_string(msg_content)
    # calculate the FER values from speech with the Keras model
    fer_result = recognize_emotions_from_image(image_to_recognize)
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
        await websocket.send(json.dumps([MSG_CODE['CONNECT'], 'I bims: FER']))
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

asyncio.run(websocket_handler())
