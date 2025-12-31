from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging

<<<<<<< HEAD
from api.v1 import health as health_router
from config.settings import Settings
from models.loader import load_models
from utils.logger import setup_logger

# 설정
settings = Settings()
setup_logger()
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="IF(이프) API",
    description="AI 기반 매칭 점수 계산 API",
=======
# API 라우터 import
from api.v1 import health, job_risk, matching

app = FastAPI(
    title="IF(이프) API",
    description="건강 점수, 산업재해 리스크, 매칭 점수 계산 API",
>>>>>>> main
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

<<<<<<< HEAD
# CORS 설정 (Backend 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://api.if.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 로드 (앱 시작 시)
@app.on_event("startup")
async def startup_event():
    logger.info("ML 모델 로딩 시작...")
    try:
        load_models()
        logger.info("ML 모델 로드 완료")
    except Exception as e:
        logger.error(f"모델 로드 실패: {str(e)}")
        raise

# 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ml-service",
        "version": "1.0.0"
    }
=======
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
>>>>>>> main

# 라우터 등록
app.include_router(
    health_router.router,
    prefix="/api/ml/v1/health",
    tags=["Health Score"]
)

<<<<<<< HEAD
# OpenAPI 커스터마이징
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IF ML Health Score API",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        log_level="info"
    )
=======
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
>>>>>>> main
