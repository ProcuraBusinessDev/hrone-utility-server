import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    sn: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    pin: Mapped[str | None] = mapped_column(String(100), nullable=True)

    attendance_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[str | None] = mapped_column(String(20))

    verify: Mapped[str | None] = mapped_column(String(20))

    raw: Mapped[str | None] = mapped_column(Text)
