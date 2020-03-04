FROM python:3.7.5-slim-stretch

RUN apt-get -y update && apt-get -y install libpq-dev

WORKDIR /src/
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY database_utils.py database_utils.py
COPY models models
COPY app app

EXPOSE 8000
EXPOSE 8888
ENV PYTHONPATH=/src:/src/app
ENV JUPYTERPATH=/src:/src/app