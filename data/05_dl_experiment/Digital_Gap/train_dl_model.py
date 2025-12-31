"""
Digital Gap Classification Model (sklearn MLP)
==============================================
문제 유형: 다중 분류
타깃(Y): digital_level (디지털 격차 수준)
피처(X): age_group, device_access, internet_usage
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from collections import Counter

# =========================
# 1. 경로 설정
# =========================
base_dir = Path(__file__).parent.parent.parent.parent
data_path = base_dir / "data" / "05_dl_experiment" / "Digital_Gap" / "train_dl.csv"
output_path = base_dir / "data" / "05_dl_experiment" / "Digital_Gap" / "dl_metrics.csv"

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

# =========================
# 2. 데이터 로드
# =========================
df = pd.read_csv(data_path, encoding="utf-8-sig")

# 필수 컬럼 확인
REQUIRED_COLS = ["age_group", "device_access", "internet_usage", "digital_level"]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

print(f"원본 데이터: {len(df)}행")

# =========================
# 3. Feature / Target 분리
# =========================
X = df.drop(columns=["digital_level"])
y = df["digital_level"]

print(f"타깃 분포:\n{y.value_counts()}")

# =========================
# 4. 타깃 라벨 인코딩
# =========================
label_enc = LabelEncoder()
y_enc = label_enc.fit_transform(y)

print(f"인코딩된 타깃 분포: {Counter(y_enc)}")

# =========================
# 5. 범주형 컬럼 전처리
# =========================
cat_cols = ["age_group", "device_access", "internet_usage"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
    ],
    remainder="passthrough"  # 향후 숫자형 feature 추가 대비
)

# =========================
# 6. MLP 분류 모델
# =========================
mlp = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1
)

pipe = Pipeline(
    steps=[
        ("preprocess", preprocess),
        ("model", mlp)
    ]
)

# =========================
# 7. Train / Test Split (stratify 안전 처리)
# =========================
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

# =========================
# 8. 학습
# =========================
print("\n모델 학습 중...")
pipe.fit(X_train, y_train)

# =========================
# 9. 평가
# =========================
y_pred = pipe.predict(X_test)

acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred, target_names=label_enc.classes_))

# =========================
# 10. 결과 저장
# =========================
metrics = pd.DataFrame([
    {
        "model": "MLPClassifier",
        "accuracy": acc,
        "f1_weighted": f1,
        "train_size": len(X_train),
        "test_size": len(X_test)
    }
])

output_path.parent.mkdir(parents=True, exist_ok=True)
metrics.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n✅ DL 분류 학습 완료")
print(f"결과 저장: {output_path}")
print(f"\n{metrics}")
