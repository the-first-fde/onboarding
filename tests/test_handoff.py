import json
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func, event as sa_event
from hr_ops.api import create_app
from hr_ops.persistence import HandoffEvent, OnboardingCase, Outbox, AuditRecord, MockReceipt
from hr_ops.worker import tick

ROOT = Path(__file__).resolve().parents[1]
AUTH = {"Authorization": "Bearer synthetic-test-only"}

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_HR_TOKEN", "synthetic-test-only")
    monkeypatch.setenv("ADAPTER_MODE", "mock")
    with TestClient(create_app(f"sqlite:///{tmp_path / 'test.db'}")) as c:
        yield c

@pytest.fixture
def payload():
    return json.loads((ROOT / "data/fixtures/hire-confirmed.json").read_text())

def count(client, model):
    with client.app.state.factory() as s:
        return s.scalar(select(func.count()).select_from(model))

def test_approval_to_case_outbox_and_idempotent_worker(client, payload):
    result = client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    assert result.status_code == 200
    case = result.json()
    assert len(case['tasks']) == 3
    assert all(t['due_on'] == '2026-08-12' and t['status'] == 'PENDING' for t in case['tasks'])
    duplicate = client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    assert duplicate.json()['id'] == case['id']
    for model in [HandoffEvent, OnboardingCase, Outbox, AuditRecord]:
        assert count(client, model) == 1
    assert client.post('/api/mock-worker/tick', json={}, headers=AUTH).json()['processed'] == 1
    assert client.post('/api/mock-worker/tick', json={}, headers=AUTH).json()['processed'] == 0
    assert count(client, MockReceipt) == 1
    assert client.get('/api/cases/'+case['id'], headers=AUTH).json()['execution_status'] == 'succeeded'
    with client.app.state.factory() as s:
        audit = s.scalar(select(AuditRecord))
        saved = s.scalar(select(HandoffEvent))
        assert audit.actor == 'demo-hr' and audit.payload_hash == saved.payload_hash
        assert saved.payload['buddy_id'] is None and saved.payload['laptop_required'] is None

def test_unauthorized_never_creates_case(client, payload):
    assert client.post('/api/hire-confirmations', json=payload).status_code == 403
    assert client.get('/api/cases').status_code == 403
    assert client.post('/api/mock-worker/tick', json={}).status_code == 403
    assert count(client, OnboardingCase) == 0

@pytest.mark.parametrize('key',['salary','interview_score','reference_text','hr_approved'])
def test_sensitive_fields_rejected_without_echo(client, payload, key):
    payload[key] = 'SENSITIVE-MARKER'
    r = client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    assert r.status_code == 422
    assert 'SENSITIVE-MARKER' not in r.text and key not in r.text
    assert count(client, HandoffEvent) == 0

def test_final_pass_is_not_confirmation(client, payload):
    payload['event_type'] = 'FinalPassNotified'
    assert client.post('/api/hire-confirmations', json=payload, headers=AUTH).status_code == 422
    assert count(client, OnboardingCase) == 0

def test_conflicts_do_not_mutate_existing(client, payload):
    client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    payload['start_on'] = '2026-09-02'
    assert client.post('/api/hire-confirmations', json=payload, headers=AUTH).status_code == 409
    payload['event_id'] = str(uuid4())
    assert client.post('/api/hire-confirmations', json=payload, headers=AUTH).status_code == 409
    assert count(client, Outbox) == 1

@pytest.mark.parametrize('field,value',[('start_on','2026-08-01'),('source_refs',[]),('candidate_id','person@example.com'),('laptop_required','false')])
def test_invalid_contract(client, payload, field, value):
    payload[field] = value
    assert client.post('/api/hire-confirmations', json=payload, headers=AUTH).status_code == 422

def test_database_failure_rolls_back_entire_handoff(client, payload):
    engine = client.app.state.factory.kw['bind']
    def fail_on_audit(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith('INSERT INTO audit_record'):
            raise RuntimeError('synthetic DB failure')
    sa_event.listen(engine, 'before_cursor_execute', fail_on_audit)
    try:
        with pytest.raises(RuntimeError, match='synthetic DB failure'):
            client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    finally:
        sa_event.remove(engine, 'before_cursor_execute', fail_on_audit)
    for model in [HandoffEvent, OnboardingCase, Outbox, AuditRecord]:
        assert count(client, model) == 0

def test_worker_restart_and_real_adapter_fail_closed(client, payload):
    client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    from hr_ops.persistence import database
    _, restarted = database(str(client.app.state.factory.kw['bind'].url))
    assert tick(restarted) == 1
    assert tick(restarted) == 0
    with pytest.raises(RuntimeError):
        tick(restarted, 'notion')

def test_catalog_and_synthetic_replay():
    catalog = json.loads((ROOT/'workflows/onboarding-v3.2.json').read_text())
    assert {t['id'] for t in catalog['tasks']} == {f'ON-{i:02}' for i in range(1,57)}
    assert all(t['source_ref'] and t['completion_criterion'] for t in catalog['tasks'])
    events = json.loads((ROOT/'data/replay_events/handoff.json').read_text())['events']
    assert not any(e['kind']=='HireConfirmedEvent' for e in events if e['observed_on'] <= '2026-08-04')
    assert len([e for e in events if e['kind']=='HireConfirmedEvent' and e['observed_on']<='2026-08-10']) == 1

def test_worker_receipt_failure_rolls_back_status(client, payload):
    client.post('/api/hire-confirmations', json=payload, headers=AUTH)
    engine = client.app.state.factory.kw['bind']
    def fail_receipt(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith('INSERT INTO mock_receipt'):
            raise RuntimeError('synthetic receipt failure')
    sa_event.listen(engine, 'before_cursor_execute', fail_receipt)
    try:
        with pytest.raises(RuntimeError, match='synthetic receipt failure'):
            tick(client.app.state.factory)
    finally:
        sa_event.remove(engine, 'before_cursor_execute', fail_receipt)
    with client.app.state.factory() as s:
        assert s.scalar(select(Outbox)).status == 'pending'
    assert count(client, MockReceipt) == 0
    assert tick(client.app.state.factory) == 1
    assert count(client, MockReceipt) == 1
