from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)


class PrincipalOut(BaseModel):
    id: uuid.UUID
    username: str


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CampaignOut(BaseModel):
    id: uuid.UUID
    name: str
    role: Literal["GM", "PLAYER"]


class AddPlayerRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)


class MemberOut(BaseModel):
    principal_id: uuid.UUID
    username: str
    role: Literal["GM", "PLAYER"]
    assigned_character_id: uuid.UUID | None = None


class AssignmentRequest(BaseModel):
    player_principal_id: uuid.UUID
    character_id: uuid.UUID


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slicing_modifier: int


class CharacterOut(BaseModel):
    id: uuid.UUID
    name: str
    slicing_modifier: int


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class LocationOut(BaseModel):
    id: uuid.UUID
    name: str


class KnowledgeFragmentCreate(BaseModel):
    claim_text: str = Field(min_length=1, max_length=4000)
    gm_veracity: Literal["TRUE", "FALSE", "UNKNOWN"]


class KnowledgeFragmentOut(BaseModel):
    id: uuid.UUID
    claim_text: str
    gm_veracity: Literal["TRUE", "FALSE", "UNKNOWN"]


class ResolutionCreate(BaseModel):
    actor_character_id: uuid.UUID
    context_location_id: uuid.UUID
    intent: str = Field(min_length=1, max_length=2000)
    risk: str = Field(min_length=1, max_length=2000)
    dc: int
    success_recipient_character_id: uuid.UUID
    success_fragment_id: uuid.UUID


class SuccessPreview(BaseModel):
    recipient_character_id: uuid.UUID
    recipient_name: str
    fragment_id: uuid.UUID
    claim_text: str


class ResolutionOut(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    actor_character_id: uuid.UUID
    context_location_id: uuid.UUID
    intent: str
    risk: str
    mechanic: str
    dc: int
    resolved_modifier: int
    state: str
    natural_roll: int | None
    total: int | None
    outcome: str | None
    failure_adjudication: str | None
    success_preview: SuccessPreview


class CloseFailureRequest(BaseModel):
    adjudication: str = Field(min_length=1, max_length=4000)


class PlayerKnowledgeOut(BaseModel):
    fragment_id: uuid.UUID
    state: Literal["AWARE"]
    claim_text: str


class PlayerCharacterOut(BaseModel):
    id: uuid.UUID
    name: str
    slicing_modifier: int


class PlayerProjectionOut(BaseModel):
    campaign_id: uuid.UUID
    character: PlayerCharacterOut
    knowledge: list[PlayerKnowledgeOut]


class HistoryItemOut(BaseModel):
    id: uuid.UUID
    event_type: str
    subject_id: uuid.UUID
    occurred_at: datetime
    message: str
