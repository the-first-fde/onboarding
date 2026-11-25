import pytest
from fakes import FakeGitHub, FakeNotion


@pytest.fixture
def github():
    return FakeGitHub()


@pytest.fixture
def notion():
    return FakeNotion()
