FROM  python:3.10-slim

WORKDIR /fer/

COPY enet_b2_7.onnx .
COPY enet_b0_8_best_vgaf.onnx .
COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y \
        libgl1-mesa-glx \
        libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

# copy after install to allow caching installations
COPY input-img_example.base64 .
COPY __init__.py .
COPY face_detector.py .
COPY hs_emotion_recognizer.py .
COPY fer.py .

CMD ["python", "fer.py"]
