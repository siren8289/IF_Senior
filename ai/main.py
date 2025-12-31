from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import uvicorn
import logging
import traceback

from api.v1 import health as health_router
from config.settings import Settings
from models.loader import load_models
from utils.logger import setup_logger
from utils.exceptions import BaseAPIException, ValidationError, ModelLoadError, ModelPredictionError, ServiceError
from schemas.health import ErrorResponse

# 설정
settings = Settings()
setup_logger()
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="IF(이프) API",
    description="AI 기반 매칭 점수 계산 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (Backend 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://api.if.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """커스텀 API 예외 핸들러"""
    status_code = status.HTTP_400_BAD_REQUEST
    
    # 예외 타입에 따른 상태 코드 결정
    if isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, ModelLoadError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, ModelPredictionError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, ServiceError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    logger.error(f"API 예외 발생: {exc.error_code} - {exc.message}", exc_info=True)
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """ValueError 핸들러 (입력 검증 오류)"""
    logger.error(f"입력 검증 오류: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message=str(exc),
            details={"field": None, "value": None}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러 (예상치 못한 오류)"""
    error_traceback = traceback.format_exc()
    logger.error(f"예상치 못한 오류 발생: {str(exc)}\n{error_traceback}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
            details={"traceback": error_traceback if settings.DEBUG else None}
        ).dict()
    )


# 모델 로드 (앱 시작 시)
@app.on_event("startup")
async def startup_event():
    logger.info("ML 모델 로딩 시작...")
    try:
        load_models()
        logger.info("ML 모델 로드 완료")
    except Exception as e:
        logger.error(f"모델 로드 실패: {str(e)}", exc_info=True)
        # 모델 로드 실패해도 서버는 시작 (규칙 기반으로 동작)
        logger.warning("모델이 없어도 규칙 기반 로직으로 동작합니다.")

# 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ml-service",
        "version": "1.0.0"
    }

# 라우터 등록
app.include_router(
    health_router.router,
    prefix="/api/ml/v1/health",
    tags=["Health Score"]
)

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
