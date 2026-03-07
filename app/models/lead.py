"""Lead model for storing tattoo client intake data."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class LeadStatus(str, enum.Enum):
    """Possible lead status values."""

    NEW = "new"
    AWAITING_CLIENT_REPLY = "awaiting_client_reply"
    IN_CONVERSATION = "in_conversation"
    SCHEDULED = "scheduled"
    CLOSED = "closed"
    LOST = "lost"


class Lead(Base):
    """Lead model - stores analyzed tattoo client messages."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_message: Mapped[str] = mapped_column(Text, nullable=False)
    tattoo_idea: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    missing_information: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Debug-friendly representation."""
        return f"<Lead id={self.id} status={self.status}>"
