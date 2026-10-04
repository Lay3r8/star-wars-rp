from datetime import datetime, timezone
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import ROLE_PLAYER, require_gm, require_membership
from star_wars_rp.application.history import append_domain_event
from star_wars_rp.errors import Conflict, InvalidOperation, NotFound
from star_wars_rp.modules.campaigns.models import CampaignMembership, PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.combat.models import CombatEncounter
from star_wars_rp.modules.combat.rules import advance_escape, apply_fixed_damage, resolve_combat_attack
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.world.models import Location


ACTIVE = "ACTIVE"
ESCAPED = "ESCAPED"
PATROL_NEUTRALIZED = "PATROL_NEUTRALIZED"
INCAPACITATED = "INCAPACITATED"
PLAYER = "PLAYER"
PATROL = "PATROL"

OBJECTIVE = "Escape the Imperial Patrol"
HOSTILE_NAME = "Imperial Patrol"
PLAYER_ATTACK_MODIFIER = 3
PLAYER_DEFENCE = 12
PLAYER_DAMAGE = 2
PLAYER_VITALITY = 4
PATROL_ATTACK_MODIFIER = 2
PATROL_DEFENCE = 12
PATROL_DAMAGE = 2
PATROL_STRENGTH = 4
ESCAPE_TARGET = 3

COMBAT_EVENT_TYPES = (
    "combat.player_attack_resolved",
    "combat.escape_advanced",
    "combat.patrol_attack_resolved",
)
ACTIVE_UNIQUE_INDEX = "uq_combat_encounter_active_character"


def roll_d20() -> int:
    return secrets.randbelow(20) + 1


def _encounter(
    db: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    *,
    for_update: bool = False,
) -> CombatEncounter:
    stmt = select(CombatEncounter).where(
        CombatEncounter.campaign_id == campaign_id,
        CombatEncounter.id == encounter_id,
    )
    if for_update:
        stmt = stmt.with_for_update()
    encounter = db.scalar(stmt)
    if encounter is None:
        raise NotFound("Combat encounter not found in campaign")
    return encounter


