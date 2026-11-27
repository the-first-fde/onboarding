from datetime import date
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

OpaqueId = Annotated[str, Field(pattern=r"^[A-Za-z0-9-]{1,80}$")]

class HireConfirmedEvent(BaseModel):
    """승인 전 검증하는 비개인 핸드오프 allowlist."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1]
    event_type: Literal["HireConfirmedEvent"]
    event_id: UUID
    candidate_id: OpaqueId
    employee_id: OpaqueId
    confirmed_on: date
    start_on: date
    team_id: OpaqueId
    leader_id: OpaqueId
    employment_type: Literal["permanent", "contract"]
    work_mode: Literal["hybrid", "office", "remote"]
    probation_months: Annotated[int, Field(strict=True, ge=0, le=12)]
    experienced: StrictBool
    buddy_id: OpaqueId | None = None
    laptop_required: StrictBool | None = None
    source_refs: Annotated[list[OpaqueId], Field(min_length=1, max_length=10)]

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_on < self.confirmed_on:
            raise ValueError("start_on precedes confirmation")
        return self
