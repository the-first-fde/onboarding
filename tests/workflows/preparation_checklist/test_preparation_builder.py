from collections.abc import MutableMapping
from dataclasses import FrozenInstanceError, fields, replace
from typing import cast

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    HOLD_REASON_LABELS,
    Applicability,
    ChecklistTemplate,
    HoldReason,
    NewHire,
    Role,
    build_preparation_checklist,
    parse_due_rule,
    resolve_due_date,
    split_into_sections,
)


def test_hold_reason_labels_complete() -> None:
    assert set(HOLD_REASON_LABELS) == set(HoldReason)
    assert all(label.strip() for label in HOLD_REASON_LABELS.values())


def test_hold_reason_labels_read_only() -> None:
    labels = cast(MutableMapping[HoldReason, str], HOLD_REASON_LABELS)
    reason = HoldReason.PERIOD_RULE
    with pytest.raises(TypeError):
        labels[reason] = labels[reason]


def test_role_order_and_fields(
    hire_experienced_laptop: NewHire, template: ChecklistTemplate
) -> None:
    result = build_preparation_checklist(hire_experienced_laptop, template)
    assert (result.hire_id, result.template_version) == ("VH-001", "vtest")
    assert tuple(group.role for group in result.role_checklists) == (
        Role.LEADER,
        Role.GENERAL_AFFAIRS,
        Role.BUDDY,
    )
    for group in result.role_checklists:
        source = tuple(item for item in template.items if item.owner == group.role.value)
        assert tuple(entry.item_id for entry in group.entries) == tuple(i.item_id for i in source)
        for entry, item in zip(group.entries, source, strict=True):
            assert (entry.title, entry.collaborator, entry.completion_criteria, entry.due_rule) == (
                item.title,
                item.collaborator,
                item.completion_criteria,
                item.due_rule,
            )
            assert entry.role == group.role
            assert entry.due_date is not None or entry.hold_reasons


def test_empty_roles(hire_experienced_laptop: NewHire, template: ChecklistTemplate) -> None:
    for items in ((), tuple(i for i in template.items if i.owner == "리더")):
        result = build_preparation_checklist(
            hire_experienced_laptop, replace(template, items=items)
        )
        assert len(result.role_checklists) == 3
        assert result.role_checklists[1].entries == result.role_checklists[2].entries == ()


def test_not_applicable_kept(hire_new_no_laptop: NewHire, template: ChecklistTemplate) -> None:
    result = build_preparation_checklist(hire_new_no_laptop, template)
    entries = {e.item_id: e for g in result.role_checklists for e in g.entries}
    for item_id in ("VT-03", "VT-05", "VT-08"):
        assert entries[item_id].applicability == Applicability.NOT_APPLICABLE
    assert entries["VT-04"].weekend_adjusted


def test_both_hold_reasons(hire_laptop_undecided: NewHire, template: ChecklistTemplate) -> None:
    result = build_preparation_checklist(hire_laptop_undecided, template)
    entries = {e.item_id: e for g in result.role_checklists for e in g.entries}
    assert entries["VT-03"].due_date is not None
    assert entries["VT-03"].hold_reasons == (HoldReason.LAPTOP_UNDECIDED,)
    assert entries["VT-08"].due_date is None
    assert entries["VT-08"].hold_reasons == (
        HoldReason.CONFIRMATION_DATE_MISSING,
        HoldReason.LAPTOP_UNDECIDED,
    )


@pytest.mark.parametrize("excluded", [False, True])
def test_duplicate_ids(
    hire_experienced_laptop: NewHire,
    template: ChecklistTemplate,
    excluded: bool,
) -> None:
    first = replace(template.items[0], owner="인사") if excluded else template.items[0]
    with pytest.raises(ValueError):
        build_preparation_checklist(
            hire_experienced_laptop, replace(template, items=(first, first))
        )


def test_unknown_template_condition(
    hire_experienced_laptop: NewHire,
    template: ChecklistTemplate,
) -> None:
    invalid = replace(template, items=(replace(template.items[0], condition="새 조건"),))
    with pytest.raises(ValueError):
        build_preparation_checklist(hire_experienced_laptop, invalid)


def test_models_frozen(hire_experienced_laptop: NewHire, template: ChecklistTemplate) -> None:
    result = build_preparation_checklist(hire_experienced_laptop, template)
    rule = parse_due_rule("D+0")
    resolution = resolve_due_date(rule, hire_experienced_laptop.start_date)
    sections = split_into_sections(
        result.role_checklists[0].entries, hire_experienced_laptop.start_date
    )
    objects = (
        hire_experienced_laptop,
        template,
        template.items[0],
        rule,
        resolution,
        result,
        result.role_checklists[0],
        result.role_checklists[0].entries[0],
        sections,
        sections.sections[0],
    )
    for obj in objects:
        field = fields(obj)[0].name
        with pytest.raises(FrozenInstanceError):
            setattr(obj, field, getattr(obj, field))
    assert isinstance(result.role_checklists, tuple)
    assert isinstance(result.role_checklists[0].entries, tuple)
    assert isinstance(sections.sections, tuple)
