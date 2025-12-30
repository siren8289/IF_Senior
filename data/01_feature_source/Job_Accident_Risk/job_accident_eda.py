import pandas as pd

def main():
    # 1. 원본 데이터 로드
    raw = pd.read_csv(
        "data/00_raw/01_산업재해현황.csv",
        encoding="utf-8-sig"
    )

    # 2. 실제 컬럼명 기준 매핑 (확정)
    col_map = {
        "나이대": "age_group",
        "산업분류": "industry",
        "발생건수": "accident_count"
    }

    # 3. 정제 (선택 → rename → 결측 제거)
    clean = (
        raw[list(col_map.keys())]
        .rename(columns=col_map)
        .dropna()
    )

    # 4. 정제 데이터 저장 (feature source)
    clean.to_csv(
        "data/01_feature_source/Job_Accident_Risk/accident_clean.csv",
        index=False
    )

    # 5. EDA: 연령대 × 산업별 평균 사고 건수
    summary = (
        clean
        .groupby(["age_group", "industry"])["accident_count"]
        .mean()
        .reset_index()
    )

    summary.to_csv(
        "data/02_analysis/job_risk_eda_summary.csv",
        index=False
    )

    print("✅ accident_clean.csv / job_risk_eda_summary.csv 생성 완료")

if __name__ == "__main__":
    main()
