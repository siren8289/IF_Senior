"""
Baseline 모델용 학습 데이터 생성
"""
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
input_path = base_dir / "data" / "01_feature_source" / "Digital_Gap_Matching" / "digital_clean.csv"
output_path = base_dir / "data" / "03_baseline_model" / "train_data.csv"

if not input_path.exists():
    raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")

digital = pd.read_csv(input_path, encoding="utf-8-sig")

output_path.parent.mkdir(parents=True, exist_ok=True)
digital.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ train_data.csv 생성 완료 ({len(digital)}행)")
print(f"저장 위치: {output_path}")
