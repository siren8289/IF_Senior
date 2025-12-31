from schemas.job_risk import JobRiskRequest
import numpy as np


class JobRiskFeatureEngineer:
    """산업재해 리스크 피처 엔지니어링"""
    
    def extract_features(self, request: JobRiskRequest) -> list:
        """
        산업재해 리스크 예측을 위한 피처 추출
        
        Args:
            request: 리스크 예측 요청
            
        Returns:
            list: 피처 벡터
        """
        features = []
        
        # 직종 인코딩
        job_types = ["construction", "mining", "manufacturing", "office", "service", "other"]
        job_type_encoded = [1.0 if job == request.job_type else 0.0 for job in job_types]
        features.extend(job_type_encoded)
        
        # 작업 환경
        env = request.work_environment or {}
        features.append(1.0 if env.get("height") == "high" else 0.0)
        features.append(1.0 if env.get("machinery", False) else 0.0)
        features.append(1.0 if env.get("chemicals", False) else 0.0)
        features.append(1.0 if env.get("noise", False) else 0.0)
        
        # 안전 장비 개수
        features.append(len(request.safety_equipment))
        
        # 안전 장비 원-핫 인코딩
        safety_items = ["helmet", "safety_harness", "gloves", "safety_shoes", "goggles"]
        for item in safety_items:
            features.append(1.0 if item in request.safety_equipment else 0.0)
        
        # 경력
        features.append(request.experience_years)
        
        # 경력 그룹
        if request.experience_years < 1:
            exp_group = 0
        elif request.experience_years < 5:
            exp_group = 1
        else:
            exp_group = 2
        features.append(exp_group)
        
        return features
