import socket

import pytest


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    """모든 기술 검증에서 네트워크 연결을 실패시킨다."""

    def blocked(*args, **kwargs):
        raise AssertionError("Network is disabled in mock tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
