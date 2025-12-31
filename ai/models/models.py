import pickle
import logging
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)

_health_model = None
_health_vectorizer = None

def load_models():
    """모델 로드 (앱 시작 시)"""
    global _health_model, _health_vectorizer

    try:
        # 건강점수 모델 로드
        model_path = Path("models/health_model.pkl")
        if model_path.exists():
            with open(model_path, "rb") as f:
                _health_model = pickle.load(f)
            logger.info("Health score 모델 로드 완료")
        else:
            logger.warning(f"모델 파일 없음: {model_path}")
            _health_model = None

        # 벡터화기 로드
        vectorizer_path = Path("models/health_vectorizer.pkl")
        if vectorizer_path.exists():
            with open(vectorizer_path, "rb") as f:
                _health_vectorizer = pickle.load(f)
            logger.info("Vectorizer 로드 완료")
        else:
            _health_vectorizer = None

    except Exception as e:
        logger.error(f"모델 로드 실패: {str(e)}")
        raise

@lru_cache(maxsize=1)
def get_health_model():
    """건강점수 모델 반환"""
    if _health_model is None:
        raise RuntimeError("Health score 모델이 로드되지 않았습니다")
    return _health_model

def get_health_vectorizer():
    """벡터화기 반환"""
    if _health_vectorizer is None:
        raise RuntimeError("Vectorizer가 로드되지 않았습니다")
    return _health_vectorizer

