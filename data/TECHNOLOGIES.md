# 프로젝트 사용 기술 목록

본 문서는 `data/` 디렉토리와 `ai/` 디렉토리에서 사용된 기술 스택을 정리한 문서입니다.

---

## 📚 핵심 라이브러리

### 1. 데이터 처리 및 분석

#### pandas
- **용도**: 데이터 로드, 전처리, 데이터 분석, 그룹화 연산
- **주요 사용 기능**:
  - `pd.read_csv()`: CSV 파일 읽기
  - `pd.to_csv()`: CSV 파일 저장
  - `pd.to_numeric()`: 숫자형 변환
  - `pd.cut()`: 연속형 변수를 범주형으로 변환
  - `pd.groupby()`: 그룹별 집계
  - `dropna()`: 결측치 제거
  - `rename()`: 컬럼명 변경
  - `map()`: 값 매핑/인코딩

**사용 파일**:
- 모든 Python 스크립트 (14개 파일)

---

### 2. 머신러닝 프레임워크

#### scikit-learn (sklearn)
- **용도**: Baseline 모델 구축, 전처리, 평가 지표

**주요 모듈 및 클래스**:

##### 모델
- `LogisticRegression`: 이진 분류 Baseline 모델
- `MLPClassifier`: 다중 분류 신경망 모델
- `MLPRegressor`: 회귀 신경망 모델

##### 데이터 분할
- `train_test_split`: 학습/테스트 데이터 분할
  - `stratify` 파라미터로 클래스 균형 유지

##### 전처리
- `StandardScaler`: 표준화 (평균 0, 표준편차 1)
- `OneHotEncoder`: 범주형 변수 원-핫 인코딩
- `LabelEncoder`: 타깃 변수 라벨 인코딩
- `ColumnTransformer`: 컬럼별 전처리 파이프라인
- `Pipeline`: 전처리 + 모델 파이프라인

##### 평가 지표
- `accuracy_score`: 정확도
- `precision_score`: 정밀도
- `recall_score`: 재현율
- `f1_score`: F1 점수
- `r2_score`: R² 점수 (회귀)
- `mean_squared_error`: 평균 제곱 오차
- `mean_absolute_error`: 평균 절대 오차
- `confusion_matrix`: 혼동 행렬
- `classification_report`: 분류 리포트

**사용 파일**:
- `03_baseline_model/train_health_model.py`
- `05_dl_experiment/Digital_Gap/train_dl_model.py`
- `05_dl_experiment/Job_Accident_Risk/train_dl_model.py`
- `05_dl_experiment/Health_Condition/train_health_mlp.py`

---

#### PyTorch
- **용도**: 딥러닝 모델 실험 및 구조적 확장 가능성 검증

**주요 모듈 및 클래스**:

##### 핵심 모듈
- `torch`: 텐서 연산
- `torch.nn`: 신경망 모듈
- `torch.utils.data`: 데이터 로더

##### 신경망 구성 요소
- `nn.Module`: 신경망 기본 클래스
- `nn.Sequential`: 순차적 레이어 구성
- `nn.Linear`: 완전 연결 레이어
- `nn.ReLU`: ReLU 활성화 함수
- `nn.Dropout`: 드롭아웃 (과적합 방지)
- `nn.Sigmoid`: 시그모이드 활성화 함수

##### 손실 함수
- `nn.BCELoss`: 이진 교차 엔트로피 손실

##### 최적화
- `torch.optim.Adam`: Adam 옵티마이저

##### 데이터 처리
- `Dataset`: 커스텀 데이터셋 클래스
- `DataLoader`: 배치 데이터 로딩
  - `batch_size`: 배치 크기
  - `shuffle`: 데이터 셔플 여부

**사용 파일**:
- `05_dl_experiment/Health_Condition/train_health_mlp.py`

---

### 3. 시각화

#### matplotlib
- **용도**: EDA 시각화, 통계 그래프 생성

