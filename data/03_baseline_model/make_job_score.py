# data/03_baseline_model/make_job_score.py

import pandas as pd
from pathlib import Path


def main():
    base_dir = Path("data")

    # 입력: EDA 결과
    job_summary_path = base_dir / "02_analysis" / "job_risk_eda_summary.csv"
    # 출력: job_score.csv
    out_path = base_dir / "03_baseline_model" / "job_score.csv"

    df = pd.read_csv(job_summary_path)

    # 컬럼 체크
    required_cols = {"industry", "accident_count"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"job_risk_eda_summary.csv에 다음 컬럼이 없습니다: {missing}")

    # 1) 산업별 평균 사고 건수
    industry_accident = (
        df.groupby("industry")["accident_count"]
          .mean()
          .reset_index()
    )

    # 2) Min-Max 정규화 → job_score (0~1)
    min_v = industry_accident["accident_count"].min()
    max_v = industry_accident["accident_count"].max()

    if max_v == min_v:
        # 모든 산업 사고건수가 같으면 동일 점수 부여
        industry_accident["job_score"] = 0.5
    else:
        industry_accident["job_score"] = (
            (industry_accident["accident_count"] - min_v)
            / (max_v - min_v)
        )

    # 3) 최종 저장
    result = industry_accident[["industry", "job_score"]]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("✅ job_score.csv 생성 완료")
    print(result.head())


if __name__ == "__main__":
    main()
