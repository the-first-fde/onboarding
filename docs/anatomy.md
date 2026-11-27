# 시스템 해부도
| 부분 | 책임 | 현재 구현 |
|---|---|---|
| model | 근거 해석·제안 | 미구현 |
| instructions | constitution와 domain skills | 문서 |
| output | Pydantic 구조화 handoff/제안 | handoff 구현 |
| tools | 승인 gateway를 통하는 읽기/실행 | mock 준비 요청만 |
| memory | case별 DB와 제한된 대화 | case DB만 |
| loop | Observe→Reason→Plan→Act→Verify | SDK loop 미구현 |
| orchestration | Python 상태/rule/evidence와 DB worker | handoff/outbox만 |
| guardrails | allowlist·인증·hooks·budget | demo token/allowlist만 |

API(hr_ops/api.py) → service → SQLAlchemy transaction → outbox → worker → mock receipt.
agent는 DB를 직접 갱신하지 않으며 정식 gateway 구현 전 도구를 연결하지 않는다.
