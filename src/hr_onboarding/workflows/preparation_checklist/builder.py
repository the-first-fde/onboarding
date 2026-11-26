"""입사자와 양식에서 담당별 준비 체크리스트를 생성한다."""

from .conditions import evaluate_condition
from .constants import TARGET_ROLES
from .due_date import parse_due_rule, resolve_due_date
from .models import (
    ChecklistEntry,
    ChecklistTemplate,
    NewHire,
    PreparationChecklist,
    Role,
    RoleChecklist,
)


def build_preparation_checklist(hire: NewHire, template: ChecklistTemplate) -> PreparationChecklist:
    """대상 담당별로 양식 순서를 유지한 목록을 만든다.

    Args:
        hire: 계산에 필요한 입사자 정보.
        template: 버전과 항목을 담은 양식.

    Returns:
        해당 없음과 보류 항목을 포함한 리더·총무·버디 목록.

    Raises:
        ValueError: 양식 ID가 중복되거나 대상 항목 조건이 지원되지 않는 경우.
    """
    item_ids = tuple(item.item_id for item in template.items)
    if len(set(item_ids)) != len(item_ids):
        raise ValueError("Duplicate item_id in template")
    grouped: dict[Role, list[ChecklistEntry]] = {role: [] for role in TARGET_ROLES}
    for item in template.items:
        if item.owner not in TARGET_ROLES:
            continue
        role = next(role for role in TARGET_ROLES if role.value == item.owner)
        resolution = resolve_due_date(parse_due_rule(item.due_rule), hire.start_date)
        applicability, condition_reason = evaluate_condition(item.condition, hire)
        reasons = tuple(
            reason for reason in (resolution.hold_reason, condition_reason) if reason is not None
        )
        grouped[role].append(
            ChecklistEntry(
                item_id=item.item_id,
                role=role,
                title=item.title,
                collaborator=item.collaborator,
                completion_criteria=item.completion_criteria,
                due_rule=item.due_rule,
                due_date=resolution.due_date,
                weekend_adjusted=resolution.weekend_adjusted,
                applicability=applicability,
                hold_reasons=reasons,
            )
        )
    return PreparationChecklist(
        hire.hire_id,
        template.version,
        tuple(RoleChecklist(role, tuple(grouped[role])) for role in TARGET_ROLES),
    )
