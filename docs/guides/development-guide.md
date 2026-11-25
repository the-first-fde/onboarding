# SDD로 작은 변경 계획하기

**학습 목표**는 확인한 요구와 가정을 구별하고, 구현 전에 관찰 가능한 완료 조건을 작성하는 것이다. 준비물은 [프로젝트 범위](../project-scope.md), 담당 README, [Spec 양식](../specs/template.md)과 [잠정 계약 양식](../contracts/template.md)이다.

SDD(Spec-Driven Development)는 요구사항을 명세(Spec)로 정리하고 구현과 테스트를 그 기준에 맞추는 방법이다. 요구사항은 필요한 결과, Acceptance Criteria(인수 조건)는 결과가 맞는지 관찰하는 방법, 구현 계획은 바꿀 파일·순서·검사다. DoR(Definition of Ready)은 착수 준비, DoD(Definition of Done)는 검증·리뷰·문서까지 끝났는지 판단하는 팀 기준이다. 선택한 설계의 이유는 ADR, 데이터 근거와 질문은 계약 문서에 둔다. [팀 기준](../../CONTRIBUTING.md)

## 실습 · Markdown 기술 확인과 고객사 요구 분리

1. 루트와 대상 README·CLAUDE.md, 관련 Issue·Spec·계약을 읽는다. 사실은 양식을 읽는 기술 검사가 있다는 점이다. 고객사가 요구하는 승인 문구는 미확정이다.
2. 기술 예제의 인수 조건을 “로컬 양식에 텍스트가 있으면 읽고, 비어 있으면 오류가 표시된다”로 잡는다. 실제 문안 규칙을 조건에 넣지 않는다. `PROVISIONAL`은 가정, `NEEDS_CLARIFICATION`은 답이 필요한 질문, `BLOCKED`는 그 답 없이는 진행할 수 없는 작업으로 표시한다.
3. 계획에 호출 코드·테스트 위치·영향과 제외 범위를 쓴다. 사람은 DoR로 확인하고 준비된 범위만 승인한다. 실제 변경이 필요할 때는 재현 실패 → 최소 구현 → 통과를 확인하고 README의 명령 변경을 함께 반영한다.
4. 아래 기존 기술 검사를 바탕으로 실제 출력과 미실행 조건을 기록한 뒤 독립 AI·CI·사람 리뷰로 넘긴다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_template_rejects_empty_content
```

루트에서 빈 Markdown의 오류 경로 하나를 선택한다. `::`는 정확한 테스트, `-q`는 요약, `--locked`는 잠금 파일 유지다. 한 건 통과가 목표다. 테스트를 찾지 못하면 파일과 이름을 확인한다. 이 테스트는 임시 양식만 만들고 저장소·원격을 수정하지 않는다.

**좋은 인수 조건**은 “빈 양식이 ValueError로 드러난다”처럼 확인할 수 있다. **개선할 조건**은 “AI가 올바른 준비 안내를 만든다”처럼 근거와 판정 기준이 빠진 문장이다. 샘플이 없어 막힌 항목은 [미확인 목록](../open-questions.md)과 [Issue 절차](github-guide.md)에 연결하고 안전한 기술 점검을 계속한다.

**Claude Code 연습** — “/plan-task로 담당 문서와 현재 Git 상태를 확인하고 사실·가정·검증 위치를 나눠줘. 변경은 계획 검토 후 진행해줘.” 사람이 요구→테스트 연결과 diff를 확인하고, AI에게 왜 해당 결과가 조건을 증명하는지 설명하도록 한다. 계약을 결정해야 하면 Issue 초안을 제안하도록 한다.

- [ ] 근거, 인수 조건, 구현 계획을 서로 다른 문장으로 설명한다.
- [ ] 기술 검증 결과와 미확정 업무 범위를 구분해 기록한다.

[GitHub의 인수 기준을 기록하는 Issue 양식](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue) · [테스트 실습](testing-guide.md)
