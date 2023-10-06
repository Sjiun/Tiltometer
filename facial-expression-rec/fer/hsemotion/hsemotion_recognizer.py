# Copyright 2022 Andrey Savchenko
# https://github.com/HSE-asavchenko/hsemotion-onnx/blob/bd8a9882924b38e859ae7801305ae203cd71acc1/hsemotion_onnx/facial_emotions.py
# Copyright for modifications 2023 Thorben Ortmann
#
# Licensed under the Apache License, Version 2.0 (the "License");

from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


class HSEmotionRecognizer:
    def __init__(self):
        self.model_name = 'enet_b2_7'
        self.img_size = 260

        path = f'{Path(__file__).parent / self.model_name}.onnx'
        self.ort_session = ort.InferenceSession(path, providers=['CPUExecutionProvider'])

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        :param image: numpy array of shape (height, width, channels)
        :return: numpy array of shape (1, channels, height, width)
        """
        x = cv2.resize(image, (self.img_size, self.img_size)) / 255
        # Normalize color channels
        x[..., 0] = (x[..., 0] - 0.485) / 0.229
        x[..., 1] = (x[..., 1] - 0.456) / 0.224
        x[..., 2] = (x[..., 2] - 0.406) / 0.225
        return x.transpose(2, 0, 1).astype("float32")[np.newaxis, ...]

    def predict_emotions(self, face_img: np.ndarray) -> list[float]:
        """
        :param face_img: numpy array of shape (height, width, channels)
        :return: probability scores in the following order:
            0: 'Anger', 1: 'Disgust', 2: 'Fear', 3: 'Happiness', 4: 'Neutral', 5: 'Sadness', 6: 'Surprise'
        """
        e_scores = self.ort_session.run(None, {"input": self.preprocess(face_img)})[0][0]
        x = e_scores
        e_x = np.exp(x - np.max(x)[np.newaxis])
        e_x = e_x / e_x.sum()[None]
        return e_x.tolist()
