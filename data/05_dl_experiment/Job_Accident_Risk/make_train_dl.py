import pandas as pd

df = pd.read_csv(
    "data/02_analysis/job_risk_eda_summary.csv"
).reset_index()

dl_cols = [
    "age_group",        # 인코딩 후 사용
    "industry",         # 인코딩 후 사용
    "accident_count"
]

df[dl_cols].dropna().to_csv(
    "data/05_dl_experiment/Job_Accident_Risk/train_dl.csv",
    index=False
)
