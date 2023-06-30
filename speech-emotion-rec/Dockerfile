FROM  python:3.10

WORKDIR /ser/

COPY requirements.txt .

RUN apt-get update 
# pyaudio requirements
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y

RUN pip install -r requirements.txt

# copy after install to allow caching installations
COPY model.h5 .
COPY input-audio_example.txt .
COPY ser.py .

# RUN apt-get install libgl1-mesa-glx -y

# required for librosa to work
RUN apt-get install libsndfile1-dev -y



CMD ["python", "ser.py"]

