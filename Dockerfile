FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /Online-Chess
COPY . .
RUN apk add --update gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    # apk add --update libressl-dev \
    # && apk add musl-dev \
    # && apk add rust cargo \
    # && apk add build-base \
    # && apk add libffi-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo
EXPOSE 8000

