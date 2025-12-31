import numpy as np
import pickle
from typing import Dict, List, Tuple
import logging

from schemas.health import HealthScoreResponse, RiskLevel
from features.health_features import HealthFeatureExtractor
from models.loader import get_health_model
from utils.validators import validate_health_input

logger = logging.getLogger(__name__)

class HealthScoreService:
    """건강점수 계산 서비스 (ML 모델)"""

    # 점수 가중치
    WEIGHTS = {
        "bmi_factor": 0.25,
        "chronic_factor": 0.30,
        "mobility_factor": 0.20,
        "cognitive_factor": 0.15,
        "age_factor": 0.10
    }

    @staticmethod
    def calculate_health_score(
        senior_profile_id: int,
        height_cm: int,
        weight_kg: float,
        chronic_conditions: Dict[str, bool],
        risk_flags: Dict[str, float]
    ) -> HealthScoreResponse:
        """
        건강점수 계산 (규칙 기반 + ML 모델)

        점수 계산 알고리즘:
        1. 피처 추출
        2. 규칙 기반 점수 계산
        3. ML 모델 예측 (앙상블)
        4. 최종 점수 정규화
        """

        logger.info(f"건강점수 계산 시작: senior_profile_id={senior_profile_id}")

        try:
            # 1️⃣ 입력 검증
            validate_health_input(height_cm, weight_kg, chronic_conditions, risk_flags)

            # 2️⃣ 피처 추출
            features = HealthFeatureExtractor.extract_features(
                height_cm, weight_kg, chronic_conditions, risk_flags
            )

            # 3️⃣ 규칙 기반 점수 계산 (0-1)
            score_components = HealthScoreService._calculate_rule_based_score(
                features, chronic_conditions, risk_flags
            )

            # 4️⃣ ML 모델 예측 (선택사항)
            ml_score = HealthScoreService._predict_with_ml_model(features)

            # 5️⃣ 앙상블 (규칙 70% + ML 30%)
            final_score_normalized = (
                0.7 * HealthScoreService._normalize_components(score_components) +
                0.3 * ml_score
            )

            # 6️⃣ 0-100 범위로 변환
            final_score = final_score_normalized * 100
            final_score = max(0, min(100, final_score))  # 클립핑

            # 7️⃣ 위험 수준 판정
            risk_level = HealthScoreService._determine_risk_level(final_score)

            # 8️⃣ 권장사항 생성
            recommendations = HealthScoreService._generate_recommendations(
                final_score, chronic_conditions, risk_flags
            )

            logger.info(f"건강점수 계산 완료: score={final_score:.1f}, risk={risk_level}")

            return HealthScoreResponse(
                senior_profile_id=senior_profile_id,
                health_score=round(final_score, 1),
                risk_level=risk_level,
                components=score_components,
                recommendations=recommendations
            )

        except ValueError as e:
            logger.error(f"입력 검증 실패: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"건강점수 계산 실패: {str(e)}")
            raise

    @staticmethod
    def _calculate_rule_based_score(
        features: Dict[str, float],
        chronic_conditions: Dict[str, bool],
        risk_flags: Dict[str, float]
    ) -> Dict[str, float]:
        """규칙 기반 점수 계산 (0-1)"""

        components = {
            "bmi_factor": features["bmi_factor"],
            "chronic_factor": features["chronic_factor"],
            "mobility_factor": features["mobility_factor"],
            "cognitive_factor": features["cognitive_factor"],
            "age_factor": 0.85  # 예: 나이별 기본값
        }

        return components

    @staticmethod
    def _predict_with_ml_model(features: Dict[str, float]) -> float:
        """
        ML 모델을 이용한 예측 (0-1)

        선택사항: BERT 기반 텍스트 분류나 다른 고급 모델 사용 가능
        현재는 규칙 기반이 주, ML은 보조
        """

        try:
            model = get_health_model()

            # 피처를 배열로 변환
            feature_vector = np.array([
                features.get("bmi_factor", 0.5),
                features.get("chronic_factor", 0.8),
                features.get("mobility_factor", 0.9),
                features.get("cognitive_factor", 0.9)
            ]).reshape(1, -1)

            # 모델 예측
            prediction = model.predict(feature_vector)[0]

            return float(prediction)

        except Exception as e:
            logger.warning(f"ML 모델 예측 실패 (규칙 기반으로 진행): {str(e)}")
            return 0.5  # 기본값으로 폴백

    @staticmethod
    def _normalize_components(components: Dict[str, float]) -> float:
        """컴포넌트 정규화 및 가중평균 계산"""

        total_score = 0.0
        total_weight = 0.0

        for component_name, component_value in components.items():
            weight = HealthScoreService.WEIGHTS.get(component_name, 0.1)
            total_score += component_value * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.5

    @staticmethod
    def _determine_risk_level(score: float) -> RiskLevel:
        """건강점수 → 위험 수준"""
        if score >= 80:
            return RiskLevel.LOW
        elif score >= 60:
            return RiskLevel.MEDIUM
        elif score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    @staticmethod
    def _generate_recommendations(
        score: float,
        chronic_conditions: Dict[str, bool],
        risk_flags: Dict[str, float]
    ) -> List[str]:
        """점수와 질환에 따른 권장사항 생성"""

        recommendations = []

        # 점수 기반
        if score < 50:
            recommendations.append("전문의 진료 권장")
            recommendations.append("건강 관리 프로그램 참여")
        elif score < 70:
            recommendations.append("정기적인 건강검진 필요")
            recommendations.append("생활습관 개선")

        # 만성질환 기반
        if chronic_conditions.get("hypertension"):
            recommendations.append("혈압 관리 필요")
            recommendations.append("염분 섭취 제한")

        if chronic_conditions.get("diabetes"):
            recommendations.append("혈당 관리 필요")
            recommendations.append("식이요법 상담")

        if chronic_conditions.get("arthritis"):
            recommendations.append("관절 운동 치료 권장")
            recommendations.append("적절한 휴식 필요")

        # 위험 지표 기반
        if risk_flags.get("mobility_limited", 0) > 0.5:
            recommendations.append("물리치료 권장")
            recommendations.append("운동 능력 회복 프로그램")

        if risk_flags.get("cognitive_impairment_risk", 0) > 0.5:
            recommendations.append("인지 기능 검사 필요")
            recommendations.append("인지 훈련 프로그램")

        # 기본 권장사항
        if len(recommendations) == 0:
            recommendations.append("현재 건강 상태 유지")
            recommendations.append("규칙적인 운동 권장")

        return recommendations[:5]  # 최대 5개
