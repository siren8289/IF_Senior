from fastapi import APIRouter, HTTPException
from typing import List
from schemas.matching import MatchingRequest, MatchingResponse
from services.matching_service import MatchingService

router = APIRouter(prefix="/api/v1/matching", tags=["matching"])

matching_service = MatchingService()


@router.post("/score", response_model=MatchingResponse)
async def calculate_matching_score(request: MatchingRequest):
    """
    매칭 점수 계산 API
    """
    try:
        result = await matching_service.calculate_score(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def matching_check():
    """
    Matching service check
    """
    return {"status": "ok", "service": "matching"}
