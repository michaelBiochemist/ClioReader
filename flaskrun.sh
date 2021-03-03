#!/bin/bash
export FLASK_APP=app.py
#python3 -m flask run --host=0.0.0.0 --port=8080
gunicorn -b 127.0.0.1:8000 app:app 
#gunicorn -b :8080 -w 4 app:app 
