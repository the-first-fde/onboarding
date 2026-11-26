"""페이지 초안의 구간·세부 문단·양식 순서를 검증한다."""

from dataclasses import FrozenInstanceError, replace
from datetime import date

import pytest

from hr_onboarding.workflows.preparation_checklist import (
    HOLD_REASON_LABELS,
    Applicability,
    ChecklistTemplate,
    NewHire,
    NotionBlock,
    NotionBlockType,
    RoleSections,
    SectionKind,
    build_notion_page_draft,
    build_preparation_checklist,
    split_into_sections,
)


@pytest.mark.parametrize("laptop", [True, None])
def test_page_structure_and_details(
    template: ChecklistTemplate, hire_experienced_laptop: NewHire, today: date, laptop: bool | None
) -> None:
    hire_experienced_laptop = replace(hire_experienced_laptop, laptop_provided=laptop)
    checklist = build_preparation_checklist(hire_experienced_laptop, template)
    for role_list in checklist.role_checklists:
        sections = split_into_sections(role_list.entries, today)
        ids = tuple(entry.item_id for entry in role_list.entries)
        role_sections = RoleSections(role_list.role, ids, sections)
        page = build_notion_page_draft(checklist.hire_id, template.version, role_sections)
        assert page.item_ids == ids
        assert page.hire_id in page.title and role_list.role in page.title
        assert page.today == today and page.template_version == template.version
        assert [block.block_type for block in page.blocks] == (
            [NotionBlockType.HEADING] * 3 + [NotionBlockType.TOGGLE] + [NotionBlockType.HEADING] * 2
        )
        assert [block.text for block in page.blocks] == [
            f"{kind} ({len(section.entries)}개)"
            for kind, section in zip(SectionKind, sections.sections, strict=True)
        ]
        for block, section in zip(page.blocks, sections.sections, strict=True):
            assert len(block.children) == len(section.entries)
            for todo, entry in zip(block.children, section.entries, strict=True):
                assert todo.block_type == NotionBlockType.TO_DO
                assert todo.text == f"{entry.item_id} {entry.title}"
                assert all(child.block_type == NotionBlockType.PARAGRAPH for child in todo.children)
                details = "\n".join(child.text for child in todo.children)
                assert entry.completion_criteria in details
                assert entry.collaborator in details and "함께" in details
                assert entry.due_rule in details
                if entry.due_date:
                    assert entry.due_date.isoformat() in details
                if entry.weekend_adjusted:
                    assert "주말" in details
                for reason in entry.hold_reasons:
                    assert HOLD_REASON_LABELS[reason] in details


def test_template_order_differs_from_display_order(
    template: ChecklistTemplate, hire_experienced_laptop: NewHire, today: date
) -> None:
    template = replace(template, items=tuple(reversed(template.items)))
    role_list = build_preparation_checklist(hire_experienced_laptop, template).role_checklists[0]
    sections = split_into_sections(role_list.entries, today)
    ids = tuple(entry.item_id for entry in role_list.entries)
    display_ids = tuple(entry.item_id for section in sections.sections for entry in section.entries)
    assert ids != display_ids
    page = build_notion_page_draft(
        "VH-001", template.version, RoleSections(role_list.role, ids, sections)
    )
    assert page.item_ids == ids


def test_not_applicable_and_empty_collaborator(
    template: ChecklistTemplate, hire_new_no_laptop: NewHire, today: date
) -> None:
    template = replace(
        template, items=tuple(replace(item, collaborator="") for item in template.items)
    )
    checklist = build_preparation_checklist(hire_new_no_laptop, template)
    assert any(
        entry.applicability == Applicability.NOT_APPLICABLE
        for role_list in checklist.role_checklists
        for entry in role_list.entries
    )
    for role_list in checklist.role_checklists:
        sections = split_into_sections(role_list.entries, today)
        page = build_notion_page_draft(
            "VH-002",
            template.version,
            RoleSections(
                role_list.role, tuple(entry.item_id for entry in role_list.entries), sections
            ),
        )
        assert any(not block.children for block in page.blocks)
        for block, section in zip(page.blocks, sections.sections, strict=True):
            for todo in block.children:
                details = "\n".join(child.text for child in todo.children)
                assert "함께" not in details
                if section.kind == SectionKind.NOT_APPLICABLE:
                    assert "해당 없음" in details
    assert NotionBlock(NotionBlockType.PARAGRAPH, "가상").children == ()


def test_page_models_are_frozen(
    template: ChecklistTemplate, hire_experienced_laptop: NewHire, today: date
) -> None:
    role_list = build_preparation_checklist(hire_experienced_laptop, template).role_checklists[0]
    role_sections = RoleSections(
        role_list.role,
        tuple(entry.item_id for entry in role_list.entries),
        split_into_sections(role_list.entries, today),
    )
    page = build_notion_page_draft(hire_experienced_laptop.hire_id, template.version, role_sections)
    for model, field in ((page, "title"), (role_sections, "role"), (page.blocks[0], "text")):
        with pytest.raises(FrozenInstanceError):
            setattr(model, field, "changed")
