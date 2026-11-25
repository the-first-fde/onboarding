"""검토·승인(HITL) 잠정 계약의 상태 전이와 실행 게이트를 검증한다.

모든 입력은 테스트 안에서 만든 가상 값이다. 고객사 원문, 실제 이름·연락처는 쓰지 않는다.
계약: docs/contracts/review-approval.md (PROVISIONAL).
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from pydantic import ValidationError

from hr_onboarding.workflows.review_approval import (
    LEADER_INPUT_NOTICE,
    AlreadyExecuted,
    DecisionAction,
    Draft,
    DraftContent,
    InvalidTransition,
    ManualActionRequired,
    MismatchedDraft,
    NotApproved,
    ReviewDecision,
    ReviewItem,
    ReviewQueue,
    ReviewStatus,
    TemplateRef,
    UnauthorizedReviewer,
    apply_decision,
    build_review_graph,
    content_hash,
    mark_executed,
    resubmit,
    review_request,
    submit_for_review,
)

FIXED_NOW = datetime(2026, 11, 25, 5, 0, tzinfo=UTC)
SOURCE_TEXT = "안녕하세요, {입사자}님.\n첫 출근 일정을 안내드립니다.\n감사합니다."
DRAFT_BODY = (
    "안녕하세요, 가상입사자님.\n첫 출근 일정을 안내드립니다.\n준비물을 챙겨 주세요.\n감사합니다."
)
WRITE_ACTION = "register_notion_row"


def make_draft(body: str = DRAFT_BODY, **overrides: Any) -> Draft:
    """가상 메일 초안을 만든다.

    Args:
        body: 초안 본문.
        **overrides: 바꿀 필드.

    Returns:
        검토 요청용 가상 초안.
    """
    values: dict[str, object] = {
        "hire_ref": "H-TEST-01",
        "artifact_type": "mail_3",
        "related_checklist_ids": ["ON-10"],
        "template_ref": TemplateRef(file="06_입사_안내메일.md", section="메일 3", version="v3.2"),
        "source_text": SOURCE_TEXT,
        "content": DraftContent(
            subject="[첫 출근 안내] 가상 일정",
            to_role="입사자",
            cc_role="리더",
            body=body,
        ),
    }
    values.update(overrides)
    return Draft.model_validate(values)


def hr_decision(action: DecisionAction, comment: str = "") -> ReviewDecision:
    """인사 담당자의 검토 결정을 만든다."""
    return ReviewDecision(action=action, reviewer_role="인사 담당자", comment=comment)


def approved_item() -> ReviewItem:
    """승인완료 상태의 검토 항목을 만든다."""
    item = submit_for_review(make_draft(), now=FIXED_NOW)
    return apply_decision(item, hr_decision("approve"), now=FIXED_NOW)


def approved_queue() -> tuple[ReviewQueue, str]:
    """승인완료 항목 하나가 든 대기열을 만든다."""
    queue = ReviewQueue()
    item = queue.submit(make_draft(), now=FIXED_NOW)
    queue.decide(item.item_id, hr_decision("approve"), now=FIXED_NOW)
    return queue, item.item_id


# 상태 전이


def test_submit_moves_to_pending_with_comparison_summary() -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)

    assert item.status is ReviewStatus.PENDING
    assert item.draft_version == 1
    assert item.content_hash == content_hash(make_draft().content)
    assert item.comparison_summary.added_lines == 2
    assert item.comparison_summary.removed_lines == 1
    assert item.comparison_summary.template_missing is False
    assert [h.to_status for h in item.history] == [ReviewStatus.DRAFT, ReviewStatus.PENDING]


def test_missing_source_text_is_flagged() -> None:
    item = submit_for_review(make_draft(source_text=None), now=FIXED_NOW)

    assert item.comparison_summary.template_missing is True


def test_leader_input_is_flagged_for_source_check() -> None:
    draft = make_draft(artifact_type="intro_chat", contains_leader_input=True)

    item = submit_for_review(draft, now=FIXED_NOW)

    assert LEADER_INPUT_NOTICE in item.comparison_summary.notices
    assert LEADER_INPUT_NOTICE in review_request(item)["suggestions"]


def test_account_request_suggests_permission_scope_check() -> None:
    item = submit_for_review(make_draft(artifact_type="account_request"), now=FIXED_NOW)

    assert any("권한" in s for s in review_request(item)["suggestions"])


def test_history_does_not_store_body_text() -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)

    dumped = item.model_dump_json()
    assert "가상입사자" not in dumped
    assert "준비물" not in dumped


@pytest.mark.parametrize(
    "overrides",
    [
        {"artifact_type": "unknown_mail"},
        {"related_checklist_ids": ["ON-1"]},
        {"hire_ref": ""},
    ],
)
def test_invalid_draft_is_rejected(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        make_draft(**overrides)


def test_too_long_comment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        hr_decision("request_changes", "가" * 501)


def test_hr_approval_completes_item() -> None:
    item = approved_item()

    assert item.status is ReviewStatus.APPROVED
    assert item.approved_hash == item.content_hash
    assert item.approved_by == "인사 담당자"
    assert item.approved_at == FIXED_NOW


@pytest.mark.parametrize("role", ["리더", "버디", "경영지원 담당"])
def test_only_hr_can_approve(role: str) -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)

    with pytest.raises(UnauthorizedReviewer):
        apply_decision(item, ReviewDecision(action="approve", reviewer_role=role), now=FIXED_NOW)


def test_request_changes_then_resubmit_returns_to_pending() -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)

    item = apply_decision(item, hr_decision("request_changes", "준비물 문구 수정"), now=FIXED_NOW)
    assert item.status is ReviewStatus.CHANGES_REQUESTED
    assert item.feedback[-1].comment == "준비물 문구 수정"

    new_draft = make_draft(
        body=DRAFT_BODY + "\n추가 안내", related_checklist_ids=["ON-10", "ON-19"]
    )
    item = resubmit(item, new_draft, now=FIXED_NOW)
    assert item.status is ReviewStatus.PENDING
    assert item.draft_version == 2
    assert item.related_checklist_ids == ["ON-10", "ON-19"]


def test_resubmit_rejects_draft_for_other_item() -> None:
    item = apply_decision(
        submit_for_review(make_draft(), now=FIXED_NOW), hr_decision("request_changes")
    )

    with pytest.raises(MismatchedDraft):
        resubmit(item, make_draft(hire_ref="H-TEST-02"), now=FIXED_NOW)


def test_hold_then_release_returns_to_pending() -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)

    item = apply_decision(item, hr_decision("hold", "서류 미제출"), now=FIXED_NOW)
    assert item.status is ReviewStatus.ON_HOLD

    item = apply_decision(item, hr_decision("release"), now=FIXED_NOW)
    assert item.status is ReviewStatus.PENDING


def test_invalid_transition_is_rejected() -> None:
    item = submit_for_review(make_draft(), now=FIXED_NOW)
    item = apply_decision(item, hr_decision("request_changes"), now=FIXED_NOW)

    with pytest.raises(InvalidTransition):
        apply_decision(item, hr_decision("approve"), now=FIXED_NOW)


def test_changed_content_after_approval_needs_reapproval() -> None:
    item = approved_item()

    item = resubmit(item, make_draft(body="바뀐 본문"), now=FIXED_NOW)

    assert item.status is ReviewStatus.PENDING
    assert item.approved_hash is None


def test_same_content_after_approval_keeps_approval() -> None:
    item = approved_item()

    assert resubmit(item, make_draft(), now=FIXED_NOW) == item


def test_mark_executed_requires_approval_and_is_idempotent() -> None:
    with pytest.raises(NotApproved):
        mark_executed(submit_for_review(make_draft(), now=FIXED_NOW), now=FIXED_NOW)

    once = mark_executed(approved_item(), now=FIXED_NOW)
    assert mark_executed(once, now=FIXED_NOW) == once


# 대기열과 실행 게이트


def test_gate_passes_only_for_approved_same_content() -> None:
    queue, item_id = approved_queue()

    queue.require_approved(item_id, make_draft().content, action=WRITE_ACTION)


def test_gate_blocks_unapproved_item() -> None:
    queue = ReviewQueue()
    item = queue.submit(make_draft(), now=FIXED_NOW)

    with pytest.raises(NotApproved):
        queue.require_approved(item.item_id, make_draft().content, action=WRITE_ACTION)


def test_gate_blocks_unknown_item() -> None:
    with pytest.raises(NotApproved):
        ReviewQueue().require_approved(
            "H-TEST-01:mail_3", make_draft().content, action=WRITE_ACTION
        )


def test_gate_ignores_forged_item_objects() -> None:
    queue = ReviewQueue()
    item = queue.submit(make_draft(), now=FIXED_NOW)
    forged = approved_item()  # 대기열 밖에서 만든 승인 객체
    assert forged.item_id == item.item_id

    with pytest.raises(NotApproved):
        queue.require_approved(item.item_id, make_draft().content, action=WRITE_ACTION)


def test_gate_blocks_changed_content() -> None:
    queue, item_id = approved_queue()

    with pytest.raises(NotApproved):
        queue.require_approved(
            item_id, make_draft(body="몰래 바뀐 본문").content, action=WRITE_ACTION
        )


def test_gate_blocks_already_executed_item() -> None:
    queue, item_id = approved_queue()
    queue.mark_executed(item_id, now=FIXED_NOW)

    with pytest.raises(AlreadyExecuted):
        queue.require_approved(item_id, make_draft().content, action=WRITE_ACTION)


@pytest.mark.parametrize(
    "action", ["send_mail", "confirm_hire", "decide_hiring", "decide_regular_conversion"]
)
def test_manual_actions_are_never_automated(action: str) -> None:
    queue, item_id = approved_queue()

    with pytest.raises(ManualActionRequired):
        queue.require_approved(item_id, make_draft().content, action=action)


def test_queue_removes_executed_items_and_dedupes() -> None:
    queue = ReviewQueue()
    first = queue.submit(make_draft(), now=FIXED_NOW)
    again = queue.submit(make_draft(), now=FIXED_NOW)
    assert again.item_id == first.item_id
    assert len(queue.pending()) == 1

    queue.decide(first.item_id, hr_decision("approve"), now=FIXED_NOW)
    assert len(queue.pending()) == 1

    queue.mark_executed(first.item_id, now=FIXED_NOW)
    assert queue.pending() == []


def test_changed_content_after_execution_returns_to_queue() -> None:
    queue, item_id = approved_queue()
    queue.mark_executed(item_id, now=FIXED_NOW)

    item = queue.submit(make_draft(body="실행 뒤 바뀐 본문"), now=FIXED_NOW)

    assert item.status is ReviewStatus.PENDING
    assert item.executed_at is None
    assert [i.item_id for i in queue.pending()] == [item_id]


@pytest.mark.parametrize("action", ["hold", None])
def test_new_content_while_pending_or_on_hold_is_rejected(action: DecisionAction | None) -> None:
    queue = ReviewQueue()
    item = queue.submit(make_draft(), now=FIXED_NOW)
    if action is not None:
        queue.decide(item.item_id, hr_decision(action), now=FIXED_NOW)

    with pytest.raises(InvalidTransition):
        queue.submit(make_draft(body="검토 중에 바뀐 본문"), now=FIXED_NOW)


# 사람 결정 대기 그래프


def start_graph(queue: ReviewQueue, thread_id: str) -> tuple[Any, RunnableConfig]:
    """그래프를 만들고 첫 interrupt까지 실행한다."""
    graph = build_review_graph(MemorySaver(), queue=queue, now=lambda: FIXED_NOW)
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"draft": make_draft().model_dump(mode="json")}, config)
    return graph, config


def test_graph_waits_for_human_then_approves() -> None:
    queue = ReviewQueue()
    graph = build_review_graph(MemorySaver(), queue=queue, now=lambda: FIXED_NOW)
    config: RunnableConfig = {"configurable": {"thread_id": "review-test-1"}}

    paused = graph.invoke({"draft": make_draft().model_dump(mode="json")}, config)
    request = paused["__interrupt__"][0].value
    assert request["status"] == ReviewStatus.PENDING.value
    assert request["artifact_type"] == "mail_3"

    result = graph.invoke(Command(resume=hr_decision("approve").model_dump()), config)
    assert result["item"]["status"] == ReviewStatus.APPROVED.value
    queue.require_approved(result["item"]["item_id"], make_draft().content, action=WRITE_ACTION)


def test_graph_returns_feedback_on_request_changes() -> None:
    graph, config = start_graph(ReviewQueue(), "review-test-2")

    result = graph.invoke(
        Command(resume=hr_decision("request_changes", "제목 수정").model_dump()), config
    )

    assert result["item"]["status"] == ReviewStatus.CHANGES_REQUESTED.value
    assert result["item"]["feedback"][-1]["comment"] == "제목 수정"


def test_graph_hold_waits_again_until_release() -> None:
    graph, config = start_graph(ReviewQueue(), "review-test-3")

    held = graph.invoke(Command(resume=hr_decision("hold").model_dump()), config)
    assert held["__interrupt__"][0].value["status"] == ReviewStatus.ON_HOLD.value

    released = graph.invoke(Command(resume=hr_decision("release").model_dump()), config)
    assert released["__interrupt__"][0].value["status"] == ReviewStatus.PENDING.value

    result = graph.invoke(Command(resume=hr_decision("approve").model_dump()), config)
    assert result["item"]["status"] == ReviewStatus.APPROVED.value


def test_graph_rejects_non_hr_decision() -> None:
    graph, config = start_graph(ReviewQueue(), "review-test-4")
    leader = ReviewDecision(action="approve", reviewer_role="리더")

    with pytest.raises(UnauthorizedReviewer):
        graph.invoke(Command(resume=leader.model_dump()), config)


def test_graph_rerun_with_same_approved_draft_ends_without_waiting() -> None:
    queue, item_id = approved_queue()
    graph = build_review_graph(MemorySaver(), queue=queue, now=lambda: FIXED_NOW)
    config: RunnableConfig = {"configurable": {"thread_id": "review-test-6"}}

    result = graph.invoke({"draft": make_draft().model_dump(mode="json")}, config)

    assert "__interrupt__" not in result
    assert result["item"]["status"] == ReviewStatus.APPROVED.value
    queue.require_approved(item_id, make_draft().content, action=WRITE_ACTION)


def test_stored_items_cannot_be_mutated_to_bypass_gate() -> None:
    queue = ReviewQueue()
    item = queue.submit(make_draft(), now=FIXED_NOW)

    with pytest.raises(ValidationError):
        queue.get(item.item_id).status = ReviewStatus.APPROVED  # type: ignore[misc]


def test_graph_rejects_unknown_action() -> None:
    graph, config = start_graph(ReviewQueue(), "review-test-5")

    with pytest.raises(ValidationError):
        graph.invoke(Command(resume={"action": "skip", "reviewer_role": "인사 담당자"}), config)
