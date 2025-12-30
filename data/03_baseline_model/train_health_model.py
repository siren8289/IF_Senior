import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score

# =========================
# 1. 데이터 로드
# =========================
df = pd.read_csv(
    "data/01_feature_source/Health_Condition/seniors_clean.csv"
)

# =========================
# 2. 컬럼 정리 (CSV 구조 맞춤)
# =========================
# activity_level / work_intent 위치 교정
df = df.rename(columns={
    "work_intent": "activity_level_tmp",
    "activity_level": "work_intent"
})
df = df.rename(columns={
    "activity_level_tmp": "activity_level"
})

for col in ["health_score", "work_intent", "activity_level"]:
    df[col] = df[col].astype(str).str.strip()

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["chronic_disease_count"] = pd.to_numeric(
    df["chronic_disease_count"], errors="coerce"
)

# =========================
# 3. 수치화
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

activity_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

work_intent_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["health_score"] = df["health_score"].map(health_map)
df["activity_level"] = df["activity_level"].map(activity_map)
df["work_intent"] = df["work_intent"].map(work_intent_map)

# =========================
# 4. ML 대상 데이터만 추림
# =========================
df = df.dropna()

X = df[[
    "age",
    "health_score",
    "chronic_disease_count",
    "activity_level"
]]

y = df["work_intent"]

print("학습 데이터 수:", len(X))

# =========================
# 5. Train / Test
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 6. 모델 학습
# =========================
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# =========================
# 7. 평가
# =========================
pred = model.predict(X_test)

metrics = {
    "accuracy": accuracy_score(y_test, pred),
    "precision": precision_score(y_test, pred),
    "recall": recall_score(y_test, pred)
}

print("METRICS:", metrics)

# =========================
# 8. 결과 저장
# =========================
with open("data/04_result/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("✅ ML 학습 완료")
