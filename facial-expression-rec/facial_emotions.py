from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pathlib import Path
import cv2
import numpy as np
import onnxruntime as ort
    
    
class HSEmotionRecognizer:
    #supported values of model_name: enet_b0_8_best_vgaf, enet_b2_7
    def __init__(self, model_name):
        # if '_7' in model_name:
        #     self.idx_to_class={0: 'Anger', 1: 'Disgust', 2: 'Fear', 3: 'Happiness', 4: 'Neutral', 5: 'Sadness', 6: 'Surprise'}
        # else:
        #     self.idx_to_class={0: 'Anger', 1: 'Contempt', 2: 'Disgust', 3: 'Fear', 4: 'Happiness', 5: 'Neutral', 6: 'Sadness', 7: 'Surprise'}

        self.img_size=224 if '_b0_' in model_name else 260
        
        path=f'{Path(__file__).parent / model_name}.onnx'
        self.ort_session = ort.InferenceSession(path,providers=['CPUExecutionProvider'])
    
    def preprocess(self,img):
        x=cv2.resize(img,(self.img_size,self.img_size))/255
        x[..., 0] = (x[..., 0]-0.485)/0.229
        x[..., 1] = (x[..., 1]-0.456)/0.224
        x[..., 2] = (x[..., 2]-0.406)/0.225
        return x.transpose(2, 0, 1).astype("float32")[np.newaxis,...]

    def predict_emotions(self,face_img) -> list[int]:
        e_scores=self.ort_session.run(None,{"input": self.preprocess(face_img)})[0][0]
        x=e_scores
        e_x = np.exp(x - np.max(x)[np.newaxis])
        e_x = e_x / e_x.sum()[None]
        return e_x.tolist()
                      