from schemas.matching import MatchingRequest, MatchingResponse
from features.matching_features import MatchingFeatureEngineer
from utils.loader import ModelLoader
import os


class MatchingService:
    """매칭 점수 계산 서비스"""
    
    def __init__(self):
        self.feature_engineer = MatchingFeatureEngineer()
        self.model_loader = ModelLoader()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """모델 로드"""
        model_path = os.path.join("models", "matching_model.pkl")
        try:
            self.model = self.model_loader.load_model(model_path)
        except FileNotFoundError:
            # 모델이 없을 경우 None으로 설정
            self.model = None
    
    async def calculate_score(self, request: MatchingRequest) -> MatchingResponse:
        """
        매칭 점수 계산
        
        Args:
            request: 매칭 점수 계산 요청
            
        Returns:
            MatchingResponse: 매칭 점수 계산 결과
        """
        # 피처 엔지니어링
        features = self.feature_engineer.extract_features(request)
        
        # 모델 예측 (모델이 있으면)
        if self.model:
            matching_score = self.model.predict([features])[0]
        else:
            # 임시 로직 (모델이 없을 경우)
            matching_score = self._calculate_baseline_score(request)
        
        # 점수 세부 내역 계산
        score_breakdown = self._calculate_score_breakdown(request)
        
        # 개선 권장사항 생성
        recommendations = self._generate_recommendations(request, matching_score)
        
        return MatchingResponse(
            matching_score=float(matching_score),
            score_breakdown=score_breakdown,
            recommendations=recommendations
        )
    
    def _calculate_baseline_score(self, request: MatchingRequest) -> float:
        """기본 점수 계산 (모델이 없을 경우)"""
        # 스킬 매칭
        seeker_skills = set(request.job_seeker_profile.get("skills", []))
        required_skills = set(request.job_posting.get("required_skills", []))
        
        if len(required_skills) == 0:
            skills_score = 100.0
        else:
            skills_match = len(seeker_skills & required_skills) / len(required_skills)
            skills_score = skills_match * 100.0
        
        # 경력 매칭
        seeker_exp = request.job_seeker_profile.get("experience", 0)
        required_exp = request.job_posting.get("required_experience", 0)
        
        if required_exp == 0:
            exp_score = 100.0
        elif seeker_exp >= required_exp:
            exp_score = 100.0
        else:
            exp_score = (seeker_exp / required_exp) * 100.0
        
        # 학력 매칭
        seeker_edu = request.job_seeker_profile.get("education", "")
        required_edu = request.job_posting.get("education_level", "")
        
        edu_scores = {"high_school": 1, "bachelor": 2, "master": 3, "phd": 4}
        seeker_edu_score = edu_scores.get(seeker_edu, 0)
        required_edu_score = edu_scores.get(required_edu, 0)
        
        if seeker_edu_score >= required_edu_score:
            edu_score = 100.0
        else:
            edu_score = (seeker_edu_score / required_edu_score) * 100.0
        
        # 가중치 적용
        weights = request.weights or {"skills": 0.4, "experience": 0.3, "education": 0.3}
        
        total_score = (
            skills_score * weights.get("skills", 0.4) +
            exp_score * weights.get("experience", 0.3) +
            edu_score * weights.get("education", 0.3)
        )
        
        return min(100.0, total_score)
    
    def _calculate_score_breakdown(self, request: MatchingRequest) -> dict:
        """점수 세부 내역 계산"""
        # 스킬 매칭
        seeker_skills = set(request.job_seeker_profile.get("skills", []))
        required_skills = set(request.job_posting.get("required_skills", []))
        
        if len(required_skills) == 0:
            skills_match = 100.0
        else:
            skills_match = len(seeker_skills & required_skills) / len(required_skills) * 100.0
        
        # 경력 매칭
        seeker_exp = request.job_seeker_profile.get("experience", 0)
        required_exp = request.job_posting.get("required_experience", 0)
        
        if required_exp == 0:
            experience_match = 100.0
        elif seeker_exp >= required_exp:
            experience_match = 100.0
        else:
            experience_match = (seeker_exp / required_exp) * 100.0
        
        # 학력 매칭
        seeker_edu = request.job_seeker_profile.get("education", "")
        required_edu = request.job_posting.get("education_level", "")
        
        edu_scores = {"high_school": 1, "bachelor": 2, "master": 3, "phd": 4}
        seeker_edu_score = edu_scores.get(seeker_edu, 0)
        required_edu_score = edu_scores.get(required_edu, 0)
        
        if seeker_edu_score >= required_edu_score:
            education_match = 100.0
        else:
            education_match = (seeker_edu_score / required_edu_score) * 100.0
        
        return {
            "skills_match": round(skills_match, 2),
            "experience_match": round(experience_match, 2),
            "education_match": round(education_match, 2)
        }
    
    def _generate_recommendations(self, request: MatchingRequest, matching_score: float) -> list:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 스킬 부족 체크
        seeker_skills = set(request.job_seeker_profile.get("skills", []))
        required_skills = set(request.job_posting.get("required_skills", []))
        missing_skills = required_skills - seeker_skills
        
        if missing_skills:
            recommendations.append(f"{', '.join(list(missing_skills)[:3])} 기술 학습 권장")
        
        # 경력 부족 체크
        seeker_exp = request.job_seeker_profile.get("experience", 0)
        required_exp = request.job_posting.get("required_experience", 0)
        
        if seeker_exp < required_exp:
            recommendations.append(f"경력 {required_exp - seeker_exp}년 추가 필요")
        
        # 학력 부족 체크
        seeker_edu = request.job_seeker_profile.get("education", "")
        required_edu = request.job_posting.get("education_level", "")
        
        edu_scores = {"high_school": 1, "bachelor": 2, "master": 3, "phd": 4}
        seeker_edu_score = edu_scores.get(seeker_edu, 0)
        required_edu_score = edu_scores.get(required_edu, 0)
        
        if seeker_edu_score < required_edu_score:
            recommendations.append(f"학력 요건 충족 필요 ({required_edu})")
        
        if matching_score >= 80:
            recommendations.append("높은 매칭 점수 - 지원 권장")
        
        return recommendations
