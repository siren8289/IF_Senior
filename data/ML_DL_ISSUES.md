# ML/DL 코드 점검 결과 및 수정 완료 보고

> ✅ **수정 완료일**: 2024년  
> ✅ **주요 수정 사항**: 컬럼명 표준화, 경로 표준화, 검증 로직 추가, stratify 안전 처리

---

## 📋 목차

1. [발견된 문제점](#발견된-문제점)
2. [해결 과정](#해결-과정)
3. [수정 완료 사항](#수정-완료-사항)
4. [표준 규칙 (최종)](#표준-규칙-최종)

---

# 발견된 문제점

## 🔴 Critical: 컬럼 매핑 불일치 문제

### 문제 상황

#### 1. 원본 데이터 구조
```
02_노인실태조사.csv
├── 근로의지: "강함", "중간", "약함" (근로 의지 강도)
└── 돌봄필요도: "필요없음", "약간필요", "많이필요" (돌봄 필요 수준)
```

#### 2. run_health_clean.py에서 매핑
```python
col_map = {
    "근로의지": "work_intent",      # ← 문제의 시작
    "돌봄필요도": "activity_level"  # ← 의미와 맞지 않음
}
```

#### 3. 결과 seniors_clean.csv
```
age,health_score,chronic_disease_count,work_intent,activity_level
88,나쁨,4,강함,필요없음
```
- `work_intent`: "강함", "중간", "약함" (실제로는 근로의지)
- `activity_level`: "필요없음", "약간필요", "많이필요" (실제로는 돌봄필요도)

#### 4. train_health_model.py에서 잘못된 사용
```python
# ❌ 문제 코드
df = df.rename(columns={
    "work_intent": "activity_level_tmp",
    "activity_level": "work_intent"
})  # swap 시도

# ❌ 잘못된 매핑
work_intent_map = {
    "필요없음": 0,    # ← work_intent에 이 값이 없음!
    "약간필요": 1,
    "많이필요": 1
}

activity_map = {
    "약함": 1,       # ← activity_level에 이 값이 없음!
    "중간": 2,
    "강함": 3
}
```

### 문제점 요약

1. ❌ **컬럼명이 의미와 불일치**: `work_intent`가 실제로는 "근로의지"를 담고 있음
2. ❌ **Swap 로직 실패**: rename으로 swap해도 실제 CSV 값은 그대로
3. ❌ **매핑 오류**: 존재하지 않는 값으로 매핑 시도
4. ❌ **모델 학습 실패**: 잘못된 데이터로 학습되어 의미 없는 결과

### 실제 영향

- 모델이 완전히 잘못된 타깃/피처로 학습
- 모든 Health 관련 모델의 결과가 신뢰할 수 없음
- EDA 결과도 잘못된 컬럼 기준으로 분석됨

---

## 🟡 Medium: 경로 문제

### 문제 상황

```python
# ❌ 문제 코드
df = pd.read_csv("data/01_feature_source/Health_Condition/seniors_clean.csv")
```

**영향**:
- 스크립트 실행 위치에 따라 파일을 찾지 못함
- 다른 디렉토리에서 실행 시 `FileNotFoundError` 발생
- 프로젝트 구조 변경 시 모든 경로 수정 필요

---

## 🟡 Medium: 데이터 검증 부족

### 문제 상황

1. **파일 존재 확인 없음**
   - 파일이 없어도 오류가 늦게 발생
   - 명확한 에러 메시지 부족

2. **컬럼 존재 확인 없음**
   - 필수 컬럼이 없어도 오류가 늦게 발생
   - 디버깅 어려움

3. **데이터 타입 검증 없음**
   - 예상과 다른 데이터 타입으로 인한 런타임 오류

---

## 🟡 Medium: Stratify 안전성 문제

### 문제 상황

```python
# ❌ 문제 코드
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_enc
)
```

**위험**:
- 클래스가 1개만 있으면 `ValueError` 발생
- 클래스 불균형이 심하면 `ValueError: The least populated class has only 1 member` 발생
- 작은 데이터셋에서 자주 발생

---

## 🟡 Medium: ColumnTransformer remainder 문제

### 문제 상황

```python
# ❌ 문제 코드
preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ],
    remainder="drop"  # ← 숫자형 컬럼이 있으면 제외됨
)
```

**위험**:
- 향후 숫자형 feature 추가 시 자동으로 제외됨
- 예상치 못한 동작

---

## 🟠 Low: DL 모델 성능 문제

### Job_Accident_Risk 모델
- **R2 Score: -10.01** (매우 나쁨)
- 음수 R2는 모델이 단순 평균보다 못함을 의미

### Digital_Gap 모델
- **Accuracy: 0.5** (랜덤 수준)

**원인 가능성**:
- 데이터 부족
- Feature 엔지니어링 부족
- 컬럼 매핑 오류로 인한 잘못된 학습

---

# 해결 과정

## 1단계: 문제 분석 및 원인 파악

### 분석 결과
1. **컬럼명이 의미와 불일치**: `work_intent`가 실제로는 "근로의지"를 담고 있음
2. **Swap 로직이 작동하지 않음**: rename으로 swap해도 실제 CSV 값은 그대로
3. **매핑 규칙이 잘못됨**: 존재하지 않는 값으로 매핑 시도

### 결정 사항
- ✅ **컬럼명을 의미에 맞게 변경**: `work_willingness`, `care_need`
- ✅ **CSV를 Single Source of Truth로 고정**: 이후 모든 코드에서 이 컬럼명만 사용
- ✅ **Swap 로직 완전 제거**: 불필요하고 오류의 원인

---

## 2단계: 컬럼명 표준화

### 표준 컬럼명 정의

| 구분 | 기존 컬럼명 | 수정 후 컬럼명 | 실제 의미 | 값 범위 |
|------|------------|--------------|----------|---------|
| 연령 | age | age | 나이 | 정수 |
| 건강상태 | health_score | health_score | 주관적 건강 상태 | 매우나쁨/나쁨/보통/좋음/매우좋음 |
| 만성질환 | chronic_disease_count | chronic_disease_count | 만성질환 개수 | 정수 |
| 근로의지 | work_intent | **work_willingness** | 근로 의지 강도 | 약함/중간/강함 |
| 돌봄필요도 | activity_level | **care_need** | 돌봄 필요 수준 | 필요없음/약간필요/많이필요 |

### 수정된 run_health_clean.py

```python
# ✅ 수정 후
col_map = {
    "나이": "age",
    "건강상태": "health_score",
    "만성질환수": "chronic_disease_count",
    "근로의지": "work_willingness",  # ← 명확한 의미
    "돌봄필요도": "care_need"        # ← 명확한 의미
}
```

---

## 3단계: Feature/Target Encoding 규칙 고정

### Feature Encoding (표준 규칙)

| Feature | 원본 값 | 인코딩 |
|---------|---------|--------|
| work_willingness | 약함 / 중간 / 강함 | 1 / 2 / 3 |
| health_score | 매우나쁨 / 나쁨 / 보통 / 좋음 / 매우좋음 | 1 / 2 / 3 / 4 / 5 |
| age | 정수 | 그대로 |
| chronic_disease_count | 정수 | 그대로 |

### Target Encoding (표준 규칙)

| Target | 원본 값 | 인코딩 |
|--------|---------|--------|
| care_need | 필요없음 / 약간필요 / 많이필요 | 0 / 1 / 1 |

### 수정된 train_health_model.py

```python
# ✅ 수정 후 - swap 로직 완전 제거
# work_willingness는 피처로 사용
work_willingness_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

# care_need는 타깃으로 사용
care_need_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

X = df[["age", "health_score", "chronic_disease_count", "work_willingness"]]
y = df["care_need"]
```

---

## 4단계: 경로 표준화

### 수정 전
```python
# ❌ 문제 코드
df = pd.read_csv("data/01_feature_source/Health_Condition/seniors_clean.csv")
```

### 수정 후
```python
# ✅ 수정 후
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent.parent
data_path = base_dir / "data" / "01_feature_source" / "Health_Condition" / "seniors_clean.csv"

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

df = pd.read_csv(data_path, encoding="utf-8-sig")
```

**적용된 파일**: 모든 Python 스크립트 (9개 파일)

---

## 5단계: 데이터 검증 강화

### 추가된 검증 로직

```python
# ✅ 필수 컬럼 확인
REQUIRED_COLS = ["age", "health_score", "chronic_disease_count", "work_willingness", "care_need"]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

# ✅ 파일 존재 확인
if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

# ✅ 데이터 크기 확인
if len(df) == 0:
    raise ValueError("전처리 후 사용 가능한 데이터가 없습니다.")
```

**적용된 파일**: 모든 학습 스크립트

---

## 6단계: Stratify 안전 처리

### 수정 전
```python
# ❌ 문제 코드
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_enc
)
```

### 수정 후
```python
# ✅ 수정 후
from collections import Counter

y_counts = Counter(y_enc)
can_stratify = len(y_counts) > 1 and min(y_counts.values()) >= 2

if can_stratify:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    print("✅ Stratified split 적용")
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42
    )
    print("⚠️ Stratified split 불가 (클래스 불균형)")
```

**적용된 파일**:
- `train_health_model.py`
- `train_health_mlp.py`
- `train_dl_model.py` (Digital_Gap)

---

## 7단계: ColumnTransformer remainder 수정

### 수정 전
```python
# ❌ 문제 코드
preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ],
    remainder="drop"  # ← 숫자형 컬럼 제외
)
```

### 수정 후
```python
# ✅ 수정 후
preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
    ],
    remainder="passthrough"  # ← 향후 숫자형 feature 추가 대비
)
```

**적용된 파일**:
- `train_dl_model.py` (Job_Accident_Risk)
- `train_dl_model.py` (Digital_Gap)

---

## 8단계: 모델 개선

### 추가된 기능

1. **Early Stopping** (과적합 방지)
```python
mlp = MLPRegressor(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    max_iter=500,
    random_state=42,
    early_stopping=True,      # ← 추가
    validation_fraction=0.1    # ← 추가
)
```

2. **평가 지표 확장**
```python
# 회귀: R2, RMSE, MAE
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

# 분류: Accuracy, F1, Confusion Matrix
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")
cm = confusion_matrix(y_test, y_pred)
```

3. **Baseline 비교**
```python
# Baseline (평균 예측)과 비교
baseline_pred = np.full_like(y_test, y_train.mean())
baseline_r2 = r2_score(y_test, baseline_pred)

if r2 < baseline_r2:
    print("⚠️ 경고: 모델이 baseline보다 성능이 낮습니다.")
```

---

# 수정 완료 사항

## ✅ 수정된 파일 목록 (9개)

### 데이터 정제
1. ✅ `01_feature_source/Health_Condition/run_health_clean.py`
   - 컬럼명 표준화 (`work_willingness`, `care_need`)
   - 경로 표준화
   - 파일 존재 검증

### Baseline 모델
2. ✅ `03_baseline_model/train_health_model.py`
   - Swap 로직 완전 제거
   - 표준 컬럼명 사용
   - 경로 표준화
   - 데이터 검증 강화
   - Stratify 안전 처리
   - 평가 지표 확장

3. ✅ `03_baseline_model/make_train_data.py`
   - 경로 표준화
   - 파일 존재 검증

### EDA
4. ✅ `02_analysis/run_health_eda.py`
   - Swap 로직 제거
   - 표준 컬럼명 사용
   - 경로 표준화
   - 데이터 검증 강화

### DL 실험
5. ✅ `05_dl_experiment/Health_Condition/train_health_mlp.py`
   - Swap 로직 완전 제거
   - 표준 컬럼명 사용
   - 경로 표준화
   - 데이터 검증 강화
   - Stratify 안전 처리
   - 모델 구조 개선 (Dropout 추가)

6. ✅ `05_dl_experiment/Digital_Gap/train_dl_model.py`
   - 경로 표준화
   - Stratify 안전 처리
   - ColumnTransformer remainder 수정
   - Early stopping 추가
   - 평가 지표 확장

7. ✅ `05_dl_experiment/Digital_Gap/make_train_dl.py`
   - 경로 표준화
   - 파일 존재 검증

8. ✅ `05_dl_experiment/Job_Accident_Risk/train_dl_model.py`
   - 경로 표준화
   - ColumnTransformer remainder 수정
   - Early stopping 추가
   - 평가 지표 확장 (MAE 추가)
   - Baseline 비교 로직 추가

9. ✅ `05_dl_experiment/Job_Accident_Risk/make_train_dl.py`
   - 경로 표준화
   - 파일 존재 검증

---

## ✅ 수정 완료 체크리스트

- [x] 컬럼명 표준화 (`work_willingness`, `care_need`)
- [x] Swap 로직 완전 제거
- [x] 경로 표준화 (pathlib.Path 사용)
- [x] 파일 존재 검증 추가
- [x] 필수 컬럼 검증 추가
- [x] Stratify 안전 처리
- [x] ColumnTransformer remainder 수정
- [x] Early stopping 추가
- [x] 평가 지표 확장
- [x] Baseline 비교 로직 추가
- [x] 코드 일관성 확보
- [x] Linter 오류 없음

---

# 표준 규칙 (최종)

## 컬럼명 표준 (Single Source of Truth)

| 구분 | 컬럼명 | 실제 의미 | 값 범위 |
|------|--------|----------|---------|
| 연령 | `age` | 나이 | 정수 |
| 건강상태 | `health_score` | 주관적 건강 상태 | 매우나쁨/나쁨/보통/좋음/매우좋음 |
| 만성질환 | `chronic_disease_count` | 만성질환 개수 | 정수 |
| 근로의지 | `work_willingness` | 근로 의지 강도 | 약함/중간/강함 |
| 돌봄필요도 | `care_need` | 돌봄 필요 수준 | 필요없음/약간필요/많이필요 |

**📌 중요**: 이후 모든 코드에서 이 컬럼명만 사용

---

## Feature Encoding 규칙

| Feature | 원본 값 | 인코딩 |
|---------|---------|--------|
| work_willingness | 약함 / 중간 / 강함 | 1 / 2 / 3 |
| health_score | 매우나쁨 / 나쁨 / 보통 / 좋음 / 매우좋음 | 1 / 2 / 3 / 4 / 5 |
| age | 정수 | 그대로 |
| chronic_disease_count | 정수 | 그대로 |

---

## Target Encoding 규칙

| Target | 원본 값 | 인코딩 |
|--------|---------|--------|
| care_need | 필요없음 / 약간필요 / 많이필요 | 0 / 1 / 1 |

---

## 모델별 문제 정의

| 모델명 | 문제 유형 | 타깃(Y) | 피처(X) |
|--------|----------|---------|---------|
| Health Care Prediction | 이진 분류 | care_need | age, health_score, chronic_disease_count, work_willingness |
| Job Accident Risk | 회귀 | accident_count | age_group, industry |
| Digital Gap | 다중 분류 | digital_level | age_group, device_access, internet_usage |

---

## Stratify 안전 처리 규칙

```python
from collections import Counter

y_counts = Counter(y)
can_stratify = len(y_counts) > 1 and min(y_counts.values()) >= 2

if can_stratify:
    # Stratified split 사용
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
else:
    # 일반 split 사용
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
```

---

## 경로 표준화 규칙

```python
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent.parent
data_path = base_dir / "data" / "..." / "file.csv"

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

df = pd.read_csv(data_path, encoding="utf-8-sig")
```

---

## 데이터 검증 규칙

```python
# 1. 필수 컬럼 확인
REQUIRED_COLS = ["age", "health_score", ...]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

# 2. 데이터 크기 확인
if len(df) == 0:
    raise ValueError("전처리 후 사용 가능한 데이터가 없습니다.")

# 3. 타깃 분포 확인
print(f"타깃 분포:\n{y.value_counts()}")
```

---

## 다음 단계

### 1. seniors_clean.csv 재생성
```bash
python data/01_feature_source/Health_Condition/run_health_clean.py
```

### 2. 모델 재학습
```bash
# Baseline (sklearn)
python data/03_baseline_model/train_health_model.py

# PyTorch MLP
python data/05_dl_experiment/Health_Condition/train_health_mlp.py

# DL 실험
python data/05_dl_experiment/Digital_Gap/train_dl_model.py
python data/05_dl_experiment/Job_Accident_Risk/train_dl_model.py
```

### 3. 성능 확인
- `data/04_result/metrics.json` 확인
- Baseline vs PyTorch 비교
- DL 모델 성능 재평가

---

## 참고: sklearn vs PyTorch 병행 사용 (의도적 설계)

### 전략
- **sklearn**: Baseline 모델 (해석 가능, 빠른 프로토타이핑)
- **PyTorch**: 실험/확장 모델 (구조적 확장 가능성 검증)

### 포트폴리오 설명 문장
> 본 프로젝트에서는 데이터 규모가 작아 **sklearn 모델을 기준선(baseline)**으로 먼저 구축하였고,
> 이후 **PyTorch 기반 MLP 모델을 통해 구조적 확장 가능성과 성능 변화 실험**을 진행하였다.
> 이를 통해 **모델 선택이 데이터 특성에 따라 달라져야 함**을 검증했다.

---

**수정 완료일**: 2024년  
**검증 상태**: ✅ Linter 오류 없음  
**다음 작업**: seniors_clean.csv 재생성 및 모델 재학습 필요
