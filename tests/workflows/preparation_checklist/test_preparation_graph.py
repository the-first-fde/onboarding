"""가상 입력의 그래프 분기와 기존 순수 함수 일치를 검증한다."""

from dataclasses import replace
from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    CONDITION_LAPTOP,
    PAGE_HOLD_REASONS,
    ChecklistTemplate,
    GraphOutcome,
    HoldReason,
    InputHoldReason,
    NewHire,
    PageHold,
    PreparationRequest,
    Role,
    SectionKind,
    build_preparation_checklist,
    build_preparation_graph,
    split_into_sections,
)


@pytest.mark.parametrize("reverse", [False, True])
def test_normal_graph_matches_builder(
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
    hire_experienced_laptop: NewHire,
    reverse: bool,
) -> None:
    if reverse:
        template = replace(template, items=tuple(reversed(template.items)))
    result = build_preparation_graph().invoke(
        dict(request=request_complete, template=template, today=today)
    )
    assert result["outcome"] == GraphOutcome.DRAFTED
    assert tuple(page.role for page in result["page_drafts"]) == tuple(Role)
    direct = build_preparation_checklist(hire_experienced_laptop, template)
    assert result["checklist"] == direct
    for roles, page, original in zip(
        result["role_sections"], result["page_drafts"], direct.role_checklists, strict=True
    ):
        ids = tuple(entry.item_id for entry in original.entries)
        assert roles.item_ids == page.item_ids == ids
        assert roles.sectioned == split_into_sections(original.entries, today)
        for block, section in zip(page.blocks, roles.sectioned.sections, strict=True):
            assert tuple(todo.text.split()[0] for todo in block.children) == tuple(
                entry.item_id for entry in section.entries
            )
    output = repr(
        (result["checklist"], result["role_sections"], result["page_drafts"], result["page_holds"])
    )
    assert request_complete.leader_ref not in output
    assert request_complete.buddy_ref not in output


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
def test_required_missing(
    field: str,
    reason: InputHoldReason,
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
) -> None:
    state = dict(request=request_complete, template=template, today=today)
    if field in ("template", "today"):
        state[field] = None
    else:
        state["request"] = replace(request_complete, **{field: "" if field == "hire_id" else None})
    result = build_preparation_graph().invoke(state)
    assert result["outcome"] == GraphOutcome.ON_HOLD
    assert result["input_hold_reasons"] == (reason,)
    assert not {"checklist", "role_sections", "page_drafts"} & result.keys()


def test_all_missing() -> None:
    result = build_preparation_graph().invoke(
        dict(
            request=PreparationRequest("", None, None, None, None, None), template=None, today=None
        )
    )
    assert result["input_hold_reasons"] == tuple(
        r for r in InputHoldReason if r not in PAGE_HOLD_REASONS
    )
    assert result["page_holds"] == (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)),)
    assert not {"checklist", "role_sections", "page_drafts"} & result.keys()


def test_buddy_missing(
    request_without_buddy: PreparationRequest, template: ChecklistTemplate, today: date
) -> None:
    result = build_preparation_graph().invoke(
        dict(request=request_without_buddy, template=template, today=today)
    )
    assert result["outcome"] == GraphOutcome.DRAFTED
    assert tuple(page.role for page in result["page_drafts"]) == (Role.LEADER, Role.GENERAL_AFFAIRS)
    assert result["page_holds"] == (PageHold(Role.BUDDY, (InputHoldReason.BUDDY_MISSING,)),)
    assert len(result["role_sections"]) == 3


def test_laptop_undecided(
    request_laptop_undecided: PreparationRequest, template: ChecklistTemplate, today: date
) -> None:
    result = build_preparation_graph().invoke(
        dict(request=request_laptop_undecided, template=template, today=today)
    )
    assert result["outcome"] == GraphOutcome.DRAFTED
    held = [
        entry
        for roles in result["role_sections"]
        for section in roles.sectioned.sections
        if section.kind == SectionKind.ON_HOLD
        for entry in section.entries
    ]
    expected_ids = {item.item_id for item in template.items if item.condition == CONDITION_LAPTOP}
    undecided_ids = {
        entry.item_id
        for roles in result["role_sections"]
        for section in roles.sectioned.sections
        for entry in section.entries
        if HoldReason.LAPTOP_UNDECIDED in entry.hold_reasons
    }
    assert undecided_ids == expected_ids
    assert expected_ids <= {entry.item_id for entry in held}


@pytest.mark.parametrize(
    ("defect", "message"),
    [("duplicate", "Duplicate item_id"), ("condition", "Unsupported condition")],
)
def test_template_errors_propagate(
    defect: str,
    message: str,
    request_complete: PreparationRequest,
    template: ChecklistTemplate,
    today: date,
) -> None:
    items = (
        template.items + (template.items[0],)
        if defect == "duplicate"
        else (replace(template.items[0], condition="알 수 없는 조건"),)
    )
    with pytest.raises(ValueError, match=message):
        build_preparation_graph().invoke(
            dict(request=request_complete, template=replace(template, items=items), today=today)
        )


def test_graph_node_names() -> None:
    assert set(build_preparation_graph().get_graph().nodes) == {
        "__start__",
        "__end__",
        "validate_input",
        "build_checklist",
        "split_sections",
        "draft_pages",
    }
