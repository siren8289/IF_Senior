import numpy as np
import pandas as pd
from typing import Dict, Tuple

class HealthFeatureExtractor:
    """건강정보 피처 엔지니어링"""

    @staticmethod
    def calculate_bmi(height_cm: int, weight_kg: float) -> float:
        """BMI 계산"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)

    @staticmethod
    def get_bmi_factor(bmi: float) -> float:
        """BMI → 점수 변환 (0-1)"""
        if bmi < 18.5:
            return 0.7  # 저체중: 위험
        elif 18.5 <= bmi < 25:
            return 1.0  # 정상: 최고
        elif 25 <= bmi < 30:
            return 0.8  # 과체중: 낮음
        else:
            return 0.5  # 비만: 위험

    @staticmethod
    def count_chronic_conditions(conditions: Dict[str, bool]) -> int:
        """만성질환 개수"""
        return sum(1 for v in conditions.values() if v)

    @staticmethod
    def get_chronic_factor(num_conditions: int) -> float:
        """만성질환 개수 → 점수 변환 (0-1)"""
        if num_conditions == 0:
            return 1.0
        elif num_conditions == 1:
            return 0.8
        elif num_conditions == 2:
            return 0.6
        else:  # 3개 이상
            return 0.4

    @staticmethod
    def extract_features(
        height_cm: int,
        weight_kg: float,
        chronic_conditions: Dict[str, bool],
        risk_flags: Dict[str, float]
    ) -> Dict[str, float]:
        """모든 피처 추출"""
        extractor = HealthFeatureExtractor()

        # BMI 관련
        bmi = extractor.calculate_bmi(height_cm, weight_kg)
        bmi_factor = extractor.get_bmi_factor(bmi)

        # 만성질환 관련
        num_conditions = extractor.count_chronic_conditions(chronic_conditions)
        chronic_factor = extractor.get_chronic_factor(num_conditions)

        # 위험 지표 평균
        risk_avg = np.mean(list(risk_flags.values())) if risk_flags else 0.0

        return {
            "bmi": bmi,
            "bmi_factor": bmi_factor,
            "num_chronic_conditions": num_conditions,
            "chronic_factor": chronic_factor,
            "avg_risk_flag": risk_avg,
            "mobility_factor": 1.0 - risk_flags.get("mobility_limited", 0.0),
            "cognitive_factor": 1.0 - risk_flags.get("cognitive_impairment_risk", 0.0)
        }
