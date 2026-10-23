from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendance import AttendanceEvent
from app.schemas.attendance import AttendanceEventCreate


def create_attendance_event(
    db: Session,
    payload: AttendanceEventCreate,
) -> AttendanceEvent:
    event = AttendanceEvent(**payload.model_dump())

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_recent_attendance_events(
    db: Session,
    limit: int = 100,
) -> list[AttendanceEvent]:
    statement = (
        select(AttendanceEvent)
        .order_by(AttendanceEvent.ts.desc())
        .limit(limit)
    )

    return list(db.scalars(statement).all())