from fastapi import APIRouter, HTTPException, status
import logging

from schemas.health import HealthScoreRequest, HealthScoreResponse, ErrorResponse
from services.health_service import HealthScoreService
from utils.exceptions import ValidationError, ServiceError

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

        logger.info(f"건강점수 계산 성공: senior_profile_id={request.senior_profile_id}, score={response.health_score}")
        return response

    except ValidationError as e:
        # ValidationError는 전역 핸들러에서 처리되지만, 여기서도 로깅
        logger.warning(f"입력 검증 오류: {e.message}")
        raise  # 전역 핸들러로 전달

    except ValueError as e:
        # ValueError를 ValidationError로 변환
        logger.warning(f"입력 검증 오류: {str(e)}")
        raise ValidationError(
            message=str(e),
            details={"field": None, "value": None}
        )

    except ServiceError as e:
        # ServiceError는 전역 핸들러에서 처리
        logger.error(f"서비스 오류: {e.message}")
        raise  # 전역 핸들러로 전달

    except Exception as e:
        # 예상치 못한 오류는 ServiceError로 변환
        logger.error(f"예상치 못한 오류: {str(e)}", exc_info=True)
        raise ServiceError(
            message="건강점수 계산 중 오류가 발생했습니다.",
            details={"error_type": type(e).__name__, "error_message": str(e)}
        )
