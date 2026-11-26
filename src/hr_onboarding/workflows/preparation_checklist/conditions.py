"""입사자 정보에 따른 양식 조건 판정."""

from .constants import CONDITION_CAREER, CONDITION_LAPTOP
from .models import Applicability, CareerType, HoldReason, NewHire


def evaluate_condition(condition: str, hire: NewHire) -> tuple[Applicability, HoldReason | None]:
    """양식 조건의 해당 여부와 미정 사유를 반환한다.

    Args:
        condition: 빈 문자열 또는 지원하는 조건 값.
        hire: 조건 판정에 필요한 입사자 정보.

    Returns:
        해당 여부와 노트북 미정 보류 사유.

    Raises:
        ValueError: 지원하지 않는 조건 값인 경우.
    """
    if condition == "":
        return Applicability.APPLICABLE, None
    if condition == CONDITION_CAREER:
        applicable = hire.career_type == CareerType.EXPERIENCED
    elif condition == CONDITION_LAPTOP:
        if hire.laptop_provided is None:
            return Applicability.UNDECIDED, HoldReason.LAPTOP_UNDECIDED
        applicable = hire.laptop_provided
    else:
        raise ValueError(f"Unsupported condition: {condition}")
    return (Applicability.APPLICABLE if applicable else Applicability.NOT_APPLICABLE), None
