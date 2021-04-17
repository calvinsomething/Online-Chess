FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir Online-Chess
WORKDIR /Online-Chess
COPY ./requirements.txt .
COPY ./chess ./chess
COPY ./entrypoint.sh .
COPY ./daphne ./daphne
COPY ./worker ./worker
RUN apk add --update gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    && mkdir ./chess/nginx-static
EXPOSE 8000 8001
ENTRYPOINT [ "sh", "entrypoint.sh" ]
