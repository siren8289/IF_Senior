from pydantic import BaseModel, Field
from typing import List, Dict

class MatchingComponentScore(BaseModel):
    """매칭 점수 구성 요소"""
    health_compatibility: float = Field(..., ge=0, le=1)
    experience_match: float = Field(..., ge=0, le=1)
    location_distance: float = Field(..., ge=0, description="km 단위")
    availability_match: float = Field(..., ge=0, le=1)

class RecommendationResult(BaseModel):
    """추천 결과"""
    senior_profile_id: int
    rank: int
    match_score: float = Field(..., ge=0, le=100, description="매칭 점수 (0-100)")
    components: MatchingComponentScore

# Request
class MatchingCalculateRequest(BaseModel):
    """매칭 점수 계산 요청"""
    job_id: int
    senior_profile_ids: List[int] = Field(..., max_items=100)
    top_k: int = Field(default=5, ge=1, le=100)

    # 옵션: 건강점수를 직접 전달하거나 ID로만 전달 가능
    health_scores: Dict[int, float] = Field(
        default_factory=dict,
        description="senior_id → health_score 매핑 (선택)"
    )

# Response
class MatchingCalculateResponse(BaseModel):
    """매칭 점수 계산 응답"""
    job_id: int
    recommendations: List[RecommendationResult]
    algorithm_version: str = "matching_v1.0"