**주요 기능**:
- `matplotlib.pyplot`: 플롯 생성
- `plt.subplots()`: 서브플롯 생성
- `plt.bar()`: 막대 그래프
- `plt.savefig()`: 이미지 저장
- `plt.close()`: 메모리 해제

**사용 파일**:
- `02_analysis/run_health_eda.py`

---

### 4. 유틸리티

#### pathlib
- **용도**: 경로 관리, 파일 시스템 작업
- **주요 기능**:
  - `Path()`: 경로 객체 생성
  - `Path(__file__).parent`: 현재 파일의 부모 디렉토리
  - `.exists()`: 파일/디렉토리 존재 확인
  - `.mkdir()`: 디렉토리 생성

**사용 파일**:
- 모든 경로 표준화된 파일 (9개 파일)

---

#### collections
- **용도**: 데이터 구조 및 유틸리티
- **주요 기능**:
  - `Counter`: 클래스 분포 확인 (stratify 안전 처리용)

**사용 파일**:
- `03_baseline_model/train_health_model.py`
- `05_dl_experiment/Health_Condition/train_health_mlp.py`
- `05_dl_experiment/Digital_Gap/train_dl_model.py`

---

#### json
- **용도**: 메트릭 결과 저장
- **주요 기능**:
  - `json.dump()`: JSON 파일 저장
  - `json.dumps()`: JSON 문자열 생성

**사용 파일**:
- `03_baseline_model/train_health_model.py`

---

#### numpy
- **용도**: 수치 연산
- **주요 기능**:
  - `np.sqrt()`: 제곱근 계산 (RMSE)
  - `np.full_like()`: 배열 생성 (Baseline 비교)

**사용 파일**:
- `05_dl_experiment/Job_Accident_Risk/train_dl_model.py`

---

## 🏗️ 아키텍처 패턴

### 1. 데이터 파이프라인 구조

```
00_raw (원본 데이터)
  ↓
01_feature_source (정제된 Feature 데이터)
  ↓
02_analysis (EDA 및 분석)
  ↓
03_baseline_model (Baseline 모델 학습)
  ↓
05_dl_experiment (딥러닝 실험)
  ↓
04_result (최종 결과)
```

### 2. 모델 학습 전략

#### Baseline 모델 (sklearn)
- **목적**: 빠른 프로토타이핑, 해석 가능성
- **모델**: LogisticRegression, MLPClassifier, MLPRegressor
- **특징**:
  - Early stopping 지원
  - Validation fraction 설정
  - Stratified split 안전 처리

#### 딥러닝 모델 (PyTorch)
- **목적**: 구조적 확장 가능성 검증, 성능 실험
- **모델**: 커스텀 MLP (Multi-Layer Perceptron)
- **특징**:
  - 모듈화된 레이어 구조
  - Dropout으로 과적합 방지
  - Adam 옵티마이저 사용

---

## 🔧 주요 기술 기법

### 1. 데이터 전처리

#### 인코딩 전략
- **Feature Encoding**: 
  - 건강 점수: 매우나쁨(1) → 매우좋음(5)
  - 근로 의지: 약함(1) → 강함(3)
- **Target Encoding**:
  - 돌봄 필요도: 필요없음(0), 약간필요/많이필요(1)
- **범주형 인코딩**:
  - OneHotEncoder: 범주형 변수 원-핫 인코딩
  - LabelEncoder: 타깃 변수 라벨 인코딩

#### 정규화
- **StandardScaler**: 평균 0, 표준편차 1로 정규화
- **Min-Max 정규화**: 수동 구현 (job_score 생성 시)

### 2. 모델 학습 기법

#### 과적합 방지
- **Early Stopping**: 검증 손실 기반 조기 종료
- **Dropout**: 랜덤 노드 비활성화
- **Validation Fraction**: 검증 데이터 비율 설정

#### 데이터 분할
- **Stratified Split**: 클래스 비율 유지
- **안전 처리**: 클래스 불균형 시 자동으로 일반 split으로 전환

### 3. 평가 지표

#### 분류 문제
- Accuracy, Precision, Recall, F1 Score
- Confusion Matrix
- Classification Report

