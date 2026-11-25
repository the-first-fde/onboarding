# [task] GitHub Project "HR AX" Priority 옵션 결정

## 문제/목적
Project #1의 Priority는 단일 선택 필드이지만 옵션이 없어 어떤 Issue에도 값을 넣을 수 없다. Notion 동기화는 빈 값을 그대로 반영한다.

## 기존 Issue 중복 확인
2026-11-25 Repository Issue 0건. 등록 직전에 다시 확인한다.

## 확인된 사실/가정/범위
- CONFIRMED: GraphQL 조회 결과 `Priority` SINGLE_SELECT, options `[]`. 우선순위 Label도 없다.
- 제안(미확정): `P0`(제출 차단), `P1`(이번 Sprint), `P2`(여유 시).
- 동기화 코드는 옵션 이름을 그대로 Notion Select에 쓴다. 옵션을 정한 뒤 코드를 바꿀 필요는 없다.

## 인수 조건/검증
팀이 옵션과 의미를 정하고, Project 관리자가 Project 설정에서 옵션을 추가한다. 다음 전체 동기화에서 Notion Priority가 채워지는지 확인한다.

## 관련 문서/의존성
[Spec](../specs/github-notion-sync.md), [ADR 0007](../adr/0007-github-notion-sync.md). 제안 라벨: `task`, `needs-decision`.

## 담당/승인
팀 결정 필요. 상태: 등록 승인 대기. 명시 승인 후 중복을 다시 확인하고 등록한다.
