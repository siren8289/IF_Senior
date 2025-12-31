"""
Health Condition EDA
====================
컬럼명 표준화 적용: work_willingness, care_need
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# 1. 경로 설정
# =========================
base_dir = Path(__file__).parent.parent.parent
data_path = base_dir / "data" / "01_feature_source" / "Health_Condition" / "seniors_clean.csv"
output_dir = base_dir / "data" / "02_analysis"
output_dir.mkdir(parents=True, exist_ok=True)

if not data_path.exists():
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

# =========================
# 2. 데이터 로드
# =========================
df = pd.read_csv(data_path, encoding="utf-8-sig")

print("원본 컬럼:", df.columns.tolist())
print(f"\n원본 데이터 샘플:\n{df.head()}")

# 필수 컬럼 확인
REQUIRED_COLS = ["age", "health_score", "chronic_disease_count", "work_willingness", "care_need"]
missing = set(REQUIRED_COLS) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

# =========================
# 3. 문자열 정리
# =========================
for col in ["health_score", "work_willingness", "care_need"]:
    df[col] = df[col].astype(str).str.strip()

# =========================
# 4. 숫자형 변환
# =========================
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["chronic_disease_count"] = pd.to_numeric(df["chronic_disease_count"], errors="coerce")

# =========================
# 5. Feature Encoding (표준 규칙)
# =========================
health_map = {
    "매우나쁨": 1,
    "나쁨": 2,
    "보통": 3,
    "좋음": 4,
    "매우좋음": 5
}

work_willingness_map = {
    "약함": 1,
    "중간": 2,
    "강함": 3
}

df["health_score_num"] = df["health_score"].map(health_map)
df["work_willingness_num"] = df["work_willingness"].map(work_willingness_map)

# =========================
# 6. Target Encoding (표준 규칙)
# =========================
care_need_map = {
    "필요없음": 0,
    "약간필요": 1,
    "많이필요": 1
}

df["care_need_num"] = df["care_need"].map(care_need_map)

# =========================
# 7. 연령대 파생
# =========================
df["age_group"] = pd.cut(
    df["age"],
    bins=[64, 69, 74, 120],
    labels=["65-69", "70-74", "75+"]
)

# =========================
# 8. EDA 대상 필터링
# =========================
eda_df = df[
    df["age_group"].notna()
    & df["health_score_num"].notna()
    & df["work_willingness_num"].notna()
    & df["care_need_num"].notna()
].copy()

print(f"\nEDA 대상 데이터 수: {len(eda_df)}")

# =========================
# 9. 요약 통계
# =========================
summary = eda_df.groupby("age_group").agg(
    avg_health_score=("health_score_num", "mean"),
    avg_work_willingness=("work_willingness_num", "mean"),
    care_need_rate=("care_need_num", "mean"),
    count=("age", "count")
).reset_index()

print("\n=== EDA SUMMARY ===")
print(summary)

summary.to_csv(
    output_dir / "health_eda_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 10. 시각화
# =========================
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 건강 점수 by 연령대
axes[0].bar(summary["age_group"], summary["avg_health_score"])
axes[0].set_title("Average Health Score by Age Group")
axes[0].set_xlabel("Age Group")
axes[0].set_ylabel("Health Score")

# 돌봄 필요율 by 연령대
axes[1].bar(summary["age_group"], summary["care_need_rate"])
axes[1].set_title("Care Need Rate by Age Group")
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("Care Need Rate")

plt.tight_layout()
plt.savefig(output_dir / "health_by_age.png", dpi=150)
plt.close()

print(f"\n✅ Health EDA 완료")
print(f"결과 저장: {output_dir}")
