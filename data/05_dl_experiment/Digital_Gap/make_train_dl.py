"""
Digital Gap DL 학습 데이터 생성
"""
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent.parent
input_path = base_dir / "data" / "01_feature_source" / "Digital_Gap_Matching" / "digital_clean.csv"
output_path = base_dir / "data" / "05_dl_experiment" / "Digital_Gap" / "train_dl.csv"

if not input_path.exists():
    raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")

df = pd.read_csv(input_path, encoding="utf-8-sig")

dl_cols = [
    "age_group",
    "device_access",
    "internet_usage",
    "digital_level"
]

# 필수 컬럼 확인
missing = set(dl_cols) - set(df.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

result = df[dl_cols].dropna()

output_path.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ train_dl.csv 생성 완료 ({len(result)}행)")
print(f"저장 위치: {output_path}")
