from schemas.health import HealthRequest, HealthResponse
from features.health_features import HealthFeatureEngineer
from utils.loader import ModelLoader
import os


class HealthService:
    """건강 점수 계산 서비스"""
    
    def __init__(self):
        self.feature_engineer = HealthFeatureEngineer()
        self.model_loader = ModelLoader()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """모델 로드"""
        model_path = os.path.join("models", "health_model.pkl")
        try:
            self.model = self.model_loader.load_model(model_path)
        except FileNotFoundError:
            # 모델이 없을 경우 None으로 설정 (나중에 학습된 모델로 교체)
            self.model = None
    
    async def calculate_score(self, request: HealthRequest) -> HealthResponse:
        """
        건강 점수 계산
        
        Args:
            request: 건강 점수 계산 요청
            
        Returns:
            HealthResponse: 건강 점수 계산 결과
        """
        # 피처 엔지니어링
        features = self.feature_engineer.extract_features(request)
        
        # 모델 예측 (모델이 있으면)
        if self.model:
            score = self.model.predict([features])[0]
        else:
            # 임시 로직 (모델이 없을 경우)
            score = self._calculate_baseline_score(request)
        
        # 위험도 레벨 결정
        risk_level = self._determine_risk_level(score)
        
        # 영향 요인 분석
        factors = self._analyze_factors(request)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(request, score)
        
        return HealthResponse(
            score=float(score),
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations
        )
    
    def _calculate_baseline_score(self, request: HealthRequest) -> float:
        """기본 점수 계산 (모델이 없을 경우)"""
        base_score = 100.0
        
        # 나이 영향
        age_penalty = max(0, (request.age - 30) * 0.5)
        
        # 건강 상태 영향
        condition_penalty = len(request.health_conditions) * 10
        
        score = base_score - age_penalty - condition_penalty
        return max(0, min(100, score))
    
    def _determine_risk_level(self, score: float) -> str:
        """위험도 레벨 결정"""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        else:
            return "high"
    
    def _analyze_factors(self, request: HealthRequest) -> dict:
        """영향 요인 분석"""
        factors = {}
        
        # 나이 영향
        if request.age > 50:
            factors["age_impact"] = -5.0
        elif request.age < 30:
            factors["age_impact"] = 5.0
        else:
            factors["age_impact"] = 0.0
        
        # 건강 상태 영향
        factors["health_conditions_impact"] = -len(request.health_conditions) * 5.0
        
        return factors
    
    def _generate_recommendations(self, request: HealthRequest, score: float) -> list:
        """권장사항 생성"""
        recommendations = []
        
        if score < 60:
            recommendations.append("정기적인 건강검진 권장")
            recommendations.append("생활습관 개선 필요")
        
        if len(request.health_conditions) > 0:
            recommendations.append("기존 건강 상태 관리 중요")
        
        if request.age > 50:
            recommendations.append("연령대에 맞는 건강 관리 필요")
        
        return recommendations
