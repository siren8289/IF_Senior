from fastapi import APIRouter, HTTPException, status
import logging

from schemas.job_risk import JobRiskRequest, JobRiskResponse
from services.job_risk_service import JobRiskService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/calculate",
    response_model=JobRiskResponse,
    summary="일자리 위험도 계산",
    description="직무 설명을 분석하여 위험도를 계산합니다"
)
async def calculate_job_risk(request: JobRiskRequest) -> JobRiskResponse:
    """일자리 위험도 계산 API"""

    try:
        logger.info(f"위험도 계산 요청: job_id={request.job_id}")

        response = JobRiskService.calculate_risk_score(
            job_id=request.job_id,
            title=request.title,
            description=request.description,
            estimated_minutes=request.estimated_minutes,
            required_health_level=request.required_health_level
        )

        return response

    except Exception as e:
        logger.error(f"위험도 계산 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
