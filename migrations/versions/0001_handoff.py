"""Initial handoff schema. Explicit schema stays fixed as ORM evolves."""
from alembic import op
import sqlalchemy as sa
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("handoff_event", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("payload_hash", sa.String(64), nullable=False), sa.Column("payload", sa.JSON(), nullable=False))
    op.create_table("onboarding_case", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("candidate_id", sa.String(80), nullable=False, unique=True),
        sa.Column("employee_id", sa.String(80), nullable=False, unique=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("handoff_event.id"), nullable=False, unique=True),
        sa.Column("tasks", sa.JSON(), nullable=False))
    op.create_table("outbox", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("onboarding_case.id"), nullable=False, unique=True),
        sa.Column("action", sa.String(80), nullable=False), sa.Column("status", sa.String(20), nullable=False))
    op.create_table("mock_receipt", sa.Column("outbox_id", sa.String(36), sa.ForeignKey("outbox.id"), primary_key=True),
        sa.Column("result", sa.String(100), nullable=False))
    op.create_table("audit_record", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("onboarding_case.id"), nullable=False),
        sa.Column("actor", sa.String(80), nullable=False), sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("recorded_at", sa.String(40), nullable=False))

def downgrade():
    for name in ["audit_record", "mock_receipt", "outbox", "onboarding_case", "handoff_event"]:
        op.drop_table(name)
