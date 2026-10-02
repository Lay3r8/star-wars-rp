import { useEffect, useState } from "react";

import { api } from "./api";

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

export default function PlayerResolutionPanel({ campaignId }: { campaignId: string }) {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api<Summary | null>(`/api/player/campaigns/${campaignId}/resolutions/latest`)
      .then(setSummary)
      .catch(() => setSummary(null));
  }, [campaignId]);

  if (!summary) return null;

  return (
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
  );
}
