import uuid

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class CustomD20CharacterProfile(Base):
    __tablename__ = "custom_d20_character_profile"
    __table_args__ = (
        ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            ondelete="CASCADE",
            name="fk_d20_profile_character",
        ),
        UniqueConstraint("campaign_id", "character_id", name="uq_d20_profile_campaign_character"),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    slicing_modifier: Mapped[int] = mapped_column(nullable=False)
