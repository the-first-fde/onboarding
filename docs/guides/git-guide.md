# Git과 GitHub Flow

**학습 목표**는 어떤 변경이 다음 commit에 들어가는지 확인하고, 공유 이력을 훼손하지 않고 실수를 복구하는 것이다. [환경 준비](getting-started.md) 뒤 루트에서 진행한다.

Git은 로컬 변경을 기록하는 도구이고 GitHub는 원격 저장소와 공동 검토 공간이다. 작업 트리(Working Tree)는 편집 중인 파일, 스테이지(Staging Area)는 다음 commit 후보, 로컬 저장소(Local Repository)는 이미 기록된 이력, 원격(Remote Repository)은 공유 사본이다. Branch는 변경 흐름을 가리키고 Commit은 스테이지의 묶음을 기록한다. Push는 로컬 이력을 원격에 보내고 Pull은 원격 이력을 받아 현재 브랜치에 반영한다. Merge는 변경 흐름을 합친다. 같은 부분을 서로 다르게 고쳤을 때 자동 합치기가 멈추는 것이 Conflict다.

```bash
git status --short --branch
git diff
git diff --staged
```

`--short --branch`는 상태와 브랜치를 요약한다. 일반 diff는 추적 파일의 편집 내용과 스테이지 차이를, `--staged`는 다음 commit 후보를 보여준다. 빈 diff에도 `??` 미추적 파일은 있을 수 있으므로 status를 함께 본다. Git이 루트를 찾지 못하면 [처음 실행](getting-started.md)에서 위치를 확인한다. 이 세 명령은 이력을 바꾸지 않는다.

## 실습 · 검토 문구 하나를 바꾸는 GitHub Flow

현재 첫 commit 전이라면 읽기 단계까지만 진행하고, 팀 리더가 최초 commit 예외를 승인한 후 아래 시나리오를 따른다. 기존 변경이 있으면 작업을 보존하고 브랜치 이동 전에 주인을 확인한다.

1. 문구 변경 Issue와 인수 조건을 검토한다. 시작 브랜치가 준비된 경우 `git switch main`, `git pull --ff-only`로 기준을 맞춘다. `--ff-only`는 분기 이력을 자동 병합하지 않는다. 실패하면 먼저 status와 브랜치 상태를 확인한다.
2. `git switch -c task/readme-wording`으로 작업 브랜치를 새로 만든다. `-c`는 새 브랜치를 만들므로 현재 기준 브랜치를 먼저 확인한다. 파일을 고치고 공통 검사를 실행한다.
3. 검토한 파일만 `git add -- docs/README.md`로 스테이지에 넣는다고 가정한다. `--`는 이후 인자를 파일 경로로 취급한다. staged diff로 한 파일의 의도한 수정인지 확인한다. 승인 후 `git commit -m "docs: clarify onboarding guide"`로 묶음을 기록한다. `-m`은 메시지다.
4. 별도 승인 후 `git push -u origin task/readme-wording`을 실행하면 원격 브랜치가 생성되고 `-u`가 추적 관계를 설정한다. [PR과 리뷰](github-guide.md)로 이어서 독립 AI·CI·사람 리뷰를 기록하고, 승인 후 squash merge를 권장한다. 변경 뒤에는 영향을 다시 검토하고 재승인한다.

## 실수와 복구

| 증상 | 안전한 다음 단계 |
|---|---|
| 잘못 스테이지함 | HEAD가 있는 브랜치에서 `git restore --staged -- 경로`로 후보에서만 뺀 뒤 편집 내용이 남았는지 status와 diff로 확인한다. 최초 commit 전에는 HEAD가 없으므로 무리하게 실행하지 말고 팀과 작업 상태를 확인한다. |
| 잘못 commit함 | 공유 여부와 `git log -1 --oneline` 결과를 보고한다. 올린 변경은 팀 승인 후 새 복구 커밋과 PR로 되돌린다. 값이 유출됐다면 [사고 절차](security-guide.md)를 먼저 따른다. |
| 잘못된 브랜치 | switch를 반복하기 전에 상태를 확인한다. 작업이 섞였거나 이미 공유했다면 변경 목록과 의도한 기준을 팀과 확인한다. 브랜치를 강제 삭제하지 않는다. |
| 충돌 | status에서 충돌 파일을 찾고 양쪽 의도를 확인한다. 편집 후 충돌 표시 제거, 파일별 diff, 테스트를 확인한다. 시작 전 상태가 불명확하면 담당자와 상의한다. |

좋은 스테이징은 파일별 diff 확인과 작은 변경이다. 피할 예는 무조건 전체 스테이지, 강제 푸시, `reset --hard`로 정리하는 것이다. 공유된 단일 commit을 되돌릴 때는 승인된 복구 브랜치에서 git revert 뒤에 확인한 commit ID를 전달한다. 이 명령은 변경을 상쇄하는 새 commit을 만들 수 있다. verify와 리뷰를 거쳐 복구 PR로 올린다. merge commit의 부모 선택과 충돌 중단은 팀 리더와 확인한다. 제출 전 승인된 commit과 시연 결과를 연결한다.

**Claude Code 연습** — “README와 지침을 읽고 status·diff에서 내가 수정한 파일과 미추적 파일을 구분해줘. 실행 전 제안만 하고, 작업 분리가 어렵다면 Issue 초안을 제안해줘.” 사람이 staged diff를 직접 보고 변경 경계와 테스트를 확인한다.

- [ ] 예시에서 어떤 내용이 편집·스테이지·commit·원격 단계에 있는지 구별한다.
- [ ] 문제 시 변경을 보존하고 승인 전에 공유 상태부터 확인한다.

[Git 기본 개념](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) · [팀 기여 기준](../../CONTRIBUTING.md)
