from fastapi import APIRouter, HTTPException, status
import logging

from schemas.monitoring import AnomalyDetectionRequest, AnomalyDetectionResponse
from services.anomaly_service import AnomalyDetectionService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/detect-anomaly",
    response_model=AnomalyDetectionResponse,
    summary="이상 탐지",
    description="센서 데이터에서 이상을 탐지하고 경고 생성"
)
async def detect_anomaly(request: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    """센서 데이터 이상 탐지 API"""

    try:
        logger.info(f"이상 탐지 요청: senior_id={request.senior_profile_id}")

        response = AnomalyDetectionService.detect_anomalies(request)

        return response

    except Exception as e:
        logger.error(f"이상 탐지 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
