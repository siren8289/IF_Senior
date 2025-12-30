import pandas as pd

df = pd.read_csv(
    "data/01_feature_source/Digital_Gap_Matching/digital_clean.csv"
)

dl_cols = [
    "age_group",
    "device_access",
    "internet_usage",
    "digital_level"
]

df[dl_cols].dropna().to_csv(
    "data/05_dl_experiment/Digital_Gap/train_dl.csv",
    index=False
)

print("train_dl.csv 생성 완료")
