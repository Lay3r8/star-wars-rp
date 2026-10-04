import type { FormEvent, ReactNode } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";

type CombatStatus = "ACTIVE" | "ESCAPED" | "PATROL_NEUTRALIZED" | "INCAPACITATED";
type CombatActor = "PLAYER" | "PATROL" | null;

type CombatLastAction = {
  action: "PLAYER_ATTACK" | "ESCAPE" | "PATROL_ATTACK";
  acting_side: "PLAYER" | "PATROL";
  round: number;
  natural_roll: number | null;
  modifier: number | null;
  total: number | null;
  defence: number | null;
  result: "HIT" | "MISS" | null;
  damage: number | null;
  vitality_before: number | null;
  vitality_after: number | null;
  strength_before: number | null;
  strength_after: number | null;
  escape_progress_before: number | null;
  escape_progress_after: number | null;
  terminal_status: CombatStatus | null;
};

type CombatBase = {
  encounter_id: string;
  objective: string;
  status: CombatStatus;
  round: number;
  current_actor: CombatActor;
  player_character_id: string;
  player_character_name: string;
  player_vitality_initial: number;
  player_vitality: number;
  hostile_name: string;
  patrol_strength_initial: number;
  patrol_strength: number;
  patrol_status: "ACTIVE" | "NEUTRALIZED";
  escape_progress: number;
  escape_target: number;
  last_action: CombatLastAction | null;
  ended_at: string | null;
};

type PlayerCombat = CombatBase & {
  can_attack: boolean;
  can_escape: boolean;
};

type GmCombat = CombatBase & {
  location_id: string;
  location_name: string;
  can_resolve_patrol_attack: boolean;
};

type Character = { id: string; name: string };
type Location = { id: string; name: string };

function terminalLabel(status: CombatStatus): string | null {
  if (status === "ESCAPED") return "Escaped";
  if (status === "PATROL_NEUTRALIZED") return "Patrol neutralized — escape secured";
  if (status === "INCAPACITATED") return "Incapacitated";
  return null;
}

function actionFeedback(action: CombatLastAction, escapeTarget: number): ReactNode {
  if (action.action === "ESCAPE") {
    return (
      <>
        Escape Progress {action.escape_progress_before} → {action.escape_progress_after} / {escapeTarget}
      </>
    );
  }

  const targetState = action.action === "PLAYER_ATTACK"
    ? `Group Strength ${action.strength_before} → ${action.strength_after}`
    : `Vitality ${action.vitality_before} → ${action.vitality_after}`;
  const actor = action.action === "PLAYER_ATTACK" ? "Globox" : "Patrol";

  return (
    <>
      {actor} roll {action.natural_roll} {action.modifier !== null && action.modifier >= 0 ? "+" : ""}
      {action.modifier} = {action.total} vs Defence {action.defence} — <strong>{action.result}</strong>
      {action.damage ? ` — ${action.damage} damage — ${targetState}` : " — No damage"}
    </>
  );
}

function CombatState({
  encounter,
  busy,
  error,
  actions,
}: {
  encounter: CombatBase;
  busy: boolean;
  error: string | null;
  actions: ReactNode;
}) {
  const terminal = terminalLabel(encounter.status);
  const turn = encounter.current_actor === "PLAYER"
    ? encounter.player_character_name
    : encounter.current_actor === "PATROL"
      ? encounter.hostile_name
      : "Encounter ended";

  return (
    <section className="panel combat-panel" aria-label="Combat encounter">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Personal-scale combat</p>
          <h3>{encounter.objective}</h3>
        </div>
        <span className="status-pill">Round {encounter.round}</span>
      </div>

      <p className="combat-turn"><strong>Current turn:</strong> {turn}</p>

      <div className="combat-stats" aria-label="Combat state">
        <div>
          <span>{encounter.player_character_name} Vitality</span>
          <strong>{encounter.player_vitality} / {encounter.player_vitality_initial}</strong>
        </div>
        <div>
          <span>{encounter.hostile_name} Strength</span>
          <strong>{encounter.patrol_strength} / {encounter.patrol_strength_initial}</strong>
        </div>
        <div>
          <span>Escape Progress</span>
          <strong>{encounter.escape_progress} / {encounter.escape_target}</strong>
        </div>
      </div>

      {encounter.last_action && (
        <div className="combat-feedback" role="status">
          <strong>Latest action</strong>
          <p>{actionFeedback(encounter.last_action, encounter.escape_target)}</p>
        </div>
      )}

      {terminal ? (
        <div className="combat-terminal" role="status">
          <strong>{terminal}</strong>
        </div>
      ) : (
        <div className="action-row combat-actions">{actions}</div>
      )}

      {busy && <p className="muted" role="status">Resolving action…</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}

export function PlayerCombatWorkspace({ campaignId }: { campaignId: string }) {
  const [encounter, setEncounter] = useState<PlayerCombat | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setEncounter(
        await api<PlayerCombat | null>(
          `/api/player/campaigns/${campaignId}/combat-encounters/latest`,
        ),
      );
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load combat state");
    }
  }, [campaignId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const waitingForGm = !encounter || (
      encounter.status === "ACTIVE" && encounter.current_actor === "PATROL"
    );
    if (!waitingForGm) return;
    const timer = window.setInterval(() => void refresh(), 1000);
    return () => window.clearInterval(timer);
  }, [encounter, refresh]);

  async function mutate(command: "attack" | "escape") {
    if (!encounter || busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api<PlayerCombat>(
        `/api/player/campaigns/${campaignId}/combat-encounters/${encounter.encounter_id}/${command}`,
        {
          method: "POST",
          body: JSON.stringify({ expected_round: encounter.round }),
        },
      );
      setEncounter(updated);
    } catch {
      await refresh();
      setError("Combat state changed. The current encounter has been reloaded.");
    } finally {
      setBusy(false);
    }
  }

  if (!encounter) {
    return (
      <section className="panel combat-panel" aria-label="Combat encounter">
        <p className="eyebrow">Personal-scale combat</p>
        <h3>No active combat encounter</h3>
        <p className="muted">Waiting for the GM to start an encounter.</p>
        {error && <p className="error" role="alert">{error}</p>}
      </section>
    );
  }

  return (
    <CombatState
      encounter={encounter}
      busy={busy}
      error={error}
      actions={
        encounter.current_actor === "PLAYER" ? (
          <>
            <button disabled={busy || !encounter.can_attack} onClick={() => void mutate("attack")}>Attack</button>
            <button disabled={busy || !encounter.can_escape} onClick={() => void mutate("escape")}>Escape</button>
          </>
        ) : (
          <span className="muted">Waiting for the GM to resolve the Imperial Patrol attack.</span>
        )
      }
    />
  );
}

