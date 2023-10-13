# Copyright 2023 Jiaxin Ye; Contact: jiaxin-ye@foxmail.com
# https://github.com/Jiaxin-Ye/TIM-Net_SER/blob/0511735616d23d24010428c5dc936cabfba95010/Code/main.py
# https://github.com/Jiaxin-Ye/TIM-Net_SER/blob/0511735616d23d24010428c5dc936cabfba95010/Code/extract_feature.py
# Copyright for modifications 2023 Thorben Ortmann


from pathlib import Path

import librosa
import numpy as np

from ser.timnet.ser_model import TIMNET_Model

MEAN_SIGNAL_LENGTH = 110000
RAVDESS_CLASS_LABELS = ('angry', 'calm', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise')
MODEL_PATH = Path(__file__).parent / '10-fold_weights_best_3.hdf5'


def get_model() -> TIMNET_Model:
    model = TIMNET_Model(input_shape=(215, 39), class_labels=RAVDESS_CLASS_LABELS,
                         filter_size=39, kernel_size=2, stack_size=1, dilation_size=8,
                         dropout=0.1, activation='relu', lr=0.001, beta1=0.93, beta2=0.98, epsilon=1e-8)
    model.load_weights(MODEL_PATH)
    return model


def get_feature(file_path: str,
                mean_signal_length: int = MEAN_SIGNAL_LENGTH,
                embed_len: int = 39) -> np.ndarray:
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

    mfcc = librosa.feature.mfcc(y=signal, sr=fs, n_mfcc=embed_len)
    feature = np.transpose(mfcc)
    return feature