#### 회귀 문제
- R² Score
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Baseline 비교 (평균 예측)

---

## 📦 의존성 요약

### 필수 라이브러리
```python
pandas>=1.0.0
scikit-learn>=1.0.0
matplotlib>=3.0.0
numpy>=1.20.0
```

### 딥러닝 (선택적)
```python
torch>=1.10.0
```

### 표준 라이브러리
- `pathlib` (Python 3.4+)
- `json` (Python 표준)
- `collections` (Python 표준)

---

## 🎯 사용 사례별 기술 매핑

### 데이터 정제
- **기술**: pandas, pathlib
- **파일**: `01_feature_source/*/run_*.py`

### 탐색적 데이터 분석 (EDA)
- **기술**: pandas, matplotlib
- **파일**: `02_analysis/run_*.py`

### Baseline 모델 학습
- **기술**: scikit-learn, pandas
- **파일**: `03_baseline_model/train_*.py`

### 딥러닝 실험
- **기술**: PyTorch, scikit-learn, pandas
- **파일**: `05_dl_experiment/*/train_*.py`

### 점수 생성
- **기술**: pandas (규칙 기반)
- **파일**: `03_baseline_model/make_*_score.py`

---

## 📝 참고 사항

### 기술 선택 이유

1. **sklearn vs PyTorch 병행 사용**
   - sklearn: Baseline 모델 (해석 가능, 빠른 프로토타이핑)
   - PyTorch: 실험/확장 모델 (구조적 확장 가능성 검증)

2. **경로 관리**
   - `pathlib.Path` 사용으로 크로스 플랫폼 호환성 확보
   - `__file__` 기준 상대 경로로 실행 위치 독립성 확보

3. **데이터 검증**
   - 필수 컬럼 존재 확인
   - 파일 존재 여부 확인
   - 결측치 처리

---

## 🌐 API 구축 (ai/ 디렉토리)

### 1. 웹 프레임워크

#### FastAPI
- **용도**: RESTful API 서버 구축, ML 모델 서빙
- **주요 기능**:
  - `FastAPI`: 애플리케이션 인스턴스 생성
  - `APIRouter`: 라우터 모듈화
  - `@router.post()`, `@router.get()`: HTTP 메서드 데코레이터
  - `response_model`: 응답 스키마 정의
  - `status_code`: HTTP 상태 코드 설정
  - `summary`, `description`: API 문서화
  - `responses`: 응답 예시 정의

**주요 엔드포인트**:
- `/api/ml/v1/health/calculate`: 건강점수 계산
- `/api/v1/job-risk/predict`: 산업재해 리스크 예측
- `/api/v1/matching/score`: 매칭 점수 계산
- `/health`: 헬스 체크

**사용 파일**:
- `ai/main.py`
- `ai/api/v1/health.py`
- `ai/api/v1/job_risk.py`
- `ai/api/v1/matching.py`

---

#### Uvicorn
- **용도**: ASGI 서버 (FastAPI 실행)
- **주요 기능**:
  - `uvicorn.run()`: 서버 실행
  - `reload`: 개발 모드 자동 리로드
  - `host`, `port`: 서버 주소 설정
  - `log_level`: 로그 레벨 설정

**사용 파일**:
- `ai/main.py`

---

### 2. 데이터 검증 및 스키마

#### Pydantic
- **용도**: 요청/응답 데이터 검증, 타입 안전성 보장
- **주요 기능**:
  - `BaseModel`: 데이터 모델 기본 클래스
  - `Field()`: 필드 검증 및 메타데이터
    - `ge`, `le`: 범위 검증
    - `description`: 필드 설명
    - `default_factory`: 기본값 팩토리
  - `Enum`: 열거형 타입
  - `json_schema_extra`: OpenAPI 스키마 확장

**주요 모델**:
- `HealthScoreRequest`, `HealthScoreResponse`
- `JobRiskRequest`, `JobRiskResponse`
- `MatchingRequest`, `MatchingResponse`
- `ErrorResponse`

