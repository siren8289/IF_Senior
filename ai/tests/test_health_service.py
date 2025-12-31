import pytest
from services.health_service import HealthScoreService
from schemas.health import RiskLevel

def test_calculate_health_score_normal():
    """정상 케이스"""
    response = HealthScoreService.calculate_health_score(
        senior_profile_id=1,
        height_cm=170,
        weight_kg=75,
        chronic_conditions={"hypertension": False},
        risk_flags={"mobility_limited": 0.1}
    )

    assert response.health_score > 70
    assert response.risk_level == RiskLevel.LOW
    assert len(response.recommendations) > 0

def test_calculate_health_score_high_risk():
    """고위험 케이스"""
    response = HealthScoreService.calculate_health_score(
        senior_profile_id=2,
        height_cm=160,
        weight_kg=100,
        chronic_conditions={
            "hypertension": True,
            "diabetes": True,
            "arthritis": True
        },
        risk_flags={"mobility_limited": 0.8}
    )

    assert response.health_score < 50
    assert response.risk_level == RiskLevel.CRITICAL

def test_bmi_calculation():
    """BMI 계산"""
    from features.health_features import HealthFeatureExtractor

    bmi = HealthFeatureExtractor.calculate_bmi(170, 75)
    assert 25 < bmi < 26

@pytest.mark.asyncio
async def test_health_api():
    """API 통합 테스트"""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    response = client.post(
        "/api/ml/v1/health/calculate",
        json={
            "senior_profile_id": 1,
            "height_cm": 170,
            "weight_kg": 75,
            "chronic_conditions": {},
            "risk_flags": {}
        }
    )

    assert response.status_code == 200
    assert response.json()["health_score"] > 0
