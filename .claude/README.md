# Claude Code 개발 환경

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

팀이 코드 작성·검토에 사용하는 AI 개발 환경이다. 런타임 에이전트의 업무 지시는 루트 agents에 둔다.

## 2. 무엇을 개발해야 하는가?

작업 계획·구현·리뷰·PR 초안 스킬과 권한 hook을 유지한다. 권한 수정은 실제 외부 실행이 없는 테스트로 확인하고 고위험 리뷰를 요청한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | 팀용 Skills·리뷰 역할·hook 정책 | 재현 가능한 개발 환경과 권한 검증 | [초기화 Spec](../docs/specs/0001-bootstrap.md) |

## 4. 개발에 필요한 기초 개념

Skill은 반복 절차, 개발 agent는 계획이나 리뷰 역할, hook은 도구 호출 시 실행되는 점검이다. 프로젝트 권한은 개인·조직 설정과 함께 적용될 수 있다.

## 5. 파일 및 모듈별 역할

[skills](skills)는 실행 절차, [agents](agents)는 계획·리뷰 역할, [hooks](hooks)는 실행 점검, [settings.json](settings.json)은 연결과 권한 설정을 담는다.

## 6. 입력 및 출력 데이터

입력은 승인된 작업 지시·Spec과 가상 hook 요청이다. 출력은 계획·검증 결과·리뷰 의견 또는 도구 권한 판단이다.

## 7. 다른 모듈과의 관계

[루트 CLAUDE.md](../CLAUDE.md)는 전체 규칙, [런타임 Markdown](../agents/README.md)은 업무 에이전트 정의를 제공한다. [tests](../tests/README.md)가 hook 동작을 확인한다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 기존 프로젝트 스킬을 먼저 읽고 요구사항을 어디에 반영할지 결정한다. 권한 변경이면 가상 hook 요청과 기대 판단을 작성한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```text
예: main에서 쓰기 요청을 모사 → test_main_edits_are_denied가 차단을 확인 → 실제 Git 상태는 그대로 유지
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 권한 또는 계획 스킬 문구 조정의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “settings.json에서 protect_files.py가 호출되는 방식를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 가상 권한 요청의 단위 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 개인 설정·CI·업무 SDK 권한과의 관계에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “개인 설정과 팀 권한 정책 충돌가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_hooks.py
```

hook 테스트가 통과해야 한다. 실패하면 테스트의 가상 요청 종류와 실제 허용·차단 응답을 비교한다. 실제 인증 세션 권한 검증은 이 테스트와 별도다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 권한을 넓히는 변경에는 근거와 별도 리뷰가 있다.
- [ ] 개발 스킬과 업무 런타임 권한이 분리된다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

전체 ECC 설치, 자동 학습, 자동 Git 변경은 금지된다. 개인 설정은 무단 열람하지 않는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [초기화 Spec](../docs/specs/0001-bootstrap.md) · [팀 운영 Issue 초안](../docs/issue-drafts/task-team-settings.md) · [ECC 출처](../third_party/ecc/SOURCE.md) · [하네스 안내](../docs/guides/harness-guide.md) · [Claude Code hooks 공식 문서](https://code.claude.com/docs/en/hooks)
