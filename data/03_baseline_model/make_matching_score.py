import pandas as pd

df = pd.read_csv("data/03_baseline_model/senior_score.csv")

# senior_score 최대값 (현재 구조상 4)
MAX_SCORE = df["senior_score"].max()

# 매칭 우선순위 점수 (낮은 역량 = 높은 우선순위)
df["matching_score"] = MAX_SCORE - df["senior_score"]

df.to_csv(
    "data/03_baseline_model/matching_score.csv",
    index=False
)

print("matching_score.csv 생성 완료")
