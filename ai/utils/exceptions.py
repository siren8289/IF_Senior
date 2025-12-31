"""커스텀 예외 클래스 정의"""


class BaseAPIException(Exception):
    """API 기본 예외 클래스"""
    def __init__(self, error_code: str, message: str, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """입력 검증 오류"""
    def __init__(self, message: str, details: dict = None):
        super().__init__("VALIDATION_ERROR", message, details)


class ModelLoadError(BaseAPIException):
    """모델 로드 오류"""
    def __init__(self, message: str, details: dict = None):
        super().__init__("MODEL_LOAD_ERROR", message, details)


class ModelPredictionError(BaseAPIException):
    """모델 예측 오류"""
    def __init__(self, message: str, details: dict = None):
        super().__init__("MODEL_PREDICTION_ERROR", message, details)


class ServiceError(BaseAPIException):
    """서비스 레이어 오류"""
    def __init__(self, message: str, details: dict = None):
        super().__init__("SERVICE_ERROR", message, details)
