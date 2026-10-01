import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";

type Principal = { id: string; username: string };
type Campaign = { id: string; name: string; role: "GM" | "PLAYER" };
type Member = {
  principal_id: string;
  username: string;
  role: "GM" | "PLAYER";
  assigned_character_id: string | null;
};
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
  mechanic: string;
  dc: number;
  resolved_modifier: number;
  state: string;
  natural_roll: number | null;
  total: number | null;
  outcome: "SUCCESS" | "FAILURE" | null;
  failure_adjudication: string | null;
  success_preview: {
    recipient_character_id: string;
    recipient_name: string;
    fragment_id: string;
    claim_text: string;
  };
};
type HistoryItem = {
  id: string;
  event_type: string;
  subject_id: string;
  occurred_at: string;
  message: string;
};
type PlayerProjection = {
  campaign_id: string;
  character: { id: string; name: string; slicing_modifier: number };
  knowledge: { fragment_id: string; state: "AWARE"; claim_text: string }[];
};

function ErrorBox({ error }: { error: string | null }) {
  return error ? <p className="error" role="alert">{error}</p> : null;
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: (p: Principal) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await api<Principal>("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({ username, password }),
        });
      }
      const principal = await api<Principal>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      onAuthenticated(principal);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  return (
    <main className="auth-shell">
      <section className="panel auth-panel">
        <p className="eyebrow">Slice 1</p>
        <h1>Star Wars RP</h1>
        <p>Authenticate as a distinct GM or Player principal.</p>
        <form onSubmit={submit}>
          <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} required /></label>
          <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
          <button type="submit">{mode === "login" ? "Login" : "Register & login"}</button>
        </form>
        <button className="link-button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Create a principal" : "Back to login"}
        </button>
        <ErrorBox error={error} />
      </section>
    </main>
  );
}

