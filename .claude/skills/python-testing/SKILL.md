---
name: python-testing
description: Python 테스트·mock·비동기 검증을 작성하거나 검토할 때 사용한다.
license: MIT
---

[루트 지침](../../../CLAUDE.md)과 [공통 Handbook](../../../docs/guides/README.md)을 준수한다.

pytest fixture/parametrize로 관찰 가능한 결과와 오류 경로를 검증한다. async는 pytest-asyncio, 외부 호출은 AsyncMock. 테스트 간 상태를 공유하지 않는다. 고객사 샘플 없는 업무 fixtures/계약 검증은 보류한다. tests/conftest.py의 네트워크 차단을 유지한다.

ECC 파생본. Copyright (c) 2026 Affaan Mustafa. MIT 고지 및 고정 출처는
[라이선스](../../../third_party/ecc/LICENSE), [출처](../../../third_party/ecc/SOURCE.md),
[변경 기록](../../../third_party/ecc/CHANGES.md)을 참조한다.
