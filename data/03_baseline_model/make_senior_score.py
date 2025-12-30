import pandas as pd

df = pd.read_csv("data/03_baseline_model/train_data.csv")

# 점수 규칙 (Baseline용, 설명 가능)
digital_level_score = {
    "가능": 2,
    "보통": 1,
    "불가": 0
}

internet_score = {
    "예": 1,
    "아니오": 0
}

device_score = {
    "예": 1,
    "아니오": 0
}

df["digital_score"] = df["digital_level"].map(digital_level_score)
df["internet_score"] = df["internet_usage"].map(internet_score)
df["device_score"] = df["device_access"].map(device_score)

# 최종 고령자 디지털 역량 점수
df["senior_score"] = (
    df["digital_score"]
    + df["internet_score"]
    + df["device_score"]
)

result = df[["age_group", "senior_score"]]

result.to_csv(
    "data/03_baseline_model/senior_score.csv",
    index=False
)

print("senior_score.csv 생성 완료")
