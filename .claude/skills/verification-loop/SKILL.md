---
name: verification-loop
description: 구현 후 또는 PR 준비 전 공통 검증 결과를 보고할 때 사용한다.
license: MIT
---

[루트 지침](../../../CLAUDE.md)과 [공통 Handbook](../../../docs/guides/README.md)을 준수한다.

uv run --locked python scripts/verify.py를 실행한다. lint/format/types/instructions/tests/coverage/Gitleaks 결과와 git diff/미추적 파일을 검토한다. 실행하지 못하면 NOT RUN과 이유를 기록한다. 초기 coverage는 측정, 이후 80% 목표. Sonar는 로컬 실행하지 않는다. 실제 운영 환경 검증과 로컬 PASS를 구분한다.

ECC 파생본. Copyright (c) 2026 Affaan Mustafa. MIT 고지 및 고정 출처는
[라이선스](../../../third_party/ecc/LICENSE), [출처](../../../third_party/ecc/SOURCE.md),
[변경 기록](../../../third_party/ecc/CHANGES.md)을 참조한다.
