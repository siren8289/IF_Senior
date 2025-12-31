from pydantic import BaseModel, Field
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
                }
            }
        }


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
