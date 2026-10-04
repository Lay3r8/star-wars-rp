from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field


CombatStatus = Literal["ACTIVE", "ESCAPED", "PATROL_NEUTRALIZED", "INCAPACITATED"]
CombatActor = Literal["PLAYER", "PATROL"]


class CombatEncounterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_character_id: uuid.UUID
    location_id: uuid.UUID


class CombatCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_round: int = Field(ge=1)


class CombatLastActionOut(BaseModel):
    action: Literal["PLAYER_ATTACK", "ESCAPE", "PATROL_ATTACK"]
    acting_side: Literal["PLAYER", "PATROL"]
    round: int
    natural_roll: int | None = None
    modifier: int | None = None
    total: int | None = None
    defence: int | None = None
    result: Literal["HIT", "MISS"] | None = None
    damage: int | None = None
    vitality_before: int | None = None
    vitality_after: int | None = None
    strength_before: int | None = None
    strength_after: int | None = None
    escape_progress_before: int | None = None
    escape_progress_after: int | None = None
    terminal_status: CombatStatus | None = None


class PlayerCombatEncounterOut(BaseModel):
    encounter_id: uuid.UUID
    objective: str
    status: CombatStatus
    round: int
    current_actor: CombatActor | None
    player_character_id: uuid.UUID
    player_character_name: str
    player_vitality_initial: int
    player_vitality: int
    hostile_name: str
    patrol_strength_initial: int
    patrol_strength: int
    patrol_status: Literal["ACTIVE", "NEUTRALIZED"]
    escape_progress: int
    escape_target: int
    can_attack: bool
    can_escape: bool
    last_action: CombatLastActionOut | None
    ended_at: datetime | None


class GmCombatEncounterOut(BaseModel):
    encounter_id: uuid.UUID
    objective: str
    status: CombatStatus
    round: int
    current_actor: CombatActor | None
    location_id: uuid.UUID
    location_name: str
    player_character_id: uuid.UUID
    player_character_name: str
    player_vitality_initial: int
    player_vitality: int
    hostile_name: str
    patrol_strength_initial: int
    patrol_strength: int
    patrol_status: Literal["ACTIVE", "NEUTRALIZED"]
    escape_progress: int
    escape_target: int
    can_resolve_patrol_attack: bool
    last_action: CombatLastActionOut | None
    ended_at: datetime | None
