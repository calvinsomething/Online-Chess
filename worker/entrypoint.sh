#!/bin/sh

cd chess
python3 manage.py runworker --only-channels=http.* --only-channels=websocket.*