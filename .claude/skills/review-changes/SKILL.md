---
name: review-changes
description: 구현 후 독립 AI 리뷰 또는 사람 리뷰 준비를 수행할 때 사용한다.
---

[루트 시작 안내](../../../README.md), [루트 지침](../../../CLAUDE.md)과 [CONTRIBUTING](../../../CONTRIBUTING.md)을 따른다.

구현자와 독립된 세션/리뷰어가 변경 전제 없이 Spec·현재 diff·미추적 파일을 읽는다. code-reviewer/python-reviewer, 보안 변경이면 security-reviewer 기준을 적용한다. .github/templates/review.md에 정확한 위치/발생 조건/영향/검증을 기록한다. 발견 없음도 가능하다. 검토만 수행하며 파일을 직접 수정하지 않는다. 독립 리뷰 미실행이면 NOT RUN. 문제 실제 등록은 승인 후.

루트와 변경 경로의 README·CLAUDE.md 및 담당 계약을 읽고 구현의 책임·입출력·명령과 대조한다. 불일치를 보고하고 팀 판단 사항은 Issue 등록을 제안한다.
