---
name: security-review
description: 권한, 의존성, 민감정보 또는 외부 연동 변경을 보안 검토할 때 사용한다.
license: MIT
---

[루트 지침](../../../CLAUDE.md)과 [공통 Handbook](../../../docs/guides/README.md)을 준수한다.

비밀값 자체를 읽거나 출력하지 않는다. Gitleaks/ignore/로그/최소 권한/경로 검증/셸 주입/외부 쓰기 경계를 확인한다. 실제 고객사 자료·MCP 연결·외부 분석을 실행하지 않는다. 증거가 있는 취약점만 경로/줄/영향으로 보고한다. No Silent Issues에 따라 민감정보 없는 초안을 제안하고 실제 등록은 승인받는다.

ECC 파생본. Copyright (c) 2026 Affaan Mustafa. MIT 고지 및 고정 출처는
[라이선스](../../../third_party/ecc/LICENSE), [출처](../../../third_party/ecc/SOURCE.md),
[변경 기록](../../../third_party/ecc/CHANGES.md)을 참조한다.
