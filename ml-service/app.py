from fastapi import FastAPI
from api.v1 import job_risk, matching

app = FastAPI(
    title="Senior ML Service",
    version="1.0.0",
    description="시니어 일자리 위험도 & 매칭 점수 계산 API"
)

# /api/ml/v1/job-risk, /api/ml/v1/matching prefix
app.include_router(job_risk.router, prefix="/api/ml/v1/job-risk", tags=["JobRisk"])
app.include_router(matching.router, prefix="/api/ml/v1/matching", tags=["Matching"])
