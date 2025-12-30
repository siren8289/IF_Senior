# data/05_dl_experiment/Job_Accident_Risk/train_dl_model.py

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np


def main():
    df = pd.read_csv(
        "data/05_dl_experiment/Job_Accident_Risk/train_dl.csv"
    )

    # 1. Feature / Target 분리
    X = df.drop(columns=["accident_count"])
    y = df["accident_count"]

    # 2. 범주형 컬럼 정의
    cat_cols = ["age_group", "industry"]

    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        ],
        remainder="drop"
    )

    # 3. MLP 회귀 모델
    mlp = MLPRegressor(
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

    # 4. Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 5. 학습
    pipe.fit(X_train, y_train)

    # 6. 평가
    y_pred = pipe.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("R2:", round(r2, 4))
    print("RMSE:", round(rmse, 4))

    # 7. 결과 저장
    metrics = pd.DataFrame(
        [
            {
                "model": "MLPRegressor",
                "r2": r2,
                "rmse": rmse,
            }
        ]
    )

    out_path = Path("data/05_dl_experiment/Job_Accident_Risk/dl_metrics.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    metrics.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("✅ DL 회귀 학습 완료")
    print(metrics)


if __name__ == "__main__":
    main()