def _player_assignment(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> PlayerCharacterAssignment:
    require_membership(db, principal_id, campaign_id, ROLE_PLAYER)
    assignment = db.get(
        PlayerCharacterAssignment,
        {"campaign_id": campaign_id, "player_principal_id": principal_id},
    )
    if assignment is None:
        raise NotFound("No character assignment for Player")
    return assignment


def _assigned_player_for_character(
    db: Session,
    campaign_id: uuid.UUID,
    character_id: uuid.UUID,
) -> PlayerCharacterAssignment | None:
    return db.scalar(
        select(PlayerCharacterAssignment)
        .join(
            CampaignMembership,
            (CampaignMembership.campaign_id == PlayerCharacterAssignment.campaign_id)
            & (CampaignMembership.principal_id == PlayerCharacterAssignment.player_principal_id),
        )
        .where(
            PlayerCharacterAssignment.campaign_id == campaign_id,
            PlayerCharacterAssignment.character_id == character_id,
            CampaignMembership.role == ROLE_PLAYER,
        )
    )


def _require_turn(encounter: CombatEncounter, actor: str, expected_round: int) -> None:
    if encounter.status != ACTIVE:
        raise Conflict("Combat encounter has already ended")
    if encounter.round != expected_round:
        raise Conflict("Combat state changed; reload the current round")
    if encounter.current_actor != actor:
        raise Conflict("Combat state changed; it is not this side's turn")


def _terminal(encounter: CombatEncounter, status: str) -> None:
    encounter.status = status
    encounter.current_actor = None
    encounter.ended_at = datetime.now(timezone.utc)


def _last_action(db: Session, encounter: CombatEncounter) -> dict | None:
    event = db.scalar(
        select(DomainEvent)
        .where(
            DomainEvent.campaign_id == encounter.campaign_id,
            DomainEvent.subject_id == encounter.id,
            DomainEvent.event_type.in_(COMBAT_EVENT_TYPES),
        )
        .order_by(DomainEvent.occurred_at.desc(), DomainEvent.id.desc())
        .limit(1)
    )
    if event is None:
        return None

    payload = event.payload
    common = {
        "round": payload.get("round"),
        "terminal_status": payload.get("terminal_status"),
    }
    if event.event_type == "combat.player_attack_resolved":
        return {
            "action": "PLAYER_ATTACK",
            "acting_side": PLAYER,
            "natural_roll": payload.get("natural_roll"),
            "modifier": payload.get("modifier"),
            "total": payload.get("total"),
            "defence": payload.get("defence"),
            "result": payload.get("result"),
            "damage": payload.get("damage"),
            "strength_before": payload.get("strength_before"),
            "strength_after": payload.get("strength_after"),
            **common,
        }
    if event.event_type == "combat.patrol_attack_resolved":
        return {
            "action": "PATROL_ATTACK",
            "acting_side": PATROL,
            "natural_roll": payload.get("natural_roll"),
            "modifier": payload.get("modifier"),
            "total": payload.get("total"),
            "defence": payload.get("defence"),
            "result": payload.get("result"),
            "damage": payload.get("damage"),
            "vitality_before": payload.get("vitality_before"),
            "vitality_after": payload.get("vitality_after"),
            **common,
        }
    return {
        "action": "ESCAPE",
        "acting_side": PLAYER,
        "escape_progress_before": payload.get("progress_before"),
        "escape_progress_after": payload.get("progress_after"),
        **common,
    }


def _base_projection(
    db: Session,
    encounter: CombatEncounter,
    character_name: str,
) -> dict:
    return {
        "encounter_id": encounter.id,
        "objective": encounter.objective,
        "status": encounter.status,
        "round": encounter.round,
        "current_actor": encounter.current_actor,
        "player_character_id": encounter.player_character_id,
        "player_character_name": character_name,
        "player_vitality_initial": encounter.player_vitality_initial,
        "player_vitality": encounter.player_vitality,
        "hostile_name": encounter.hostile_name,
        "patrol_strength_initial": encounter.patrol_strength_initial,
        "patrol_strength": encounter.patrol_strength,
        "patrol_status": "NEUTRALIZED" if encounter.patrol_strength == 0 else "ACTIVE",
        "escape_progress": encounter.escape_progress,
        "escape_target": encounter.escape_target,
        "last_action": _last_action(db, encounter),
        "ended_at": encounter.ended_at,
    }


def _character_name(db: Session, encounter: CombatEncounter) -> str:
    name = db.scalar(
        select(Character.name).where(
            Character.campaign_id == encounter.campaign_id,
            Character.entity_id == encounter.player_character_id,
        )
    )
    if name is None:
        raise InvalidOperation("Combat encounter Player Character is unavailable")
    return name


def player_encounter_projection(
    db: Session,
    player_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID | None = None,
) -> dict | None:
    assignment = _player_assignment(db, player_principal_id, campaign_id)
    stmt = select(CombatEncounter).where(
        CombatEncounter.campaign_id == campaign_id,
        CombatEncounter.player_character_id == assignment.character_id,
    )
    if encounter_id is not None:
        stmt = stmt.where(CombatEncounter.id == encounter_id)
    else:
        stmt = stmt.order_by(CombatEncounter.created_at.desc(), CombatEncounter.id.desc()).limit(1)
    encounter = db.scalar(stmt)
    if encounter is None:
        return None

    result = _base_projection(db, encounter, _character_name(db, encounter))
    can_act = encounter.status == ACTIVE and encounter.current_actor == PLAYER
    result.update({"can_attack": can_act, "can_escape": can_act})
    return result


def gm_encounter_projection(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID | None = None,
) -> dict | None:
    require_gm(db, gm_principal_id, campaign_id)
    stmt = select(CombatEncounter).where(CombatEncounter.campaign_id == campaign_id)
    if encounter_id is not None:
        stmt = stmt.where(CombatEncounter.id == encounter_id)
    else:
        stmt = stmt.order_by(CombatEncounter.created_at.desc(), CombatEncounter.id.desc()).limit(1)
    encounter = db.scalar(stmt)
    if encounter is None:
        return None

    location_name = db.scalar(
        select(Location.name).where(
            Location.campaign_id == campaign_id,
            Location.entity_id == encounter.location_id,
        )
    )
    if location_name is None:
        raise InvalidOperation("Combat encounter Location is unavailable")

    result = _base_projection(db, encounter, _character_name(db, encounter))
    result.update(
        {
            "location_id": encounter.location_id,
            "location_name": location_name,
            "can_resolve_patrol_attack": (
                encounter.status == ACTIVE and encounter.current_actor == PATROL
            ),
        }
    )
    return result


def create_encounter(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    player_character_id: uuid.UUID,
    location_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)

    character = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == player_character_id,
        )
    )
    if character is None:
        raise NotFound("Character not found in campaign")

    location = db.scalar(
        select(Location).where(
            Location.campaign_id == campaign_id,
            Location.entity_id == location_id,
        )
    )
    if location is None:
        raise NotFound("Location not found in campaign")

    if _assigned_player_for_character(db, campaign_id, player_character_id) is None:
        raise InvalidOperation("Combat Character must be assigned to a Player")

    existing = db.scalar(
        select(CombatEncounter).where(
            CombatEncounter.campaign_id == campaign_id,
            CombatEncounter.player_character_id == player_character_id,
            CombatEncounter.status == ACTIVE,
        )
    )
    if existing is not None:
        raise Conflict("An active combat encounter already exists for this Character")

    encounter = CombatEncounter(
        campaign_id=campaign_id,
        location_id=location_id,
        player_character_id=player_character_id,
        objective=OBJECTIVE,
        status=ACTIVE,
        round=1,
        current_actor=PLAYER,
        player_attack_modifier=PLAYER_ATTACK_MODIFIER,
        player_defence=PLAYER_DEFENCE,
        player_attack_damage=PLAYER_DAMAGE,
        player_vitality_initial=PLAYER_VITALITY,
        player_vitality=PLAYER_VITALITY,
        hostile_name=HOSTILE_NAME,
        patrol_attack_modifier=PATROL_ATTACK_MODIFIER,
        patrol_defence=PATROL_DEFENCE,
        patrol_attack_damage=PATROL_DAMAGE,
        patrol_strength_initial=PATROL_STRENGTH,
        patrol_strength=PATROL_STRENGTH,
        escape_progress=0,
        escape_target=ESCAPE_TARGET,
        created_by_principal_id=gm_principal_id,
    )
    db.add(encounter)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint_name == ACTIVE_UNIQUE_INDEX or ACTIVE_UNIQUE_INDEX in str(exc.orig):
            raise Conflict("An active combat encounter already exists for this Character") from exc
        raise

    return gm_encounter_projection(db, gm_principal_id, campaign_id, encounter.id)  # type: ignore[return-value]


