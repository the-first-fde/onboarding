"""입력 검증부터 담당별 페이지 초안까지 연결하는 로컬 그래프."""

from datetime import date
from enum import StrEnum
from typing import Required, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .builder import build_preparation_checklist
from .models import (
    ChecklistTemplate,
    InputHoldReason,
    NewHire,
    PreparationChecklist,
    RoleSections,
)
from .notion_draft import NotionPageDraft, build_notion_page_draft
from .request import PageHold, PreparationRequest, validate_request
from .sections import split_into_sections


class GraphOutcome(StrEnum):
    """전체 보류 또는 페이지 초안 생성 결과."""

    DRAFTED = "DRAFTED"
    ON_HOLD = "ON_HOLD"


class PreparationState(TypedDict, total=False):
    """이 워크플로 안에서만 사용하는 잠정 상태(G2)."""

    request: Required[PreparationRequest]
    template: Required[ChecklistTemplate | None]
    today: Required[date | None]
    hire: NewHire
    input_hold_reasons: tuple[InputHoldReason, ...]
    page_holds: tuple[PageHold, ...]
    outcome: GraphOutcome
    checklist: PreparationChecklist
    role_sections: tuple[RoleSections, ...]
    page_drafts: tuple[NotionPageDraft, ...]


class PreparationUpdate(TypedDict, total=False):
    """입력을 제외한 부분 갱신의 키와 값을 정적 검사한다."""

    hire: NewHire
    input_hold_reasons: tuple[InputHoldReason, ...]
    page_holds: tuple[PageHold, ...]
    outcome: GraphOutcome
    checklist: PreparationChecklist
    role_sections: tuple[RoleSections, ...]
    page_drafts: tuple[NotionPageDraft, ...]


def _require[T](value: T | None) -> T:
    """후속 노드가 사용하는 상태 값의 타입을 좁힌다.

    Args:
        value: 이전 단계에서 준비한 상태 값.

    Returns:
        None이 아닌 상태 값.

    Raises:
        ValueError: 이전 단계의 상태 값이 없는 경우.
    """
    if value is None:
        raise ValueError("이전 단계의 상태 값이 필요합니다")
    return value


def validate_input(state: PreparationState) -> PreparationUpdate:
    """입력 누락을 전체·페이지 보류로 구분한다(G3·G6).

    Args:
        state: 요청·양식·기준 날짜가 있는 입력 상태.

    Returns:
        검증된 입사자 또는 전체 보류 결과와 보류 사유.
    """
    result = validate_request(state["request"], state["template"], state["today"])
    if result.hire is None:
        return {
            "input_hold_reasons": result.hold_reasons,
            "page_holds": result.page_holds,
            "outcome": GraphOutcome.ON_HOLD,
        }
    return {"hire": result.hire, "input_hold_reasons": (), "page_holds": result.page_holds}


def route_after_validation(state: PreparationState) -> str:
    """전체 보류 시 종료하고 그 외에는 목록 생성으로 이동한다.

    Args:
        state: 입력 검증 결과.

    Returns:
        종료 또는 목록 생성 노드 이름.
    """
    return END if _require(state.get("input_hold_reasons")) else "build_checklist"


def build_checklist(state: PreparationState) -> PreparationUpdate:
    """검증된 입력으로 기존 목록 생성 함수를 호출한다.

    Args:
        state: 검증된 입사자와 양식.

    Returns:
        담당별 준비 목록.

    Raises:
        ValueError: 양식이 없거나 기존 함수가 양식 결함을 발견한 경우.
    """
    return {
        "checklist": build_preparation_checklist(
            _require(state.get("hire")), _require(state["template"])
        )
    }


def split_sections(state: PreparationState) -> PreparationUpdate:
    """양식 순서 ID를 보존하며 담당별 표시 구간을 만든다.

    Args:
        state: 담당별 목록과 기준 날짜.

    Returns:
        리더·총무·버디 순서의 구간 결과.

    Raises:
        ValueError: 검증된 기준 날짜가 없는 경우.
    """
    today = _require(state["today"])
    checklist = _require(state.get("checklist"))
    return {
        "role_sections": tuple(
            RoleSections(
                roles.role,
                tuple(entry.item_id for entry in roles.entries),
                split_into_sections(roles.entries, today),
            )
            for roles in checklist.role_checklists
        )
    }


def draft_pages(state: PreparationState) -> PreparationUpdate:
    """보류된 담당을 제외하고 페이지 초안을 만든다(G1·G3).

    Args:
        state: 목록·구간·페이지 보류 결과.

    Returns:
        생성된 페이지와 초안 완료 상태.
    """
    held_roles = {hold.role for hold in _require(state.get("page_holds"))}
    checklist = _require(state.get("checklist"))
    return {
        "page_drafts": tuple(
            build_notion_page_draft(checklist.hire_id, checklist.template_version, roles)
            for roles in _require(state.get("role_sections"))
            if roles.role not in held_roles
        ),
        "outcome": GraphOutcome.DRAFTED,
    }


def build_preparation_graph() -> CompiledStateGraph[
    PreparationState, None, PreparationState, PreparationState
]:
    """외부 호출과 체크포인터 없이 네 단계 그래프를 조립한다(G4).

    Returns:
        입력 검증에서 페이지 초안까지 실행하는 컴파일된 그래프.
    """
    builder = StateGraph(PreparationState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("build_checklist", build_checklist)
    builder.add_node("split_sections", split_sections)
    builder.add_node("draft_pages", draft_pages)
    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges(
        "validate_input", route_after_validation, {END: END, "build_checklist": "build_checklist"}
    )
    builder.add_edge("build_checklist", "split_sections")
    builder.add_edge("split_sections", "draft_pages")
    builder.add_edge("draft_pages", END)
    return builder.compile()
