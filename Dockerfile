# syntax=docker/dockerfile:1

FROM python:3.9.18-slim-bullseye

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN python3 -m pip install install -r requirements.txt

COPY static static
COPY templates templates
COPY videos videos
COPY flask_src flask_src
COPY app.py app.py
#COPY . .

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD [ "uwsgi", "--http", "0.0.0.0:8000", "--master", "--enable-threads", "-w", "app:app" ]