def _player_locked_encounter(
    db: Session,
    player_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
) -> CombatEncounter:
    assignment = _player_assignment(db, player_principal_id, campaign_id)
    encounter = _encounter(db, campaign_id, encounter_id, for_update=True)
    if encounter.player_character_id != assignment.character_id:
        raise NotFound("Combat encounter not found for assigned Player Character")
    return encounter


def player_attack(
    db: Session,
    player_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    expected_round: int,
) -> dict:
    encounter = _player_locked_encounter(db, player_principal_id, campaign_id, encounter_id)
    _require_turn(encounter, PLAYER, expected_round)

    natural_roll = roll_d20()
    total, result, damage = resolve_combat_attack(
        natural_roll,
        encounter.player_attack_modifier,
        encounter.patrol_defence,
        encounter.player_attack_damage,
    )
    strength_before = encounter.patrol_strength
    if damage:
        encounter.patrol_strength = apply_fixed_damage(encounter.patrol_strength, damage)

    terminal_status = None
    if encounter.patrol_strength == 0:
        terminal_status = PATROL_NEUTRALIZED
        _terminal(encounter, terminal_status)
    else:
        encounter.current_actor = PATROL

    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="combat.player_attack_resolved",
        subject_type="combat_encounter",
        subject_id=encounter.id,
        actor_principal_id=player_principal_id,
        payload={
            "encounter_id": str(encounter.id),
            "round": encounter.round,
            "natural_roll": natural_roll,
            "modifier": encounter.player_attack_modifier,
            "total": total,
            "defence": encounter.patrol_defence,
            "result": result,
            "damage": damage,
            "strength_before": strength_before,
            "strength_after": encounter.patrol_strength,
            "terminal_status": terminal_status,
        },
    )
    db.commit()
    projection = player_encounter_projection(db, player_principal_id, campaign_id, encounter.id)
    if projection is None:
        raise InvalidOperation("Combat encounter became unavailable after Player Attack")
    return projection


