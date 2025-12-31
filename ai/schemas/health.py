from pydantic import BaseModel, Field
<<<<<<< HEAD
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
=======
from typing import Optional, List


class HealthRequest(BaseModel):
    """건강 점수 계산 요청"""
    age: int = Field(..., description="나이", ge=0, le=120)
    gender: str = Field(..., description="성별", pattern="^(M|F)$")
    health_conditions: Optional[List[str]] = Field(default=[], description="건강 상태 리스트")
    lifestyle_factors: Optional[dict] = Field(default={}, description="생활습관 요소")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "M",
                "health_conditions": ["diabetes", "hypertension"],
                "lifestyle_factors": {
                    "smoking": False,
                    "exercise": True
>>>>>>> main
                }
            }
        }

<<<<<<< HEAD
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
=======

class HealthResponse(BaseModel):
    """건강 점수 계산 응답"""
    score: float = Field(..., description="건강 점수", ge=0, le=100)
    risk_level: str = Field(..., description="위험도 레벨")
    factors: dict = Field(..., description="영향 요인")
    recommendations: Optional[List[str]] = Field(default=[], description="권장사항")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 75.5,
                "risk_level": "medium",
                "factors": {
                    "age_impact": -5.0,
                    "health_conditions_impact": -10.0
                },
                "recommendations": [
                    "정기적인 건강검진",
                    "운동 습관 개선"
                ]
            }
        }
>>>>>>> main
