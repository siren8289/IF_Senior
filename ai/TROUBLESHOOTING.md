# 트러블슈팅 가이드

이 문서는 IF ML Service 개발 및 운영 중 발생하는 문제와 해결 방법을 정리합니다.

## 목차
1. [Import 오류](#import-오류)
2. [의존성 문제](#의존성-문제)
3. [Pydantic 버전 호환성](#pydantic-버전-호환성)
4. [모델 로딩 오류](#모델-로딩-오류)
5. [서버 실행 오류](#서버-실행-오류)

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
- [ ] `config/settings.py` 파일 존재
- [ ] Pydantic v2 호환성 확인 (`json_schema_extra` 사용)
- [ ] 현재 디렉토리가 `ai/`인지 확인

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

**최종 업데이트:** 2025-12-31
**작성자:** AI Assistant
