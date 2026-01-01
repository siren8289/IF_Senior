import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

# ======================================================
# 설정
# ======================================================
MODEL_DIR = "ai/models"
MODEL_PATH = os.path.join(MODEL_DIR, "isolation_forest.pkl")

# monitoring_features.py의 to_model_input() 기준
FEATURE_DIM = 10  # ⚠️ 반드시 일치해야 함

# ======================================================
# 더미 학습 데이터 생성
# (실데이터 없을 때 정상 범위 기준 시뮬레이션)
# ======================================================
np.random.seed(42)

X_train = np.column_stack([
    np.random.normal(75, 5, 500),     # hr_mean
    np.random.normal(4, 1, 500),      # hr_std
    np.random.normal(95, 8, 500),     # hr_max
    np.random.normal(60, 5, 500),     # hr_min
    np.random.normal(0, 5, 500),      # hr_trend
    np.random.normal(30, 10, 500),    # step_rate
    np.random.uniform(0, 1, 500),     # activity_walking
    np.random.uniform(0, 1, 500),     # activity_sitting
    np.random.uniform(0, 1, 500),     # activity_lying
    np.random.uniform(0, 1, 500),     # activity_standing
])

assert X_train.shape[1] == FEATURE_DIM, "❌ 피처 차원 불일치"

# ======================================================
# Isolation Forest 학습
# ======================================================
model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

model.fit(X_train)

# ======================================================
# 모델 저장
# ======================================================
os.makedirs(MODEL_DIR, exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("✅ Isolation Forest 재학습 완료")
print(f"📦 저장 위치: {MODEL_PATH}")
