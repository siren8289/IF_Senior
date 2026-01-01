import logging
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime

from schemas.monitoring import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    DetectedAnomaly,
    AlertLevel,
    AnomalySeverity
)
from features.monitoring_features import MonitoringFeatureExtractor
from models.loader import get_lstm_model, get_isolation_forest

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    """센서 데이터 이상 탐지 서비스"""

    @staticmethod
    def detect_anomalies(
        request: AnomalyDetectionRequest
    ) -> AnomalyDetectionResponse:
        """
        종합 이상 탐지 (앙상블)

        알고리즘:
        1. 통계적 이상점 탐지
        2. LSTM 기반 패턴 이상
        3. Isolation Forest 앙상블
        4. 비즈니스 규칙 (낙상 등)
        5. 최종 점수 계산
        """

        logger.info(f"이상 탐지 시작: senior_id={request.senior_profile_id}")

        try:
            # 1️⃣ 데이터 준비
            readings_dict = [r.dict() for r in request.sensor_readings]

            # 2️⃣ 통계적 이상점 탐지
            statistical_anomalies = AnomalyDetectionService._detect_statistical_anomalies(
                readings_dict
            )

            # 3️⃣ LSTM 기반 탐지
            lstm_anomalies = AnomalyDetectionService._detect_lstm_anomalies(
                readings_dict
            )

            # 4️⃣ Isolation Forest 탐지
            if_anomalies = AnomalyDetectionService._detect_isolation_forest_anomalies(
                readings_dict
            )

            # 5️⃣ 비즈니스 규칙 (낙상, 심박수 이상 등)
            rule_based_anomalies = AnomalyDetectionService._detect_rule_based_anomalies(
                readings_dict
            )

            # 6️⃣ 앙상블 (투표)
            all_anomalies = statistical_anomalies + lstm_anomalies + if_anomalies + rule_based_anomalies
            detected_anomalies = AnomalyDetectionService._merge_anomalies(all_anomalies)

            # 7️⃣ 최종 점수
            anomaly_score = AnomalyDetectionService._calculate_final_score(
                detected_anomalies, len(readings_dict)
            )

            # 8️⃣ 경고 수준
            alert_level = AnomalyDetectionService._determine_alert_level(anomaly_score, detected_anomalies)

            # 9️⃣ 권장사항
            recommendations = AnomalyDetectionService._generate_recommendations(detected_anomalies)

            logger.info(f"이상 탐지 완료: score={anomaly_score:.2f}, level={alert_level}")

            return AnomalyDetectionResponse(
                senior_profile_id=request.senior_profile_id,
                matching_id=request.matching_id,
                anomalies_detected=len(detected_anomalies) > 0,
                anomaly_score=round(anomaly_score, 2),
                alert_level=alert_level,
                detected_anomalies=detected_anomalies,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"이상 탐지 실패: {str(e)}")
            raise

    @staticmethod
    def _detect_statistical_anomalies(readings: List[Dict]) -> List[DetectedAnomaly]:
        """통계적 이상점 탐지"""

        anomalies = []

        # 심박수 이상
        heart_rates = [r["heart_rate"] for r in readings if r.get("heart_rate")]
        if heart_rates:
            outlier_indices = MonitoringFeatureExtractor.detect_outliers_statistical(heart_rates)

            for idx in outlier_indices:
                reading = readings[idx]
                anomalies.append(DetectedAnomaly(
                    timestamp=reading["timestamp"],
                    type="heart_rate_spike",
                    value=reading["heart_rate"],
                    normal_range=[60, 85],
                    severity=AnomalySeverity.MEDIUM
                ))

        return anomalies

    @staticmethod
    def _detect_lstm_anomalies(readings: List[Dict]) -> List[DetectedAnomaly]:
        """LSTM 기반 시계열 패턴 이상"""

        try:
            model = get_lstm_model()

            # 심박수 시계열
            heart_rates = np.array([r["heart_rate"] for r in readings if r.get("heart_rate")])

            if len(heart_rates) < 10:
                return []

            # LSTM 재구성 오차
            reconstructed = model.predict(heart_rates.reshape(-1, 1))
            errors = np.abs(heart_rates - reconstructed.flatten())

            # 높은 오차 = 이상
            threshold = np.mean(errors) + 2 * np.std(errors)
            anomaly_indices = np.where(errors > threshold)[0]

            anomalies = []
            for idx in anomaly_indices:
                reading = readings[idx]
                anomalies.append(DetectedAnomaly(
                    timestamp=reading["timestamp"],
                    type="lstm_anomaly",
                    value=reading["heart_rate"],
                    normal_range=[60, 85],
                    severity=AnomalySeverity.LOW
                ))

            return anomalies

        except Exception as e:
            logger.warning(f"LSTM 탐지 실패: {str(e)}")
            return []

    @staticmethod
    def _detect_isolation_forest_anomalies(readings: List[Dict]) -> List[DetectedAnomaly]:
        """Isolation Forest 앙상블"""

        try:
            model = get_isolation_forest()

            # 피처 추출
            features = MonitoringFeatureExtractor.extract_time_series_features(readings)

            # 예측
            scores = model.score_samples(np.array(list(features.values())).reshape(1, -1))

            # scores < -0.5 = 이상
            if scores[0] < -0.5:
                return [DetectedAnomaly(
                    timestamp=readings[-1]["timestamp"],
                    type="ensemble_anomaly",
                    value=float(scores[0]),
                    normal_range=[-1.0, -0.5],
                    severity=AnomalySeverity.MEDIUM
                )]

            return []

        except Exception as e:
            logger.warning(f"Isolation Forest 탐지 실패: {str(e)}")
            return []

    @staticmethod
    def _detect_rule_based_anomalies(readings: List[Dict]) -> List[DetectedAnomaly]:
        """비즈니스 규칙 기반 탐지"""

        anomalies = []

        # 낙상 탐지
        for i, reading in enumerate(readings):
            if MonitoringFeatureExtractor.detect_fall(
                reading.get("posture"),
                reading["activity"]
            ):
                anomalies.append(DetectedAnomaly(
                    timestamp=reading["timestamp"],
                    type="fall_detected",
                    value=reading["posture"]["angle"],
                    normal_range=[80, 100],
                    severity=AnomalySeverity.HIGH
                ))

        # 극단적 심박수
        for i, reading in enumerate(readings):
            if reading.get("heart_rate"):
                if reading["heart_rate"] > 150:
                    anomalies.append(DetectedAnomaly(
                        timestamp=reading["timestamp"],
                        type="high_heart_rate_critical",
                        value=reading["heart_rate"],
                        normal_range=[60, 85],
                        severity=AnomalySeverity.HIGH
                    ))

        return anomalies

    @staticmethod
    def _merge_anomalies(anomalies: List[DetectedAnomaly]) -> List[DetectedAnomaly]:
        """중복 이상점 병합"""

        # 타임스탬프 기준 그룹화
        merged = {}
        for anomaly in anomalies:
            key = anomaly.timestamp.isoformat()
            if key not in merged:
                merged[key] = anomaly
            else:
                # 더 심각한 것으로 덮어쓰기
                if anomaly.severity.value > merged[key].severity.value:
                    merged[key] = anomaly

        return list(merged.values())

    @staticmethod
    def _calculate_final_score(
        anomalies: List[DetectedAnomaly],
        total_readings: int
    ) -> float:
        """최종 이상도 점수 (0-1)"""

        if not anomalies:
            return 0.0

        # 심각도 가중치
        severity_weights = {
            AnomalySeverity.LOW: 0.2,
            AnomalySeverity.MEDIUM: 0.5,
            AnomalySeverity.HIGH: 1.0
        }

        total_score = sum(severity_weights.get(a.severity, 0.0) for a in anomalies)

        # 정규화
        score = min(1.0, total_score / (total_readings / 10))

        return score

    @staticmethod
    def _determine_alert_level(
        score: float,
        anomalies: List[DetectedAnomaly]
    ) -> AlertLevel:
        """경고 수준 결정"""

        # 심각한 이상 있으면 CRITICAL
        if any(a.severity == AnomalySeverity.HIGH for a in anomalies):
            return AlertLevel.CRITICAL

        # 점수 기반
        if score > 0.7:
            return AlertLevel.CRITICAL
        elif score > 0.4:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO

    @staticmethod
    def _generate_recommendations(anomalies: List[DetectedAnomaly]) -> List[str]:
        """권장사항 생성"""

        recommendations = []

        for anomaly in anomalies:
            if anomaly.type == "fall_detected":
                recommendations.append("즉시 도움 필요 (낙상 감지)")
            elif anomaly.type == "high_heart_rate_critical":
                recommendations.append("휴식 후 병원 방문 권장")
            elif anomaly.type == "heart_rate_spike":
                recommendations.append("쉬게 해주세요")
                recommendations.append("수분 섭취 확인")
            elif anomaly.type == "lstm_anomaly":
                recommendations.append("비정상적인 패턴 감지")

        return list(set(recommendations))[:5]  # 중복 제거, 최대 5개
