import pandas as pd

# Digital Gap 정제 데이터 로드
digital = pd.read_csv(
    "data/01_feature_source/Digital_Gap_Matching/digital_clean.csv"
)

# Baseline에서는 일단 그대로 학습 데이터로 사용
digital.to_csv(
    "data/03_baseline_model/train_data.csv",
    index=False
)

print("train_data.csv 생성 완료")
