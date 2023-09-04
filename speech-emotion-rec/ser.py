import asyncio
import json
import socket
import wave
from collections import deque
from typing import Optional, Dict

import librosa
import numpy as np
from websockets import connect

from ser_model import TIMNET_Model

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

# Model and Feature Extraction Code is based on https://github.com/Jiaxin-Ye/TIM-Net_SER

MODEL_PATH = './10-fold_weights_best_1.hdf5'
RAVDESS_CLASS_LABELS = ("angry", "calm", "disgust", "fear", "happy", "neutral", "sad", "surprise")

model = TIMNET_Model(input_shape=(215, 39), class_labels=RAVDESS_CLASS_LABELS,
                     filter_size=39, kernel_size=2, stack_size=1, dilation_size=8,
                     dropout=0.1, activation='relu', lr=0.001, beta1=0.93, beta2=0.98, epsilon=1e-8)
model.load_weights(MODEL_PATH)

MEAN_SIGNAL_LENGTH = 110000


def get_feature(file_path: str,
                feature_type: str = "MFCC",
                mean_signal_length: int = MEAN_SIGNAL_LENGTH,
                embed_len: int = 39) -> np.ndarray:
    feature = None
    signal, fs = librosa.load(file_path)
    s_len = len(signal)
    if s_len < mean_signal_length:
        pad_len = mean_signal_length - s_len
        pad_rem = pad_len % 2
        pad_len //= 2
        signal = np.pad(signal, (pad_len, pad_len + pad_rem), 'constant', constant_values=0)
    else:
        pad_len = s_len - mean_signal_length
        pad_len //= 2
        signal = signal[pad_len:pad_len + mean_signal_length]
    if feature_type == "MFCC":
        mfcc = librosa.feature.mfcc(y=signal, sr=fs, n_mfcc=embed_len)
        feature = np.transpose(mfcc)
    return feature


'''
Following the training of the model we are using, we want a signal_length of 110k.
The original feature extraction loads data at librosa's default sampling rate of 22.05 kHz
Our training data's (RAVDESS) original sampling rate is 48 kHz.
We receive data in chunks as Float32Arrays of length 4096 from the device manager. Data is recorded at 48 kHz.
To achieve a signal_length of 110k, we need a buffer capacity of 110000/(22.05/48)=239456 for the data sampled at 48kHz.
That is about 5 seconds.
'''
BUFFER_CAPACITY = 239456
buffer_deque = deque(maxlen=BUFFER_CAPACITY)
dtype = np.float32
chunk_counter = 0
WAVE_OUTPUT_FILE = "output.wav"


async def recognize_emotions_from_wav_file() -> Dict[str, float]:
    feature_vector = get_feature(WAVE_OUTPUT_FILE)
    feature_vector = np.expand_dims(feature_vector, axis=0)
    prediction_array = model.predict(feature_vector).tolist()

    prediction = {
        "neutral": prediction_array[5],
        "happy": prediction_array[4],
        "sad": prediction_array[6],
        "angry": prediction_array[0],
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


async def get_ser_result_from_server_message(msg_content) -> Optional[Dict]:
    global chunk_counter
    chunk_counter += 1

    audio_data = np.array(msg_content, dtype=dtype)
    buffer_deque.extend(audio_data)

    if len(buffer_deque) >= BUFFER_CAPACITY:
        # 24 chunks of 4096 at a sampling rate of 48 kHz equal about two seconds
        if chunk_counter >= 24:
            audio_to_save = np.array(buffer_deque, dtype=dtype)
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
