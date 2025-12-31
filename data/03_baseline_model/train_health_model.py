"""
Health Care Prediction Model (sklearn Baseline)
===============================================
문제 유형: 이진 분류
타깃(Y): care_need (돌봄 필요 여부)
피처(X): age, health_score, chronic_disease_count, work_willingness
"""
import pandas as pd
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

# =========================
# 1. 경로 설정
# =========================
base_dir = Path(__file__).parent.parent.parent
data_path = base_dir / "data" / "01_feature_source" / "Health_Condition" / "seniors_clean.csv"
output_path = base_dir / "data" / "04_result" / "metrics.json"

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

# =========================
# 2. 데이터 로드
# =========================
df = pd.read_csv(data_path, encoding="utf-8-sig")

# 필수 컬럼 확인
REQUIRED_COLS = ["age", "health_score", "chronic_disease_count", "work_willingness", "care_need"]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

print(f"원본 데이터: {len(df)}행")
print(f"컬럼: {df.columns.tolist()}")

# =========================
# 3. 데이터 전처리
# =========================
# 문자열 정리
for col in ["health_score", "work_willingness", "care_need"]:
    df[col] = df[col].astype(str).str.strip()

# 숫자형 변환
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["chronic_disease_count"] = pd.to_numeric(df["chronic_disease_count"], errors="coerce")

# =========================
# 4. Feature Encoding (표준 규칙)
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

work_willingness_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

df["health_score"] = df["health_score"].map(health_map)
df["work_willingness"] = df["work_willingness"].map(work_willingness_map)

# =========================
# 5. Target Encoding (표준 규칙)
# =========================
care_need_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["care_need"] = df["care_need"].map(care_need_map)

# =========================
# 6. 결측치 제거
# =========================
df = df.dropna()
print(f"전처리 후 데이터: {len(df)}행")

if len(df) == 0:
    raise ValueError("전처리 후 사용 가능한 데이터가 없습니다.")

# =========================
# 7. Feature / Target 분리
# =========================
X = df[[
    "age",
    "health_score",
    "chronic_disease_count",
    "work_willingness"
]]

y = df["care_need"]

print(f"\n학습 데이터 수: {len(X)}")
print(f"타깃 분포:\n{y.value_counts()}")

# =========================
# 8. Train / Test Split
# =========================
# stratify 안전 처리
from collections import Counter
y_counts = Counter(y)
can_stratify = len(y_counts) > 1 and min(y_counts.values()) >= 2

if can_stratify:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("✅ Stratified split 적용")
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print("⚠️ Stratified split 불가 (클래스 불균형)")

# =========================
# 9. 모델 학습 (Baseline: LogisticRegression)
# =========================
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# =========================
# 10. 평가
# =========================
y_pred = model.predict(X_test)

metrics = {
    "model": "LogisticRegression (Baseline)",
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    "train_size": len(X_train),
    "test_size": len(X_test)
}

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
metrics["confusion_matrix"] = {
    "tn": int(cm[0, 0]),
    "fp": int(cm[0, 1]),
    "fn": int(cm[1, 0]),
    "tp": int(cm[1, 1])
}

print("\n=== METRICS ===")
print(json.dumps(metrics, indent=2, ensure_ascii=False))

# =========================
# 11. 결과 저장
# =========================
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print(f"\n✅ ML 학습 완료 (결과 저장: {output_path})")
