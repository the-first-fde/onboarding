# hr_onboarding Python 패키지

[프로젝트 시작 안내](../../README.md) · [공통 착수·완료 기준](../../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

Python으로 실행할 수 있는 공통 시작점이다. 하위 모듈에서 업무 흐름, SDK, 외부 도구의 책임을 나눈다.

## 2. 무엇을 개발해야 하는가?

기술 실행과 공통 설정을 유지한다. 후속 기능은 책임에 맞는 하위 디렉터리에 배치하고 여러 담당자가 공유하는 변경은 인터페이스 검토부터 한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | 공통 설정·실행 진입점·기술 smoke | 재현 가능한 로컬 실행과 검증 | [초기화 Spec](../../docs/specs/0001-bootstrap.md) |

## 4. 개발에 필요한 기초 개념

패키지는 관련 Python 파일을 한 이름으로 묶은 단위다. python -m은 그 패키지의 __main__.py를 실행한다. 타입 힌트는 입력과 반환을 읽을 때 도움이 된다.

## 5. 파일 및 모듈별 역할

[config.py](config.py)는 mock 설정, [__main__.py](__main__.py)는 실행 시작점, [smoke.py](smoke.py)는 기술 그래프·Markdown·SDK 옵션을 담는다. 실제 업무 구현은 하위 README의 계획 위치에서 다룬다.

## 6. 입력 및 출력 데이터

현재 CLI에는 HR 입력이 없고 기술 결과 메시지를 출력한다. 기술 함수는 카운터와 Markdown 텍스트를 다룬다. 업무 공통 Schema는 보류 중이다.

## 7. 다른 모듈과의 관계

[워크플로우](workflows/README.md) · [SDK](agents/README.md) · [연동](integrations/README.md)의 역할을 확인한다. [테스트](../../tests/README.md)는 각 최소 동작을 확인한다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 실행 진입점에서 smoke.py까지 찾아가고 설정을 바꿀 경우 기존 mock 기본값과 호출 위치를 확인한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
import asyncio
from hr_onboarding.smoke import run_smoke


def local_count() -> int:
    """초기화 패키지의 기술 그래프 결과를 확인한다.

    Returns:
        네트워크 없이 실행된 카운터 결과.
    """
    return asyncio.run(run_smoke())


assert local_count() == 1
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 공통 실행 또는 설정의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “__main__.py에서 run_smoke까지의 호출 관계를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 mock 진입점의 작은 변경만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 하위 모듈의 import와 기본 설정에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “공통 설정 소유권 또는 실제 인증 의존가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked python -m hr_onboarding
```

Mock graph count: 1; HR functionality deferred가 출력된다. 실패하면 doctor와 smoke 테스트를 실행해 환경 문제와 코드 문제를 구분한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 공통 진입점이 인증 없이 실행된다.
- [ ] 어떤 하위 모듈이 변경을 소비하는지 검토했다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 SDK 실행·HR 상태·외부 쓰기·프론트엔드·FastAPI는 현재 범위에 없다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](../CLAUDE.md) · [Engineering Handbook](../../docs/guides/README.md) · [데이터 확인 Issue 초안](../../docs/issue-drafts/research-data-contract.md) · [기술 설계](../../docs/architecture.md) · [테스트 가이드](../../docs/guides/testing-guide.md) · [Python 실행 진입점 공식 문서](https://docs.python.org/3.12/library/__main__.html)
