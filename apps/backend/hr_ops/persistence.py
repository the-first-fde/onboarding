import os
from datetime import datetime, timezone
from sqlalchemy import JSON, String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

class Base(DeclarativeBase):
    pass

class HandoffEvent(Base):
    __tablename__ = "handoff_event"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)

class OnboardingCase(Base):
    __tablename__ = "onboarding_case"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String(80), unique=True)
    employee_id: Mapped[str] = mapped_column(String(80), unique=True)
    event_id: Mapped[str] = mapped_column(ForeignKey("handoff_event.id"), unique=True)
    tasks: Mapped[list] = mapped_column(JSON)

class Outbox(Base):
    __tablename__ = "outbox"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("onboarding_case.id"), unique=True)
    action: Mapped[str] = mapped_column(String(80), default="mock-preparation-request")
    status: Mapped[str] = mapped_column(String(20), default="pending")

class MockReceipt(Base):
    __tablename__ = "mock_receipt"
    outbox_id: Mapped[str] = mapped_column(ForeignKey("outbox.id"), primary_key=True)
    result: Mapped[str] = mapped_column(String(100), default="mock-recorded-no-external-write")

class AuditRecord(Base):
    __tablename__ = "audit_record"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("onboarding_case.id"))
    actor: Mapped[str] = mapped_column(String(80))
    payload_hash: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[str] = mapped_column(String(40), default=lambda: datetime.now(timezone.utc).isoformat())

def database(url: str | None = None):
    target = url or os.getenv("DATABASE_URL", "sqlite:///./hr_ops.db")
    options = {"connect_args": {"check_same_thread": False}} if target.startswith("sqlite") else {}
    engine = create_engine(target, **options)
    return engine, sessionmaker(engine, expire_on_commit=False)
