import uuid

from sqlalchemy import ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class Location(Base):
    __tablename__ = "location"
    __table_args__ = (
        ForeignKeyConstraint(
            ["campaign_id", "entity_id"],
            ["entity.campaign_id", "entity.id"],
            ondelete="CASCADE",
            name="fk_location_entity",
        ),
        UniqueConstraint("campaign_id", "entity_id", name="uq_location_campaign_entity"),
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
