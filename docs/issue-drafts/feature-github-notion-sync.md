# [feature] GitHub Issues·Projects → Notion 단방향 동기화

## 문제/목적
팀원이 Notion에서도 개발 Issue와 GitHub Project 진행 상태를 확인할 수 있게 한다. GitHub이 기준이고 Notion은 읽기용이다.

## 기존 Issue 중복 확인
2026-11-25 `gh issue list -R the-first-fde/onboarding --state all` 결과 0건. 등록 직전에 다시 확인한다.

## 확인된 사실과 근거
[Spec](../specs/github-notion-sync.md)의 CONFIRMED 근거(Project #1 "HR AX" 필드와 옵션, Notion API 2026-03-11, Issue·Label 현황).

## 가정/미확인/차단
- PROVISIONAL: 팀원 3명의 Issue만 동기화, 15분 주기.
- NEEDS_CLARIFICATION: Priority 옵션([결정 초안](decision-project-priority.md)), Project 내장 workflow 전이 규칙.
- BLOCKED(실제 연동): GitHub App·Notion Integration·DB 미생성, Secrets·Variables 미등록.

## 범위/제외 범위
Spec 범위와 같다. 양방향 동기화, PR DB, 알림, Webhook 서버, HR 데이터는 제외한다.

## 재현 또는 조사 방법 / 기대와 실제 결과
가이드의 dry-run 절차를 실행하면 Notion에 쓰지 않고 예정 결과 요약이 나온다.

## Spec/ADR/담당 계약
[Spec](../specs/github-notion-sync.md) · [ADR 0007](../adr/0007-github-notion-sync.md) · HR 업무 계약 없음.

## 인수 조건/검증 계획
Spec 인수 조건, `uv run --locked python scripts/verify.py` PASS, 실제 연동 테스트는 [가이드](../guides/collaboration-integration-guide.md) 14절.

## 담당/의존성/위험/보안/결정 필요사항
담당 미정. 보안·권한 변경이므로 사람 리뷰 2명. Public Repository 위협 모델은 Spec 보안 절. 제안 라벨: `feature`, `area:ci`, `area:security`.

## 등록 승인
초안 검토자: 미정 / 명시 승인: 없음(등록하지 않음).
