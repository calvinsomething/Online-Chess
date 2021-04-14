FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /Online-Chess
COPY . .
RUN apk add --update gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo
EXPOSE 8000