**사용 파일**:
- `ai/schemas/health.py`
- `ai/schemas/job_risk.py`
- `ai/schemas/matching.py`

---

#### pydantic-settings
- **용도**: 환경 변수 및 설정 관리
- **주요 기능**:
  - `BaseSettings`: 설정 클래스 기본
  - `env_file`: 환경 변수 파일 지정
  - `case_sensitive`: 대소문자 구분 설정

**사용 파일**:
- `ai/config/settings.py`

---

### 3. 미들웨어 및 보안

#### CORS (Cross-Origin Resource Sharing)
- **용도**: 프론트엔드와의 통신 허용
- **구현**:
  - `CORSMiddleware`: CORS 미들웨어
  - `allow_origins`: 허용할 오리진 목록
  - `allow_credentials`: 인증 정보 허용
  - `allow_methods`, `allow_headers`: 메서드/헤더 허용

**사용 파일**:
- `ai/main.py`

---

### 4. 예외 처리

#### 커스텀 예외 클래스
- **구조**:
  - `BaseAPIException`: 기본 예외 클래스
  - `ValidationError`: 입력 검증 오류
  - `ModelLoadError`: 모델 로드 오류
  - `ModelPredictionError`: 모델 예측 오류
  - `ServiceError`: 서비스 레이어 오류

**예외 핸들러**:
- `@app.exception_handler()`: 전역 예외 핸들러
- `HTTPException`: FastAPI HTTP 예외
- 상태 코드별 자동 매핑

**사용 파일**:
- `ai/utils/exceptions.py`
- `ai/main.py`

---

### 5. 로깅

#### Python logging
- **용도**: 애플리케이션 로그 관리
- **주요 기능**:
  - `logging.getLogger()`: 로거 인스턴스 생성
  - `setup_logger()`: 로거 설정
  - `JSONFormatter`: JSON 형식 로그 포맷터
  - 로그 레벨: DEBUG, INFO, WARNING, ERROR

**사용 파일**:
- `ai/utils/logger.py`
- 모든 서비스 및 API 파일

---

### 6. 모델 관리

#### pickle
- **용도**: 학습된 ML 모델 직렬화/역직렬화
- **주요 기능**:
  - `pickle.load()`: 모델 파일 로드
  - `pickle.dump()`: 모델 파일 저장
  - 전역 모델 캐시 관리

**모델 로딩 전략**:
- 앱 시작 시 모델 로드 (`@app.on_event("startup")`)
- 모델 없을 경우 규칙 기반 폴백
- `lru_cache`를 통한 모델 캐싱

**사용 파일**:
- `ai/models/loader.py`
- `ai/models/models.py`

---

### 7. 피처 엔지니어링

#### Feature Extraction 클래스
- **구조**:
  - `HealthFeatureExtractor`: 건강 정보 피처 추출
  - `JobRiskFeatureEngineer`: 산업재해 리스크 피처 추출
  - `MatchingFeatureEngineer`: 매칭 점수 피처 추출

**주요 기능**:
- BMI 계산 및 정규화
- 만성질환 개수 계산
- 위험 지표 변환
- 스킬/경력/학력 매칭 비율 계산

**사용 파일**:
- `ai/features/health_features.py`
- `ai/features/job_risk_features.py`
- `ai/features/matching_features.py`

---

### 8. 서비스 레이어

#### Service 클래스 패턴
- **구조**:
  - `HealthScoreService`: 건강점수 계산 서비스
  - `JobRiskService`: 산업재해 리스크 예측 서비스
  - `MatchingService`: 매칭 점수 계산 서비스

**주요 기능**:
- 피처 추출
- 모델 예측 (또는 규칙 기반 계산)
- 점수 정규화 및 앙상블
- 위험 수준 판정
- 권장사항 생성

**사용 파일**:
- `ai/services/health_service.py`
- `ai/services/job_risk_service.py`
- `ai/services/matching_service.py`

---

### 9. 입력 검증

