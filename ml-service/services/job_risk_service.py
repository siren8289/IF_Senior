import logging
from typing import List, Dict
from schemas.job_risk import JobRiskResponse, RiskLevelEnum
from features.job_risk_features import JobRiskFeatureExtractor

logger = logging.getLogger("services.job_risk")
logger.setLevel(logging.INFO)

class JobRiskService:
    """일자리 위험도 계산 서비스"""

    WEIGHTS: Dict[str, float] = {
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

        logger.info(f"[JobRisk] 요청 | job_id={job_id}")

        try:
            # 1️⃣ 피처 추출
            features = JobRiskFeatureExtractor.extract_features(
                title, description, estimated_minutes, required_health_level
            )

            logger.debug(f"[JobRisk] 추출된 피처 = {features}")

            # 2️⃣ 점수 계산
            risk_score = 0.0
            for key, weight in JobRiskService.WEIGHTS.items():
                value = features.get(key, 0.0)
                contribution = value * weight
                risk_score += contribution
                logger.debug(
                    f"[JobRisk][calc] {key} value={value:.2f}, "
                    f"weight={weight}, contribution={contribution:.2f}"
                )

            # 3️⃣ 0~10 정규화
            risk_score = min(10.0, max(0.0, risk_score))

            # 4️⃣ 위험 수준
            risk_level = JobRiskService._determine_risk_level(risk_score)

            # 5️⃣ 위험 요소
            risk_factors = JobRiskService._extract_risk_factors(features, risk_score)

            # ✅ 최종 요약 로그 (INFO — 깔끔하게 1줄)
            logger.info(
                f"[JobRisk] 완료 | job_id={job_id} | "
                f"score={risk_score:.1f}, level={risk_level}, "
                f"factors={len(risk_factors)}개"
            )

            return JobRiskResponse(
                job_id=job_id,
                risk_score=round(risk_score, 1),
                risk_level=risk_level,
                risk_factors=risk_factors
            )

        except Exception:
            logger.exception(f"[JobRisk] 💥 위험도 계산 실패 | job_id={job_id}")
            raise

    @staticmethod
    def _determine_risk_level(score: float) -> RiskLevelEnum:
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
        factors = []

        if features.get("text_risk", 0) > 5:
            factors.append(f"위험한 작업 내용 ({features['text_risk']:.0f}점)")
        if features.get("physical_load", 0) > 6:
            factors.append(f"신체 활동 많음 ({features['physical_load']:.0f}점)")
        if features.get("health_level_factor", 0) > 8:
            factors.append(f"높은 건강 요구 ({features['health_level_factor']:.0f}점)")
        if features.get("duration_factor", 0) > 7:
            factors.append(f"장시간 업무 ({features['duration_factor']:.0f}점)")

        return factors[:5]
