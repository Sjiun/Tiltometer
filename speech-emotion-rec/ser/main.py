import asyncio
import json
import socket
import wave
from collections import deque
from typing import Optional, Dict

import numpy as np
from websockets import connect

from ser.timnet.main import get_feature, get_model

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

model = get_model()

'''
We receive data in chunks as Float32Arrays of length 4096 from the device manager. Data is recorded at 48 kHz.
Our training data's (RAVDESS) original average signal_length is about 192k (48 kHz * 4 seconds) = BUFFER_CAPACITY.
'''
BUFFER_CAPACITY = 192000
buffer_deque = deque(maxlen=BUFFER_CAPACITY)
dtype = np.float32
AVERAGE_VOLUME_AMPLITUDE_THRESHOLD = 0.1
TOTAL_VOLUME_AMPLITUDE_THRESHOLD = 0.4
WAVE_OUTPUT_FILE = "output.wav"
chunk_counter = 0


async def recognize_emotions_from_wav_file() -> Dict[str, float]:
    feature_vector = get_feature(WAVE_OUTPUT_FILE)
    feature_vector = np.expand_dims(feature_vector, axis=0)
    prediction_array = model.predict(feature_vector).tolist()

    prediction = {
        "angry": prediction_array[0],
        "happy": prediction_array[4],
        "neutral": prediction_array[5],
        "sad": prediction_array[6],
        "surprise": prediction_array[7],
    }
    return prediction


def save_to_wav(audio_data: np.ndarray) -> None:
    scaled_audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    with wave.open(WAVE_OUTPUT_FILE, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(48000)
        wav_file.writeframes(scaled_audio_data.tobytes())


def is_too_quiet(audio_data: np.ndarray) -> bool:
    average_amplitude = np.mean(np.abs(audio_data))
    total_amplitude = np.max(audio_data) - np.min(audio_data)
    return average_amplitude < AVERAGE_VOLUME_AMPLITUDE_THRESHOLD or total_amplitude < TOTAL_VOLUME_AMPLITUDE_THRESHOLD


async def get_ser_result_from_server_message(msg_content) -> Optional[Dict]:
    global chunk_counter
    chunk_counter += 1

    audio_data = np.array(msg_content, dtype=dtype)
    buffer_deque.extend(audio_data)

    # 12 chunks of 4096 at a sampling rate of 48 kHz equal about one second
    if len(buffer_deque) >= BUFFER_CAPACITY and chunk_counter >= 12:
        audio_to_save = np.array(buffer_deque, dtype=dtype)
        if is_too_quiet(audio_to_save):
            print("\nCould not detect loud enough speech for the last time interval.\n"
                  f"Average Amplitude was: {np.mean(np.abs(audio_to_save)):.4f} but should be more than "
                  f"{AVERAGE_VOLUME_AMPLITUDE_THRESHOLD}\n"
                  f"Total Amplitude was: {np.max(audio_data) - np.min(audio_data):.4f} but should be more than "
                  f"{TOTAL_VOLUME_AMPLITUDE_THRESHOLD}"
                  )
            return None
        save_to_wav(audio_to_save)
        chunk_counter = 0

        return await recognize_emotions_from_wav_file()


async def handle_incoming_message_from_websocket(msg_content, msg_time, websocket):
    ser_result = await get_ser_result_from_server_message(msg_content)
    if ser_result is not None:
        print('---')
        print(ser_result)
        print('---')
        ser_res_string = json.dumps(ser_result)
        # send the SER result back to the server (as a string)
        ser_result_message = json.dumps(
            [MSG_CODE['SER_RESULT'], ser_res_string, msg_time])
        await websocket.send(ser_result_message)


async def websocket_handler():
    async with connect(URI) as websocket:
        await websocket.send(json.dumps([MSG_CODE['CONNECT'], 'SER CONTAINER IS UP AND CONNECTED']))
        # keep websocket open
        while True:
            message = await websocket.recv()
            msg_json = json.loads(message)
            msg_code = msg_json[0]
            msg_content = msg_json[1]
            msg_time = msg_json[2]
            # only handle SER input messages
            if msg_code == MSG_CODE['SER_INPUT']:
                await handle_incoming_message_from_websocket(msg_content, msg_time, websocket)


if __name__ == '__main__':
    asyncio.run(websocket_handler())
