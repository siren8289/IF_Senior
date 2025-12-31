from pydantic import BaseModel, Field
from typing import Optional, List


class JobRiskRequest(BaseModel):
    """산업재해 리스크 예측 요청"""
    job_type: str = Field(..., description="직종")
    work_environment: Optional[dict] = Field(default={}, description="작업 환경")
    safety_equipment: Optional[List[str]] = Field(default=[], description="안전 장비")
    experience_years: Optional[int] = Field(default=0, description="경력 연수", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_type": "construction",
                "work_environment": {
                    "height": "high",
                    "machinery": True
                },
                "safety_equipment": ["helmet", "safety_harness"],
                "experience_years": 5
            }
        }


class JobRiskResponse(BaseModel):
    """산업재해 리스크 예측 응답"""
    risk_score: float = Field(..., description="리스크 점수", ge=0, le=100)
    risk_level: str = Field(..., description="위험도 레벨")
    risk_factors: dict = Field(..., description="위험 요인")
    safety_recommendations: Optional[List[str]] = Field(default=[], description="안전 권장사항")
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_score": 65.3,
                "risk_level": "high",
                "risk_factors": {
                    "job_type_risk": 40.0,
                    "environment_risk": 25.3
                },
                "safety_recommendations": [
                    "안전 장비 착용 필수",
                    "정기적인 안전 교육"
                ]
            }
        }
