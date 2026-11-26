"""가상 요청의 전체·페이지 보류와 불변성을 검증한다."""

from dataclasses import FrozenInstanceError, replace
from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    INPUT_HOLD_REASON_LABELS,
    PAGE_HOLD_REASONS,
    ChecklistTemplate,
    InputHoldReason,
    NewHire,
    Role,
)
from hr_onboarding.workflows.preparation_checklist.request import (
    PageHold,
    PreparationRequest,
    RequestValidation,
    validate_request,
)


def test_complete_request(
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
    hire_experienced_laptop: NewHire,
) -> None:
    result = validate_request(request_complete, template, today)
    assert result == RequestValidation(hire_experienced_laptop, (), ())


@pytest.mark.parametrize(
    ("field", "reason"),
    [
        ("hire_id", InputHoldReason.HIRE_ID_MISSING),
        ("start_date", InputHoldReason.START_DATE_MISSING),
        ("career_type", InputHoldReason.CAREER_TYPE_MISSING),
        ("leader_ref", InputHoldReason.LEADER_MISSING),
        ("template", InputHoldReason.TEMPLATE_MISSING),
        ("today", InputHoldReason.TODAY_MISSING),
    ],
)
def test_missing_required(
    field: str,
    reason: InputHoldReason,
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
) -> None:
    request = request_complete
    if field == "template":
        template = None
    elif field == "today":
        today = None
    else:
        request = replace(request, **{field: "" if field == "hire_id" else None})
    result = validate_request(request, template, today)
    assert result.hire is None
    assert result.hold_reasons == (reason,)


@pytest.mark.parametrize(
    ("field", "reasons"),
    [
        ("hire_id", (InputHoldReason.HIRE_ID_MISSING,)),
        ("leader_ref", (InputHoldReason.LEADER_MISSING,)),
        ("buddy_ref", ()),
    ],
)
@pytest.mark.parametrize("value", ["", " \t\n"])
def test_blank_references(
    field: str,
    reasons: tuple[InputHoldReason, ...],
    value: str,
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
) -> None:
    result = validate_request(replace(request_complete, **{field: value}), template, today)
    if field == "buddy_ref":
        assert result.hold_reasons == reasons
        assert result.page_holds == (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)),)
    else:
        assert result.hire is None
        assert result.hold_reasons == reasons


def test_all_missing_collects_reasons_and_page_hold() -> None:
    request = PreparationRequest("", None, None, None, None, None)
    result = validate_request(request, None, None)
    assert result.hire is None
    assert result.hold_reasons == tuple(r for r in InputHoldReason if r not in PAGE_HOLD_REASONS)
    assert result.page_holds == (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)),)


def test_buddy_only_holds_page(
    request_without_buddy: PreparationRequest, template: ChecklistTemplate, today: date
) -> None:
    result = validate_request(request_without_buddy, template, today)
    assert result.hire is not None
    assert result.hold_reasons == ()
    assert result.page_holds == (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)),)


def test_laptop_undecided_is_valid(
    request_laptop_undecided: PreparationRequest, template: ChecklistTemplate, today: date
) -> None:
    result = validate_request(request_laptop_undecided, template, today)
    assert result.hire is not None
    assert result.hire.laptop_provided is None
    assert not result.hold_reasons


def test_request_models_are_frozen(
    request_complete: PreparationRequest, template: ChecklistTemplate, today: date
) -> None:
    result = validate_request(request_complete, template, today)
    for model, field, value in (
        (request_complete, "hire_id", "changed"),
        (result, "hire", None),
        (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)), "role", Role.LEADER),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(model, field, value)


def test_hold_constants_are_complete_and_read_only() -> None:
    assert tuple(INPUT_HOLD_REASON_LABELS) == tuple(InputHoldReason)
    assert all(INPUT_HOLD_REASON_LABELS.values())
    assert dict(PAGE_HOLD_REASONS) == {InputHoldReason.BUDDY_MISSING: Role.BUDDY}
    for mapping, key, value in (
        (INPUT_HOLD_REASON_LABELS, InputHoldReason.HIRE_ID_MISSING, "changed"),
        (PAGE_HOLD_REASONS, InputHoldReason.BUDDY_MISSING, Role.LEADER),
    ):
        with pytest.raises(TypeError):
            mapping[key] = value
