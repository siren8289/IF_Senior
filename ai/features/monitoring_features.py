import numpy as np
import pandas as pd
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

class MonitoringFeatureExtractor:
    """센서 데이터 피처 엔지니어링"""

    # 정상 범위
    NORMAL_RANGES = {
        "heart_rate": (60, 85),
        "heart_rate_max": (70, 100),
        "step_rate": (0, 150),  # steps/minute
        "posture_angle": (80, 100)
    }

    # 경고 범위
    ALERT_RANGES = {
        "heart_rate": (120, 150),
        "heart_rate_critical": (150, 200)
    }

    @staticmethod
    def extract_time_series_features(
        sensor_readings: List[Dict]
    ) -> Dict[str, float]:
        """시계열 데이터 → 피처 추출"""

        heart_rates = [r["heart_rate"] for r in sensor_readings if r.get("heart_rate")]
        step_counts = [r["step_count"] for r in sensor_readings if r.get("step_count")]

        features = {}

        # 심박수 관련
        if heart_rates:
            features["hr_mean"] = np.mean(heart_rates)
            features["hr_std"] = np.std(heart_rates)
            features["hr_max"] = np.max(heart_rates)
            features["hr_min"] = np.min(heart_rates)
            features["hr_trend"] = heart_rates[-1] - heart_rates[0]  # 추세

        # 걸음수 관련
        if step_counts:
            features["step_mean"] = np.mean(step_counts)
            features["step_std"] = np.std(step_counts)
            features["step_rate"] = sum(step_counts) / len(step_counts)

        # 활동 유형 분포
        activities = [r["activity"] for r in sensor_readings]
        for activity in set(activities):
            features[f"activity_{activity}"] = activities.count(activity) / len(activities)

        return features

    @staticmethod
    def detect_outliers_statistical(
        values: List[float],
        threshold: float = 3.0
    ) -> List[int]:
        """통계적 이상점 탐지 (Z-score)"""

        if len(values) < 2:
            return []

        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        z_scores = np.abs((values - mean) / std)
        outlier_indices = np.where(z_scores > threshold)[0].tolist()

        return outlier_indices

    @staticmethod
    def detect_fall(posture_data: Dict, activity: str) -> bool:
        """낙상 탐지 (자세 + 활동 유형)"""

        if not posture_data:
            return False

        angle = posture_data.get("angle", 90)

        # 누운 자세 + walking → 낙상 가능성
        if angle < 45 and activity in ["walking", "standing"]:
            return True

        return False
