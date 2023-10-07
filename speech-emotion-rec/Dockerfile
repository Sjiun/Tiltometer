FROM python:3.8.10-slim

# Ensure Python output is direcly sent to terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y libsndfile1-dev \
    && apt-get clean

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ser /app/ser

CMD ["python", "-m", "ser.main"]
