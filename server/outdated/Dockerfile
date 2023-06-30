FROM  python:3

WORKDIR /app/server

COPY pip_requirements.txt ./

# install pip packages from requirements file
RUN pip install -r pip_requirements.txt

# CMD ["python", "server.py"]
# RUN python server.py

# expose port for talking to services and host
# EXPOSE 5000