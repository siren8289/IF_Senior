#!/bin/bash

# Python 버전 확인
python --version

# 패키지 설치
pip install -r requirements.txt

# 테스트 실행
pytest tests/ -v

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
