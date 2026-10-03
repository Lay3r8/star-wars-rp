import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";

type Character = { id: string; name: string; slicing_modifier: number };
type Location = { id: string; name: string };
type Fragment = { id: string; claim_text: string; gm_veracity: "TRUE" | "FALSE" | "UNKNOWN" };

type Resolution = {
  id: string;
  campaign_id: string;
  actor_character_id: string;
  context_location_id: string;
  intent: string;
  risk: string;
  roll_authority: "GM" | "PLAYER";
  risk_visibility: "GM_ONLY" | "PLAYER_VISIBLE";
  mechanic: string;
  dc: number;
  resolved_modifier: number;
  state: "READY" | "AWAITING_ADJUDICATION" | "FINALIZED";
  natural_roll: number | null;
  total: number | null;
  mechanical_result: "SUCCESS" | "FAILURE" | null;
  final_outcome: "SUCCESS" | "FAILURE" | null;
  failure_adjudication: string | null;
  adjudication_reason: string | null;
  adjudicated_at: string | null;
  adjudication_revision: number;
  is_overridden: boolean;
  is_corrected: boolean;
  previous_final_outcome: "SUCCESS" | "FAILURE" | null;
  success_preview: {
    recipient_character_id: string;
    recipient_name: string;
    fragment_id: string;
    claim_text: string;
  };
};

type Props = {
  campaignId: string;
  characters: Character[];
  locations: Location[];
  fragments: Fragment[];
  assignedCharacterIds: string[];
};

