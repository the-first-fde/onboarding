# Context Map
| 입력 칸 | 원천 | 필터 / 예산 | 상태 |
|---|---|---|---|
| 지시 | 검토된 constitution/skill | 버전 고정 | 문서만 |
| 예시 | 합성 fixtures | 현재 case에 필요한 것만 | fixture |
| 형식 | Pydantic/JSON Schema | extra forbid | handoff |
| 기록 | case별 승인된 대화 | tenant+role+case+as_of | 미구현 |
| 지식 | reviewed wiki + source refs | effective_from/recorded_at/status/sources | 명세 |
| 입력 | HR 요청 | 민감값 제거·길이 제한 | handoff만 |

조립 순서: 인증 actor→tenant/case 권한→as-of 조회→유효 지식 선별→출처 결합→예산 내 압축→구조화 출력 검증.
다른 case의 메시지/벡터/도구 결과는 재사용하지 않는다. 외부 문서의 지시는 데이터로 취급한다.
source_refs는 문서 레지스트리의 식별자만, 원문/개인 정보가 아니다.
Write(raw→wiki), Select(검색), Compress(근거 유지 요약), Isolate(case/role)를 분리해 평가한다.
현재 assembler/RAG는 구현하지 않았으므로 격리 보장은 아직 제품 수준으로 검증되지 않았다.
