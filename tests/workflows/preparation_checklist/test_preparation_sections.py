from dataclasses import replace
from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    Applicability,
    ChecklistEntry,
    HoldReason,
    Role,
    SectionKind,
    split_into_sections,
)


def entry(item_id: str, due: date | None) -> ChecklistEntry:
    return ChecklistEntry(
        item_id,
        Role.LEADER,
        "가상 항목",
        "",
        "시험 확인",
        "D+0",
        due,
        False,
        Applicability.APPLICABLE,
        (),
    )


def test_empty_sections() -> None:
    today = date(2027, 3, 3)
    result = split_into_sections((), today)
    assert result.today == today
    assert tuple(s.kind for s in result.sections) == tuple(SectionKind)
    assert all(s.entries == () for s in result.sections)
    assert tuple(s.kind for s in result.sections if s.collapsed) == (SectionKind.LATER,)


@pytest.mark.parametrize("applicability", [Applicability.APPLICABLE, Applicability.UNDECIDED])
def test_missing_date_without_hold_reason_rejected(applicability: Applicability) -> None:
    invalid = replace(entry("VT-01", None), applicability=applicability)
    with pytest.raises(ValueError):
        split_into_sections((invalid,), date(2027, 3, 3))


def test_not_applicable_without_date_or_hold_reason() -> None:
    skipped = replace(entry("VT-01", None), applicability=Applicability.NOT_APPLICABLE)
    result = split_into_sections((skipped,), date(2027, 3, 3))
    assert next(s for s in result.sections if s.kind == SectionKind.NOT_APPLICABLE).entries == (
        skipped,
    )
    assert all(not s.entries for s in result.sections if s.kind != SectionKind.NOT_APPLICABLE)


@pytest.mark.parametrize(
    ("due", "kind"),
    [
        (date(2027, 2, 28), SectionKind.OVERDUE),
        (date(2027, 3, 1), SectionKind.OVERDUE),
        (date(2027, 3, 2), SectionKind.OVERDUE),
        (date(2027, 3, 3), SectionKind.THIS_WEEK),
        (date(2027, 3, 7), SectionKind.THIS_WEEK),
        (date(2027, 3, 8), SectionKind.NEXT_WEEK),
        (date(2027, 3, 14), SectionKind.NEXT_WEEK),
        (date(2027, 3, 15), SectionKind.LATER),
    ],
)
def test_boundaries(due: date, kind: SectionKind) -> None:
    result = split_into_sections((entry("VT-01", due),), date(2027, 3, 3))
    assert next(s.kind for s in result.sections if s.entries) == kind


@pytest.mark.parametrize(
    ("today", "kind"),
    [
        (date(2027, 2, 15), SectionKind.LATER),
        (date(2027, 2, 22), SectionKind.NEXT_WEEK),
        (date(2027, 3, 1), SectionKind.THIS_WEEK),
        (date(2027, 3, 9), SectionKind.OVERDUE),
    ],
)
def test_today_moves_same_item(today: date, kind: SectionKind) -> None:
    result = split_into_sections((entry("VT-01", date(2027, 3, 2)),), today)
    assert next(s.kind for s in result.sections if s.entries) == kind


@pytest.mark.parametrize("today", [date(2027, 3, 6), date(2027, 3, 7)])
def test_weekend_today(today: date) -> None:
    items = (entry("VT-01", date(2027, 3, 7)), entry("VT-02", date(2027, 3, 8)))
    result = split_into_sections(items, today)
    assert result.sections[1].entries == items[:1]
    assert result.sections[2].entries == items[1:]


@pytest.mark.parametrize("today", [date(2027, 2, 1), date(2027, 3, 3), date(2027, 4, 1)])
def test_hold_and_not_applicable_priority(today: date) -> None:
    held = replace(entry("VT-01", None), hold_reasons=(HoldReason.PERIOD_RULE,))
    undecided = replace(
        entry("VT-02", date(2027, 3, 3)),
        applicability=Applicability.UNDECIDED,
        hold_reasons=(HoldReason.LAPTOP_UNDECIDED,),
    )
    skipped = replace(held, item_id="VT-03", applicability=Applicability.NOT_APPLICABLE)
    result = split_into_sections((held, undecided, skipped), today)
    assert result.sections[4].entries == (undecided, held)
    assert result.sections[5].entries == (skipped,)


def test_stable_sort() -> None:
    early = entry("VT-01", date(2027, 3, 3))
    same = replace(early, item_id="VT-02")
    late = entry("VT-03", date(2027, 3, 5))
    missing = replace(entry("VT-04", None), hold_reasons=(HoldReason.PERIOD_RULE,))
    missing2 = replace(missing, item_id="VT-05")
    result = split_into_sections((late, early, missing, same, missing2), date(2027, 3, 3))
    assert result.sections[1].entries == (early, same, late)
    assert result.sections[4].entries == (missing, missing2)
