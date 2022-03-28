FROM python:3.8

RUN mkdir /src
WORKDIR /src
COPY . /src
RUN apt-get update && apt-get install sqlite3
RUN pip install -r requirements.txt
