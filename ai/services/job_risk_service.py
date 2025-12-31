from schemas.job_risk import JobRiskRequest, JobRiskResponse
from features.job_risk_features import JobRiskFeatureEngineer
from utils.loader import ModelLoader
import os


class JobRiskService:
    """산업재해 리스크 예측 서비스"""
    
    def __init__(self):
        self.feature_engineer = JobRiskFeatureEngineer()
        self.model_loader = ModelLoader()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """모델 로드"""
        model_path = os.path.join("models", "job_risk_model.pkl")
        try:
            self.model = self.model_loader.load_model(model_path)
        except FileNotFoundError:
            # 모델이 없을 경우 None으로 설정
            self.model = None
    
    async def predict_risk(self, request: JobRiskRequest) -> JobRiskResponse:
        """
        산업재해 리스크 예측
        
        Args:
            request: 리스크 예측 요청
            
        Returns:
            JobRiskResponse: 리스크 예측 결과
        """
        # 피처 엔지니어링
        features = self.feature_engineer.extract_features(request)
        
        # 모델 예측 (모델이 있으면)
        if self.model:
            risk_score = self.model.predict([features])[0]
        else:
            # 임시 로직 (모델이 없을 경우)
            risk_score = self._calculate_baseline_risk(request)
        
        # 위험도 레벨 결정
        risk_level = self._determine_risk_level(risk_score)
        
        # 위험 요인 분석
        risk_factors = self._analyze_risk_factors(request)
        
        # 안전 권장사항 생성
        safety_recommendations = self._generate_safety_recommendations(request, risk_score)
        
        return JobRiskResponse(
            risk_score=float(risk_score),
            risk_level=risk_level,
            risk_factors=risk_factors,
            safety_recommendations=safety_recommendations
        )
    
    def _calculate_baseline_risk(self, request: JobRiskRequest) -> float:
        """기본 리스크 계산 (모델이 없을 경우)"""
        base_risk = 30.0
        
        # 직종별 기본 리스크
        high_risk_jobs = ["construction", "mining", "manufacturing"]
        if request.job_type in high_risk_jobs:
            base_risk += 30.0
        
        # 작업 환경 영향
        if request.work_environment.get("height") == "high":
            base_risk += 20.0
        
        # 안전 장비 감소
        safety_reduction = len(request.safety_equipment) * 5.0
        base_risk -= safety_reduction
        
        # 경력에 따른 감소
        experience_reduction = min(10.0, request.experience_years * 1.0)
        base_risk -= experience_reduction
        
        return max(0, min(100, base_risk))
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """위험도 레벨 결정"""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _analyze_risk_factors(self, request: JobRiskRequest) -> dict:
        """위험 요인 분석"""
        factors = {}
        
        # 직종 리스크
        high_risk_jobs = ["construction", "mining", "manufacturing"]
        if request.job_type in high_risk_jobs:
            factors["job_type_risk"] = 40.0
        else:
            factors["job_type_risk"] = 20.0
        
        # 환경 리스크
        env_risk = 0.0
        if request.work_environment.get("height") == "high":
            env_risk += 15.0
        if request.work_environment.get("machinery"):
            env_risk += 10.0
        factors["environment_risk"] = env_risk
        
        return factors
    
    def _generate_safety_recommendations(self, request: JobRiskRequest, risk_score: float) -> list:
        """안전 권장사항 생성"""
        recommendations = []
        
        if risk_score >= 70:
            recommendations.append("높은 위험도 - 안전 조치 필수")
        
        if len(request.safety_equipment) < 3:
            recommendations.append("추가 안전 장비 착용 권장")
        
        if request.work_environment.get("height") == "high":
            recommendations.append("고소 작업 안전 수칙 준수")
        
        if request.experience_years < 2:
            recommendations.append("신입 작업자 안전 교육 필수")
        
        return recommendations
