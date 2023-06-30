import asyncio
import struct
import wave

import librosa
from pydub import AudioSegment, effects
from websockets import connect
from keras import models
import pyaudio
import numpy as np
from array import array
import json
import noisereduce as nr

# Initialize variables
RATE = 44100
CHUNK = 4096
RECORD_SECONDS = 7.1

FORMAT = pyaudio.paInt32
CHANNELS = 1
WAVE_OUTPUT_FILE = "output.wav"

MAYBE_TOO_BIG_FOR_C = 30

# local machine's IP goes here.
# Port corresponds to where websocket server is running (`./server/server.js`)
uri = "ws://192.168.178.31:5000"

global_frames = []

# ein paar Codes, um zwischen Port-Nachrichten zu unterscheiden
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

model = models.load_model("model.h5")


async def recognize_emotions_from_wav_file():
    x = preprocess(WAVE_OUTPUT_FILE)
    prediction_ndarray = model.predict(x, use_multiprocessing=True)[0]
    prediction_array = prediction_ndarray.tolist()

    prediction = {
        "neutral": prediction_array[0],
        "happy": prediction_array[1],
        "sad": prediction_array[2],
        "angry": prediction_array[3],
        "surprise": prediction_array[4],
    }
    return prediction


# Über den port wird nur ein string weitergegeben, der für SER wieder decoded werden muss
async def decode_speech_from_string(string: str):
    buffer_input_array = array(
        "l", [int(i * pow(2, MAYBE_TOO_BIG_FOR_C)) for i in list(string.values())])

    return buffer_input_array


def write_string_to_wav_file(buffer):
    global_frames.append(buffer)

    wf = wave.open(WAVE_OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(global_frames))


def preprocess(file_path, hop_length=4096):
    '''
    A process to an audio .wav file before execcuting a prediction.
      Arguments:
      - file_path - The system path to the audio file.
      - frame_length - Length of the frame over which to compute the speech features. default: 2048
      - hop_length - Number of samples to advance for each frame. default: 512

      Return:
        'X_3D' variable, containing a shape of: (batch, timesteps, feature) for a single file (batch = 1).
    '''
    # Fetch sample rate.
    _, sr = librosa.load(path=file_path, sr=None)
    # Load audio file
    raw_sound = AudioSegment.from_file(file_path, duration=None)
    # Normalize to 5 dBFS
    normalized_sound = effects.normalize(raw_sound, headroom=5.0)
    # Transform the audio file to np.array of samples
    normal_x = np.array(
        normalized_sound.get_array_of_samples(), dtype='float32')
    # Noise reduction
    final_x = nr.reduce_noise(normal_x, sr=sr)

    # f1 = librosa.feature.rms(final_x, frame_length=frame_length, hop_length=hop_length, center=True,
    #                          pad_mode='reflect').T  # Energy - Root Mean Square
    # f2 = librosa.feature.zero_crossing_rate(final_x, frame_length=frame_length, hop_length=hop_length,
    #                                         center=True).T  # ZCR

    # Extracting MFCC feature
    mfcc = librosa.feature.mfcc(
        y=final_x, sr=sr, S=None, n_mfcc=40, hop_length=hop_length)
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_min = mfcc.min(axis=1)
    mfcc_max = mfcc.max(axis=1)
    mfcc_feature = np.concatenate((mfcc_mean, mfcc_min, mfcc_max))

    # Extracting Mel Spectrogram feature
    mel_spectrogram = librosa.feature.melspectrogram(
        y=final_x, sr=sr, hop_length=hop_length)
    mel_spectrogram_mean = mel_spectrogram.mean(axis=1)
    mel_spectrogram_min = mel_spectrogram.min(axis=1)
    mel_spectrogram_max = mel_spectrogram.max(axis=1)
    mel_spectrogram_feature = np.concatenate(
        (mel_spectrogram_mean, mel_spectrogram_min, mel_spectrogram_max))

    # # Extracting chroma vector feature
    # chroma = get_chroma_vector(file_path)
    # chroma_mean = chroma.mean(axis=1)
    # chroma_min = chroma.min(axis=1)
    # chroma_max = chroma.max(axis=1)
    # chroma_feature = numpy.concatenate((chroma_mean, chroma_min, chroma_max))
    #
    # # Extracting tonnetz feature
    # tntz = get_tonnetz(file_path)
    # tntz_mean = tntz.mean(axis=1)
    # tntz_min = tntz.min(axis=1)
    # tntz_max = tntz.max(axis=1)
    # tntz_feature = numpy.concatenate((tntz_mean, tntz_min, tntz_max))
    #
    #    X_3D = np.expand_dims(X, axis=0)

    # return X_3D

    features = np.concatenate((mfcc_feature, mel_spectrogram_feature))
    features_3D = np.expand_dims(features, axis=0)
    return features_3D


def is_meeting_silence_threshold():

    if not len(global_frames) > 24:
        return False

    # last_frames = np.array(
    #     struct.unpack(str(96 * CHUNK) + 'B', np.stack((global_frames[-1], global_frames[-2], global_frames[-3], global_frames[-4],
    #                                                    global_frames[-5], global_frames[-6], global_frames[-7], global_frames[-8],
    #                                                    global_frames[-9], global_frames[-10], global_frames[-11], global_frames[-12],
    #                                                    global_frames[-13], global_frames[-14], global_frames[-15], global_frames[-16],
    #                                                    global_frames[-17], global_frames[-18], global_frames[-19], global_frames[-20],
    #                                                    global_frames[-21], global_frames[-22], global_frames[-23], global_frames[-24]),
    #                                                   axis=0)), dtype='b')
    # @TODO add real silence detection
    global_frames.clear()
    return True
    # return max(last_frames) < 100
    # Mean Silence with *24 modifier : -0.685
    # Mean Normales Reden : -0.638 / -0.608
    # Mean Wirklich laut: 0.139


async def get_ser_result_from_server_message(msg_content: str, websocket) -> None:
    # get the speech object from message string
    speech_buffer = await decode_speech_from_string(msg_content)
    write_string_to_wav_file(speech_buffer)
    if is_meeting_silence_threshold():
        return await recognize_emotions_from_wav_file()
    else:
        return None


async def handle_incoming_message_from_websocket(msg_content, msg_time, websocket):
    ser_result = await get_ser_result_from_server_message(msg_content, websocket)
    if ser_result != None:
        print('---')
        print(ser_result)
        print('---')
        ser_res_string = json.dumps(ser_result)
        # send the SER result back to the server (as a string)
        ser_result_message = json.dumps(
            [MSG_CODE['SER_RESULT'], ser_res_string, msg_time])
        await websocket.send(ser_result_message)


async def websocket_handler():
    async with connect(uri) as websocket:
        await websocket.send(json.dumps([MSG_CODE['CONNECT'], 'I bims: SER']))
        # keep websocket open
        while True:
            message = await websocket.recv()
            msg_json = json.loads(message)
            msg_code = msg_json[0]
            msg_content = msg_json[1]
            msg_time = msg_json[2]
            # only handle SER input messages
            if (msg_code == MSG_CODE['SER_INPUT']):
                await handle_incoming_message_from_websocket(msg_content, msg_time, websocket)


asyncio.run(websocket_handler())
