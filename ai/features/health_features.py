from schemas.health import HealthRequest
import numpy as np


class HealthFeatureEngineer:
    """건강 점수 피처 엔지니어링"""
    
    def extract_features(self, request: HealthRequest) -> list:
        """
        건강 점수 계산을 위한 피처 추출
        
        Args:
            request: 건강 점수 계산 요청
            
        Returns:
            list: 피처 벡터
        """
        features = []
        
        # 기본 정보
        features.append(request.age)
        features.append(1.0 if request.gender == "M" else 0.0)
        
        # 건강 상태 개수
        features.append(len(request.health_conditions))
        
        # 건강 상태 원-핫 인코딩 (주요 질환)
        major_conditions = ["diabetes", "hypertension", "heart_disease", "cancer"]
        for condition in major_conditions:
            features.append(1.0 if condition in request.health_conditions else 0.0)
        
        # 생활습관 요소
        lifestyle = request.lifestyle_factors or {}
        features.append(1.0 if lifestyle.get("smoking", False) else 0.0)
        features.append(1.0 if lifestyle.get("exercise", False) else 0.0)
        features.append(lifestyle.get("exercise_hours_per_week", 0.0))
        features.append(lifestyle.get("alcohol_consumption", 0.0))
        
        # 나이 그룹
        if request.age < 30:
            age_group = 0
        elif request.age < 50:
            age_group = 1
        else:
            age_group = 2
        features.append(age_group)
        
        return features
