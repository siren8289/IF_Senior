import pandas as pd

raw = pd.read_csv("data/00_raw/02_노인실태조사.csv")

# 실제 컬럼명 기준 매핑 (확정)
col_map = {
    "나이": "age",
    "건강상태": "health_score",
    "만성질환수": "chronic_disease_count",
    "근로의지": "work_intent",
    "돌봄필요도": "activity_level"
}

clean = (
    raw[list(col_map.keys())]
    .rename(columns=col_map)
    .dropna()
)

clean.to_csv(
    "data/01_feature_source/Health_Condition/seniors_clean.csv",
    index=False
)

print("✅ seniors_clean.csv 생성 완료")
