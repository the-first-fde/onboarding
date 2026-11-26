from dataclasses import replace
from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    CareerType,
    ChecklistTemplate,
    ChecklistTemplateItem,
    NewHire,
    PreparationRequest,
)


@pytest.fixture
def hire_experienced_laptop() -> NewHire:
    return NewHire("VH-001", date(2027, 3, 2), CareerType.EXPERIENCED, True)


@pytest.fixture
def hire_new_no_laptop() -> NewHire:
    return NewHire("VH-002", date(2027, 3, 8), CareerType.NEW_GRADUATE, False)


@pytest.fixture
def hire_laptop_undecided() -> NewHire:
    return NewHire("VH-003", date(2027, 3, 2), CareerType.EXPERIENCED, None)


@pytest.fixture
def template() -> ChecklistTemplate:
    rows = (
        ("리더", "D-14", ""),
        ("인사", "D-7", ""),
        ("총무", "D-3", "노트북 지급"),
        ("버디", "D-1", ""),
        ("리더", "D+0", "경력"),
        ("총무", "D+29", ""),
        ("리더", "D+89", ""),
        ("총무", "확정+2일", "노트북 지급"),
        ("버디", "첫 정기 사무실 출근일", ""),
        ("리더", "첫 주", ""),
        ("버디", "3주 차", ""),
        ("총무", "미정 표기", ""),
        ("입사자", "D-7", ""),
    )
    return ChecklistTemplate(
        "vtest",
        tuple(
            ChecklistTemplateItem(
                f"VT-{index:02}",
                "가상 단계",
                rule,
                f"시험 준비 {index}",
                owner,
                "시험 협력 역할",
                condition,
                f"시험 확인 {index} 기록",
                "",
                "가상 비고",
            )
            for index, (owner, rule, condition) in enumerate(rows, 1)
        ),
    )


@pytest.fixture
def today() -> date:
    return date(2027, 2, 22)


@pytest.fixture
def request_complete(hire_experienced_laptop: NewHire) -> PreparationRequest:
    hire = hire_experienced_laptop
    return PreparationRequest(
        hire.hire_id, hire.start_date, hire.career_type, hire.laptop_provided, "VL-001", "VB-001"
    )


@pytest.fixture
def request_without_buddy(request_complete: PreparationRequest) -> PreparationRequest:
    return replace(request_complete, buddy_ref=None)


@pytest.fixture
def request_laptop_undecided(request_complete: PreparationRequest) -> PreparationRequest:
    return replace(request_complete, laptop_provided=None)
