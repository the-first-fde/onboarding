# ADR 0005: SonarQube CI 전용

- 날짜: 2026-11-25
- 상태: 사용자 확정 정책 반영, 추천/미확인은 본문 구분
- 근거: 초기화 Spec 0001 및 사용자 지시

확정: 사용자가 만든 기존 Organization/Project만 사용, CI coverage.xml 연결. 로컬 설치/호출/verify/hooks 포함 금지. 외부 분석 허용/Private/CI-based analysis/토큰 상태 미확인. 기본 비활성; 승인 후 관리자 Variables/Secret 설정, 수동 main 실행만 허용한다.
