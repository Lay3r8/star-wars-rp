import uuid

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class Entity(Base):
    __tablename__ = "entity"
    __table_args__ = (
        CheckConstraint("entity_type IN ('character', 'location')", name="ck_entity_type"),
        UniqueConstraint("campaign_id", "id", name="uq_entity_campaign_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
