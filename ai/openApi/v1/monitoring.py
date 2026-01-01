from fastapi import APIRouter
from schemas.monitoring import MonitoringRequest, MonitoringResponse
from services.monitoring_service import analyze_monitoring

router = APIRouter()

@router.post("/monitoring", response_model=MonitoringResponse)
def monitoring_api(req: MonitoringRequest):
    result = analyze_monitoring(req.data)
    return result
