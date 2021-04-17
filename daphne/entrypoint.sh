#!/bin/sh

cd chess
python3 manage.py migrate
daphne -b 0.0.0.0 -p 8001 --ws-protocol "graphql-ws" --proxy-headers chess.asgi:application