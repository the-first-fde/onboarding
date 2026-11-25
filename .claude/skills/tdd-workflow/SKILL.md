---
name: tdd-workflow
description: 승인된 Python 기능 또는 버그 수정의 RED/GREEN/refactor 증거가 필요할 때 사용한다.
license: MIT
---

[루트 지침](../../../CLAUDE.md)과 [공통 Handbook](../../../docs/guides/README.md)을 준수한다.

Spec 인수 조건을 테스트로 만들고 의도한 이유로 실패하는 것을 실제 실행한다. 최소 구현으로 통과시키고 필요한 범위만 리팩터링한다. 명령·실패 이유·최종 결과를 PR에 기록한다. 자동 add/commit/checkpoint는 금지한다. 초기화 smoke를 업무 TDD 완료로 보고하지 않는다.

ECC 파생본. Copyright (c) 2026 Affaan Mustafa. MIT 고지 및 고정 출처는
[라이선스](../../../third_party/ecc/LICENSE), [출처](../../../third_party/ecc/SOURCE.md),
[변경 기록](../../../third_party/ecc/CHANGES.md)을 참조한다.
