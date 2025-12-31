#!/bin/bash
# FastAPI 서버 실행 스크립트

cd "$(dirname "$0")"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
