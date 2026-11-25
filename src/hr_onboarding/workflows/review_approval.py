"""산출물 검토·승인(HITL) 서브그래프와 실행 게이트.

PROVISIONAL: docs/contracts/review-approval.md 잠정 계약을 따른다. 팀 합의 전에는
공통 HR Schema/State로 쓰지 않는다. 검토 항목에는 본문·이름·연락처를 저장하지 않고
해시와 차이 요약만 남긴다. 외부 시스템은 호출하지 않는다.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, NotRequired, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, ConfigDict, Field

HR_ROLE = "인사 담당자"
LEADER_INPUT_NOTICE = "리더 제공 내용 포함, 출처 확인 필요"
COMMENT_MAX_LENGTH = 500

ArtifactType = Literal[
    "mail_1",
    "mail_2",
    "mail_3",
    "mail_4",
    "mail_5",
    "mail_6",
    "intro_chat",
    "leader_checklist",
    "staff_request",
    "account_request",
    "onboarding_plan",
]
DecisionAction = Literal["approve", "request_changes", "hold", "release"]
Event = Literal[
    "create", "submit", "approve", "request_changes", "hold", "release", "resubmit", "execute"
]

MANUAL_ACTIONS: frozenset[str] = frozenset(
    {"send_mail", "confirm_hire", "decide_hiring", "decide_regular_conversion"}
)
"""승인과 관계없이 담당자가 직접 수행하는 행위."""


class ReviewStatus(StrEnum):
    """검토 항목 상태."""

    DRAFT = "초안생성"
    PENDING = "검토대기"
    CHANGES_REQUESTED = "수정필요"
    APPROVED = "승인완료"
    ON_HOLD = "보류"


TRANSITIONS: dict[tuple[ReviewStatus, Event], ReviewStatus] = {
    (ReviewStatus.DRAFT, "submit"): ReviewStatus.PENDING,
    (ReviewStatus.PENDING, "approve"): ReviewStatus.APPROVED,
    (ReviewStatus.PENDING, "request_changes"): ReviewStatus.CHANGES_REQUESTED,
    (ReviewStatus.PENDING, "hold"): ReviewStatus.ON_HOLD,
    (ReviewStatus.CHANGES_REQUESTED, "resubmit"): ReviewStatus.PENDING,
    (ReviewStatus.ON_HOLD, "release"): ReviewStatus.PENDING,
    (ReviewStatus.APPROVED, "resubmit"): ReviewStatus.PENDING,
}
"""허용 전이표. 여기에 없는 전이는 InvalidTransition으로 거부한다."""


class ReviewError(Exception):
    """검토·승인 오류의 기본 클래스."""


class InvalidTransition(ReviewError):
    """허용되지 않은 상태 전이."""


class UnauthorizedReviewer(ReviewError):
    """검토 결정 권한이 없는 역할."""


class NotApproved(ReviewError):
    """승인되지 않았거나 승인 뒤 내용이 바뀐 항목의 실행 시도."""


class ManualActionRequired(ReviewError):
    """자동 실행하지 않고 담당자가 직접 해야 하는 행위."""


class AlreadyExecuted(ReviewError):
    """이미 실행 완료된 항목의 중복 실행 시도."""


class MismatchedDraft(ReviewError):
    """다른 입사자·산출물 종류의 초안으로 기존 항목을 다시 올리려는 시도."""


class TemplateRef(BaseModel):
    """원본 양식 위치(데이터팩 경로·절·버전)."""

    file: str = Field(min_length=1)
    section: str = Field(min_length=1)
    version: str = Field(min_length=1)


class DraftContent(BaseModel):
    """검토할 초안 내용. 받는 사람은 주소가 아니라 역할로만 적는다."""

    subject: str | None = None
    to_role: str | None = None
    cc_role: str | None = None
    body: str = Field(min_length=1)


class Draft(BaseModel):
    """다른 서브에이전트가 검토를 요청하는 초안."""

    hire_ref: str = Field(min_length=1)
    artifact_type: ArtifactType
    related_checklist_ids: list[str] = Field(default_factory=list[str])
    template_ref: TemplateRef
    source_text: str | None = None
    content: DraftContent
    contains_leader_input: bool = False

    def model_post_init(self, context: Any, /) -> None:
        """체크리스트 ID 형식(ON-두 자리)을 확인한다.

        Raises:
            ValueError: 형식이 맞지 않는 ID가 있을 때.
        """
        for checklist_id in self.related_checklist_ids:
            number = checklist_id.removeprefix("ON-")
            if not (checklist_id.startswith("ON-") and len(number) == 2 and number.isdigit()):
                raise ValueError(f"invalid checklist id: {checklist_id}")


class ComparisonSummary(BaseModel):
    """원본 양식 대비 초안 차이 요약. 본문 문장은 담지 않는다."""

    template_missing: bool
    added_lines: int = 0
    removed_lines: int = 0
    notices: list[str] = Field(default_factory=list[str])


class ReviewDecision(BaseModel):
    """사람의 검토 결정(interrupt 재개 값).

    comment에는 이름·연락처·처우를 쓰지 않고 수정할 칸과 이유만 적는다(계약 문서 규칙).
    """

    action: DecisionAction
    reviewer_role: str = Field(min_length=1)
    comment: str = Field(default="", max_length=COMMENT_MAX_LENGTH)


class Feedback(BaseModel):
    """검토 의견 기록."""

    action: DecisionAction
    reviewer_role: str
    comment: str
    draft_version: int
    at: datetime


class HistoryEntry(BaseModel):
    """상태 전이 기록. 본문은 남기지 않는다."""

    from_status: ReviewStatus | None
    to_status: ReviewStatus
    event: Event
    actor_role: str
    at: datetime


class ReviewItem(BaseModel):
    """검토 대기열의 항목. 불변이며 바꿀 때는 model_copy로 새 객체를 만든다."""

    model_config = ConfigDict(frozen=True)

    item_id: str
    hire_ref: str
    artifact_type: ArtifactType
    related_checklist_ids: list[str]
    template_ref: TemplateRef
    draft_version: int
    content_hash: str
    status: ReviewStatus
    comparison_summary: ComparisonSummary
    reviewer_role: str = HR_ROLE
    feedback: list[Feedback] = Field(default_factory=list[Feedback])
    approved_hash: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    executed_at: datetime | None = None
    history: list[HistoryEntry] = Field(default_factory=list[HistoryEntry])


def _now() -> datetime:
    """현재 시각(UTC)을 돌려준다. 표시할 때 KST로 바꾼다."""
    return datetime.now(UTC)


def content_hash(content: DraftContent) -> str:
    """초안 내용의 SHA-256 해시를 만든다.

    Args:
        content: 초안 내용.

    Returns:
        16진수 해시 문자열.
    """
    payload = json.dumps(content.model_dump(), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def summarize_comparison(draft: Draft) -> ComparisonSummary:
    """원본 양식과 초안 본문의 줄 단위 차이를 센다.

    Args:
        draft: 검토 요청 초안.

    Returns:
        추가·삭제 줄 수와 검토자 주의 문구.
    """
    notices = [LEADER_INPUT_NOTICE] if draft.contains_leader_input else []
    if draft.source_text is None:
        return ComparisonSummary(template_missing=True, notices=notices)
    added = removed = 0
    for line in difflib.ndiff(draft.source_text.splitlines(), draft.content.body.splitlines()):
        if line.startswith("+ "):
            added += 1
        elif line.startswith("- "):
            removed += 1
    return ComparisonSummary(
        template_missing=False, added_lines=added, removed_lines=removed, notices=notices
    )


def _transition(item: ReviewItem, event: Event, actor_role: str, at: datetime) -> ReviewItem:
    """전이표에 따라 상태를 바꾸고 기록을 남긴다.

    Raises:
        InvalidTransition: 전이표에 없는 전이일 때.
    """
    target = TRANSITIONS.get((item.status, event))
    if target is None:
        raise InvalidTransition(f"{item.status.value} --{event}--> 허용되지 않음")
    entry = HistoryEntry(
        from_status=item.status, to_status=target, event=event, actor_role=actor_role, at=at
    )
    return item.model_copy(update={"status": target, "history": [*item.history, entry]})


def submit_for_review(draft: Draft, *, now: datetime | None = None) -> ReviewItem:
    """초안을 검토 항목으로 만들고 차이 요약 뒤 검토대기로 올린다.

    Args:
        draft: 검토 요청 초안.
        now: 기록 시각. 테스트에서 고정할 때 쓴다.

    Returns:
        검토대기 상태의 항목.
    """
    at = now or _now()
    created = HistoryEntry(
        from_status=None, to_status=ReviewStatus.DRAFT, event="create", actor_role="system", at=at
    )
    item = ReviewItem(
        item_id=f"{draft.hire_ref}:{draft.artifact_type}",
        hire_ref=draft.hire_ref,
        artifact_type=draft.artifact_type,
        related_checklist_ids=list(draft.related_checklist_ids),
        template_ref=draft.template_ref,
        draft_version=1,
        content_hash=content_hash(draft.content),
        status=ReviewStatus.DRAFT,
        comparison_summary=summarize_comparison(draft),
        history=[created],
    )
    return _transition(item, "submit", "system", at)


def apply_decision(
    item: ReviewItem, decision: ReviewDecision, *, now: datetime | None = None
) -> ReviewItem:
    """사람의 검토 결정을 반영한다.

    Args:
        item: 검토 항목.
        decision: 승인·수정 요청·보류·보류 해제 결정.
        now: 기록 시각.

    Returns:
        결정이 반영된 항목.

    Raises:
        UnauthorizedReviewer: 인사 담당자가 아닌 역할의 결정일 때.
        InvalidTransition: 현재 상태에서 할 수 없는 결정일 때.
    """
    if decision.reviewer_role != item.reviewer_role:
        raise UnauthorizedReviewer(f"{decision.reviewer_role}는 검토 결정 권한이 없음")
    at = now or _now()
    updated = _transition(item, decision.action, decision.reviewer_role, at)
    feedback = Feedback(
        action=decision.action,
        reviewer_role=decision.reviewer_role,
        comment=decision.comment,
        draft_version=item.draft_version,
        at=at,
    )
    changes: dict[str, object] = {"feedback": [*item.feedback, feedback]}
    if decision.action == "approve":
        changes |= {
            "approved_hash": item.content_hash,
            "approved_by": decision.reviewer_role,
            "approved_at": at,
        }
    return updated.model_copy(update=changes)


def resubmit(item: ReviewItem, draft: Draft, *, now: datetime | None = None) -> ReviewItem:
    """수정한 초안을 다시 검토대기로 올린다. 승인 뒤 내용이 바뀌면 재승인을 요구한다.

    Args:
        item: 수정필요 또는 승인완료 항목.
        draft: 새 초안.
        now: 기록 시각.

    Returns:
        새 버전으로 검토대기 상태가 된 항목. 승인완료이고 내용이 같으면 그대로 돌려준다.
        실행 완료 기록은 지워 다시 대기열에 보이게 한다.

    Raises:
        MismatchedDraft: 입사자 참조 키나 산출물 종류가 기존 항목과 다를 때.
        InvalidTransition: 다시 올릴 수 없는 상태(검토대기·보류)일 때.
    """
    if (draft.hire_ref, draft.artifact_type) != (item.hire_ref, item.artifact_type):
        raise MismatchedDraft(f"{item.item_id}: 다른 항목의 초안")
    new_hash = content_hash(draft.content)
    if item.status is ReviewStatus.APPROVED and new_hash == item.approved_hash:
        return item
    updated = _transition(item, "resubmit", "system", now or _now())
    return updated.model_copy(
        update={
            "draft_version": item.draft_version + 1,
            "content_hash": new_hash,
            "related_checklist_ids": list(draft.related_checklist_ids),
            "template_ref": draft.template_ref,
            "comparison_summary": summarize_comparison(draft),
            "approved_hash": None,
            "approved_by": None,
            "approved_at": None,
            "executed_at": None,
        }
    )


def _check_approved(item: ReviewItem, content: DraftContent, action: str) -> None:
    """저장된 항목 기준으로 실행 가능 여부를 확인한다.

    Raises:
        ManualActionRequired: 메일 발송·입사 확정 등 사람이 직접 해야 하는 행위일 때.
        NotApproved: 승인완료가 아니거나 승인 뒤 내용이 바뀌었을 때.
        AlreadyExecuted: 이미 실행 완료된 항목일 때.
    """
    if action in MANUAL_ACTIONS:
        raise ManualActionRequired(f"{action}은 담당자가 직접 수행")
    if item.status is not ReviewStatus.APPROVED:
        raise NotApproved(f"{item.item_id}: {item.status.value}")
    if content_hash(content) != item.approved_hash:
        raise NotApproved(f"{item.item_id}: 승인 뒤 내용 변경")
    if item.executed_at is not None:
        raise AlreadyExecuted(f"{item.item_id}: 이미 실행됨")


def mark_executed(item: ReviewItem, *, now: datetime | None = None) -> ReviewItem:
    """승인된 항목의 실행(수동 포함) 완료를 기록한다.

    Args:
        item: 승인완료 항목.
        now: 실행 완료 시각.

    Returns:
        executed_at이 기록된 항목. 이미 기록돼 있으면 그대로 돌려준다(멱등).

    Raises:
        NotApproved: 승인완료가 아닐 때.
    """
    if item.status is not ReviewStatus.APPROVED:
        raise NotApproved(f"{item.item_id}: {item.status.value}")
    if item.executed_at is not None:
        return item
    at = now or _now()
    entry = HistoryEntry(
        from_status=item.status, to_status=item.status, event="execute", actor_role="system", at=at
    )
    return item.model_copy(update={"executed_at": at, "history": [*item.history, entry]})


class ReviewQueue:
    """메모리 검토 대기열과 실행 게이트.

    항목은 이 대기열의 메서드로만 바뀐다. 게이트는 호출자가 넘긴 객체가 아니라
    저장된 항목을 item_id로 찾아 판단한다. 영속화 방식은 팀 합의 전이라 테스트·데모 용도다.
    """

    def __init__(self) -> None:
        """빈 대기열을 만든다."""
        self._items: dict[str, ReviewItem] = {}

    def submit(self, draft: Draft, *, now: datetime | None = None) -> ReviewItem:
        """초안을 올린다. 같은 항목·같은 내용이면 기존 항목을 돌려준다.

        Args:
            draft: 검토 요청 초안.
            now: 기록 시각.

        Returns:
            대기열의 항목.

        Raises:
            InvalidTransition: 검토대기·보류 중인 항목에 다른 내용을 올릴 때
                (PROVISIONAL: 거부. 버전 교체 여부는 팀 판단).
        """
        item_id = f"{draft.hire_ref}:{draft.artifact_type}"
        existing = self._items.get(item_id)
        if existing is None:
            item = submit_for_review(draft, now=now)
        elif existing.content_hash == content_hash(draft.content):
            return existing
        else:
            item = resubmit(existing, draft, now=now)
        self._items[item_id] = item
        return item

    def decide(
        self, item_id: str, decision: ReviewDecision, *, now: datetime | None = None
    ) -> ReviewItem:
        """저장된 항목에 사람의 검토 결정을 반영한다.

        Args:
            item_id: 항목 ID.
            decision: 검토 결정.
            now: 기록 시각.

        Returns:
            결정이 반영된 항목.

        Raises:
            KeyError: 없는 항목일 때.
            UnauthorizedReviewer: 권한 없는 역할의 결정일 때.
            InvalidTransition: 현재 상태에서 할 수 없는 결정일 때.
        """
        item = apply_decision(self._items[item_id], decision, now=now)
        self._items[item_id] = item
        return item

    def require_approved(self, item_id: str, content: DraftContent, *, action: str) -> None:
        """외부 시스템 등록·수정 전에 승인 여부를 확인하는 게이트.

        Args:
            item_id: 항목 ID.
            content: 실제로 실행에 쓰려는 내용.
            action: 실행하려는 행위 이름.

        Raises:
            ManualActionRequired: 메일 발송·입사 확정 등 사람이 직접 해야 하는 행위일 때.
            NotApproved: 없는 항목이거나, 승인완료가 아니거나, 승인 뒤 내용이 바뀌었을 때.
            AlreadyExecuted: 이미 실행 완료된 항목일 때.
        """
        item = self._items.get(item_id)
        if item is None:
            if action in MANUAL_ACTIONS:
                raise ManualActionRequired(f"{action}은 담당자가 직접 수행")
            raise NotApproved(f"{item_id}: 검토 대기열에 없음")
        _check_approved(item, content, action)

    def mark_executed(self, item_id: str, *, now: datetime | None = None) -> ReviewItem:
        """저장된 승인 항목의 실행 완료를 기록한다(멱등).

        Args:
            item_id: 항목 ID.
            now: 실행 완료 시각.

        Returns:
            executed_at이 기록된 항목.

        Raises:
            KeyError: 없는 항목일 때.
            NotApproved: 승인완료가 아닐 때.
        """
        item = mark_executed(self._items[item_id], now=now)
        self._items[item_id] = item
        return item

    def get(self, item_id: str) -> ReviewItem:
        """항목을 찾는다.

        Raises:
            KeyError: 없는 항목일 때.
        """
        return self._items[item_id]

    def pending(self) -> list[ReviewItem]:
        """실행 완료되지 않은 항목을 돌려준다."""
        return [item for item in self._items.values() if item.executed_at is None]


class ReviewGraphState(TypedDict):
    """검토 서브그래프 State(PROVISIONAL, 공통 State 아님)."""

    draft: dict[str, Any]
    item: NotRequired[dict[str, Any]]


def _state_item(state: ReviewGraphState) -> dict[str, Any]:
    """State에서 검토 항목을 꺼낸다.

    Raises:
        KeyError: prepare 노드 전에 호출됐을 때.
    """
    item = state.get("item")
    if item is None:
        raise KeyError("item")
    return item


def review_request(item: ReviewItem) -> dict[str, Any]:
    """담당자에게 보여 줄 검토 요청을 만든다.

    Args:
        item: 검토 항목.

    Returns:
        항목·상태·차이 요약·후속 제안.
    """
    suggestions = ["원본 양식과 바뀐 칸을 확인하세요."]
    if item.artifact_type == "account_request":
        suggestions.append("신청 권한이 직무에 맞고 넘치지 않는지 확인하세요.")
    suggestions.extend(item.comparison_summary.notices)
    return {
        "item_id": item.item_id,
        "artifact_type": item.artifact_type,
        "status": item.status.value,
        "draft_version": item.draft_version,
        "related_checklist_ids": item.related_checklist_ids,
        "comparison_summary": item.comparison_summary.model_dump(),
        "reviewer_role": item.reviewer_role,
        "suggestions": suggestions,
    }


def build_review_graph(
    checkpointer: BaseCheckpointSaver[Any],
    *,
    queue: ReviewQueue,
    now: Callable[[], datetime] = _now,
) -> CompiledStateGraph[ReviewGraphState, None, ReviewGraphState, ReviewGraphState]:
    """초안 등록 → 사람 결정 대기 → 결과 반환 서브그래프를 만든다.

    등록 직후와 결정 뒤 모두, 승인완료·수정필요면 끝내고 보류·검토대기면 사람 결정을 기다린다.
    같은 내용으로 다시 요청하면 기존 결과를 바로 돌려준다.
    항목은 queue에 저장되며, 외부 실행 전에는 같은 queue의 require_approved로 확인한다.

    제약: queue는 메모리 대기열이다. 영속 checkpointer와 함께 쓰다 프로세스가 재시작되면
    대기열이 비어 재개 시 KeyError가 난다. 영속화 방식은 팀 합의 전이다.

    Args:
        checkpointer: interrupt 재개에 필요한 체크포인터.
        queue: 검토 대기열. 게이트와 같은 객체를 넘긴다.
        now: 기록 시각 함수.

    Returns:
        컴파일된 그래프.
    """
    review_queue = queue

    def prepare(state: ReviewGraphState) -> dict[str, Any]:
        draft = Draft.model_validate(state["draft"])
        return {"item": review_queue.submit(draft, now=now()).model_dump(mode="json")}

    def await_review(state: ReviewGraphState) -> dict[str, Any]:
        item = review_queue.get(_state_item(state)["item_id"])
        decision = ReviewDecision.model_validate(interrupt(review_request(item)))
        updated = review_queue.decide(item.item_id, decision, now=now())
        return {"item": updated.model_dump(mode="json")}

    def route(state: ReviewGraphState) -> str:
        status = ReviewStatus(_state_item(state)["status"])
        if status in {ReviewStatus.APPROVED, ReviewStatus.CHANGES_REQUESTED}:
            return END
        return "await_review"

    builder = StateGraph(ReviewGraphState)
    builder.add_node("prepare", prepare)
    builder.add_node("await_review", await_review)
    builder.add_edge(START, "prepare")
    builder.add_conditional_edges("prepare", route, ["await_review", END])
    builder.add_conditional_edges("await_review", route, ["await_review", END])
    return builder.compile(checkpointer=checkpointer)
