from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Request
class HealthScoreRequest(BaseModel):
    """건강점수 계산 요청"""
    senior_profile_id: int = Field(..., description="시니어 프로필 ID")
    height_cm: int = Field(..., ge=100, le=250, description="키 (cm)")
    weight_kg: float = Field(..., ge=20, le=200, description="체중 (kg)")

    chronic_conditions: Dict[str, bool] = Field(
        default_factory=dict,
        description="만성질환 (hypertension, diabetes, etc.)"
    )
    risk_flags: Dict[str, float] = Field(
        default_factory=dict,
        description="위험 지표 (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "senior_profile_id": 1,
                "height_cm": 170,
                "weight_kg": 75.5,
                "chronic_conditions": {
                    "hypertension": True,
                    "diabetes": False,
                    "arthritis": False
                },
                "risk_flags": {
                    "mobility_limited": 0.3,
                    "cognitive_impairment_risk": 0.2
                }
            }
        }

# Response
class ScoreComponent(BaseModel):
    """점수 구성 요소"""
    name: str
    value: float = Field(..., ge=0, le=1)
    weight: float = Field(..., ge=0, le=1)

class HealthScoreResponse(BaseModel):
    """건강점수 계산 응답"""
    senior_profile_id: int
    health_score: float = Field(..., ge=0, le=100, description="종합 건강점수 (0-100)")
    risk_level: RiskLevel = Field(..., description="위험 수준")
    components: Dict[str, float] = Field(..., description="점수 구성 요소")
    recommendations: List[str] = Field(..., description="권장사항")

    class Config:
        json_schema_extra = {
            "example": {
                "senior_profile_id": 1,
                "health_score": 78.5,
                "risk_level": "medium",
                "components": {
                    "age_factor": 0.85,
                    "bmi_factor": 0.90,
                    "chronic_conditions_factor": 0.65,
                    "mobility_factor": 0.95
                },
                "recommendations": [
                    "혈압 관리 필요",
                    "규칙적인 운동 권장",
                    "식이요법 상담"
                ]
            }
        }

class ErrorResponse(BaseModel):
    """에러 응답"""
    error_code: str
    message: str
    details: Optional[Dict] = None
