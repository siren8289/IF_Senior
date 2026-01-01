from typing import Dict, List
import math

class MatchingFeatureExtractor:
    """매칭 점수 피처 추출"""

    @staticmethod
    def calculate_health_compatibility(
        senior_health_score: float,
        required_health_level: int
    ) -> float:
        """건강 호환성 (0-1)"""

        # 건강점수 (0-100) ↔ 레벨 (1-5) 변환
        health_level = senior_health_score / 20  # 0-100 → 0-5

        # 레벨 차이
        diff = abs(health_level - required_health_level)

        # 차이가 작을수록 높은 점수
        if diff == 0:
            return 1.0
        elif diff <= 1:
            return 0.9
        elif diff <= 2:
            return 0.7
        else:
            return 0.4

    @staticmethod
    def calculate_experience_match(
        senior_years_experience: int,
        senior_titles: List[str],
        job_title: str,
        job_description: str
    ) -> float:
        """경험 매칭도 (0-1)"""

        score = 0.0

        # 경험 년수
        if senior_years_experience >= 5:
            score += 0.5
        elif senior_years_experience >= 2:
            score += 0.3
        elif senior_years_experience > 0:
            score += 0.1

        # 직무 유사성 (키워드 기반)
        if senior_titles:
            for title in senior_titles:
                if title.lower() in job_title.lower():
                    score += 0.3
                elif any(keyword in job_description.lower()
                        for keyword in title.lower().split()):
                    score += 0.2

        return min(1.0, score)

    @staticmethod
    def calculate_location_distance(
        senior_region: str,
        job_location: str
    ) -> float:
        """거리 (km) - 정확한 좌표가 있으면 실제 거리 계산"""

        # 임시: 같은 지역이면 0, 다르면 추정 거리
        if senior_region == job_location:
            return 0.0
        elif senior_region.split()[0] == job_location.split()[0]:  # 시/도만 확인
            return 5.0
        else:
            return 20.0

    @staticmethod
    def calculate_availability_match(
        senior_available: bool,
        schedule_conflict: bool = False
    ) -> float:
        """가용성 매칭 (0-1)"""

        if not senior_available:
            return 0.0
        elif schedule_conflict:
            return 0.5
        else:
            return 1.0
