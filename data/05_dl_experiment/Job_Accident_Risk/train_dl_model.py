"""
Job Accident Risk Prediction Model (sklearn MLP)
===============================================
문제 유형: 회귀
타깃(Y): accident_count (산업재해 발생 건수)
피처(X): age_group, industry
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np


def main():
    # =========================
    # 1. 경로 설정
    # =========================
    base_dir = Path(__file__).parent.parent.parent.parent
    data_path = base_dir / "data" / "05_dl_experiment" / "Job_Accident_Risk" / "train_dl.csv"
    output_path = base_dir / "data" / "05_dl_experiment" / "Job_Accident_Risk" / "dl_metrics.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

    # =========================
    # 2. 데이터 로드
    # =========================
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # 필수 컬럼 확인
    REQUIRED_COLS = ["age_group", "industry", "accident_count"]
    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {missing}")

    print(f"원본 데이터: {len(df)}행")

    # =========================
    # 3. Feature / Target 분리
    # =========================
    X = df.drop(columns=["accident_count"])
    y = df["accident_count"]

    # 타깃 통계
    print(f"\n타깃 통계:")
    print(f"  평균: {y.mean():.2f}")
    print(f"  표준편차: {y.std():.2f}")
    print(f"  최소값: {y.min():.2f}")
    print(f"  최대값: {y.max():.2f}")

    # =========================
    # 4. 범주형 컬럼 전처리
    # =========================
    cat_cols = ["age_group", "industry"]

    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
        ],
        remainder="passthrough"  # 향후 숫자형 feature 추가 대비
    )

    # =========================
    # 5. MLP 회귀 모델
    # =========================
    mlp = MLPRegressor(
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
    # 6. Train / Test Split
    # =========================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\n학습 데이터: {len(X_train)}행, 테스트 데이터: {len(X_test)}행")

    # =========================
    # 7. 학습
    # =========================
    print("\n모델 학습 중...")
    pipe.fit(X_train, y_train)

    # =========================
    # 8. 평가
    # =========================
    y_pred = pipe.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    print("\n=== 평가 결과 ===")
    print(f"R2 Score: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")

    # Baseline 비교 (평균 예측)
    baseline_pred = np.full_like(y_test, y_train.mean())
    baseline_r2 = r2_score(y_test, baseline_pred)
    print(f"\nBaseline (평균 예측) R2: {baseline_r2:.4f}")

    if r2 < baseline_r2:
        print("⚠️ 경고: 모델이 baseline보다 성능이 낮습니다.")
        print("   원인 가능성: 데이터 부족, feature 부족, 하이퍼파라미터 조정 필요")

    # =========================
    # 9. 결과 저장
    # =========================
    metrics = pd.DataFrame([
        {
            "model": "MLPRegressor",
            "r2": r2,
            "rmse": rmse,
            "mae": mae,
            "baseline_r2": baseline_r2,
            "train_size": len(X_train),
            "test_size": len(X_test)
        }
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n✅ DL 회귀 학습 완료")
    print(f"결과 저장: {output_path}")
    print(f"\n{metrics}")


if __name__ == "__main__":
    main()
