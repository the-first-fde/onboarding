---
name: prepare-pr
description: 검증을 마친 변경을 공통 PR 초안으로 정리할 때 사용한다.
---

[루트 시작 안내](../../../README.md), [루트 지침](../../../CLAUDE.md)과 [CONTRIBUTING](../../../CONTRIBUTING.md)을 따른다.

verify 및 독립 AI 리뷰 결과, 관련 Issue/Spec/ADR, diff/미추적 파일/비밀 검사를 확인한다. .github/pull_request_template.md에 PASS/FAIL/NOT RUN과 coverage, 업무 검증 보류, Sonar 상태를 기록한다. 일반 사람 1명/고위험 2명, 변경 후 재승인, squash 추천을 안내한다. PR 초안을 제시하며 commit/push/PR 등록은 각각 별도 승인 후 수행한다.

루트와 변경 경로의 README·CLAUDE.md, Issue·Spec·잠정 계약을 확인한다. 개발 안내 변경 파일과 링크·명령·예제 검증 결과를 PR 초안에 기록한다. 문서와 구현의 불일치와 영향은 사용자에게 보고한다.