export default function ResolutionWorkspace({
  campaignId,
  characters,
  locations,
  fragments,
  assignedCharacterIds,
}: Props) {
  const [resolution, setResolution] = useState<Resolution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [overrideOpen, setOverrideOpen] = useState(false);
  const [correctionOpen, setCorrectionOpen] = useState(false);
  const [correctionOutcome, setCorrectionOutcome] = useState<"SUCCESS" | "FAILURE">("SUCCESS");
  const [rollAuthority, setRollAuthority] = useState<"GM" | "PLAYER">("GM");

  const refresh = useCallback(async () => {
    try {
      setResolution(
        await api<Resolution | null>(`/api/campaigns/${campaignId}/resolutions/latest`),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load resolution");
    }
  }, [campaignId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (resolution?.state !== "READY" || resolution.roll_authority !== "PLAYER") return;
    const timer = window.setInterval(() => {
      void refresh();
    }, 2000);
    return () => window.clearInterval(timer);
  }, [refresh, resolution?.id, resolution?.roll_authority, resolution?.state]);

  const defaultActor = characters[0]?.id ?? "";
  const defaultLocation = locations[0]?.id ?? "";
  const defaultFragment = fragments[0]?.id ?? "";
  const readyForResolution = Boolean(
    defaultActor &&
      defaultLocation &&
      defaultFragment &&
      assignedCharacterIds.includes(defaultActor),
  );

  async function mutate(path: string, body?: unknown) {
    if (!resolution) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api<Resolution>(
        `/api/campaigns/${campaignId}/resolutions/${resolution.id}/${path}`,
        {
          method: "POST",
          body: body === undefined ? undefined : JSON.stringify(body),
        },
      );
      setResolution(updated);
      setOverrideOpen(false);
      setCorrectionOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resolution action failed");
    } finally {
      setBusy(false);
    }
  }

  async function createResolution(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const actor = String(data.get("actor") || defaultActor);
    const location = String(data.get("location") || defaultLocation);
    const fragment = String(data.get("fragment") || defaultFragment);
    setBusy(true);
    setError(null);
    try {
      const created = await api<Resolution>(`/api/campaigns/${campaignId}/resolutions`, {
        method: "POST",
        body: JSON.stringify({
          actor_character_id: actor,
          context_location_id: location,
          intent: data.get("intent"),
          risk: data.get("risk"),
          roll_authority: data.get("roll_authority"),
          risk_visibility: data.get("risk_visibility"),
          dc: Number(data.get("dc")),
          success_recipient_character_id: actor,
          success_fragment_id: fragment,
        }),
      });
      setResolution(created);
      setOverrideOpen(false);
      setCorrectionOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create resolution");
    } finally {
      setBusy(false);
    }
  }

  const overrideOutcome = useMemo(() => {
    if (!resolution?.mechanical_result) return null;
    return resolution.mechanical_result === "SUCCESS" ? "FAILURE" : "SUCCESS";
  }, [resolution?.mechanical_result]);

  function openCorrection() {
    if (!resolution?.final_outcome) return;
    setCorrectionOutcome(resolution.final_outcome === "SUCCESS" ? "FAILURE" : "SUCCESS");
    setCorrectionOpen(true);
    setOverrideOpen(false);
  }

  return (
    <section className="resolution-workspace" aria-label="Resolution adjudication">
      <form className="panel resolution-panel" onSubmit={(event) => void createResolution(event)}>
        <p className="eyebrow">Live resolution</p>
        <h3>Slice the terminal</h3>
        <p className="muted">
          Roll only when the outcome is uncertain, meaningful risk exists, and success and
          failure are both fictionally possible.
        </p>

        {characters.length > 1 ? (
          <label>
            Actor
            <select name="actor" defaultValue={defaultActor}>
              {characters.map((character) => (
                <option key={character.id} value={character.id}>{character.name}</option>
              ))}
            </select>
          </label>
        ) : (
          <p>Actor: <strong>{characters[0]?.name ?? "Create a character"}</strong></p>
        )}

        {locations.length > 1 ? (
          <label>
            Context
            <select name="location" defaultValue={defaultLocation}>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>{location.name}</option>
              ))}
            </select>
          </label>
        ) : (
          <p>Context: <strong>{locations[0]?.name ?? "Create a location"}</strong></p>
        )}

        {fragments.length > 1 ? (
          <label>
            Success reveal
            <select name="fragment" defaultValue={defaultFragment}>
              {fragments.map((fragment) => (
                <option key={fragment.id} value={fragment.id}>{fragment.claim_text}</option>
              ))}
            </select>
          </label>
        ) : (
          <p>
            Success reveal: <strong>{fragments[0]?.claim_text ?? "Create a hidden claim"}</strong>
          </p>
        )}

        <label>
          Roll authority
          <select
            name="roll_authority"
            value={rollAuthority}
            onChange={(event) =>
              setRollAuthority(event.target.value as "GM" | "PLAYER")
            }
          >
            <option value="GM">GM</option>
            <option value="PLAYER">Player</option>
          </select>
        </label>

        <label>
          Risk visibility
          <select name="risk_visibility" defaultValue="GM_ONLY">
            <option value="GM_ONLY">GM only</option>
            <option value="PLAYER_VISIBLE">Player visible</option>
          </select>
        </label>

        {rollAuthority === "PLAYER" && (
          <p className="muted" role="note">
            Intent is Player-visible for a Player-roll request. Do not place hidden GM
            information in Intent.
          </p>
        )}

        <label>
          Intent
          <textarea
            name="intent"
            defaultValue="Discover where the confiscated shipment was transferred."
            required
          />
        </label>
        <label>
          Risk
          <textarea
            name="risk"
            defaultValue="On failure, Imperial security notices the intrusion."
            required
          />
        </label>
        <label>DC<input name="dc" type="number" defaultValue="10" required /></label>
        <button disabled={!readyForResolution || busy}>
          {busy ? "Working…" : "Create pre-bound resolution"}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}

      {resolution && (
        <section className="panel resolution-panel" aria-label="Current resolution">
          <div className="workspace-header">
            <div>
              <p className="eyebrow">Roll → Review → Adjudicate</p>
              <h3>Resolution</h3>
            </div>
            <span className="status-pill">
              {resolution.state === "READY"
                ? resolution.roll_authority === "PLAYER"
                  ? "Waiting for Player Roll"
                  : "Ready"
                : resolution.state === "AWAITING_ADJUDICATION"
                  ? "Awaiting GM adjudication"
                  : resolution.is_corrected
                    ? "Finalized · Corrected"
                    : "Finalized"}
            </span>
          </div>

          <dl>
            <dt>Intent</dt><dd>{resolution.intent}</dd>
            <dt>Risk</dt><dd>{resolution.risk}</dd>
            <dt>Roll authority</dt><dd>{resolution.roll_authority}</dd>
            <dt>Risk visibility</dt><dd>{resolution.risk_visibility}</dd>
            <dt>Check</dt>
            <dd>d20 {resolution.resolved_modifier >= 0 ? "+" : ""}{resolution.resolved_modifier} vs DC {resolution.dc}</dd>
            <dt>Success</dt>
            <dd>Reveal “{resolution.success_preview.claim_text}” to {resolution.success_preview.recipient_name}</dd>
          </dl>

          {resolution.state === "READY" && resolution.roll_authority === "GM" && (
            <button disabled={busy} onClick={() => void mutate("roll")}>
              {busy ? "Rolling…" : "Roll"}
            </button>
          )}

          {resolution.state === "READY" && resolution.roll_authority === "PLAYER" && (
            <p className="muted" role="status">
              Waiting for the assigned Player to roll…
            </p>
          )}

          {resolution.natural_roll !== null && (
            <div className="mechanical-evidence">
              <p className="eyebrow">Immutable mechanical evidence</p>
              <p className="result">
                d20 {resolution.natural_roll}
                {" "}{resolution.resolved_modifier >= 0 ? "+" : "-"}{" "}
                {Math.abs(resolution.resolved_modifier)}
                {" "}→ total {resolution.total}
              </p>
              <p>
                Mechanical result: <strong>{resolution.mechanical_result}</strong>
              </p>
            </div>
          )}

          {resolution.state === "AWAITING_ADJUDICATION" && resolution.mechanical_result && (
            <div className="adjudication-box">
              <h4>GM adjudication</h4>
              <p>
                Mechanical result: <strong>{resolution.mechanical_result}</strong>
              </p>

              {resolution.mechanical_result === "SUCCESS" ? (
                <div className="apply-box">
                  <p>Finalize Success will reveal exactly:</p>
                  <blockquote>{resolution.success_preview.claim_text}</blockquote>
                  <p>Recipient: <strong>{resolution.success_preview.recipient_name}</strong></p>
                  <button
                    disabled={busy}
                    onClick={() => void mutate("finalize", { final_outcome: "SUCCESS" })}
                  >
                    Finalize Success
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    const data = new FormData(event.currentTarget);
                    void mutate("finalize", {
                      final_outcome: "FAILURE",
                      failure_adjudication: data.get("failure_adjudication"),
                    });
                  }}
                >
                  <label>
                    Failure consequence
                    <textarea
                      name="failure_adjudication"
                      defaultValue={resolution.risk}
                      required
                    />
                  </label>
                  <button disabled={busy}>Finalize Failure</button>
                </form>
              )}

              <button
                className="link-button"
                disabled={busy}
                onClick={() => setOverrideOpen((value) => !value)}
              >
                Override outcome…
              </button>

              {overrideOpen && overrideOutcome && (
                <form
                  className="exception-box"
                  onSubmit={(event) => {
                    event.preventDefault();
                    const data = new FormData(event.currentTarget);
                    void mutate("finalize", {
                      final_outcome: overrideOutcome,
                      failure_adjudication:
                        overrideOutcome === "FAILURE"
                          ? data.get("failure_adjudication")
                          : undefined,
                      reason: data.get("reason"),
                    });
                  }}
                >
                  <p>
                    Mechanical result remains <strong>{resolution.mechanical_result}</strong>.
                  </p>
                  <p>
                    Proposed final outcome: <strong>{overrideOutcome}</strong> — overridden by GM.
                  </p>

                  {overrideOutcome === "SUCCESS" ? (
                    <div className="apply-box">
                      <p>This will reveal:</p>
                      <blockquote>{resolution.success_preview.claim_text}</blockquote>
                      <p>Recipient: <strong>{resolution.success_preview.recipient_name}</strong></p>
                    </div>
                  ) : (
                    <label>
                      Failure consequence
                      <textarea
                        name="failure_adjudication"
                        defaultValue={resolution.risk}
                        required
                      />
                    </label>
                  )}

                  <label>
                    Override reason <span className="muted">(optional, GM-only)</span>
                    <textarea name="reason" />
                  </label>
                  <button disabled={busy}>Finalize as {overrideOutcome === "SUCCESS" ? "Success" : "Failure"}</button>
                </form>
              )}
            </div>
          )}

          {resolution.state === "FINALIZED" && resolution.final_outcome && (
            <div className="adjudication-box">
              <p>
                Final outcome: <strong>{resolution.final_outcome}</strong>
                {resolution.is_overridden ? " — overridden by GM" : ""}
              </p>
              {resolution.is_corrected && (
                <p>
                  <strong>Corrected.</strong>
                  {resolution.previous_final_outcome
                    ? ` Previously finalized as ${resolution.previous_final_outcome}.`
                    : ""}
                </p>
              )}
              {resolution.failure_adjudication && (
                <p>Failure consequence: <strong>{resolution.failure_adjudication}</strong></p>
              )}

              <button className="link-button" disabled={busy} onClick={openCorrection}>
                Correct outcome…
              </button>

              {correctionOpen && (
                <form
                  className="exception-box"
                  onSubmit={(event) => {
                    event.preventDefault();
                    const data = new FormData(event.currentTarget);
                    void mutate("correct", {
                      expected_adjudication_revision: resolution.adjudication_revision,
                      final_outcome: correctionOutcome,
                      failure_adjudication:
                        correctionOutcome === "FAILURE"
                          ? data.get("failure_adjudication")
                          : undefined,
                      correction_reason: data.get("correction_reason"),
                    });
                  }}
                >
                  <h4>Correct outcome</h4>
                  <p>
                    Mechanical result: <strong>{resolution.mechanical_result}</strong> — immutable
                  </p>
                  <p>
                    Current final outcome: <strong>{resolution.final_outcome}</strong>
                  </p>

                  <label>
                    New final outcome
                    <select
                      name="final_outcome"
                      value={correctionOutcome}
                      onChange={(event) =>
                        setCorrectionOutcome(event.target.value as "SUCCESS" | "FAILURE")
                      }
                    >
                      <option value="SUCCESS">SUCCESS</option>
                      <option value="FAILURE">FAILURE</option>
                    </select>
                  </label>

                  {correctionOutcome === "FAILURE" && (
                    <label>
                      Failure consequence
                      <textarea
                        name="failure_adjudication"
                        defaultValue={
                          resolution.final_outcome === "FAILURE" && resolution.failure_adjudication
                            ? resolution.failure_adjudication
                            : resolution.risk
                        }
                        required
                      />
                    </label>
                  )}

                  {resolution.final_outcome === "SUCCESS" && correctionOutcome === "FAILURE" && (
                    <div className="warning-box" role="note">
                      <strong>This information has already been shown to {resolution.success_preview.recipient_name}.</strong>
                      <p>
                        Correcting the outcome to Failure will not remove it from known information
                        or make the Player unaware of it.
                      </p>
                      <blockquote>{resolution.success_preview.claim_text}</blockquote>
                    </div>
                  )}

                  {resolution.final_outcome === "FAILURE" && correctionOutcome === "SUCCESS" && (
                    <div className="apply-box">
                      <p>Apply correction will reveal:</p>
                      <blockquote>{resolution.success_preview.claim_text}</blockquote>
                      <p>Recipient: <strong>{resolution.success_preview.recipient_name}</strong></p>
                    </div>
                  )}

                  <label>
                    Correction reason
                    <textarea name="correction_reason" required />
                  </label>
                  <button disabled={busy}>Apply correction</button>
                </form>
              )}
            </div>
          )}
        </section>
      )}
    </section>
  );
}
