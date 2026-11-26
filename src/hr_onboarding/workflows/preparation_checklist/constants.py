"""팀 확인이 필요한 PROVISIONAL 표시 및 조건 상수."""

from collections.abc import Mapping
from types import MappingProxyType

from .models import HoldReason, InputHoldReason, Role, SectionKind

# PROVISIONAL: Spec P8 대상 역할과 순서.
TARGET_ROLES = (Role.LEADER, Role.GENERAL_AFFAIRS, Role.BUDDY)
# PROVISIONAL: Spec P2 월요일 시작.
WEEK_START_WEEKDAY = 0
# PROVISIONAL: 표시 방식 A와 P4, 이후 구간만 접는다.
COLLAPSED_SECTIONS = (SectionKind.LATER,)
# PROVISIONAL: 양식 3절의 조건 칸 값. 공통 계약이 아니다.
CONDITION_CAREER = "경력"
CONDITION_LAPTOP = "노트북 지급"
# PROVISIONAL: Spec P1·P7 및 Q20의 화면 표시용 설명.
HOLD_REASON_LABELS: Mapping[HoldReason, str] = MappingProxyType(
    {
        HoldReason.CONFIRMATION_DATE_MISSING: "합격 확정일 없음",
        HoldReason.OFFICE_SCHEDULE_MISSING: "사무실 출근 일정 없음",
        HoldReason.PERIOD_RULE: "기간형 기준일 확인 필요",
        HoldReason.LAPTOP_UNDECIDED: "노트북 지급 여부 미정",
        HoldReason.UNSUPPORTED_RULE: "해석할 수 없는 기준일",
    }
)

# PROVISIONAL: 그래프 Spec G6 입력 보류 사유와 화면 표시용 설명.
INPUT_HOLD_REASON_LABELS: Mapping[InputHoldReason, str] = MappingProxyType(
    {
        InputHoldReason.HIRE_ID_MISSING: "입사자 식별자 없음",
        InputHoldReason.START_DATE_MISSING: "입사일 없음",
        InputHoldReason.CAREER_TYPE_MISSING: "경력 구분 없음",
        InputHoldReason.LEADER_MISSING: "리더 없음",
        InputHoldReason.TEMPLATE_MISSING: "체크리스트 양식 없음",
        InputHoldReason.TODAY_MISSING: "기준 날짜 없음",
        InputHoldReason.BUDDY_MISSING: "버디 없음",
    }
)
# PROVISIONAL: 그래프 Spec G3 버디 누락만 페이지 단위 보류.
PAGE_HOLD_REASONS: Mapping[InputHoldReason, Role] = MappingProxyType(
    {InputHoldReason.BUDDY_MISSING: Role.BUDDY}
)