def player_escape(
    db: Session,
    player_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    expected_round: int,
) -> dict:
    encounter = _player_locked_encounter(db, player_principal_id, campaign_id, encounter_id)
    _require_turn(encounter, PLAYER, expected_round)

    progress_before = encounter.escape_progress
    encounter.escape_progress = advance_escape(encounter.escape_progress, encounter.escape_target)

    terminal_status = None
    if encounter.escape_progress >= encounter.escape_target:
        terminal_status = ESCAPED
        _terminal(encounter, terminal_status)
    else:
        encounter.current_actor = PATROL

    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="combat.escape_advanced",
        subject_type="combat_encounter",
        subject_id=encounter.id,
        actor_principal_id=player_principal_id,
        payload={
            "encounter_id": str(encounter.id),
            "round": encounter.round,
            "progress_before": progress_before,
            "progress_after": encounter.escape_progress,
            "escape_target": encounter.escape_target,
            "terminal_status": terminal_status,
        },
    )
    db.commit()
    projection = player_encounter_projection(db, player_principal_id, campaign_id, encounter.id)
    if projection is None:
        raise InvalidOperation("Combat encounter became unavailable after Escape")
    return projection


def patrol_attack(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    expected_round: int,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    encounter = _encounter(db, campaign_id, encounter_id, for_update=True)
    _require_turn(encounter, PATROL, expected_round)

    natural_roll = roll_d20()
    total, result, damage = resolve_combat_attack(
        natural_roll,
        encounter.patrol_attack_modifier,
        encounter.player_defence,
        encounter.patrol_attack_damage,
    )
    vitality_before = encounter.player_vitality
    if damage:
        encounter.player_vitality = apply_fixed_damage(encounter.player_vitality, damage)

    terminal_status = None
    if encounter.player_vitality == 0:
        terminal_status = INCAPACITATED
        _terminal(encounter, terminal_status)
    else:
        encounter.round += 1
        encounter.current_actor = PLAYER

    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="combat.patrol_attack_resolved",
        subject_type="combat_encounter",
        subject_id=encounter.id,
        actor_principal_id=gm_principal_id,
        payload={
            "encounter_id": str(encounter.id),
            "round": expected_round,
            "natural_roll": natural_roll,
            "modifier": encounter.patrol_attack_modifier,
            "total": total,
            "defence": encounter.player_defence,
            "result": result,
            "damage": damage,
            "vitality_before": vitality_before,
            "vitality_after": encounter.player_vitality,
            "terminal_status": terminal_status,
        },
    )
    db.commit()
    projection = gm_encounter_projection(db, gm_principal_id, campaign_id, encounter.id)
    if projection is None:
        raise InvalidOperation("Combat encounter became unavailable after Patrol Attack")
    return projection
