from fastapi import APIRouter, HTTPException, status
import logging

from schemas.matching import MatchingCalculateRequest, MatchingCalculateResponse
from services.matching_service import MatchingService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/calculate",
    response_model=MatchingCalculateResponse,
    summary="매칭 점수 계산",
    description="시니어 워커와 일자리의 매칭 점수를 계산합니다"
)
async def calculate_matching(request: MatchingCalculateRequest) -> MatchingCalculateResponse:
    """매칭 점수 계산 API"""

    try:
        logger.info(f"매칭 계산 요청: job_id={request.job_id}")

        response = MatchingService.calculate_matching_scores(request)

        return response

    except Exception as e:
        logger.error(f"매칭 계산 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
