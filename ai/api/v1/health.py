<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, status
import logging

from schemas.health import HealthScoreRequest, HealthScoreResponse, ErrorResponse
from services.health_service import HealthScoreService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/calculate",
    response_model=HealthScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="건강점수 계산",
    description="시니어의 건강정보를 입력받아 AI 건강점수를 계산합니다",
    responses={
        200: {"description": "계산 성공"},
        400: {"model": ErrorResponse, "description": "입력 검증 실패"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    }
)
async def calculate_health_score(request: HealthScoreRequest) -> HealthScoreResponse:
    """
    건강점수 계산 API

    ### 입력 예시:
    ```json
    {
        "senior_profile_id": 1,
        "height_cm": 170,
        "weight_kg": 75.5,
        "chronic_conditions": {
            "hypertension": true,
            "diabetes": false
        },
        "risk_flags": {
            "mobility_limited": 0.3,
            "cognitive_impairment_risk": 0.2
        }
    }
    ```

    ### 출력 예시:
    ```json
    {
        "senior_profile_id": 1,
        "health_score": 78.5,
        "risk_level": "medium",
        "components": {
            "bmi_factor": 0.90,
            "chronic_factor": 0.65,
            "mobility_factor": 0.95,
            "cognitive_factor": 0.95,
            "age_factor": 0.85
        },
        "recommendations": [
            "혈압 관리 필요",
            "규칙적인 운동 권장"
        ]
    }
    ```
    """

    try:
        logger.info(f"건강점수 계산 요청: senior_profile_id={request.senior_profile_id}")

        response = HealthScoreService.calculate_health_score(
            senior_profile_id=request.senior_profile_id,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            chronic_conditions=request.chronic_conditions,
            risk_flags=request.risk_flags
        )

        return response

    except ValueError as e:
        logger.error(f"입력 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"내부 서버 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="건강점수 계산 중 오류 발생"
        )
=======
from fastapi import APIRouter, HTTPException
from typing import List
from schemas.health import HealthRequest, HealthResponse
from services.health_service import HealthService

router = APIRouter(prefix="/api/v1/health", tags=["health"])

health_service = HealthService()


@router.post("/score", response_model=HealthResponse)
async def calculate_health_score(request: HealthRequest):
    """
    건강 점수 계산 API
    """
    try:
        result = await health_service.calculate_score(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "service": "health"}
>>>>>>> main
