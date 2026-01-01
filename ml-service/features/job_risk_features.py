from typing import List, Dict
import numpy as np
from datetime import datetime

class JobRiskFeatureExtractor:
    """일자리 위험도 피처 추출"""

    # 위험한 키워드 (BERT 대체용 규칙)
    RISK_KEYWORDS = {
        "이동": 3, "들기": 4, "옮기기": 4, "들어올리기": 5,
        "계단": 3, "무거운": 4, "위험": 5,
        "응급": 5, "신체접촉": 3, "감염": 4,
        "신경": 4, "혼자": 2, "밤": 2
    }

    SAFE_KEYWORDS = {
        "앉아서": -2, "사무": -3, "전화": -2,
        "상담": -1, "관리": -1, "감시": -1
    }

    @staticmethod
    def extract_text_risk_score(description: str) -> float:
        """텍스트 설명 → 위험도 점수 (0-10)"""

        risk_score = 5.0  # 기본값

        # 키워드 매칭
        for keyword, weight in JobRiskFeatureExtractor.RISK_KEYWORDS.items():
            if keyword in description.lower():
                risk_score += weight * 0.2

        for keyword, weight in JobRiskFeatureExtractor.SAFE_KEYWORDS.items():
            if keyword in description.lower():
                risk_score += weight * 0.2

        return min(10.0, max(0.0, risk_score))

    @staticmethod
    def calculate_physical_load_factor(estimated_minutes: int) -> float:
        """신체 부담도 계산 (분 → 0-10)"""

        if estimated_minutes < 60:
            return 2.0  # 짧은 업무
        elif estimated_minutes < 240:
            return 5.0  # 중간
        elif estimated_minutes < 480:
            return 7.0  # 높음
        else:
            return 9.0  # 매우 높음

    @staticmethod
    def get_health_level_factor(required_health_level: int) -> float:
        """요구 건강 레벨 → 위험도 (1-5 → 0-10)"""

        # 레벨이 높을수록 위험도도 높음 (높은 건강이 필요 = 높은 부담)
        return required_health_level * 2.0

    @staticmethod
    def extract_features(
        title: str,
        description: str,
        estimated_minutes: int,
        required_health_level: int
    ) -> Dict[str, float]:
        """모든 피처 추출"""

        extractor = JobRiskFeatureExtractor()

        return {
            "text_risk": extractor.extract_text_risk_score(description),
            "physical_load": extractor.calculate_physical_load_factor(estimated_minutes),
            "health_level_factor": extractor.get_health_level_factor(required_health_level),
            "title_risk": extractor.extract_text_risk_score(title),
            "duration_factor": min(10.0, estimated_minutes / 60)  # 시간 → 점수
        }
