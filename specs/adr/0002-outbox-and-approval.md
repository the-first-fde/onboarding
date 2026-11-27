# ADR-002 · DB outbox와 승인 경계
상태: 초기 코어 채택. 실연동 상세는 미결.
case/event/outbox/audit를 한 트랜잭션으로 저장한다. 원격 API는 DB 커밋과 원자적이지 않다.
따라서 at-least-once 전달 + 고정 idempotency key + receipt 조회/조정 전략이 필요하다.
초기 mock은 receipt를 같은 DB에 기록하므로 crash 시 함께 롤백된다.
실연동의 retry/backoff/lease/DLQ는 별도 구현하고 검증 전 성공을 주장하지 않는다.
승인은 서버 액터로 귀속하고 payload hash를 기록한다. demo bearer는 로컬 합성 시연에만 허용한다.
정식 인증·tenant RBAC·만료/revoke approval은 미구현이다.
