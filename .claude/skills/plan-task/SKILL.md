---
name: plan-task
description: Issue와 Spec을 바탕으로 구현 전에 검토할 계획을 작성할 때 사용한다.
---

[루트 시작 안내](../../../README.md), [루트 지침](../../../CLAUDE.md)과 [CONTRIBUTING](../../../CONTRIBUTING.md)을 따른다.

Issue/Spec/관련 ADR/담당 데이터 계약을 읽는다. DoR, 확인된 사실과 가정, 미확인/차단 항목을 분리한다. .claude/agents/planner.md 기준으로 작은 구현 단계/검증/위험/의존성을 기록한다. 업무 계약이 미확정이면 의존 구현을 보류하고 안전한 탐색 범위를 제안한다. 외부 등록은 하지 않는다.

계획 전에 작업 경로의 README·CLAUDE.md를 읽고, 해당 작업의 책임과 인접 모듈 인터페이스를 나눈다. README와 코드가 다르면 근거와 영향을 보고하고 팀 판단 사항은 Issue 초안을 제안한다.
