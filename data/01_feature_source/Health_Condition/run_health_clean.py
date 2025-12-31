import pandas as pd
from pathlib import Path

# =========================
# 컬럼명 표준화 (최종 기준)
# =========================
# CSV가 Single Source of Truth
# 이후 모든 코드에서 이 컬럼명만 사용
col_map = {
    "나이": "age",
    "건강상태": "health_score",
    "만성질환수": "chronic_disease_count",
    "근로의지": "work_willingness",  # 근로 의지 강도 (약함/중간/강함)
    "돌봄필요도": "care_need"        # 돌봄 필요 수준 (필요없음/약간필요/많이필요)
}

# =========================
# 데이터 로드 및 정제
# =========================
base_dir = Path(__file__).parent.parent.parent.parent
raw_path = base_dir / "data" / "00_raw" / "02_노인실태조사.csv"
out_path = base_dir / "data" / "01_feature_source" / "Health_Condition" / "seniors_clean.csv"

if not raw_path.exists():
    raise FileNotFoundError(f"원본 데이터 파일을 찾을 수 없습니다: {raw_path}")

raw = pd.read_csv(raw_path)

# 필수 컬럼 확인
required_cols = list(col_map.keys())
missing = set(required_cols) - set(raw.columns)
if missing:
    raise ValueError(f"필수 컬럼이 없습니다: {missing}")

clean = (
    raw[required_cols]
    .rename(columns=col_map)
    .dropna()
)

# 출력 디렉토리 생성
out_path.parent.mkdir(parents=True, exist_ok=True)
clean.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"✅ seniors_clean.csv 생성 완료 ({len(clean)}행)")
print(f"컬럼: {clean.columns.tolist()}")
