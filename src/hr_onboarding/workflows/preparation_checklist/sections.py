"""기준 날짜에 따른 여섯 표시 구간 분류."""

from collections.abc import Sequence
from datetime import date, timedelta

from .constants import COLLAPSED_SECTIONS, WEEK_START_WEEKDAY
from .models import (
    Applicability,
    ChecklistEntry,
    ChecklistSection,
    SectionedChecklist,
    SectionKind,
)


def split_into_sections(entries: Sequence[ChecklistEntry], today: date) -> SectionedChecklist:
    """해당 없음·보류 우선순위와 날짜 경계로 항목을 나눈다.

    Args:
        entries: 날짜 누락 시 보류 사유가 있는 항목 목록.
        today: 호출자가 KST로 변환한 기준 날짜(P3).

    Returns:
        날짜순으로 정렬한 여섯 구간. 같은 날짜와 날짜 없는 항목은 입력 순서다.

    Raises:
        ValueError: 해당 없음이 아닌 항목에 날짜와 보류 사유가 모두 없는 경우.
    """
    week_start = today - timedelta(days=(today.weekday() - WEEK_START_WEEKDAY) % 7)
    week_end = week_start + timedelta(days=6)
    next_week_end = week_end + timedelta(days=7)
    grouped: dict[SectionKind, list[ChecklistEntry]] = {kind: [] for kind in SectionKind}
    for entry in entries:
        if entry.applicability == Applicability.NOT_APPLICABLE:
            kind = SectionKind.NOT_APPLICABLE
        elif entry.hold_reasons:
            kind = SectionKind.ON_HOLD
        elif entry.due_date is None:
            raise ValueError("해당 없음이 아닌 항목에는 날짜 또는 보류 사유가 필요합니다")
        elif entry.due_date < today:
            kind = SectionKind.OVERDUE
        elif entry.due_date <= week_end:
            kind = SectionKind.THIS_WEEK
        elif entry.due_date <= next_week_end:
            kind = SectionKind.NEXT_WEEK
        else:
            kind = SectionKind.LATER
        grouped[kind].append(entry)
    return SectionedChecklist(
        today,
        tuple(
            ChecklistSection(
                kind,
                tuple(
                    sorted(
                        grouped[kind], key=lambda e: (e.due_date is None, e.due_date or date.max)
                    )
                ),
                kind in COLLAPSED_SECTIONS,
            )
            for kind in SectionKind
        ),
    )
