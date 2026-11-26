import pytest

from hr_onboarding.workflows.preparation_checklist import (
    Applicability,
    HoldReason,
    NewHire,
    evaluate_condition,
)


@pytest.mark.parametrize(
    ("fixture", "condition", "expected", "reason"),
    [
        ("hire_experienced_laptop", "", Applicability.APPLICABLE, None),
        ("hire_experienced_laptop", "경력", Applicability.APPLICABLE, None),
        ("hire_new_no_laptop", "경력", Applicability.NOT_APPLICABLE, None),
        ("hire_experienced_laptop", "노트북 지급", Applicability.APPLICABLE, None),
        ("hire_new_no_laptop", "노트북 지급", Applicability.NOT_APPLICABLE, None),
        (
            "hire_laptop_undecided",
            "노트북 지급",
            Applicability.UNDECIDED,
            HoldReason.LAPTOP_UNDECIDED,
        ),
    ],
)
def test_condition(
    request: pytest.FixtureRequest,
    fixture: str,
    condition: str,
    expected: Applicability,
    reason: HoldReason | None,
) -> None:
    hire: NewHire = request.getfixturevalue(fixture)
    assert evaluate_condition(condition, hire) == (expected, reason)


def test_unknown_condition(hire_experienced_laptop: NewHire) -> None:
    with pytest.raises(ValueError):
        evaluate_condition("알 수 없는 조건", hire_experienced_laptop)
