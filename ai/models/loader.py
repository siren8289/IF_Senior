import pickle
import os
import logging
from typing import Optional

import joblib
import torch

from config.settings import settings

logger = logging.getLogger(__name__)

# =========================
# 전역 모델 캐시
# =========================

_health_model: Optional[object] = None
_lstm_model: Optional[object] = None
_iforest_model: Optional[object] = None


# =========================
# Health Model
# =========================

def get_health_model():
    """
    건강점수 모델 가져오기
    """
    global _health_model

    if _health_model is None:
        logger.warning("건강점수 모델이 로드되지 않았습니다. 기본값을 사용합니다.")
        return None

    return _health_model


def load_health_model(model_path: Optional[str] = None) -> bool:
    """
    건강점수 모델 로드
    """
    global _health_model

    if model_path is None:
        model_path = settings.HEALTH_MODEL_PATH

    if not model_path or not os.path.exists(model_path):
        logger.warning(f"건강점수 모델 파일을 찾을 수 없습니다: {model_path}")
        _health_model = None
        return False

    try:
        with open(model_path, "rb") as f:
            _health_model = pickle.load(f)
        logger.info(f"건강점수 모델 로드 완료: {model_path}")
        return True
    except Exception as e:
        logger.error(f"건강점수 모델 로드 실패: {str(e)}")
        _health_model = None
        return False


# =========================
# Monitoring Models
# =========================

def get_lstm_model():
    """
    LSTM 이상 탐지 모델 가져오기
    """
    return _lstm_model


def get_isolation_forest():
    """
    Isolation Forest 모델 가져오기
    """
    return _iforest_model


def load_monitoring_models(
    lstm_path: Optional[str] = None,
    iforest_path: Optional[str] = None
) -> None:
    """
    Monitoring용 ML 모델 로드 (LSTM + Isolation Forest)
    """
    global _lstm_model, _iforest_model

    # 기본 경로 (설정값 없으면 models 폴더 기준)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if lstm_path is None:
        lstm_path = os.path.join(base_dir, "lstm_model.pt")

    if iforest_path is None:
        iforest_path = os.path.join(base_dir, "isolation_forest.pkl")

    # LSTM 로드
    if os.path.exists(lstm_path):
        try:
            _lstm_model = torch.load(lstm_path, map_location="cpu")
            logger.info(f"LSTM 모델 로드 완료: {lstm_path}")
        except Exception as e:
            logger.error(f"LSTM 모델 로드 실패: {str(e)}")
            _lstm_model = None
    else:
        logger.warning(f"LSTM 모델 파일이 없습니다: {lstm_path}")
        _lstm_model = None

    # Isolation Forest 로드
    if os.path.exists(iforest_path):
        try:
            _iforest_model = joblib.load(iforest_path)
            logger.info(f"Isolation Forest 모델 로드 완료: {iforest_path}")
        except Exception as e:
            logger.error(f"Isolation Forest 모델 로드 실패: {str(e)}")
            _iforest_model = None
    else:
        logger.warning(f"Isolation Forest 모델 파일이 없습니다: {iforest_path}")
        _iforest_model = None


# =========================
# App Startup Hook
# =========================

def load_models():
    """
    모든 ML 모델 로드
    앱 시작 시 호출됨
    """
    logger.info("모델 로딩 시작...")

    # 1️⃣ Health 모델
    load_health_model()

    # 2️⃣ Monitoring 모델 (실패해도 서버 유지)
    load_monitoring_models()

    logger.info("모델 로딩 완료")


def clear_models():
    """
    모델 캐시 클리어 (테스트용)
    """
    global _health_model, _lstm_model, _iforest_model

    _health_model = None
    _lstm_model = None
    _iforest_model = None

    logger.info("모델 캐시 클리어 완료")
