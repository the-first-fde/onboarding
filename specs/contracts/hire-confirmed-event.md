# HireConfirmedEvent v1 · G0 핵심 계약
계약 상태: 초기 구현용 기준. 실연동·조직별 권한 매핑은 미확정.

## 조건
최종합격은 별개 사건이다. 지원자가 입사 의사를 확정하고 HR이 근거를 검토한 뒤에만 이 이벤트를 승인한다.
입사일은 입사확정일 이전일 수 없다. buddy_id/laptop_required는 null 허용한다.
source_refs는 source register의 불투명 참조만 받으며 메일 원문·자유문·주소를 받지 않는다.

## 입력 allowlist
schema_version=1, event_type=HireConfirmedEvent, event_id(UUID), candidate_id, employee_id,
confirmed_on, start_on, team_id, leader_id, employment_type(permanent/contract),
work_mode(hybrid/office/remote), probation_months, experienced, buddy_id?, laptop_required?, source_refs[].
모든 ID는 영문/숫자/하이픈의 불투명 식별자다. 이름·개인 이메일은 이 초기 이벤트에서 제외했다.
연락처 등은 추후 승인된 전용 입력 저장소로 분리한다. onboarding accommodation 자유문도 정제 경계 확정까지 제외한다.
연봉·처우·면접 점수·레퍼런스 원문·제공자 이름·이력서·수습 확인 원문은 extra=forbid로 거부한다.

## 승인과 전달
POST /api/hire-confirmations는 demo HR 토큰 소유자를 server actor demo-hr로 식별한다.
입력 payload hash + actor + case를 audit에 결합한다. 현재는 이 직접 승인 endpoint만 구현했다.
장기 대기 approval의 expiry/revoke/reapproval은 F-010에서 구현한다.
GET /api/cases, GET /api/cases/{id}, POST /api/mock-worker/tick도 같은 demo 인증이 필요하다.
인증 실패 403, 계약 오류 422(본문 값 미노출), 충돌 409. 같은 이벤트/동일 payload 재수신은 같은 case 200.
같은 지원자에 다른 event_id는 자동 갱신하지 않고 409/검토 대상으로 남긴다.

## EARS
- WHEN 최종합격 통보만 관측된다 THE SYSTEM SHALL 입사확정 이벤트나 온보딩을 생성하지 않는다.
- WHEN 인증된 HR이 유효한 이벤트를 승인한다 THE SYSTEM SHALL case/event/outbox/audit를 원자적으로 저장한다.
- WHEN 동일 event_id와 동일 payload가 다시 온다 THE SYSTEM SHALL 기존 case를 반환하고 outbox를 늘리지 않는다.
- WHEN 동일 event_id의 내용이 바뀐다 THE SYSTEM SHALL 409를 반환하고 기존 데이터를 유지한다.
- WHEN 허용되지 않은 필드가 온다 THE SYSTEM SHALL 입력을 거부하고 오류에 입력 값을 반사하지 않는다.

ON-01~03 기한은 입사확정+2일이다. 초기 구현은 이 세 가지의 PENDING task만 생성한다.
56개 전체 생성 및 역사적 v3 판 선택은 아직 구현하지 않았다.
