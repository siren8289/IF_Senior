from schemas.matching import MatchingRequest
import numpy as np


class MatchingFeatureEngineer:
    """매칭 점수 피처 엔지니어링"""
    
    def extract_features(self, request: MatchingRequest) -> list:
        """
        매칭 점수 계산을 위한 피처 추출
        
        Args:
            request: 매칭 점수 계산 요청
            
        Returns:
            list: 피처 벡터
        """
        features = []
        
        # 스킬 매칭
        seeker_skills = set(request.job_seeker_profile.get("skills", []))
        required_skills = set(request.job_posting.get("required_skills", []))
        
        if len(required_skills) == 0:
            skills_match_ratio = 1.0
        else:
            skills_match_ratio = len(seeker_skills & required_skills) / len(required_skills)
        
        features.append(skills_match_ratio)
        features.append(len(seeker_skills))
        features.append(len(required_skills))
        features.append(len(seeker_skills & required_skills))
        features.append(len(required_skills - seeker_skills))  # 부족한 스킬 수
        
        # 경력 매칭
        seeker_exp = request.job_seeker_profile.get("experience", 0)
        required_exp = request.job_posting.get("required_experience", 0)
        
        if required_exp == 0:
            exp_match_ratio = 1.0
        elif seeker_exp >= required_exp:
            exp_match_ratio = 1.0
        else:
            exp_match_ratio = seeker_exp / required_exp
        
        features.append(exp_match_ratio)
        features.append(seeker_exp)
        features.append(required_exp)
        features.append(max(0, required_exp - seeker_exp))  # 부족한 경력
        
        # 학력 매칭
        seeker_edu = request.job_seeker_profile.get("education", "")
        required_edu = request.job_posting.get("education_level", "")
        
        edu_scores = {"high_school": 1, "bachelor": 2, "master": 3, "phd": 4}
        seeker_edu_score = edu_scores.get(seeker_edu, 0)
        required_edu_score = edu_scores.get(required_edu, 0)
        
        if required_edu_score == 0:
            edu_match_ratio = 1.0
        elif seeker_edu_score >= required_edu_score:
            edu_match_ratio = 1.0
        else:
            edu_match_ratio = seeker_edu_score / required_edu_score
        
        features.append(edu_match_ratio)
        features.append(seeker_edu_score)
        features.append(required_edu_score)
        
        # 가중치
        weights = request.weights or {}
        features.append(weights.get("skills", 0.4))
        features.append(weights.get("experience", 0.3))
        features.append(weights.get("education", 0.3))
        
        return features
