from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    DueRule,
    DueRuleKind,
    HoldReason,
    parse_due_rule,
    resolve_due_date,
    shift_to_previous_weekday,
)


@pytest.mark.parametrize(
    ("raw", "kind", "offset"),
    [
        ("D-14", DueRuleKind.START_OFFSET, -14),
        ("D+29", DueRuleKind.START_OFFSET, 29),
        (" D+0 ", DueRuleKind.START_OFFSET, 0),
        ("D-0", DueRuleKind.START_OFFSET, 0),
        (" 확정+2일 ", DueRuleKind.CONFIRMATION_OFFSET, 2),
        ("확정+0일", DueRuleKind.CONFIRMATION_OFFSET, 0),
        (" 첫 정기 사무실 출근일 ", DueRuleKind.FIRST_OFFICE_DAY, None),
        ("첫 주", DueRuleKind.PERIOD, None),
        ("3주 차", DueRuleKind.PERIOD, None),
        (" 12주 차 ", DueRuleKind.PERIOD, None),
        ("미정", DueRuleKind.UNSUPPORTED, None),
        ("", DueRuleKind.UNSUPPORTED, None),
        ("D+1일", DueRuleKind.UNSUPPORTED, None),
        ("D--1", DueRuleKind.UNSUPPORTED, None),
        ("D+1x", DueRuleKind.UNSUPPORTED, None),
    ],
)
def test_parse_rule(raw: str, kind: DueRuleKind, offset: int | None) -> None:
    assert parse_due_rule(raw) == DueRule(kind, offset)


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2027, 2, 27), date(2027, 2, 26)),
        (date(2027, 2, 28), date(2027, 2, 26)),
        (date(2027, 3, 1), date(2027, 3, 1)),
        (date(2027, 2, 26), date(2027, 2, 26)),
    ],
)
def test_shift_weekend(day: date, expected: date) -> None:
    assert shift_to_previous_weekday(day) == expected


@pytest.mark.parametrize(
    ("raw", "expected", "adjusted"),
    [
        ("D-3", date(2027, 2, 26), True),
        ("D+89", date(2027, 5, 28), True),
        ("D+0", date(2027, 3, 2), False),
        ("D-14", date(2027, 2, 16), False),
    ],
)
def test_resolve_offset(raw: str, expected: date, adjusted: bool) -> None:
    result = resolve_due_date(parse_due_rule(raw), date(2027, 3, 2))
    assert (result.due_date, result.weekend_adjusted, result.hold_reason) == (
        expected,
        adjusted,
        None,
    )


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        ("확정+2일", HoldReason.CONFIRMATION_DATE_MISSING),
        ("첫 정기 사무실 출근일", HoldReason.OFFICE_SCHEDULE_MISSING),
        ("첫 주", HoldReason.PERIOD_RULE),
        ("3주 차", HoldReason.PERIOD_RULE),
        ("알 수 없음", HoldReason.UNSUPPORTED_RULE),
    ],
)
def test_unresolved_rule(raw: str, reason: HoldReason) -> None:
    result = resolve_due_date(parse_due_rule(raw), date(2027, 3, 2))
    assert (result.due_date, result.weekend_adjusted, result.hold_reason) == (None, False, reason)
