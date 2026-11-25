# 프로젝트 범위

## CONFIRMED
- 사용자 명세: The First 3인 HR onboarding, 2026-12-03 23:59 KST 제출.
- LangGraph가 실행 순서 통제, Claude Agent SDK가 업무 agent 실행, Markdown 정의, MCP 연동.
- Python/uv/lock, 프론트엔드·FastAPI 없음. 실제 고객사 데이터/비밀/실제 MCP 쓰기 금지.
- Sonar Organization/Project 생성 완료는 사용자 진술이며 CI만 사용, 새 project 생성 금지.
- 현재 저장소는 초기화 전 .git만 있었고 커밋/작업 파일이 없었다.

## DEFERRED / BLOCKED
샘플 미수령으로 실제 업무 기능, HR Schema/State/규칙/공통 업무 테스트 데이터 및 통합 보류.
실제 메일/입사 확정은 수동. 외부 서비스 정책/권한 확인 전 실제 전송/연결 보류.

## PROVISIONAL
일반 1명/고위험 2명 리뷰, squash merge, Private monorepo 운영 추천.
공통 모듈 담당/영속화/일정 실행/시연 인터페이스는 합의 후 결정한다.
현재 smoke.py State는 기술 테스트 카운터로 공통 업무 계약이 아니다.

## 이전 대화에 기록된 담당 범위

다음은 참조 대화의 분담 기록이다. 업무 명세·잠정 데이터 요구만 준비하며 구현/계약 확정은 하지 않는다.

| 담당 | 범위 | 시작 문서 |
|---|---|---|
| 예빈님 | 온보딩 계획 수립, 진행 상황 관리 | [계획·진행 Spec](specs/onboarding-planning.md) |
| 종은 | 입사 안내 메일, 리더·담당자 준비 체크리스트 및 요청 | [안내·준비 Spec](specs/communication-preparation.md) |
| 정현님 | 산출물 검토, 수정 요청 처리, HITL, 승인 상태 관리 | [검토·승인 Spec](specs/review-approval.md) |
| 공통 | MCP, 데이터 계약, 오케스트레이션, 통합 테스트 | 담당 미확정 |

README 감사 요청에서 종은의 이름과 정현의 수정 요청 처리 범위를 명시했다. 현재 분담의 적용 방식과 공통 모듈 담당/리뷰 대체자는 팀에서 확인한다.
