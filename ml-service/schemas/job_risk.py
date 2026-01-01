from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class RiskLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Request
class JobRiskRequest(BaseModel):
    """일자리 위험도 계산 요청"""
    job_id: int = Field(..., description="일자리 ID")
    title: str = Field(..., max_length=200, description="직무 제목")
    description: str = Field(..., description="직무 설명 (BERT 분석 대상)")
    estimated_minutes: int = Field(..., ge=1, le=1440, description="예상 소요 시간 (분)")
    required_health_level: int = Field(..., ge=1, le=5, description="필요 건강 레벨")

    class Config:
        schema_extra = {
            "example": {
                "job_id": 1,
                "title": "노인 요양 업무",
                "description": "거동이 불편한 노인의 이동 보조, 신체 활동 지원, 일상생활 보조",
                "estimated_minutes": 480,
                "required_health_level": 4
            }
        }

# Response
class JobRiskResponse(BaseModel):
    """일자리 위험도 계산 응답"""
    job_id: int
    risk_score: float = Field(..., ge=0, le=10, description="위험도 점수 (0-10)")
    risk_level: RiskLevelEnum = Field(..., description="위험 수준")
    risk_factors: List[str] = Field(..., description="주요 위험 요소")

    class Config:
        schema_extra = {
            "example": {
                "job_id": 1,
                "risk_score": 7.2,
                "risk_level": "high",
                "risk_factors": [
                    "신체 활동 많음 (8점)",
                    "장시간 서있기 (7점)",
                    "높은 건강 요구 (6점)"
                ]
            }
        }
