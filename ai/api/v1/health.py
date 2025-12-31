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
