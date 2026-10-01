import uuid

from sqlalchemy import ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class Contact(Base):
    __tablename__ = "contact"
    __table_args__ = (
        ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            ondelete="CASCADE",
            name="fk_contact_character",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_contact_location",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "prepared_fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            name="fk_contact_prepared_fragment",
        ),
        UniqueConstraint("campaign_id", "character_id", name="uq_contact_campaign_character"),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(240), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    gm_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    prepared_fragment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
