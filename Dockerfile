# syntax=docker/dockerfile:1

FROM python:3.12.1-alpine3.19

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]
