"""PROVISIONAL G1: 외부 쓰기 없는 담당별 페이지 초안."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from .constants import HOLD_REASON_LABELS
from .models import Applicability, ChecklistEntry, ChecklistSection, Role, RoleSections


class NotionBlockType(StrEnum):
    """노션 API 이전 중립 블록 종류(G1)."""

    HEADING = "heading"
    TOGGLE = "toggle"
    TO_DO = "to_do"
    PARAGRAPH = "paragraph"


@dataclass(frozen=True)
class NotionBlock:
    """텍스트와 자식 블록을 담은 불변 블록."""

    block_type: NotionBlockType
    text: str
    children: tuple[NotionBlock, ...] = ()


@dataclass(frozen=True)
class NotionPageDraft:
    """양식 순서 ID와 구간별 블록을 담은 페이지 초안."""

    hire_id: str
    role: Role
    title: str
    template_version: str
    today: date
    item_ids: tuple[str, ...]
    blocks: tuple[NotionBlock, ...]


def _entry_block(entry: ChecklistEntry) -> NotionBlock:
    """항목의 기준일·보류·완료 기준을 문단으로 만든다.

    Args:
        entry: 기존 계산 함수가 반환한 항목.

    Returns:
        세부 문단을 자식으로 가진 할 일 블록.
    """
    details = [f"기준일 표기: {entry.due_rule}"]
    if entry.due_date is not None:
        adjusted = " (주말 보정)" if entry.weekend_adjusted else ""
        details.append(f"기준일: {entry.due_date.isoformat()}{adjusted}")
    details.extend(f"보류: {HOLD_REASON_LABELS[reason]}" for reason in entry.hold_reasons)
    if entry.applicability == Applicability.NOT_APPLICABLE:
        details.append("해당 없음")
    details.append(f"완료 기준: {entry.completion_criteria}")
    if entry.collaborator.strip():
        details.append(f"함께: {entry.collaborator}")
    return NotionBlock(
        NotionBlockType.TO_DO,
        f"{entry.item_id} {entry.title}",
        tuple(NotionBlock(NotionBlockType.PARAGRAPH, text) for text in details),
    )


def _section_block(section: ChecklistSection) -> NotionBlock:
    """빈 구간도 유지하며 접힘 여부를 블록 종류로 표현한다.

    Args:
        section: 표시 순서로 분류된 구간.

    Returns:
        항목 블록을 담은 제목 또는 토글 블록.
    """
    return NotionBlock(
        NotionBlockType.TOGGLE if section.collapsed else NotionBlockType.HEADING,
        f"{section.kind} ({len(section.entries)}개)",
        tuple(_entry_block(entry) for entry in section.entries),
    )


def build_notion_page_draft(
    hire_id: str, template_version: str, role_sections: RoleSections
) -> NotionPageDraft:
    """담당별 구간을 쓰기 없는 중립 페이지 초안으로 바꾼다(G1·G5).

    Args:
        hire_id: 가상 입사자 식별자.
        template_version: 양식 판.
        role_sections: 양식 순서 ID와 날짜순 구간.

    Returns:
        인물 참조값을 포함하지 않는 불변 페이지 초안.
    """
    return NotionPageDraft(
        hire_id,
        role_sections.role,
        f"{hire_id} {role_sections.role} 준비 체크리스트",
        template_version,
        role_sections.sectioned.today,
        role_sections.item_ids,
        tuple(_section_block(section) for section in role_sections.sectioned.sections),
    )
