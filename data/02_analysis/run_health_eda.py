import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 0. CSV 로드
# =========================
df = pd.read_csv(
    "data/01_feature_source/Health_Condition/seniors_clean.csv"
)

print("원본 컬럼:", df.columns.tolist())
print(df.head())

# =========================
# 1. 컬럼 순서 교정 (🔥 핵심)
# 실제 데이터 기준으로 교체
# =========================
df = df.rename(columns={
    "work_intent": "activity_level_tmp",
    "activity_level": "work_intent"
})

df = df.rename(columns={
    "activity_level_tmp": "activity_level"
})

# =========================
# 2. 문자열 정리
# =========================
for col in ["health_score", "work_intent", "activity_level"]:
    df[col] = df[col].astype(str).str.strip()

# =========================
# 3. age 숫자화
# =========================
df["age"] = pd.to_numeric(df["age"], errors="coerce")

# =========================
# 4. health_score 매핑
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

df["health_score_num"] = df["health_score"].map(health_map)

# =========================
# 5. work_intent 매핑 (이제 정상)
# =========================
work_intent_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["work_intent_num"] = df["work_intent"].map(work_intent_map)

# =========================
# 6. 연령대 파생
# =========================
df["age_group"] = pd.cut(
    df["age"],
    bins=[64, 69, 74, 120],
    labels=["65-69", "70-74", "75+"]
)

# =========================
# 7. EDA 대상 필터링
# =========================
eda_df = df[
    df["age_group"].notna()
    & df["health_score_num"].notna()
    & df["work_intent_num"].notna()
]

print("EDA 대상 데이터 수:", len(eda_df))

# =========================
# 8. 요약 통계
# =========================
summary = eda_df.groupby("age_group").agg(
    avg_health_score=("health_score_num", "mean"),
    work_intent_rate=("work_intent_num", "mean"),
    count=("age", "count")
).reset_index()

print("=== EDA SUMMARY ===")
print(summary)

summary.to_csv(
    "data/02_analysis/health_eda_summary.csv",
    index=False
)

# =========================
# 9. 시각화
# =========================
plt.figure(figsize=(6, 4))
plt.bar(summary["age_group"], summary["avg_health_score"])
plt.title("Average Health Score by Age Group")
plt.xlabel("Age Group")
plt.ylabel("Health Score")
plt.tight_layout()
plt.savefig("data/02_analysis/health_by_age.png")
plt.close()

print("✅ Health EDA 완료")
