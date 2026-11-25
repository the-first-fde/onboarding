# 업무 명세와 개발 문서

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

업무의 근거와 결정 이력을 공유한다. 사용할 위치와 실행법은 각 모듈의 README, 상태와 근거는 이 영역에 둔다.

## 2. 무엇을 개발해야 하는가?

업무별 인수 조건, 필요한 데이터 질문, 공통 설계 결정을 작성한다. 운영 가이드는 여러 담당자에게 적용되는 절차를 관리한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | specs·contracts에서 계획·진행 정리 | 인수 조건과 샘플 질문 | [계획 Spec](specs/onboarding-planning.md) |
| 종은 | specs·contracts에서 안내·준비 정리 | 문안 및 요청 데이터 질문 | [안내 Spec](specs/communication-preparation.md) |
| 정현 | specs·contracts에서 검토·승인 정리 | 검토 기준 및 승인 질문 | [검토 Spec](specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

Spec은 구현할 범위와 인수 조건, 계약은 입력·출력 경계, ADR은 중요한 설계 결정의 이유다. 잠정 사실의 상태를 표시하면 가정을 구현 규칙으로 오해하지 않는다.

## 5. 파일 및 모듈별 역할

[specs](specs/template.md)·[contracts](contracts/template.md)·[adr](adr/template.md)는 각 양식을 제공한다. [guides](guides/README.md)는 팀 공통 절차이며 [open-questions.md](open-questions.md)는 미결정을 모은다.

## 6. 입력 및 출력 데이터

입력은 사용자 요청과 확인된 근거, 출력은 시험 가능한 인수 조건·잠정 데이터 요구·결정 기록이다. 원본 고객사 자료는 넣지 않는다.

## 7. 다른 모듈과의 관계

제품과 테스트가 승인된 Spec을 따른다. 관련 [모듈 README](../src/README.md)는 착수 위치와 실행 방법을 설명한다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 기존 양식을 선택하고 확인된 사실, 가정, 차단 조건을 분리한다. 구현 위치가 바뀌면 해당 README를 연결한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```text
상태: NEEDS_CLARIFICATION
확인 질문: 검토 결과를 어느 담당자가 소비하는가?
인수 조건: 소비 모듈과 권한을 합의한 뒤 작성
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 업무 Spec과 잠정 계약의 연결의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “Spec·계약·ADR의 차이와 현재 상태를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 문서 범위와 상대 링크 검증만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 다른 담당자의 Spec과 README에 미치는 영향에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “업무 규칙 근거가 서로 다른 경우가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked python scripts/check_instructions.py
```

문서 검사 PASS가 보여야 한다. 깨진 링크가 있으면 링크를 쓴 파일을 기준으로 상대 경로를 계산한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 현재 사실과 미확정 내용이 분리된다.
- [ ] 관련 README·Spec·계약 사이의 링크가 확인된다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

업무 인수 조건을 고객사 근거 없이 확정하지 않는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](guides/README.md) · [데이터 확인 Issue 초안](issue-drafts/research-data-contract.md) · [초기화 Spec](specs/0001-bootstrap.md) · [계약 양식](contracts/template.md) · [기술 설계](architecture.md) · [GitHub Markdown 공식 문서](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
