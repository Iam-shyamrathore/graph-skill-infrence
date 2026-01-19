#!/bin/bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 --timeout 120 src.server:app
