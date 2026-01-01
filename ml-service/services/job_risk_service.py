import logging
from typing import List
from schemas.job_risk import JobRiskResponse, RiskLevelEnum
from features.job_risk_features import JobRiskFeatureExtractor

logger = logging.getLogger(__name__)

class JobRiskService:
    """일자리 위험도 계산 서비스"""

    # 가중치
    WEIGHTS = {
        "text_risk": 0.40,
        "physical_load": 0.35,
        "health_level_factor": 0.20,
        "duration_factor": 0.05
    }

    @staticmethod
    def calculate_risk_score(
        job_id: int,
        title: str,
        description: str,
        estimated_minutes: int,
        required_health_level: int
    ) -> JobRiskResponse:
        """일자리 위험도 계산"""

        logger.info(f"일자리 위험도 계산: job_id={job_id}")

        try:
            # 1️⃣ 피처 추출
            features = JobRiskFeatureExtractor.extract_features(
                title, description, estimated_minutes, required_health_level
            )

            # 2️⃣ 가중평균 계산
            risk_score = sum(
                features[key] * JobRiskService.WEIGHTS.get(key, 0.0)
                for key in features.keys()
            )

            # 3️⃣ 0-10 범위로 정규화
            risk_score = min(10.0, max(0.0, risk_score))

            # 4️⃣ 위험 수준 판정
            risk_level = JobRiskService._determine_risk_level(risk_score)

            # 5️⃣ 위험 요소 추출
            risk_factors = JobRiskService._extract_risk_factors(features, risk_score)

            logger.info(f"위험도 계산 완료: score={risk_score:.1f}, level={risk_level}")

            return JobRiskResponse(
                job_id=job_id,
                risk_score=round(risk_score, 1),
                risk_level=risk_level,
                risk_factors=risk_factors
            )

        except Exception as e:
            logger.error(f"위험도 계산 실패: {str(e)}")
            raise

    @staticmethod
    def _determine_risk_level(score: float) -> RiskLevelEnum:
        """위험도 점수 → 수준"""
        if score >= 8:
            return RiskLevelEnum.CRITICAL
        elif score >= 6:
            return RiskLevelEnum.HIGH
        elif score >= 4:
            return RiskLevelEnum.MEDIUM
        else:
            return RiskLevelEnum.LOW

    @staticmethod
    def _extract_risk_factors(features: dict, total_score: float) -> List[str]:
        """주요 위험 요소 추출"""

        factors = []

        if features["text_risk"] > 5:
            factors.append(f"위험한 작업 내용 ({features['text_risk']:.0f}점)")

        if features["physical_load"] > 6:
            factors.append(f"신체 활동 많음 ({features['physical_load']:.0f}점)")

        if features["health_level_factor"] > 8:
            factors.append(f"높은 건강 요구 ({features['health_level_factor']:.0f}점)")

        if features["duration_factor"] > 7:
            factors.append(f"장시간 업무 ({features['duration_factor']:.0f}점)")

        return factors[:5]  # 최대 5개
