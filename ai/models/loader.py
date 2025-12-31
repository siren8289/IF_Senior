import pickle
import os
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

# 전역 모델 캐시
_health_model: Optional[object] = None


def get_health_model():
    """
    건강점수 모델 가져오기
    
    Returns:
        모델 객체 (없으면 None)
    """
    global _health_model
    
    if _health_model is None:
        logger.warning("건강점수 모델이 로드되지 않았습니다. 기본값을 사용합니다.")
        return None
    
    return _health_model


def load_health_model(model_path: Optional[str] = None) -> bool:
    """
    건강점수 모델 로드
    
    Args:
        model_path: 모델 파일 경로 (None이면 설정에서 가져옴)
        
    Returns:
        bool: 로드 성공 여부
    """
    global _health_model
    
    if model_path is None:
        model_path = settings.HEALTH_MODEL_PATH
    
    if not os.path.exists(model_path):
        logger.warning(f"건강점수 모델 파일을 찾을 수 없습니다: {model_path}")
        _health_model = None
        return False
    
    try:
        with open(model_path, 'rb') as f:
            _health_model = pickle.load(f)
        logger.info(f"건강점수 모델 로드 완료: {model_path}")
        return True
    except Exception as e:
        logger.error(f"건강점수 모델 로드 실패: {str(e)}")
        _health_model = None
        return False


def load_models():
    """
    모든 ML 모델 로드
    
    앱 시작 시 호출됨
    """
    logger.info("모델 로딩 시작...")
    
    # 건강점수 모델 로드 (실패해도 계속 진행)
    load_health_model()
    
    logger.info("모델 로딩 완료")


def clear_models():
    """모델 캐시 클리어 (테스트용)"""
    global _health_model
    _health_model = None
    logger.info("모델 캐시 클리어 완료")
