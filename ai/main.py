import os
from fastapi import FastAPI
import yaml

# API 라우터 import
from api.v1 import health, job_risk, matching

app = FastAPI(
    title="IF(이프) API",
    description="건강 점수, 산업재해 리스크, 매칭 점수 계산 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# API 라우터 등록
app.include_router(health.router)
app.include_router(job_risk.router)
app.include_router(matching.router)

# OpenAPI 스키마 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
swagger_path = os.path.join(BASE_DIR, "openApi", "v1", "swagger.yaml")

try:
    with open(swagger_path, "r", encoding="utf-8") as f:
        openapi_schema = yaml.safe_load(f)
    app.openapi_schema = openapi_schema
except FileNotFoundError:
    pass  # swagger.yaml이 없어도 동작하도록


@app.get("/")
def root():
    """루트 엔드포인트"""
    return {
        "status": "ok",
        "message": "IF(이프) API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "job_risk": "/api/v1/job-risk",
            "matching": "/api/v1/matching",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
