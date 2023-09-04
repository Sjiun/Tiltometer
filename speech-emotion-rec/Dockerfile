FROM python:3.8.10-slim

WORKDIR /ser/

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y libsndfile1-dev \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

COPY 10-fold_weights_best_1.hdf5 .
COPY __init__.py .
COPY ser.py .
COPY ser_model.py .
COPY TIMNET.py .
COPY Common_Model.py .

CMD ["python", "ser.py"]