#### Validator 함수
- **용도**: API 입력 데이터 검증
- **주요 기능**:
  - `validate_health_input()`: 건강점수 입력 검증
  - `validate_bmi()`: BMI 계산 및 검증
  - 범위 검증 (키, 체중, 위험 지표)
  - 타입 검증

**사용 파일**:
- `ai/utils/validators.py`

---

### 10. OpenAPI/Swagger

#### 자동 API 문서화
- **용도**: API 스펙 문서 자동 생성
- **주요 기능**:
  - `get_openapi()`: OpenAPI 스키마 생성
  - `/docs`: Swagger UI
  - `/redoc`: ReDoc UI
  - `custom_openapi()`: 커스텀 스키마 생성

**사용 파일**:
- `ai/main.py`
- `ai/openApi/v1/swagger.yaml`
- `ai/openApi/v2/swagger.yaml`

---

## 🏗️ API 아키텍처 패턴

### 1. 레이어드 아키텍처

```
API Layer (FastAPI Router)
  ↓
Service Layer (Business Logic)
  ↓
Feature Engineering Layer
  ↓
Model Layer (ML Models)
```

### 2. 디렉토리 구조

```
ai/
├── api/v1/          # API 엔드포인트
├── services/        # 비즈니스 로직
├── features/        # 피처 엔지니어링
├── models/          # ML 모델 로딩
├── schemas/         # Pydantic 스키마
├── utils/           # 유틸리티 (예외, 검증, 로깅)
├── config/         # 설정 관리
└── main.py         # FastAPI 앱 진입점
```

### 3. 요청 처리 흐름

```
1. HTTP Request
   ↓
2. Pydantic Validation (Request Schema)
   ↓
3. Service Layer (Business Logic)
   ↓
4. Feature Extraction
   ↓
5. Model Prediction (or Rule-based)
   ↓
6. Response Formatting (Response Schema)
   ↓
7. HTTP Response
```

---

## 📦 API 의존성 요약

### 필수 라이브러리
```python
fastapi>=0.128.0
uvicorn>=0.40.0
pydantic>=2.12.0
pydantic-settings>=2.12.0
python-dotenv>=1.2.1
```

### ML 관련 (선택적)
```python
numpy>=2.4.0
pandas>=2.3.3
scikit-learn>=1.0.0  # 모델 예측용
```

### 표준 라이브러리
- `pickle` (모델 직렬화)
- `logging` (로깅)
- `json` (JSON 처리)
- `typing` (타입 힌팅)
- `enum` (열거형)
- `pathlib` (경로 관리)

---

## 🎯 API 사용 사례별 기술 매핑

### 건강점수 계산 API
- **기술**: FastAPI, Pydantic, HealthFeatureExtractor, ML 모델
- **파일**: `ai/api/v1/health.py`, `ai/services/health_service.py`

### 산업재해 리스크 예측 API
- **기술**: FastAPI, Pydantic, JobRiskFeatureEngineer
- **파일**: `ai/api/v1/job_risk.py`, `ai/services/job_risk_service.py`

### 매칭 점수 계산 API
- **기술**: FastAPI, Pydantic, MatchingFeatureEngineer
- **파일**: `ai/api/v1/matching.py`, `ai/services/matching_service.py`

---

## 📝 API 설계 원칙

### 1. RESTful API 설계
- 명확한 엔드포인트 네이밍
- HTTP 메서드 적절한 사용 (POST, GET)
- 상태 코드 표준 준수

### 2. 타입 안전성
- Pydantic을 통한 런타임 검증
- 타입 힌팅으로 개발 시점 오류 방지

### 3. 에러 처리
- 커스텀 예외 클래스로 명확한 에러 메시지
- 전역 예외 핸들러로 일관된 에러 응답

### 4. 문서화
- OpenAPI 자동 생성
- Swagger UI를 통한 인터랙티브 문서
- 요청/응답 예시 포함

### 5. 모델 폴백 전략
- ML 모델 없을 경우 규칙 기반 계산
- 서비스 안정성 확보

---

**작성일**: 2024년  
**업데이트**: data/ 및 ai/ 디렉토리 전체 Python 스크립트 분석 기준
