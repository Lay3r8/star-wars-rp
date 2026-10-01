import uuid

from sqlalchemy import DateTime, ForeignKeyConstraint, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class DomainEvent(Base):
    __tablename__ = "domain_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["campaign_id", "actor_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_domain_event_actor_membership",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    actor_principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    occurred_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
