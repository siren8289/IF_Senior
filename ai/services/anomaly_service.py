import logging
import numpy as np
from typing import List, Dict

from schemas.monitoring import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    DetectedAnomaly,
    AlertLevel,
    AnomalySeverity,
)
from features.monitoring_features import MonitoringFeatureExtractor
from models.loader import get_isolation_forest, get_lstm_model

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """센서 데이터 이상 탐지 서비스"""

    @staticmethod
    def detect_anomalies(
        request: AnomalyDetectionRequest
    ) -> AnomalyDetectionResponse:

        logger.info(f"이상 탐지 시작: senior_id={request.senior_profile_id}")

        # --------------------------------------------------
        # 입력 데이터 정리
        # --------------------------------------------------
        readings: List[Dict] = [r.dict() for r in request.sensor_readings]

        detected_anomalies: List[DetectedAnomaly] = []

        # --------------------------------------------------
        # 1️⃣ 통계 기반 이상 탐지
        # --------------------------------------------------
        detected_anomalies.extend(
            AnomalyDetectionService._detect_statistical_anomalies(readings)
        )

        # --------------------------------------------------
        # 2️⃣ Isolation Forest (⭐ 핵심 ML)
        # --------------------------------------------------
        detected_anomalies.extend(
            AnomalyDetectionService._detect_isolation_forest_anomalies(readings)
        )

        # --------------------------------------------------
        # 3️⃣ LSTM (선택적, 실패 허용)
        # --------------------------------------------------
        detected_anomalies.extend(
            AnomalyDetectionService._detect_lstm_anomalies(readings)
        )

        # --------------------------------------------------
        # 4️⃣ 규칙 기반 (낙상, 위험 심박)
        # --------------------------------------------------
        detected_anomalies.extend(
            AnomalyDetectionService._detect_rule_based_anomalies(readings)
        )

        # --------------------------------------------------
        # 후처리
        # --------------------------------------------------
        detected_anomalies = AnomalyDetectionService._merge_anomalies(
            detected_anomalies
        )

        anomaly_score = AnomalyDetectionService._calculate_final_score(
            detected_anomalies, len(readings)
        )

        alert_level = AnomalyDetectionService._determine_alert_level(
            anomaly_score, detected_anomalies
        )

        recommendations = AnomalyDetectionService._generate_recommendations(
            detected_anomalies
        )

        logger.info(
            f"이상 탐지 완료: score={anomaly_score:.2f}, level={alert_level}"
        )

        return AnomalyDetectionResponse(
            senior_profile_id=request.senior_profile_id,
            matching_id=request.matching_id,
            anomalies_detected=len(detected_anomalies) > 0,
            anomaly_score=round(anomaly_score, 2),
            alert_level=alert_level,
            detected_anomalies=detected_anomalies,
            recommendations=recommendations,
        )

    # =====================================================
    # 통계 기반 이상 탐지
    # =====================================================
    @staticmethod
    def _detect_statistical_anomalies(
        readings: List[Dict],
    ) -> List[DetectedAnomaly]:

        anomalies: List[DetectedAnomaly] = []

        heart_rates = [
            r["heart_rate"]
            for r in readings
            if r.get("heart_rate") is not None
        ]

        if not heart_rates:
            return anomalies

        indices = MonitoringFeatureExtractor.detect_outliers_statistical(heart_rates)

        for idx in indices:
            r = readings[idx]
            anomalies.append(
                DetectedAnomaly(
                    timestamp=r["timestamp"],
                    type="heart_rate_spike",
                    value=r["heart_rate"],
                    normal_range=[60, 85],
                    severity=AnomalySeverity.MEDIUM,
                )
            )

        return anomalies

    # =====================================================
    # ⭐ Isolation Forest (10개 피처 고정)
    # =====================================================
    @staticmethod
    def _detect_isolation_forest_anomalies(
        readings: List[Dict],
    ) -> List[DetectedAnomaly]:

        try:
            model = get_isolation_forest()
            if model is None:
                return []

            # 1️⃣ 시계열 → 피처 dict
            features = MonitoringFeatureExtractor.extract_time_series_features(
                readings
            )

            # 2️⃣ ⭐ 고정된 입력 벡터 (10개)
            vector = MonitoringFeatureExtractor.to_model_input(features)

            # 🔍 디버그 확인용 (문제 해결 후 제거 가능)
            logger.warning(
                f"[DEBUG] Isolation Forest input dim = {len(vector)}"
            )

            # 3️⃣ sklearn 입력 형태
            X = np.array(vector).reshape(1, -1)

            # 4️⃣ anomaly score
            score = float(model.decision_function(X)[0])

            # 경험적 기준
            if score < -0.5:
                return [
                    DetectedAnomaly(
                        timestamp=readings[-1]["timestamp"],
                        type="isolation_forest_anomaly",
                        value=score,
                        normal_range=[-0.5, 1.0],
                        severity=AnomalySeverity.MEDIUM,
                    )
                ]

            return []

        except Exception as e:
            logger.warning(f"Isolation Forest 탐지 실패: {str(e)}")
            return []

    # =====================================================
    # LSTM (선택적)
    # =====================================================
    @staticmethod
    def _detect_lstm_anomalies(
        readings: List[Dict],
    ) -> List[DetectedAnomaly]:

        try:
            model = get_lstm_model()
            if model is None:
                return []

            heart_rates = np.array(
                [
                    r["heart_rate"]
                    for r in readings
                    if r.get("heart_rate") is not None
                ]
            )

            if len(heart_rates) < 10:
                return []

            reconstructed = model.predict(heart_rates.reshape(-1, 1))
            errors = np.abs(heart_rates - reconstructed.flatten())

            threshold = np.mean(errors) + 2 * np.std(errors)
            indices = np.where(errors > threshold)[0]

            anomalies: List[DetectedAnomaly] = []

            for idx in indices:
                r = readings[idx]
                anomalies.append(
                    DetectedAnomaly(
                        timestamp=r["timestamp"],
                        type="lstm_anomaly",
                        value=r["heart_rate"],
                        normal_range=[60, 85],
                        severity=AnomalySeverity.LOW,
                    )
                )

            return anomalies

        except Exception as e:
            logger.warning(f"LSTM 탐지 실패: {str(e)}")
            return []

    # =====================================================
    # 규칙 기반
    # =====================================================
    @staticmethod
    def _detect_rule_based_anomalies(
        readings: List[Dict],
    ) -> List[DetectedAnomaly]:

        anomalies: List[DetectedAnomaly] = []

        for r in readings:
            # 낙상
            if MonitoringFeatureExtractor.detect_fall(
                r.get("posture"), r.get("activity")
            ):
                anomalies.append(
                    DetectedAnomaly(
                        timestamp=r["timestamp"],
                        type="fall_detected",
                        value=r["posture"]["angle"],
                        normal_range=[80, 100],
                        severity=AnomalySeverity.HIGH,
                    )
                )

            # 치명적 심박
            if r.get("heart_rate") and r["heart_rate"] > 150:
                anomalies.append(
                    DetectedAnomaly(
                        timestamp=r["timestamp"],
                        type="high_heart_rate_critical",
                        value=r["heart_rate"],
                        normal_range=[60, 85],
                        severity=AnomalySeverity.HIGH,
                    )
                )

        return anomalies

    # =====================================================
    # 후처리 로직
    # =====================================================
    @staticmethod
    def _merge_anomalies(
        anomalies: List[DetectedAnomaly],
    ) -> List[DetectedAnomaly]:

        merged = {}

        for a in anomalies:
            key = (a.timestamp, a.type)
            if key not in merged or a.severity.value > merged[key].severity.value:
                merged[key] = a

        return list(merged.values())

    @staticmethod
    def _calculate_final_score(
        anomalies: List[DetectedAnomaly],
        total_readings: int,
    ) -> float:

        if not anomalies:
            return 0.0

        weights = {
            AnomalySeverity.LOW: 0.2,
            AnomalySeverity.MEDIUM: 0.5,
            AnomalySeverity.HIGH: 1.0,
        }

        raw_score = sum(weights[a.severity] for a in anomalies)
        return min(1.0, raw_score / max(1, total_readings / 10))

    @staticmethod
    def _determine_alert_level(
        score: float,
        anomalies: List[DetectedAnomaly],
    ) -> AlertLevel:

        if any(a.severity == AnomalySeverity.HIGH for a in anomalies):
            return AlertLevel.CRITICAL
        if score > 0.7:
            return AlertLevel.CRITICAL
        if score > 0.4:
            return AlertLevel.WARNING
        return AlertLevel.INFO

    @staticmethod
    def _generate_recommendations(
        anomalies: List[DetectedAnomaly],
    ) -> List[str]:

        recs = []

        for a in anomalies:
            if a.type == "fall_detected":
                recs.append("즉시 보호자 및 응급 대응이 필요합니다.")
            elif a.type == "high_heart_rate_critical":
                recs.append("휴식 후 병원 방문을 권장합니다.")
            elif a.type == "heart_rate_spike":
                recs.append("휴식 및 수분 섭취를 권장합니다.")
            elif a.type == "lstm_anomaly":
                recs.append("비정상 패턴 지속 관찰이 필요합니다.")

        return list(set(recs))[:5]
