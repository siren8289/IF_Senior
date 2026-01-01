import logging
from typing import List, Dict

from schemas.matching import (
    MatchingCalculateRequest,
    MatchingCalculateResponse,
    RecommendationResult,
    MatchingComponentScore
)
from features.matching_features import MatchingFeatureExtractor

logger = logging.getLogger("services.matching")
logger.setLevel(logging.INFO)


class MatchingService:
    """매칭 점수 계산 서비스 (앙상블)"""

    WEIGHTS: Dict[str, float] = {
        "health_compatibility": 0.30,
        "experience_match": 0.30,
        "location_distance": 0.20,
        "availability_match": 0.20,
    }

    @staticmethod
    def calculate_matching_scores(
        request: MatchingCalculateRequest,
    ) -> MatchingCalculateResponse:
        """
        매칭 점수 계산 (여러 시니어와 일자리 비교)

        알고리즘:
        1. 각 senior별 특성 분석
        2. 4개 요소 점수 계산
        3. 가중평균으로 최종 점수
        4. 상위 K개 추천
        """

        logger.info(
            f"[Matching] 요청 | job_id={request.job_id}, "
            f"candidates={len(request.senior_profile_ids)}, top_k={request.top_k}"
        )

        try:
            recommendations: List[RecommendationResult] = []

            for senior_id in request.senior_profile_ids:
                score_obj = MatchingService._calculate_single_matching(
                    senior_id=senior_id,
                    health_score=request.health_scores.get(senior_id, 50.0),  # 기본값 50
                    request=request,
                )

                if score_obj:
                    recommendations.append(score_obj)

            # 점수 기준 정렬 (내림차순)
            recommendations.sort(key=lambda x: x.match_score, reverse=True)

            # 상위 K개
            top_recommendations = recommendations[: request.top_k]

            # 순위 부여
            for i, rec in enumerate(top_recommendations):
                rec.rank = i + 1

            # ✅ 최종 요약 로그 (INFO)
            if top_recommendations:
                best = top_recommendations[0]
                logger.info(
                    f"[Matching] 완료 | job_id={request.job_id} | "
                    f"top={len(top_recommendations)}, "
                    f"best_senior={best.senior_profile_id}, best_score={best.match_score}"
                )
            else:
                logger.info(
                    f"[Matching] 완료 | job_id={request.job_id} | 추천 결과 없음"
                )

            return MatchingCalculateResponse(
                job_id=request.job_id,
                recommendations=top_recommendations,
                algorithm_version="matching_v1.0",
            )

        except Exception:
            logger.exception(
                f"[Matching] 💥 매칭 계산 실패 | job_id={request.job_id}"
            )
            raise

    @staticmethod
    def _calculate_single_matching(
        senior_id: int,
        health_score: float,
        request: MatchingCalculateRequest,
    ) -> RecommendationResult:
        """개별 매칭 점수 계산"""

        # ⭐ 임시 데이터 (실제로는 DB에서 가져옴)
        senior_data = {
            "region": "서울 강남구",
            "years_experience": 3,
            "titles": ["요양보호사"],
            "available": True,
        }

        job_data = {
            "title": "노인 요양 업무",
            "location": "서울 강남구",
            "description": "거동이 불편한 노인 이동 보조",
        }

        # 4개 요소 계산
        health_compat = MatchingFeatureExtractor.calculate_health_compatibility(
            senior_health_score=health_score,
            required_health_level=4,
        )

        exp_match = MatchingFeatureExtractor.calculate_experience_match(
            senior_years_experience=senior_data["years_experience"],
            senior_titles=senior_data["titles"],
            job_title=job_data["title"],
            job_description=job_data["description"],
        )

        location_dist = MatchingFeatureExtractor.calculate_location_distance(
            senior_region=senior_data["region"],
            job_location=job_data["location"],
        )

        availability_match = MatchingFeatureExtractor.calculate_availability_match(
            senior_available=senior_data["available"]
        )

        # 거리 → 점수 (0~1)
        location_score = max(0.0, 1.0 - (location_dist / 50.0))  # 50km 기준

        # DEBUG 용 상세 로그
        logger.debug(
            f"[Matching][detail] senior_id={senior_id} | "
            f"health={health_compat:.2f}, exp={exp_match:.2f}, "
            f"loc_dist={location_dist:.2f}, loc_score={location_score:.2f}, "
            f"avail={availability_match:.2f}"
        )

        # 가중평균 (0~100 점수)
        match_score = (
            health_compat * MatchingService.WEIGHTS["health_compatibility"]
            + exp_match * MatchingService.WEIGHTS["experience_match"]
            + location_score * MatchingService.WEIGHTS["location_distance"]
            + availability_match * MatchingService.WEIGHTS["availability_match"]
        ) * 100.0

        return RecommendationResult(
            senior_profile_id=senior_id,
            rank=0,  # 정렬 후 부여
            match_score=round(match_score, 1),
            components=MatchingComponentScore(
                health_compatibility=health_compat,
                experience_match=exp_match,
                location_distance=location_dist,
                availability_match=availability_match,
            ),
        )
