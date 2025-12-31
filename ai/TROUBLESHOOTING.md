# 트러블슈팅 가이드

이 문서는 IF ML Service 개발 및 운영 중 발생하는 문제와 해결 방법을 정리합니다.

## 목차
1. [Import 오류](#import-오류)
2. [의존성 문제](#의존성-문제)
3. [Pydantic 버전 호환성](#pydantic-버전-호환성)
4. [모델 로딩 오류](#모델-로딩-오류)
5. [서버 실행 오류](#서버-실행-오류)
6. [에러 처리 및 예외 처리](#에러-처리-및-예외-처리)

---

## Import 오류

### 문제: `ModuleNotFoundError: No module named 'pandas'`

**증상:**
```
ModuleNotFoundError: No module named 'pandas'
```

**원인:**
- `features/health_features.py`에서 pandas를 import하지만 requirements.txt에 포함되지 않음
- 가상환경에 pandas가 설치되지 않음

**해결 방법:**
```bash
cd /Users/m/IF/ai
source venv/bin/activate
pip install pandas
pip freeze > requirements.txt  # requirements.txt 업데이트
```

**참고:**
- 현재 코드에서 pandas는 실제로 사용되지 않으므로, import를 제거하거나 유지할 수 있습니다.
- 향후 데이터 분석이 필요하면 pandas를 유지하는 것이 좋습니다.

---

### 문제: `ImportError: cannot import name 'HealthScoreRequest'`

**증상:**
```
ImportError: cannot import name 'HealthScoreRequest' from 'schemas.health'
```

**원인:**
- `schemas/health.py` 파일이 비어있거나 클래스가 정의되지 않음
- 파일이 삭제되었거나 내용이 손실됨

**해결 방법:**
1. `schemas/health.py` 파일 확인:
```bash
cat ai/schemas/health.py
```

2. 필요한 클래스가 모두 정의되어 있는지 확인:
   - `HealthScoreRequest`
   - `HealthScoreResponse`
   - `ErrorResponse`
   - `RiskLevel` (Enum)

3. 파일이 손상된 경우 Git에서 복원:
```bash
git checkout ai/schemas/health.py
```

---

### 문제: `cannot import name 'get_health_model' from 'models.loader'`

**증상:**
```
ImportError: cannot import name 'get_health_model' from 'models.loader'
```

**원인:**
- `models/loader.py` 파일이 없거나 함수가 정의되지 않음

**해결 방법:**
1. `models/loader.py` 파일 생성 확인:
```bash
ls -la ai/models/loader.py
```

2. 파일이 없으면 생성:
```python
# models/loader.py
import pickle
import os
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

_health_model: Optional[object] = None

def get_health_model():
    global _health_model
    if _health_model is None:
        logger.warning("건강점수 모델이 로드되지 않았습니다.")
        return None
    return _health_model

def load_health_model(model_path: Optional[str] = None) -> bool:
    # 구현...
    pass

def load_models():
    # 구현...
    pass
```

---

## 의존성 문제

### 문제: `pydantic-settings` 모듈 없음

**증상:**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**원인:**
- Pydantic v2에서 설정 관리를 위해 `pydantic-settings` 패키지가 별도로 분리됨

**해결 방법:**
```bash
cd /Users/m/IF/ai
source venv/bin/activate
pip install pydantic-settings
pip freeze > requirements.txt
```

---

## Pydantic 버전 호환성

### 문제: `'schema_extra' has been renamed to 'json_schema_extra'`

**증상:**
```
UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
```

**원인:**
- Pydantic v2에서 `Config.schema_extra`가 `Config.json_schema_extra`로 변경됨

**해결 방법:**
모든 `schemas/*.py` 파일에서 다음 변경:
```python
# 변경 전 (Pydantic v1)
class Config:
    schema_extra = {
        "example": {...}
    }

# 변경 후 (Pydantic v2)
class Config:
    json_schema_extra = {
        "example": {...}
    }
```

**영향받는 파일:**
- `schemas/health.py`
- 기타 모든 Pydantic 모델이 있는 파일

---

## 모델 로딩 오류

### 문제: 모델 파일을 찾을 수 없음

**증상:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/health_model.pkl'
```

**원인:**
- 학습된 모델 파일이 `models/` 디렉토리에 없음
- 모델 파일 경로가 잘못 설정됨

**해결 방법:**
1. 모델 파일 확인:
```bash
ls -la ai/models/*.pkl
```

2. 모델이 없으면:
   - 모델 학습 스크립트 실행
   - 또는 기본 규칙 기반 로직 사용 (현재 구현됨)

3. 모델 경로 확인:
```python
# config/settings.py
HEALTH_MODEL_PATH: str = "models/health_model.pkl"
```

**참고:**
- 현재 구현은 모델이 없어도 규칙 기반으로 동작합니다.
- 모델이 없으면 경고만 출력하고 기본값을 사용합니다.

---

## 서버 실행 오류

### 문제: `Error loading ASGI app. Could not import module "main"`

**증상:**
```
ERROR: Error loading ASGI app. Could not import module "main".
```

**원인:**
- 현재 디렉토리가 잘못됨 (루트에서 실행)
- Python 경로 문제

**해결 방법:**
1. 올바른 디렉토리에서 실행:
```bash
cd /Users/m/IF/ai
source venv/bin/activate
uvicorn main:app --reload
```

2. 또는 실행 스크립트 사용:
```bash
cd /Users/m/IF/ai
./run.sh
```

---

### 문제: `uvicorn: command not found`

**증상:**
```
uvicorn: command not found
```

**원인:**
- 가상환경이 활성화되지 않음
- uvicorn이 설치되지 않음

**해결 방법:**
```bash
cd /Users/m/IF/ai
source venv/bin/activate
pip install uvicorn[standard]
```

---

## 에러 처리 및 예외 처리

### 에러 처리 구조

이 프로젝트는 계층화된 에러 처리 시스템을 사용합니다:

```
API 레이어 (api/v1/health.py)
  ↓
서비스 레이어 (services/health_service.py)
  ↓
유틸리티 레이어 (utils/validators.py, utils/exceptions.py)
  ↓
전역 예외 핸들러 (main.py)
```

### 커스텀 예외 클래스

**위치:** `utils/exceptions.py`

```python
BaseAPIException          # 기본 예외 클래스
├── ValidationError      # 입력 검증 오류 (400)
├── ModelLoadError       # 모델 로드 오류 (503)
├── ModelPredictionError # 모델 예측 오류 (500)
└── ServiceError         # 서비스 레이어 오류 (500)
```

### 에러 응답 형식

모든 에러는 `ErrorResponse` 스키마를 따릅니다:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "키는 100-250cm 범위여야 합니다. 입력값: 300cm",
  "details": {
    "field": "height_cm",
    "value": 300,
    "constraint": "100-250cm"
  }
}
```

### 문제: `VALIDATION_ERROR` - 입력 검증 실패

**증상:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "키는 100-250cm 범위여야 합니다. 입력값: 300cm",
  "details": {
    "field": "height_cm",
    "value": 300,
    "constraint": "100-250cm"
  }
}
```

**원인:**
- 입력값이 유효성 검증 규칙을 위반함
- `utils/validators.py`의 `validate_health_input()` 함수에서 검증 실패

**해결 방법:**
1. 요청 데이터 확인:
```bash
curl -X POST http://localhost:5000/api/ml/v1/health/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "senior_profile_id": 1,
    "height_cm": 170,  # 100-250 범위 내
    "weight_kg": 75.5,  # 20-200 범위 내
    "chronic_conditions": {},
    "risk_flags": {}
  }'
```

2. 검증 규칙 확인:
   - `height_cm`: 100-250cm
   - `weight_kg`: 20-200kg
   - `chronic_conditions`: 딕셔너리, 값은 boolean
   - `risk_flags`: 딕셔너리, 값은 0-1 범위의 숫자

**참고:**
- 모든 검증 오류는 `ValidationError`로 변환되어 400 상태 코드로 반환됩니다.
- `details` 필드에 구체적인 필드명과 제약 조건이 포함됩니다.

---

### 문제: `MODEL_LOAD_ERROR` - 모델 로드 실패

**증상:**
```json
{
  "error_code": "MODEL_LOAD_ERROR",
  "message": "건강점수 모델 파일을 찾을 수 없습니다: models/health_model.pkl",
  "details": {
    "model_path": "models/health_model.pkl"
  }
}
```

**원인:**
- 모델 파일이 존재하지 않음
- 모델 파일 경로가 잘못 설정됨
- 모델 파일이 손상됨

**해결 방법:**
1. 모델 파일 확인:
```bash
ls -la ai/models/*.pkl
```

2. 모델이 없으면:
   - 규칙 기반 로직으로 자동 폴백 (서버는 정상 동작)
   - 모델 학습 스크립트 실행하여 모델 생성

3. 모델 경로 확인:
```python
# config/settings.py
HEALTH_MODEL_PATH: str = "models/health_model.pkl"
```

**참고:**
- 모델이 없어도 서버는 정상적으로 동작합니다.
- ML 모델 예측 실패 시 기본값(0.5)을 사용하여 규칙 기반 점수만 계산합니다.

---

### 문제: `MODEL_PREDICTION_ERROR` - 모델 예측 실패

**증상:**
```json
{
  "error_code": "MODEL_PREDICTION_ERROR",
  "message": "모델 예측 중 오류가 발생했습니다.",
  "details": {
    "error": "AttributeError: 'NoneType' object has no attribute 'predict'"
  }
}
```

**원인:**
- 모델 객체가 None
- 모델에 `predict` 메서드가 없음
- 피처 벡터 형식이 잘못됨

**해결 방법:**
1. 모델 로드 확인:
```python
from models.loader import get_health_model
model = get_health_model()
if model is None:
    print("모델이 로드되지 않았습니다.")
```

2. 모델 형식 확인:
   - 모델이 scikit-learn 형식인지 확인
   - `predict` 메서드가 있는지 확인

3. 피처 벡터 확인:
   - 피처 개수가 모델 입력과 일치하는지 확인

**참고:**
- 모델 예측 실패 시 자동으로 기본값(0.5)을 사용합니다.
- 경고 로그만 출력하고 서비스는 계속 동작합니다.

---

### 문제: `SERVICE_ERROR` - 서비스 레이어 오류

**증상:**
```json
{
  "error_code": "SERVICE_ERROR",
  "message": "건강점수 계산 중 오류가 발생했습니다.",
  "details": {
    "error_type": "KeyError",
    "error_message": "'bmi_factor'"
  }
}
```

**원인:**
- 피처 추출 실패
- 점수 계산 로직 오류
- 예상치 못한 예외 발생

**해결 방법:**
1. 로그 확인:
```bash
# 서버 로그에서 상세한 스택 트레이스 확인
tail -f logs/app.log | grep ERROR
```

2. 피처 추출 확인:
```python
from features.health_features import HealthFeatureExtractor
features = HealthFeatureExtractor.extract_features(
    height_cm=170,
    weight_kg=75.5,
    chronic_conditions={},
    risk_flags={}
)
print(features)  # 모든 필수 키가 있는지 확인
```

3. 디버그 모드 활성화:
```python
# config/settings.py
DEBUG = True  # 상세한 에러 정보 포함
```

**참고:**
- `DEBUG=True`일 때만 `details`에 스택 트레이스가 포함됩니다.
- 프로덕션 환경에서는 보안을 위해 스택 트레이스를 숨깁니다.

---

### 문제: `INTERNAL_SERVER_ERROR` - 예상치 못한 오류

**증상:**
```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
  "details": null  # 또는 DEBUG=True일 때 스택 트레이스
}
```

**원인:**
- 예외 처리되지 않은 예외
- 시스템 레벨 오류
- 메모리 부족 등

**해결 방법:**
1. 로그 확인:
```bash
# 전체 스택 트레이스 확인
grep -A 50 "예상치 못한 오류" logs/app.log
```

2. 서버 상태 확인:
```bash
# 메모리 사용량
free -h

# 디스크 공간
df -h

# 프로세스 상태
ps aux | grep uvicorn
```

3. 재시작:
```bash
cd /Users/m/IF/ai
./run.sh
```

**참고:**
- 이 오류는 전역 예외 핸들러에서 처리됩니다.
- 모든 예외는 로그에 기록되므로 로그를 확인하세요.

---

### 에러 처리 테스트

**1. 입력 검증 오류 테스트:**
```bash
# 잘못된 키 값
curl -X POST http://localhost:5000/api/ml/v1/health/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "senior_profile_id": 1,
    "height_cm": 300,  # 범위 초과
    "weight_kg": 75.5,
    "chronic_conditions": {},
    "risk_flags": {}
  }'
```

**예상 응답:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "키는 100-250cm 범위여야 합니다. 입력값: 300cm",
  "details": {
    "field": "height_cm",
    "value": 300,
    "constraint": "100-250cm"
  }
}
```

**2. 정상 요청 테스트:**
```bash
curl -X POST http://localhost:5000/api/ml/v1/health/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "senior_profile_id": 1,
    "height_cm": 170,
    "weight_kg": 75.5,
    "chronic_conditions": {
      "hypertension": true
    },
    "risk_flags": {
      "mobility_limited": 0.3
    }
  }'
```

**예상 응답:**
```json
{
  "senior_profile_id": 1,
  "health_score": 78.5,
  "risk_level": "medium",
  "components": {
    "bmi_factor": 0.90,
    "chronic_factor": 0.65,
    "mobility_factor": 0.95,
    "cognitive_factor": 0.95,
    "age_factor": 0.85
  },
  "recommendations": [
    "혈압 관리 필요",
    "규칙적인 운동 권장"
  ]
}
```

---

### 에러 처리 체크리스트

에러 처리가 제대로 작동하는지 확인:

- [ ] `ValidationError`가 400 상태 코드로 반환됨
- [ ] `ModelLoadError`가 503 상태 코드로 반환됨
- [ ] `ServiceError`가 500 상태 코드로 반환됨
- [ ] 모든 에러 응답이 `ErrorResponse` 스키마를 따름
- [ ] `details` 필드에 구체적인 정보가 포함됨
- [ ] 로그에 모든 예외가 기록됨
- [ ] 모델이 없어도 서비스가 정상 동작함
- [ ] 디버그 모드에서만 스택 트레이스가 포함됨

---

## 일반적인 문제 해결 절차

### 1. 가상환경 확인
```bash
cd /Users/m/IF/ai
source venv/bin/activate
which python  # /Users/m/IF/ai/venv/bin/python 이어야 함
```

### 2. 의존성 재설치
```bash
pip install -r requirements.txt
```

### 3. Import 테스트
```bash
python -c "from main import app; print('✅ OK')"
```

### 4. 서버 실행 테스트
```bash
uvicorn main:app --reload --port 8000
```

---

## 로그 확인

### 문제 디버깅을 위한 로그 레벨 설정

```python
# utils/logger.py 또는 main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 주요 로그 위치
- 애플리케이션 로그: 콘솔 출력
- 모델 로딩 로그: `models/loader.py`
- 서비스 로그: `services/health_service.py`

---

## 빠른 체크리스트

서버 실행 전 확인사항:

- [ ] 가상환경 활성화됨
- [ ] 모든 의존성 설치됨 (`pip install -r requirements.txt`)
- [ ] `schemas/health.py`에 모든 클래스 정의됨
- [ ] `models/loader.py` 파일 존재
- [ ] `utils/validators.py` 파일 존재
- [ ] `utils/exceptions.py` 파일 존재 (커스텀 예외 클래스)
- [ ] `config/settings.py` 파일 존재
- [ ] Pydantic v2 호환성 확인 (`json_schema_extra` 사용)
- [ ] 현재 디렉토리가 `ai/`인지 확인
- [ ] 전역 예외 핸들러가 `main.py`에 등록됨

---

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Pydantic v2 마이그레이션 가이드](https://docs.pydantic.dev/latest/migration/)
- [Python 가상환경 가이드](https://docs.python.org/3/tutorial/venv.html)

---

## 문제가 해결되지 않으면

1. 에러 메시지 전체 복사
2. 관련 파일 내용 확인
3. Git 상태 확인 (`git status`)
4. 최근 변경사항 확인 (`git log`)

---

---

## 에러 처리 아키텍처 요약

### 에러 처리 흐름도

```
클라이언트 요청
    ↓
API 엔드포인트 (api/v1/health.py)
    ↓ 예외 발생 시
서비스 레이어 (services/health_service.py)
    ↓ 예외 발생 시
유틸리티 레이어 (utils/validators.py, utils/exceptions.py)
    ↓
전역 예외 핸들러 (main.py)
    ↓
ErrorResponse JSON 응답
```

### 예외 타입별 처리

| 예외 타입 | HTTP 상태 코드 | 사용 시점 |
|---------|--------------|----------|
| `ValidationError` | 400 Bad Request | 입력 검증 실패 |
| `ModelLoadError` | 503 Service Unavailable | 모델 로드 실패 |
| `ModelPredictionError` | 500 Internal Server Error | 모델 예측 실패 |
| `ServiceError` | 500 Internal Server Error | 서비스 로직 오류 |
| `ValueError` | 400 Bad Request | 일반적인 값 오류 |
| 기타 예외 | 500 Internal Server Error | 예상치 못한 오류 |

### 에러 응답 예시

**입력 검증 오류:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "키는 100-250cm 범위여야 합니다. 입력값: 300cm",
  "details": {
    "field": "height_cm",
    "value": 300,
    "constraint": "100-250cm"
  }
}
```

**서비스 오류:**
```json
{
  "error_code": "SERVICE_ERROR",
  "message": "건강점수 계산 중 오류가 발생했습니다.",
  "details": {
    "error_type": "KeyError",
    "error_message": "'bmi_factor'"
  }
}
```

---

**최종 업데이트:** 2025-01-01
**작성자:** AI Assistant
**주요 변경사항:** 에러 처리 시스템 추가 및 트러블슈팅 문서 보완
