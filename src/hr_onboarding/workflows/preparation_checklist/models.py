"""담당별 준비 체크리스트의 모듈 전용 잠정 불변 모델."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Role(StrEnum):
    """출력 체크리스트 담당 역할."""

    LEADER = "리더"
    GENERAL_AFFAIRS = "총무"
    BUDDY = "버디"


class CareerType(StrEnum):
    """조건 판정에 사용하는 경력 구분."""

    EXPERIENCED = "경력"
    NEW_GRADUATE = "신입"


class DueRuleKind(StrEnum):
    """기준일 표기의 해석 종류."""

    START_OFFSET = "START_OFFSET"
    CONFIRMATION_OFFSET = "CONFIRMATION_OFFSET"
    FIRST_OFFICE_DAY = "FIRST_OFFICE_DAY"
    PERIOD = "PERIOD"
    UNSUPPORTED = "UNSUPPORTED"


class HoldReason(StrEnum):
    """날짜 계산 또는 조건 판정을 보류한 이유."""

    CONFIRMATION_DATE_MISSING = "CONFIRMATION_DATE_MISSING"
    OFFICE_SCHEDULE_MISSING = "OFFICE_SCHEDULE_MISSING"
    PERIOD_RULE = "PERIOD_RULE"
    LAPTOP_UNDECIDED = "LAPTOP_UNDECIDED"
    UNSUPPORTED_RULE = "UNSUPPORTED_RULE"


class Applicability(StrEnum):
    """입사자에게 항목 조건이 해당하는지 나타낸다."""

    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNDECIDED = "UNDECIDED"


class SectionKind(StrEnum):
    """표시 순서대로 정의한 체크리스트 구간."""

    OVERDUE = "지연"
    THIS_WEEK = "이번 주"
    NEXT_WEEK = "다음 주"
    LATER = "이후"
    ON_HOLD = "보류"
    NOT_APPLICABLE = "해당 없음"


@dataclass(frozen=True)
class NewHire:
    """계산에 필요한 최소 입사자 정보."""

    hire_id: str
    start_date: date
    career_type: CareerType
    laptop_provided: bool | None


@dataclass(frozen=True)
class ChecklistTemplateItem:
    """진행 상태를 제외한 양식 한 행."""

    item_id: str
    stage: str
    due_rule: str
    title: str
    owner: str
    collaborator: str
    condition: str
    completion_criteria: str
    guide_doc: str
    note: str


@dataclass(frozen=True)
class ChecklistTemplate:
    """버전과 양식 순서의 항목 묶음."""

    version: str
    items: tuple[ChecklistTemplateItem, ...]


@dataclass(frozen=True)
class DueRule:
    """해석한 기준일 종류와 일 단위 오프셋."""

    kind: DueRuleKind
    offset_days: int | None


@dataclass(frozen=True)
class DueDateResolution:
    """계산된 날짜 또는 계산을 보류한 이유."""

    due_date: date | None
    weekend_adjusted: bool
    hold_reason: HoldReason | None


@dataclass(frozen=True)
class ChecklistEntry:
    """담당별 목록의 기준일 및 조건 판정 결과."""

    item_id: str
    role: Role
    title: str
    collaborator: str
    completion_criteria: str
    due_rule: str
    due_date: date | None
    weekend_adjusted: bool
    applicability: Applicability
    hold_reasons: tuple[HoldReason, ...]


@dataclass(frozen=True)
class RoleChecklist:
    """한 담당의 양식 순서 항목 묶음."""

    role: Role
    entries: tuple[ChecklistEntry, ...]


@dataclass(frozen=True)
class PreparationChecklist:
    """입사자 한 건의 담당별 준비 목록."""

    hire_id: str
    template_version: str
    role_checklists: tuple[RoleChecklist, ...]


@dataclass(frozen=True)
class ChecklistSection:
    """날짜순 항목과 접힘 여부를 담은 표시 구간."""

    kind: SectionKind
    entries: tuple[ChecklistEntry, ...]
    collapsed: bool


@dataclass(frozen=True)
class SectionedChecklist:
    """호출자가 넘긴 기준 날짜와 여섯 표시 구간."""

    today: date
    sections: tuple[ChecklistSection, ...]


class InputHoldReason(StrEnum):
    """PROVISIONAL G6: 입력 누락 사유와 표시 순서."""

    HIRE_ID_MISSING = "HIRE_ID_MISSING"
    START_DATE_MISSING = "START_DATE_MISSING"
    CAREER_TYPE_MISSING = "CAREER_TYPE_MISSING"
    LEADER_MISSING = "LEADER_MISSING"
    TEMPLATE_MISSING = "TEMPLATE_MISSING"
    TODAY_MISSING = "TODAY_MISSING"
    BUDDY_MISSING = "BUDDY_MISSING"


@dataclass(frozen=True)
class RoleSections:
    """담당별 양식 순서 ID와 표시 구간."""

    role: Role
    item_ids: tuple[str, ...]
    sectioned: SectionedChecklist
