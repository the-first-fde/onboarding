"""기준일 표기 해석과 입사일 기준 날짜 계산."""

import re
from datetime import date, timedelta

from .models import DueDateResolution, DueRule, DueRuleKind, HoldReason


def parse_due_rule(raw: str) -> DueRule:
    """양식의 기준일을 해석한다.

    Args:
        raw: 앞뒤 공백을 포함할 수 있는 기준일 표기.

    Returns:
        기준일 종류와 오프셋. 해석 불가는 UNSUPPORTED다.
    """
    value = raw.strip()
    if match := re.fullmatch(r"D([+-])([0-9]+)", value):
        offset = int(match[2]) * (-1 if match[1] == "-" else 1)
        return DueRule(DueRuleKind.START_OFFSET, offset)
    if match := re.fullmatch(r"확정\+([0-9]+)일", value):
        return DueRule(DueRuleKind.CONFIRMATION_OFFSET, int(match[1]))
    if value == "첫 정기 사무실 출근일":
        return DueRule(DueRuleKind.FIRST_OFFICE_DAY, None)
    if value == "첫 주" or re.fullmatch(r"[0-9]+주 차", value):
        return DueRule(DueRuleKind.PERIOD, None)
    return DueRule(DueRuleKind.UNSUPPORTED, None)


def shift_to_previous_weekday(day: date) -> date:
    """주말을 직전 금요일로 당긴다(P6: 공휴일 제외).

    Args:
        day: 보정 전 날짜.

    Returns:
        평일은 원래 날짜, 주말은 직전 금요일.
    """
    return day - timedelta(days=max(0, day.weekday() - 4))


def resolve_due_date(rule: DueRule, start_date: date) -> DueDateResolution:
    """입사일 오프셋만 날짜로 계산하고 나머지는 보류한다.

    Args:
        rule: 해석한 기준일 규칙.
        start_date: 입사일.

    Returns:
        주말 보정 날짜 또는 종류별 보류 사유.

    Raises:
        ValueError: 입사일 오프셋 규칙에 오프셋이 없는 경우.
    """
    if rule.kind == DueRuleKind.START_OFFSET:
        if rule.offset_days is None:
            raise ValueError("START_OFFSET requires offset_days")
        original = start_date + timedelta(days=rule.offset_days)
        adjusted = shift_to_previous_weekday(original)
        return DueDateResolution(adjusted, original != adjusted, None)
    reason = {
        DueRuleKind.CONFIRMATION_OFFSET: HoldReason.CONFIRMATION_DATE_MISSING,
        DueRuleKind.FIRST_OFFICE_DAY: HoldReason.OFFICE_SCHEDULE_MISSING,
        DueRuleKind.PERIOD: HoldReason.PERIOD_RULE,
        DueRuleKind.UNSUPPORTED: HoldReason.UNSUPPORTED_RULE,
    }[rule.kind]
    return DueDateResolution(None, False, reason)
