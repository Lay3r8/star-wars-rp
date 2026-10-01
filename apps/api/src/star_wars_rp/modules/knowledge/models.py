import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class KnowledgeFragment(Base):
    __tablename__ = "knowledge_fragment"
    __table_args__ = (
        CheckConstraint("gm_veracity IN ('TRUE', 'FALSE', 'UNKNOWN')", name="ck_knowledge_veracity"),
        UniqueConstraint("campaign_id", "id", name="uq_knowledge_fragment_campaign_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    gm_veracity: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CharacterKnowledge(Base):
    __tablename__ = "character_knowledge"
    __table_args__ = (
        CheckConstraint("state = 'AWARE'", name="ck_character_knowledge_state"),
        ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            ondelete="CASCADE",
            name="fk_character_knowledge_character",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            ondelete="CASCADE",
            name="fk_character_knowledge_fragment",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    fragment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    state: Mapped[str] = mapped_column(String(16), nullable=False, default="AWARE")
    acquired_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
