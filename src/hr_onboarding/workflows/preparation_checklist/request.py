"""그래프 입력의 전체·페이지 보류를 검증한다."""

from dataclasses import dataclass
from datetime import date

from .constants import PAGE_HOLD_REASONS
from .models import CareerType, ChecklistTemplate, InputHoldReason, NewHire, Role


@dataclass(frozen=True)
class PreparationRequest:
    """인물의 가상 참조값과 계산 입력만 받는 요청."""

    hire_id: str
    start_date: date | None
    career_type: CareerType | None
    laptop_provided: bool | None
    leader_ref: str | None
    buddy_ref: str | None


@dataclass(frozen=True)
class PageHold:
    """특정 담당의 페이지를 생성하지 않는 사유."""

    role: Role
    reasons: tuple[InputHoldReason, ...]


@dataclass(frozen=True)
class RequestValidation:
    """검증된 입사자 또는 전체 보류 사유와 페이지 보류."""

    hire: NewHire | None
    hold_reasons: tuple[InputHoldReason, ...]
    page_holds: tuple[PageHold, ...]


def validate_request(
    request: PreparationRequest, template: ChecklistTemplate | None, today: date | None
) -> RequestValidation:
    """누락 사유를 열거형 순서로 모두 모은다(G2·G3·G5·G6).

    Args:
        request: 인물 참조값을 포함한 가상 입력.
        template: 사용할 양식. None이면 전체 보류.
        today: 호출자가 KST로 변환한 날짜. None이면 전체 보류.

    Returns:
        전체 보류 시 hire가 None인 검증 결과. 버디 누락은 페이지 보류다.
    """
    missing = {
        InputHoldReason.HIRE_ID_MISSING: not (request.hire_id and request.hire_id.strip()),
        InputHoldReason.START_DATE_MISSING: request.start_date is None,
        InputHoldReason.CAREER_TYPE_MISSING: request.career_type is None,
        InputHoldReason.LEADER_MISSING: not (request.leader_ref and request.leader_ref.strip()),
        InputHoldReason.TEMPLATE_MISSING: template is None,
        InputHoldReason.TODAY_MISSING: today is None,
        InputHoldReason.BUDDY_MISSING: not (request.buddy_ref and request.buddy_ref.strip()),
    }
    holds = tuple(
        reason for reason in InputHoldReason if missing[reason] and reason not in PAGE_HOLD_REASONS
    )
    page_holds = tuple(
        PageHold(role, (reason,)) for reason, role in PAGE_HOLD_REASONS.items() if missing[reason]
    )
    if holds or request.start_date is None or request.career_type is None:
        return RequestValidation(None, holds, page_holds)
    hire = NewHire(
        request.hire_id, request.start_date, request.career_type, request.laptop_provided
    )
    return RequestValidation(hire, (), page_holds)
