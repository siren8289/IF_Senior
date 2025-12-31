from typing import Dict
import logging

from utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_health_input(
    height_cm: int,
    weight_kg: float,
    chronic_conditions: Dict[str, bool],
    risk_flags: Dict[str, float]
) -> None:
    """
    건강점수 입력 검증
    
    Args:
        height_cm: 키 (cm)
        weight_kg: 체중 (kg)
        chronic_conditions: 만성질환 딕셔너리
        risk_flags: 위험 지표 딕셔너리
        
    Raises:
        ValueError: 검증 실패 시
    """
    # 키 검증
    if not (100 <= height_cm <= 250):
        raise ValidationError(
            f"키는 100-250cm 범위여야 합니다. 입력값: {height_cm}cm",
            details={"field": "height_cm", "value": height_cm, "constraint": "100-250cm"}
        )
    
    # 체중 검증
    if not (20 <= weight_kg <= 200):
        raise ValidationError(
            f"체중은 20-200kg 범위여야 합니다. 입력값: {weight_kg}kg",
            details={"field": "weight_kg", "value": weight_kg, "constraint": "20-200kg"}
        )
    
    # 만성질환 검증
    if not isinstance(chronic_conditions, dict):
        raise ValidationError(
            "chronic_conditions는 딕셔너리여야 합니다",
            details={"field": "chronic_conditions", "value": type(chronic_conditions).__name__}
        )
    
    for condition, value in chronic_conditions.items():
        if not isinstance(value, bool):
            raise ValidationError(
                f"만성질환 값은 boolean이어야 합니다. {condition}: {value}",
                details={"field": f"chronic_conditions.{condition}", "value": value, "expected_type": "bool"}
            )
    
    # 위험 지표 검증
    if not isinstance(risk_flags, dict):
        raise ValidationError(
            "risk_flags는 딕셔너리여야 합니다",
            details={"field": "risk_flags", "value": type(risk_flags).__name__}
        )
    
    for flag_name, flag_value in risk_flags.items():
        if not isinstance(flag_value, (int, float)):
            raise ValidationError(
                f"위험 지표 값은 숫자여야 합니다. {flag_name}: {flag_value}",
                details={"field": f"risk_flags.{flag_name}", "value": flag_value, "expected_type": "number"}
            )
        
        if not (0 <= flag_value <= 1):
            raise ValidationError(
                f"위험 지표는 0-1 범위여야 합니다. {flag_name}: {flag_value}",
                details={"field": f"risk_flags.{flag_name}", "value": flag_value, "constraint": "0-1"}
            )
    
    logger.debug("입력 검증 통과")


def validate_bmi(height_cm: int, weight_kg: float) -> float:
    """
    BMI 계산 및 검증
    
    Args:
        height_cm: 키 (cm)
        weight_kg: 체중 (kg)
        
    Returns:
        float: BMI 값
        
    Raises:
        ValueError: BMI가 비정상 범위일 때
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 10 or bmi > 50:
        raise ValidationError(
            f"BMI가 비정상 범위입니다: {bmi:.2f}",
            details={"bmi": bmi, "constraint": "10-50"}
        )
    
    return bmi
