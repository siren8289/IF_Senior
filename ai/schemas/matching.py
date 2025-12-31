from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class MatchingRequest(BaseModel):
    """매칭 점수 계산 요청"""
    job_seeker_profile: dict = Field(..., description="구직자 프로필")
    job_posting: dict = Field(..., description="채용 공고")
    weights: Optional[dict] = Field(default={}, description="가중치 설정")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_seeker_profile": {
                    "skills": ["Python", "FastAPI"],
                    "experience": 3,
                    "education": "bachelor"
                },
                "job_posting": {
                    "required_skills": ["Python", "FastAPI", "Docker"],
                    "required_experience": 2,
                    "education_level": "bachelor"
                },
                "weights": {
                    "skills": 0.4,
                    "experience": 0.3,
                    "education": 0.3
                }
            }
        }


class MatchingResponse(BaseModel):
    """매칭 점수 계산 응답"""
    matching_score: float = Field(..., description="매칭 점수", ge=0, le=100)
    score_breakdown: dict = Field(..., description="점수 세부 내역")
    recommendations: Optional[List[str]] = Field(default=[], description="개선 권장사항")
    
    class Config:
        json_schema_extra = {
            "example": {
                "matching_score": 82.5,
                "score_breakdown": {
                    "skills_match": 85.0,
                    "experience_match": 90.0,
                    "education_match": 75.0
                },
                "recommendations": [
                    "Docker 기술 학습 권장",
                    "경력 강화"
                ]
            }
        }
