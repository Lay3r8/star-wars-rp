import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "./api";

type PendingResolution = {
  resolution_id: string;
  actor_character_id: string;
  actor_name: string;
  mechanic: string;
  context_location_id: string;
  context_location_name: string;
  intent: string;
  known_risk?: string;
  state: "READY" | "AWAITING_ADJUDICATION";
  natural_roll?: number;
  resolved_modifier?: number;
  total?: number;
  mechanical_result?: "SUCCESS" | "FAILURE";
};

type Summary = {
  resolution_id: string;
  natural_roll: number;
  resolved_modifier: number;
  total: number;
  mechanical_result: "SUCCESS" | "FAILURE";
  final_outcome: "SUCCESS" | "FAILURE";
  is_overridden: boolean;
  is_corrected: boolean;
  previous_final_outcome: "SUCCESS" | "FAILURE" | null;
};

type Props = {
  campaignId: string;
  refreshKey: number;
  onFinalized: () => void;
};

export default function PlayerResolutionPanel({
  campaignId,
  refreshKey,
  onFinalized,
}: Props) {
  const [pending, setPending] = useState<PendingResolution | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const notifiedFinalized = useRef<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [nextPending, nextSummary] = await Promise.all([
        api<PendingResolution | null>(
          `/api/player/campaigns/${campaignId}/resolutions/pending`,
        ),
        api<Summary | null>(
          `/api/player/campaigns/${campaignId}/resolutions/latest`,
        ),
      ]);
      setPending(nextPending);
      setSummary(nextSummary);
      setError(null);

      if (
        nextSummary &&
        notifiedFinalized.current !== nextSummary.resolution_id
      ) {
        notifiedFinalized.current = nextSummary.resolution_id;
        onFinalized();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load resolution state");
    }
  }, [campaignId, onFinalized]);

  useEffect(() => {
    void refresh();
  }, [refresh, refreshKey]);

  const shouldPoll =
    summary === null ||
    pending?.state === "READY" ||
    pending?.state === "AWAITING_ADJUDICATION";

  useEffect(() => {
    if (!shouldPoll) return;
    const timer = window.setInterval(() => {
      void refresh();
    }, 2000);
    return () => window.clearInterval(timer);
  }, [refresh, shouldPoll]);

  async function roll() {
    if (!pending || pending.state !== "READY") return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api<PendingResolution>(
        `/api/player/campaigns/${campaignId}/resolutions/${pending.resolution_id}/roll`,
        { method: "POST" },
      );
      setPending(updated);
      await refresh();
    } catch (err) {
      // Network uncertainty is resolved from authoritative server state before
      // offering Roll again.
      await refresh();
      setError(err instanceof Error ? err.message : "Could not roll");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      {error && <p className="error" role="alert">{error}</p>}

      {pending && (
        <section className="panel" aria-label="Pending roll request">
          <p className="eyebrow">Requested roll</p>
          <h3>{pending.actor_name}</h3>
          <p>
            <strong>{pending.mechanic}</strong> — {pending.context_location_name}
          </p>
          <p><strong>Action:</strong> {pending.intent}</p>
          {pending.known_risk && (
            <p><strong>Known stakes:</strong> {pending.known_risk}</p>
          )}

          {pending.state === "READY" ? (
            <button disabled={busy} onClick={() => void roll()}>
              {busy ? "Rolling…" : "Roll"}
            </button>
          ) : (
            <div className="mechanical-evidence" role="status">
              <p className="eyebrow">Immutable mechanical evidence</p>
              <p className="result">
                d20 {pending.natural_roll}{" "}
                {(pending.resolved_modifier ?? 0) >= 0 ? "+" : "-"}{" "}
                {Math.abs(pending.resolved_modifier ?? 0)}
                {" "}→ total {pending.total}
              </p>
              <p>
                Mechanical result: <strong>{pending.mechanical_result}</strong>
              </p>
              <p className="muted">Waiting for GM adjudication…</p>
            </div>
          )}
        </section>
      )}

      {!pending && summary && (
        <section className="panel" aria-label="Latest finalized resolution">
          <p className="eyebrow">Latest finalized resolution</p>
          <h3>Mechanical result vs final outcome</h3>
          <p className="result">
            Roll: {summary.natural_roll}{" "}
            {summary.resolved_modifier >= 0 ? "+" : "-"} {Math.abs(summary.resolved_modifier)}
            {" "}→ {summary.total}
          </p>
          <p>Mechanical result: <strong>{summary.mechanical_result}</strong></p>
          <p>
            Final outcome: <strong>{summary.final_outcome}</strong>
            {summary.is_overridden ? " (GM adjudication)" : ""}
          </p>
          {summary.is_corrected && (
            <p>
              <strong>Corrected.</strong>
              {summary.previous_final_outcome
                ? ` Previously finalized as ${summary.previous_final_outcome}.`
                : ""}
            </p>
          )}
        </section>
      )}
    </>
  );
}