export function GmCombatWorkspace({
  campaignId,
  characters,
  locations,
  assignedCharacterIds,
}: {
  campaignId: string;
  characters: Character[];
  locations: Location[];
  assignedCharacterIds: string[];
}) {
  const [encounter, setEncounter] = useState<GmCombat | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const assignedCharacters = useMemo(
    () => characters.filter((character) => assignedCharacterIds.includes(character.id)),
    [assignedCharacterIds, characters],
  );
  const [characterId, setCharacterId] = useState("");
  const [locationId, setLocationId] = useState("");

  useEffect(() => {
    if (!assignedCharacters.some((character) => character.id === characterId)) {
      setCharacterId(assignedCharacters[0]?.id ?? "");
    }
  }, [assignedCharacters, characterId]);

  useEffect(() => {
    if (!locations.some((location) => location.id === locationId)) {
      setLocationId(locations[0]?.id ?? "");
    }
  }, [locationId, locations]);

  const refresh = useCallback(async () => {
    try {
      setEncounter(
        await api<GmCombat | null>(`/api/campaigns/${campaignId}/combat-encounters/latest`),
      );
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load combat state");
    }
  }, [campaignId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (!encounter || encounter.status !== "ACTIVE" || encounter.current_actor !== "PLAYER") return;
    const timer = window.setInterval(() => void refresh(), 1000);
    return () => window.clearInterval(timer);
  }, [encounter, refresh]);

  async function start(event: FormEvent) {
    event.preventDefault();
    if (!characterId || !locationId || busy) return;
    setBusy(true);
    setError(null);
    try {
      const created = await api<GmCombat>(`/api/campaigns/${campaignId}/combat-encounters`, {
        method: "POST",
        body: JSON.stringify({ player_character_id: characterId, location_id: locationId }),
      });
      setEncounter(created);
    } catch (err) {
      await refresh();
      setError(err instanceof Error ? err.message : "Could not start combat encounter");
    } finally {
      setBusy(false);
    }
  }

  async function resolvePatrolAttack() {
    if (!encounter || busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api<GmCombat>(
        `/api/campaigns/${campaignId}/combat-encounters/${encounter.encounter_id}/patrol-attack`,
        {
          method: "POST",
          body: JSON.stringify({ expected_round: encounter.round }),
        },
      );
      setEncounter(updated);
    } catch {
      await refresh();
      setError("Combat state changed. The current encounter has been reloaded.");
    } finally {
      setBusy(false);
    }
  }

  const canStart = !encounter || encounter.status !== "ACTIVE";

  return (
    <section className="combat-workspace">
      {canStart && (
        <form className="panel combat-start" onSubmit={start} aria-label="Start combat encounter">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Combat</p>
              <h3>Start Escape the Imperial Patrol</h3>
            </div>
          </div>
          {assignedCharacters.length === 0 || locations.length === 0 ? (
            <p className="empty-state">Assign a Player Character and create a Location before starting combat.</p>
          ) : (
            <div className="combat-start-fields">
              <label>Player Character
                <select value={characterId} onChange={(event) => setCharacterId(event.target.value)} required>
                  {assignedCharacters.map((character) => (
                    <option key={character.id} value={character.id}>{character.name}</option>
                  ))}
                </select>
              </label>
              <label>Location
                <select value={locationId} onChange={(event) => setLocationId(event.target.value)} required>
                  {locations.map((location) => (
                    <option key={location.id} value={location.id}>{location.name}</option>
                  ))}
                </select>
              </label>
              <button disabled={busy || !characterId || !locationId}>Start encounter</button>
            </div>
          )}
          {error && <p className="error" role="alert">{error}</p>}
        </form>
      )}

      {encounter && (
        <CombatState
          encounter={encounter}
          busy={busy}
          error={error}
          actions={
            encounter.current_actor === "PATROL" ? (
              <button
                disabled={busy || !encounter.can_resolve_patrol_attack}
                onClick={() => void resolvePatrolAttack()}
              >
                Resolve Patrol Attack
              </button>
            ) : (
              <span className="muted">Waiting for {encounter.player_character_name} to Attack or Escape.</span>
            )
          }
        />
      )}
    </section>
  );
}
