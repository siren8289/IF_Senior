import numpy as np
from typing import List, Dict


class MonitoringFeatureExtractor:
    """
    센서 데이터 피처 엔지니어링
    - 통계 기반 피처
    - 규칙 기반 탐지
    - ML 모델 입력 벡터 생성
    """

    # 정상 범위
    NORMAL_RANGES = {
        "heart_rate": (60, 85),
        "heart_rate_max": (70, 100),
        "step_rate": (0, 150),  # steps/minute
        "posture_angle": (80, 100),
    }

    # 경고 범위
    ALERT_RANGES = {
        "heart_rate": (120, 150),
        "heart_rate_critical": (150, 200),
    }

    # =========================================================
    # 1️⃣ 시계열 → 통계 피처 추출
    # =========================================================
    @staticmethod
    def extract_time_series_features(
        sensor_readings: List[Dict]
    ) -> Dict[str, float]:
        """
        시계열 센서 데이터 → 통계 피처 추출
        """

        if not sensor_readings:
            return {}

        heart_rates = [
            r["heart_rate"]
            for r in sensor_readings
            if r.get("heart_rate") is not None
        ]
        step_counts = [
            r["step_count"]
            for r in sensor_readings
            if r.get("step_count") is not None
        ]

        features: Dict[str, float] = {}

        # 심박수 관련 피처
        if heart_rates:
            features["hr_mean"] = float(np.mean(heart_rates))
            features["hr_std"] = float(np.std(heart_rates))
            features["hr_max"] = float(np.max(heart_rates))
            features["hr_min"] = float(np.min(heart_rates))
            features["hr_trend"] = float(heart_rates[-1] - heart_rates[0])

        # 걸음수 관련 피처
        if step_counts:
            features["step_mean"] = float(np.mean(step_counts))
            features["step_std"] = float(np.std(step_counts))
            features["step_rate"] = float(sum(step_counts) / len(step_counts))

        # 활동 유형 분포
        activities = [r.get("activity") for r in sensor_readings if r.get("activity")]
        total = len(activities)

        if total > 0:
            for activity in ["walking", "sitting", "lying", "standing"]:
                features[f"activity_{activity}"] = activities.count(activity) / total

        return features

    # =========================================================
    # 2️⃣ 통계적 이상치 탐지 (Z-score)
    # =========================================================
    @staticmethod
    def detect_outliers_statistical(
        values: List[float],
        threshold: float = 3.0
    ) -> List[int]:
        """
        통계적 이상점 탐지 (Z-score)
        """

        if len(values) < 2:
            return []

        values_np = np.array(values)
        mean = np.mean(values_np)
        std = np.std(values_np)

        if std == 0:
            return []

        z_scores = np.abs((values_np - mean) / std)
        return np.where(z_scores > threshold)[0].tolist()

    # =========================================================
    # 3️⃣ 규칙 기반 낙상 탐지
    # =========================================================
    @staticmethod
    def detect_fall(posture_data: Dict, activity: str) -> bool:
        """
        낙상 탐지 (자세 + 활동 유형)
        """

        if not posture_data:
            return False

        angle = posture_data.get("angle", 90)

        # 누운 자세 + 보행/서있음 → 낙상 가능성
        if angle < 45 and activity in ["walking", "standing"]:
            return True

        return False

    # =========================================================
    # 4️⃣ ⭐ ML 모델 입력 벡터 생성 (핵심)
    # =========================================================
    @staticmethod
    def to_model_input(features: Dict[str, float]) -> List[float]:
        """
        Isolation Forest / LSTM 공통 입력 벡터
        ⚠️ 순서 절대 변경 금지 (모델 계약)
        """

        return [
            features.get("hr_mean", 0.0),
            features.get("hr_std", 0.0),
            features.get("hr_max", 0.0),
            features.get("hr_min", 0.0),
            features.get("hr_trend", 0.0),
            features.get("step_rate", 0.0),
            features.get("activity_walking", 0.0),
            features.get("activity_sitting", 0.0),
            features.get("activity_lying", 0.0),
            features.get("activity_standing", 0.0),
        ]
