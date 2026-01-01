from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class ActivityType(str, Enum):
    WALKING = "walking"
    SITTING = "sitting"
    STANDING = "standing"
    LYING = "lying"
    MOVING = "moving"

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Request
class PostureData(BaseModel):
    angle: float = Field(..., ge=0, le=180, description="몸 각도")
    balance: str = Field(..., description="균형 상태")

class SensorReading(BaseModel):
    timestamp: datetime
    heart_rate: Optional[int] = Field(None, ge=30, le=200)
    step_count: Optional[int] = Field(None, ge=0)
    posture: Optional[PostureData] = None
    activity: ActivityType = ActivityType.WALKING

class AnomalyDetectionRequest(BaseModel):
    """이상 탐지 요청"""
    senior_profile_id: int
    matching_id: int
    sensor_readings: List[SensorReading] = Field(..., min_items=1, max_items=1000)

    class Config:
        schema_extra = {
            "example": {
                "senior_profile_id": 1,
                "matching_id": 1,
                "sensor_readings": [
                    {
                        "timestamp": "2025-01-01T10:00:00Z",
                        "heart_rate": 72,
                        "step_count": 100,
                        "posture": {"angle": 90, "balance": "normal"},
                        "activity": "walking"
                    }
                ]
            }
        }

# Response
class DetectedAnomaly(BaseModel):
    timestamp: datetime
    type: str = Field(..., description="이상 유형 (heart_rate_spike, fall, etc.)")
    value: float = Field(..., description="현재값")
    normal_range: List[float] = Field(..., description="정상 범위 [min, max]")
    severity: AnomalySeverity

class AnomalyDetectionResponse(BaseModel):
    """이상 탐지 응답"""
    senior_profile_id: int
    matching_id: int
    anomalies_detected: bool
    anomaly_score: float = Field(..., ge=0, le=1, description="종합 이상도 (0-1)")
    alert_level: AlertLevel
    detected_anomalies: List[DetectedAnomaly]
    recommendations: List[str]

    class Config:
        schema_extra = {
            "example": {
                "senior_profile_id": 1,
                "matching_id": 1,
                "anomalies_detected": True,
                "anomaly_score": 0.78,
                "alert_level": "warning",
                "detected_anomalies": [
                    {
                        "timestamp": "2025-01-01T10:15:00Z",
                        "type": "heart_rate_spike",
                        "value": 95,
                        "normal_range": [60, 85],
                        "severity": "medium"
                    }
                ],
                "recommendations": ["쉬게 해주세요", "수분 섭취 확인"]
            }
        }

