import pickle
import os
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """모델 로딩 유틸리티"""
    
    @staticmethod
    def load_model(model_path: str):
        """
        모델 파일 로드
        
        Args:
            model_path: 모델 파일 경로
            
        Returns:
            모델 객체
        """
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Model loaded successfully: {model_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    @staticmethod
    def save_model(model, model_path: str):
        """
        모델 파일 저장
        
        Args:
            model: 모델 객체
            model_path: 저장할 모델 파일 경로
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Model saved successfully: {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
