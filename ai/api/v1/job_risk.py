from fastapi import APIRouter, HTTPException
from typing import List
from schemas.job_risk import JobRiskRequest, JobRiskResponse
from services.job_risk_service import JobRiskService

router = APIRouter(prefix="/api/v1/job-risk", tags=["job-risk"])

job_risk_service = JobRiskService()


@router.post("/predict", response_model=JobRiskResponse)
async def predict_job_risk(request: JobRiskRequest):
    """
    산업재해 리스크 예측 API
    """
    try:
        result = await job_risk_service.predict_risk(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def job_risk_check():
    """
    Job risk service check
    """
    return {"status": "ok", "service": "job-risk"}
