FROM python:3.7-alpine

RUN apk add --no-cache \
    musl-dev=1.1.24-r1 \
    gcc=9.2.0-r3
