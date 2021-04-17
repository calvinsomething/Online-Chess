#!/bin/sh

cd chess
python3 manage.py collectstatic --no-input
gunicorn -b :8000 --workers 2 chess.wsgi