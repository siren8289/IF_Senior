import pandas as pd

# 1. 원본 데이터 로드
raw = pd.read_csv("data/00_raw/04_정보격차실태조사.csv")

# 2. 컬럼명 영어로 통일 (실무적으로 매우 중요)
raw = raw.rename(columns={
    "연령대": "age_group",
    "스마트폰보유": "device_access",
    "인터넷이용": "internet_usage",
    "AI사용능력": "digital_level"
})

# 3. Feature용 정제 데이터 생성
raw[["age_group", "device_access", "internet_usage", "digital_level"]] \
    .dropna() \
    .to_csv(
        "data/01_feature_source/Digital_Gap_Matching/digital_clean.csv",
        index=False
    )

# 4. 디지털 역량 분포 EDA
raw.groupby("digital_level").size().to_csv(
    "data/02_analysis/digital_gap_eda_summary.csv",
    encoding="utf-8-sig"
)