function PlayerWorkspace({ campaign }: { campaign: Campaign }) {
  const [projection, setProjection] = useState<PlayerProjection | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      setProjection(await api<PlayerProjection>(`/api/player/campaigns/${campaign.id}/character`));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load player projection");
    }
  }, [campaign.id]);

  useEffect(() => { void refresh(); }, [refresh]);

  return (
    <section className="workspace">
      <div className="workspace-header">
        <div><p className="eyebrow">Player projection</p><h2>{campaign.name}</h2></div>
        <button onClick={() => void refresh()}>Refresh</button>
      </div>
      <ErrorBox error={error} />
      {projection && (
        <>
          <div className="panel">
            <h3>{projection.character.name}</h3>
            <p>Slicing modifier: <strong>{projection.character.slicing_modifier >= 0 ? "+" : ""}{projection.character.slicing_modifier}</strong></p>
          </div>
          <div className="panel">
            <h3>Known information</h3>
            {projection.knowledge.length === 0 ? (
              <p className="muted">No disclosed knowledge yet.</p>
            ) : (
              <ul>{projection.knowledge.map((item) => <li key={item.fragment_id}>{item.claim_text}</li>)}</ul>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function GmWorkspace({ campaign }: { campaign: Campaign }) {
  const [members, setMembers] = useState<Member[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [fragments, setFragments] = useState<Fragment[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [resolution, setResolution] = useState<Resolution | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [m, c, l, f, h, r] = await Promise.all([
        api<Member[]>(`/api/campaigns/${campaign.id}/members`),
        api<Character[]>(`/api/campaigns/${campaign.id}/characters`),
        api<Location[]>(`/api/campaigns/${campaign.id}/locations`),
        api<Fragment[]>(`/api/campaigns/${campaign.id}/knowledge-fragments`),
        api<HistoryItem[]>(`/api/campaigns/${campaign.id}/history`),
        api<Resolution | null>(`/api/campaigns/${campaign.id}/resolutions/latest`),
      ]);
      setMembers(m); setCharacters(c); setLocations(l); setFragments(f); setHistory(h); setResolution(r);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load campaign");
    }
  }, [campaign.id]);

  useEffect(() => { void refresh(); }, [refresh]);

  async function run(action: () => Promise<unknown>) {
    setError(null);
    try {
      await action();
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Operation failed");
    }
  }

  const players = members.filter((member) => member.role === "PLAYER");
  const defaultActor = characters[0]?.id ?? "";
  const defaultLocation = locations[0]?.id ?? "";
  const defaultFragment = fragments[0]?.id ?? "";
  const readyForResolution = Boolean(defaultActor && defaultLocation && defaultFragment && players.some((p) => p.assigned_character_id === defaultActor));

  async function createResolution(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const actor = String(data.get("actor") || defaultActor);
    const location = String(data.get("location") || defaultLocation);
    const fragment = String(data.get("fragment") || defaultFragment);
    const created = await api<Resolution>(`/api/campaigns/${campaign.id}/resolutions`, {
      method: "POST",
      body: JSON.stringify({
        actor_character_id: actor,
        context_location_id: location,
        intent: data.get("intent"),
        risk: data.get("risk"),
        dc: Number(data.get("dc")),
        success_recipient_character_id: actor,
        success_fragment_id: fragment,
      }),
    });
    setResolution(created);
  }

  async function resolutionAction(path: string, body?: unknown) {
    if (!resolution) return;
    try {
      const updated = await api<Resolution>(
        `/api/campaigns/${campaign.id}/resolutions/${resolution.id}/${path}`,
        { method: "POST", body: body ? JSON.stringify(body) : undefined },
      );
      setResolution(updated);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resolution action failed");
    }
  }

  return (
    <section className="workspace">
      <div className="workspace-header">
        <div><p className="eyebrow">GM workspace</p><h2>{campaign.name}</h2></div>
        <button onClick={() => void refresh()}>Refresh</button>
      </div>
      <ErrorBox error={error} />

      <div className="grid">
        <form className="panel" onSubmit={(e) => {
          e.preventDefault();
          const username = String(new FormData(e.currentTarget).get("username"));
          void run(() => api(`/api/campaigns/${campaign.id}/members`, { method: "POST", body: JSON.stringify({ username }) }));
          e.currentTarget.reset();
        }}>
          <h3>1. Add Player</h3>
          <label>Registered username<input name="username" required /></label>
          <button>Add to campaign</button>
          <ul className="compact">{players.map((p) => <li key={p.principal_id}>{p.username}</li>)}</ul>
        </form>

        <form className="panel" onSubmit={(e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          void run(() => api(`/api/campaigns/${campaign.id}/characters`, {
            method: "POST",
            body: JSON.stringify({ name: data.get("name"), slicing_modifier: Number(data.get("modifier")) }),
          }));
          e.currentTarget.reset();
        }}>
          <h3>2. Create Character</h3>
          <label>Character name<input name="name" required /></label>
          <label>Slicing modifier<input name="modifier" type="number" defaultValue="2" required /></label>
          <button>Create character</button>
        </form>

        <form className="panel" onSubmit={(e) => {
          e.preventDefault();
          const name = String(new FormData(e.currentTarget).get("name"));
          void run(() => api(`/api/campaigns/${campaign.id}/locations`, { method: "POST", body: JSON.stringify({ name }) }));
          e.currentTarget.reset();
        }}>
          <h3>3. Create Location</h3>
          <label>Location name<input name="name" defaultValue="Imperial Cargo Terminal" required /></label>
          <button>Create location</button>
        </form>

        <form className="panel" onSubmit={(e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          void run(() => api(`/api/campaigns/${campaign.id}/knowledge-fragments`, {
            method: "POST",
            body: JSON.stringify({ claim_text: data.get("claim"), gm_veracity: data.get("veracity") }),
          }));
          e.currentTarget.reset();
        }}>
          <h3>4. Create hidden claim</h3>
          <label>Player-visible claim<textarea name="claim" defaultValue="The confiscated shipment was transferred to Dock 47." required /></label>
          <label>GM veracity<select name="veracity" defaultValue="TRUE"><option>TRUE</option><option>FALSE</option><option>UNKNOWN</option></select></label>
          <button>Create secret</button>
        </form>

        <form className="panel" onSubmit={(e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          void run(() => api(`/api/campaigns/${campaign.id}/player-assignment`, {
            method: "PUT",
            body: JSON.stringify({ player_principal_id: data.get("player"), character_id: data.get("character") }),
          }));
        }}>
          <h3>5. Assign Player</h3>
          <label>Player<select name="player" required>{players.map((p) => <option key={p.principal_id} value={p.principal_id}>{p.username}</option>)}</select></label>
          <label>Character<select name="character" required>{characters.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
          <button>Assign</button>
        </form>
      </div>

      <form className="panel resolution-panel" onSubmit={(e) => { void createResolution(e); }}>
        <p className="eyebrow">Live resolution</p>
        <h3>Slice the terminal</h3>
        <p className="muted">Roll only when the outcome is uncertain, meaningful risk exists, and success and failure are both fictionally possible.</p>

        {characters.length > 1 ? (
          <label>Actor<select name="actor" defaultValue={defaultActor}>{characters.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
        ) : <p>Actor: <strong>{characters[0]?.name ?? "Create a character"}</strong></p>}
        {locations.length > 1 ? (
          <label>Context<select name="location" defaultValue={defaultLocation}>{locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}</select></label>
        ) : <p>Context: <strong>{locations[0]?.name ?? "Create a location"}</strong></p>}
        {fragments.length > 1 ? (
          <label>Success reveal<select name="fragment" defaultValue={defaultFragment}>{fragments.map((f) => <option key={f.id} value={f.id}>{f.claim_text}</option>)}</select></label>
        ) : <p>Success reveal: <strong>{fragments[0]?.claim_text ?? "Create a hidden claim"}</strong></p>}

        <label>Intent<textarea name="intent" defaultValue="Discover where the confiscated shipment was transferred." required /></label>
        <label>Risk<textarea name="risk" defaultValue="On failure, Imperial security notices the intrusion." required /></label>
        <label>DC<input name="dc" type="number" defaultValue="10" required /></label>
        <button disabled={!readyForResolution}>Create pre-bound resolution</button>
      </form>

      {resolution && (
        <section className="panel resolution-panel">
          <h3>Resolution</h3>
          <dl>
            <dt>State</dt><dd>{resolution.state}</dd>
            <dt>Intent</dt><dd>{resolution.intent}</dd>
            <dt>Risk</dt><dd>{resolution.risk}</dd>
            <dt>Check</dt><dd>d20 {resolution.resolved_modifier >= 0 ? "+" : ""}{resolution.resolved_modifier} vs DC {resolution.dc}</dd>
            <dt>Success</dt><dd>Reveal “{resolution.success_preview.claim_text}” to {resolution.success_preview.recipient_name}</dd>
          </dl>

          {resolution.state === "READY" && <button onClick={() => void resolutionAction("roll")}>Roll</button>}
          {resolution.natural_roll !== null && <p className="result">d20 {resolution.natural_roll} → total {resolution.total}: <strong>{resolution.outcome}</strong></p>}

          {resolution.state === "SUCCESS_PENDING_APPLY" && (
            <div className="apply-box">
              <p>Apply will reveal exactly:</p>
              <blockquote>{resolution.success_preview.claim_text}</blockquote>
              <p>Recipient: <strong>{resolution.success_preview.recipient_name}</strong></p>
              <button onClick={() => void resolutionAction("apply")}>Apply reveal</button>
            </div>
          )}

          {resolution.state === "FAILURE_PENDING_CLOSE" && (
            <form onSubmit={(e) => {
              e.preventDefault();
              const adjudication = String(new FormData(e.currentTarget).get("adjudication"));
              void resolutionAction("close-failure", { adjudication });
            }}>
              <p>Declared Risk: <strong>{resolution.risk}</strong></p>
              <label>Concrete adjudication<textarea name="adjudication" defaultValue="Imperial security logs the intrusion." required /></label>
              <button>Close failed resolution</button>
            </form>
          )}

          {resolution.state.startsWith("CLOSED_") && <p className="success">Resolution closed.</p>}
        </section>
      )}

      <section className="panel">
        <h3>Meaningful history</h3>
        {history.length === 0 ? <p className="muted">No terminal resolution history yet.</p> : (
          <ul>{history.map((item) => <li key={item.id}>{item.message}</li>)}</ul>
        )}
      </section>
    </section>
  );
}

export default function App() {
  const [principal, setPrincipal] = useState<Principal | null | undefined>(undefined);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadCampaigns = useCallback(async () => {
    if (!principal) return;
    try {
      const values = await api<Campaign[]>("/api/campaigns");
      setCampaigns(values);
      if (!selectedId && values.length === 1) setSelectedId(values[0].id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load campaigns");
    }
  }, [principal, selectedId]);

  useEffect(() => {
    api<Principal>("/api/auth/me").then(setPrincipal).catch(() => setPrincipal(null));
  }, []);

  useEffect(() => { void loadCampaigns(); }, [loadCampaigns]);

  const selected = useMemo(() => campaigns.find((c) => c.id === selectedId) ?? null, [campaigns, selectedId]);

  if (principal === undefined) return <main className="auth-shell"><p>Loading…</p></main>;
  if (!principal) return <AuthScreen onAuthenticated={setPrincipal} />;

  async function logout() {
    await api<void>("/api/auth/logout", { method: "POST" });
    setPrincipal(null); setCampaigns([]); setSelectedId(null);
  }

  return (
    <main className="app-shell">
      <header>
        <div><p className="eyebrow">Star Wars RP</p><h1>Slice 1</h1></div>
        <div className="header-actions"><span>{principal.username}</span><button onClick={() => void logout()}>Logout</button></div>
      </header>

      <section className="campaign-bar panel">
        <label>Campaign
          <select value={selectedId ?? ""} onChange={(e) => setSelectedId(e.target.value)}>
            <option value="">Select…</option>
            {campaigns.map((c) => <option key={c.id} value={c.id}>{c.name} — {c.role}</option>)}
          </select>
        </label>
        <form onSubmit={(e) => {
          e.preventDefault();
          const name = String(new FormData(e.currentTarget).get("name"));
          void api<Campaign>("/api/campaigns", { method: "POST", body: JSON.stringify({ name }) })
            .then(async (campaign) => { await loadCampaigns(); setSelectedId(campaign.id); })
            .catch((err) => setError(err instanceof Error ? err.message : "Could not create campaign"));
          e.currentTarget.reset();
        }}>
          <label>New campaign<input name="name" required /></label><button>Create as GM</button>
        </form>
      </section>

      <ErrorBox error={error} />
      {selected?.role === "GM" && <GmWorkspace key={selected.id} campaign={selected} />}
      {selected?.role === "PLAYER" && <PlayerWorkspace key={selected.id} campaign={selected} />}
    </main>
  );
}
