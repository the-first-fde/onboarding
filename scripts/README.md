# 개발 환경과 검증 스크립트

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

팀과 CI가 같은 기준으로 설치·검증하도록 명령을 모아둔다. 제품 업무는 src에 둔다.

## 2. 무엇을 개발해야 하는가?

설치와 진단이 실패 원인을 명확히 보고하도록 유지한다. 검사를 추가할 때 공통 verify의 적용 위치와 종료코드 의미를 정한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | 설치·진단·검증 스크립트 유지 | 재현 가능한 검증 명령·출력 | [초기화 Spec](../docs/specs/0001-bootstrap.md) |

## 4. 개발에 필요한 기초 개념

종료코드 0은 성공이며 0이 아닌 값은 실패를 알린다. 진단 스크립트는 문제 위치를 찾고 검증 스크립트는 통과 기준을 확인한다.

## 5. 파일 및 모듈별 역할

[bootstrap.py](bootstrap.py)는 설치, [doctor.py](doctor.py)는 환경 진단, [verify.py](verify.py)는 공통 검사, [check_instructions.py](check_instructions.py)는 문서 검사다. [install_tools.py](install_tools.py)와 [scan_secrets.py](scan_secrets.py)는 Gitleaks 설치와 공유 파일 검사를 맡는다.

## 6. 입력 및 출력 데이터

입력은 저장소 경로·잠금 환경·공유 파일이며 출력은 도구별 PASS/FAIL과 종료코드다. 비밀값은 출력하지 않는다.

## 7. 다른 모듈과의 관계

[CI](../.github/README.md)와 로컬 pre-commit이 공통 verify를 사용한다. 환경 파일과 고객사 자료는 검사 대상으로 읽지 않는다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 스크립트를 단독 실행해 기존 종료코드와 출력을 보고, 호출하는 CI와 hook의 순서를 확인한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
from pathlib import Path


def instruction_script_exists(root: Path) -> bool:
    """공통 진입점이 참조하는 문서 검사 파일을 확인한다.

    Args:
        root: 저장소 루트 경로.

    Returns:
        검사 파일이 있으면 True.
    """
    return (root / "scripts/check_instructions.py").is_file()


assert instruction_script_exists(Path.cwd())
```

실제 문서 검증이 실패하면 check_instructions가 해당 경로와 FAIL을 출력하며 verify도 실패를 보고한다.

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 검사 하나를 수정할 때 실행 순서의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “verify가 자식 명령의 실패를 전달하는 방식를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 진단 메시지와 재현 명령만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 CI와 pre-commit의 종료코드 처리에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “검사 추가에 필요한 외부 연결 또는 비밀 접근가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked python scripts/check_instructions.py
uv run --locked python scripts/doctor.py
uv run --locked python scripts/verify.py
```

문서 검사와 진단에 PASS가 표시된다. 실패하면 누락된 경로와 첫 실패 도구를 확인하고, 환경 문제는 문제 해결 가이드를 따른다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 실패가 해당 도구와 종료코드로 드러난다.
- [ ] 로컬과 CI가 같은 진입점을 사용한다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 .env를 읽지 않는다. Sonar는 CI에서만 실행하며 verify에 포함하지 않는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [문제 해결](../docs/guides/troubleshooting.md) · [공통 검사 안내](../docs/guides/quality-guide.md) · [uv 공식 문서](https://docs.astral.sh/uv/)
