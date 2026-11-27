import hashlib
import json
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .contracts import HireConfirmedEvent
from .persistence import HandoffEvent, OnboardingCase, Outbox, AuditRecord

class Conflict(Exception):
    pass

def confirm(factory, event: HireConfirmedEvent, actor: str) -> dict:
    """인증 계층이 확인한 액터의 승인을 원자적으로 저장한다."""
    payload = event.model_dump(mode="json")
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    event_id = str(event.event_id)
    try:
        with factory.begin() as session:
            previous = session.get(HandoffEvent, event_id)
            if previous:
                if previous.payload_hash != digest:
                    raise Conflict("event payload changed")
                case = session.scalar(select(OnboardingCase).where(OnboardingCase.event_id == event_id))
                return view(session, case)
            existing = session.scalar(select(OnboardingCase).where(OnboardingCase.candidate_id == event.candidate_id))
            if existing:
                raise Conflict("candidate already has onboarding; review required")
            case_id = str(uuid4())
            due = (event.confirmed_on + timedelta(days=2)).isoformat()
            session.add(HandoffEvent(id=event_id, payload_hash=digest, payload=payload))
            session.flush()
            case = OnboardingCase(id=case_id, candidate_id=event.candidate_id,
                employee_id=event.employee_id, event_id=event_id,
                tasks=[{"id": f"ON-{i:02}", "status": "PENDING", "due_on": due} for i in range(1, 4)])
            session.add(case)
            session.flush()
            session.add(Outbox(id=str(uuid4()), case_id=case_id))
            session.add(AuditRecord(id=str(uuid4()), case_id=case_id, actor=actor, payload_hash=digest))
            session.flush()
            return view(session, case)
    except IntegrityError as exc:
        # A simultaneous identical delivery may lose the unique-key race.
        # Retry from a fresh transaction so only identical payloads are replayed.
        with factory() as session:
            previous = session.get(HandoffEvent, event_id)
            case = session.scalar(select(OnboardingCase).where(OnboardingCase.event_id == event_id))
            if previous and case and previous.payload_hash == digest:
                return view(session, case)
        raise Conflict("unique constraint conflict; review required") from exc

def view(session, case: OnboardingCase) -> dict:
    outbox = session.scalar(select(Outbox).where(Outbox.case_id == case.id))
    return {"id": case.id, "candidate_id": case.candidate_id, "employee_id": case.employee_id,
        "tasks": case.tasks, "execution_status": outbox.status if outbox else "pending",
        "adapter_mode": "mock"}
