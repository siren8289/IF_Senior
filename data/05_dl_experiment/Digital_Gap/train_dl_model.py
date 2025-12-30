import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score

# 1. 데이터 로드
df = pd.read_csv(
    "data/05_dl_experiment/Digital_Gap/train_dl.csv"
)

X = df.drop(columns=["digital_level"])
y = df["digital_level"]

# 2. 타깃 라벨 인코딩
label_enc = LabelEncoder()
y_enc = label_enc.fit_transform(y)

# 3. 범주형 컬럼
cat_cols = ["age_group", "device_access", "internet_usage"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ]
)

# 4. MLP 분류 모델
mlp = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    max_iter=500,
    random_state=42
)

pipe = Pipeline(
    steps=[
        ("preprocess", preprocess),
        ("model", mlp)
    ]
)

# 5. Train / Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# 6. 학습
pipe.fit(X_train, y_train)

# 7. 평가
y_pred = pipe.predict(X_test)

acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")

# 8. 결과 저장
metrics = pd.DataFrame([
    {
        "model": "MLPClassifier",
        "accuracy": acc,
        "f1_weighted": f1
    }
])

metrics.to_csv(
    "data/05_dl_experiment/Digital_Gap/dl_metrics.csv",
    index=False
)

print("DL 분류 학습 완료")
print(metrics)
