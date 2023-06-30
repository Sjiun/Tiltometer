FROM  python:3.10

WORKDIR /fer/

COPY requirements.txt .
COPY model.h5 .

RUN apt-get update 
RUN apt-get install libgl1-mesa-glx -y
RUN pip install -r requirements.txt

# copy after install to allow caching installations
COPY input-img_example.base64 .
COPY fer.py .

CMD ["python", "fer.py"]

