from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttendanceEventCreate(BaseModel):
    ts: datetime
    sn: str
    pin: str | None = None
    attendance_time: datetime
    status: str | None = None
    verify: str | None = None
    raw: str | None = None


class AttendanceEventResponse(AttendanceEventCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)