import type { FormEvent, KeyboardEvent } from "react";
import { useCallback, useEffect, useState } from "react";

import { api } from "./api";

type Location = { id: string; name: string };

type ContactSearchResult = {
  contact_id: string;
  name: string;
  role: string;
  location_name: string;
};

type ContactSummary = {
  contact_id: string;
  name: string;
  role: string;
  location_id: string;
  location_name: string;
  gm_note: string | null;
  prepared_information: {
    claim_text: string;
    gm_veracity: "TRUE" | "FALSE" | "UNKNOWN";
  };
  reveal_preview: {
    recipient_character_id: string;
    recipient_name: string;
    claim_text: string;
  } | null;
};

type RevealResult = {
  contact_id: string;
  recipient_character_id: string;
  recipient_name: string;
  claim_text: string;
  state: "AWARE";
  already_revealed: boolean;
};

type Props = {
  campaignId: string;
  locations: Location[];
};

type ContactForm = {
  name: string;
  role: string;
  locationId: string;
  gmNote: string;
  claimText: string;
  gmVeracity: "TRUE" | "FALSE" | "UNKNOWN";
};

const emptyForm: ContactForm = {
  name: "",
  role: "",
  locationId: "",
  gmNote: "",
  claimText: "",
  gmVeracity: "TRUE",
};

export default function ContactWorkspace({ campaignId, locations }: Props) {
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<"idle" | "pending" | "success" | "error">("idle");
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ContactSearchResult[]>([]);
  const [highlighted, setHighlighted] = useState(0);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ContactSummary | null>(null);

  const [showRevealPreview, setShowRevealPreview] = useState(false);
  const [revealPending, setRevealPending] = useState(false);
  const [revealMessage, setRevealMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!form.locationId && locations.length > 0) {
      setForm((current) => ({ ...current, locationId: locations[0].id }));
    }
  }, [form.locationId, locations]);

  const performSearch = useCallback(async (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) {
      setResults([]);
      setHighlighted(0);
      setSearchError(null);
      return;
    }
    setSearching(true);
    setSearchError(null);
    try {
      const found = await api<ContactSearchResult[]>(
        `/api/campaigns/${campaignId}/contacts/search?q=${encodeURIComponent(trimmed)}`,
      );
      setResults(found);
      setHighlighted(0);
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : "Contact search failed");
    } finally {
      setSearching(false);
    }
  }, [campaignId]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void performSearch(query); }, 160);
    return () => window.clearTimeout(timer);
  }, [performSearch, query]);

  useEffect(() => {
    if (!selected) return;
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelected(null);
        setShowRevealPreview(false);
      }
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [selected]);

  async function openContact(contactId: string) {
    setSearchError(null);
    try {
      const summary = await api<ContactSummary>(
        `/api/campaigns/${campaignId}/contacts/${contactId}`,
      );
      setSelected(summary);
      setShowRevealPreview(false);
      setRevealMessage(null);
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : "Could not open Contact");
    }
  }

  function onSearchKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown" && results.length > 0) {
      event.preventDefault();
      setHighlighted((current) => Math.min(current + 1, results.length - 1));
    } else if (event.key === "ArrowUp" && results.length > 0) {
      event.preventDefault();
      setHighlighted((current) => Math.max(current - 1, 0));
    } else if (event.key === "Enter" && results[highlighted]) {
      event.preventDefault();
      void openContact(results[highlighted].contact_id);
    } else if (event.key === "Escape") {
      event.preventDefault();
      if (selected) {
        setSelected(null);
        setShowRevealPreview(false);
      } else {
        setQuery("");
        setResults([]);
      }
    }
  }

  function startCreate() {
    setEditingId(null);
    setForm({ ...emptyForm, locationId: locations[0]?.id ?? "" });
    setSaveState("idle");
    setSaveMessage(null);
  }

  function startEdit(contact: ContactSummary) {
    setEditingId(contact.contact_id);
    setForm({
      name: contact.name,
      role: contact.role,
      locationId: contact.location_id,
      gmNote: contact.gm_note ?? "",
      claimText: contact.prepared_information.claim_text,
      gmVeracity: contact.prepared_information.gm_veracity,
    });
    setSaveState("idle");
    setSaveMessage(null);
    document.getElementById("contact-editor")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function saveContact(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (saveState === "pending") return;
    setSaveState("pending");
    setSaveMessage(null);
    const payload = {
      name: form.name,
      role: form.role,
      location_id: form.locationId,
      gm_note: form.gmNote || null,
      prepared_information: {
        claim_text: form.claimText,
        gm_veracity: form.gmVeracity,
      },
    };
    try {
      const summary = editingId
        ? await api<ContactSummary>(
            `/api/campaigns/${campaignId}/contacts/${editingId}`,
            { method: "PATCH", body: JSON.stringify(payload) },
          )
        : await api<ContactSummary>(
            `/api/campaigns/${campaignId}/contacts`,
            { method: "POST", body: JSON.stringify(payload) },
          );
      setSelected(summary);
      setQuery(summary.name);
      setSaveState("success");
      setSaveMessage(editingId ? "Contact changes saved." : "Contact saved.");
      setEditingId(summary.contact_id);
      await performSearch(summary.name);
    } catch (error) {
      setSaveState("error");
      setSaveMessage(error instanceof Error ? error.message : "Could not save Contact");
    }
  }

  async function reveal() {
    if (!selected?.reveal_preview || revealPending) return;
    setRevealPending(true);
    setRevealMessage(null);
    try {
      const result = await api<RevealResult>(
        `/api/campaigns/${campaignId}/contacts/${selected.contact_id}/reveal`,
        {
          method: "POST",
          body: JSON.stringify({
            recipient_character_id: selected.reveal_preview.recipient_character_id,
          }),
        },
      );
      setRevealMessage(
        result.already_revealed
          ? `${result.recipient_name} already knows this information.`
          : `Revealed to ${result.recipient_name}.`,
      );
      setShowRevealPreview(false);
    } catch (error) {
      setRevealMessage(error instanceof Error ? error.message : "Reveal failed");
    } finally {
      setRevealPending(false);
    }
  }

  const canSave = locations.length > 0 && saveState !== "pending";

  return (
    <section className="contact-workspace" aria-label="Contacts">
      <div className="contact-columns">
        <section id="contact-editor" className="panel contact-editor">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Preparation</p>
              <h3>{editingId ? "Edit Contact" : "Create Contact"}</h3>
            </div>
            {editingId && <button type="button" className="secondary" onClick={startCreate}>New Contact</button>}
          </div>

          {locations.length === 0 ? (
            <div className="empty-state">
              <strong>No Location available</strong>
              <p>A Contact needs an existing campaign Location. Location authoring is outside Slice 2.</p>
            </div>
          ) : (
            <form onSubmit={(event) => { void saveContact(event); }}>
              <label>
                Name
                <input
                  value={form.name}
                  onChange={(event) => setForm({ ...form, name: event.target.value })}
                  minLength={1}
                  maxLength={120}
                  required
                />
              </label>
              <label>
                Role
                <input
                  value={form.role}
                  onChange={(event) => setForm({ ...form, role: event.target.value })}
                  minLength={1}
                  maxLength={240}
                  placeholder="Imperial dock clerk and discreet informant"
                  required
                />
              </label>
              <label>
                Location
                <select
                  value={form.locationId}
                  onChange={(event) => setForm({ ...form, locationId: event.target.value })}
                  required
                >
                  {locations.map((location) => (
                    <option key={location.id} value={location.id}>{location.name}</option>
                  ))}
                </select>
              </label>
              <label>
                GM note <span className="muted">(optional)</span>
                <textarea
                  value={form.gmNote}
                  onChange={(event) => setForm({ ...form, gmNote: event.target.value })}
                  maxLength={4000}
                />
              </label>

              <fieldset>
                <legend>Prepared information</legend>
                <label>
                  Information this Contact knows
                  <textarea
                    value={form.claimText}
                    onChange={(event) => setForm({ ...form, claimText: event.target.value })}
                    minLength={1}
                    maxLength={4000}
                    required
                  />
                </label>
                <label>
                  Truth status
                  <select
                    value={form.gmVeracity}
                    onChange={(event) => setForm({
                      ...form,
                      gmVeracity: event.target.value as "TRUE" | "FALSE" | "UNKNOWN",
                    })}
                  >
                    <option value="TRUE">True</option>
                    <option value="FALSE">False</option>
                    <option value="UNKNOWN">Unknown</option>
                  </select>
                </label>
              </fieldset>

              <div className="action-row">
                <button type="submit" disabled={!canSave}>
                  {saveState === "pending" ? "Saving…" : editingId ? "Save changes" : "Save Contact"}
                </button>
                {saveMessage && (
                  <span className={saveState === "error" ? "inline-error" : "inline-success"} role="status">
                    {saveMessage}
                  </span>
                )}
              </div>
            </form>
          )}
        </section>

        <section className="panel contact-search">
          <p className="eyebrow">Live use</p>
          <h3>Find a Contact</h3>
          <label>
            Search name or role
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={onSearchKeyDown}
              placeholder="Nira or dock clerk"
              aria-controls="contact-search-results"
            />
          </label>

          {searching && <p className="muted" role="status">Searching…</p>}
          {searchError && <p className="error" role="alert">{searchError}</p>}
          {!searching && query.trim() && results.length === 0 && !searchError && (
            <p className="empty-state">No Contacts found.</p>
          )}

          <ul id="contact-search-results" className="search-results" role="listbox">
            {results.map((result, index) => (
              <li key={result.contact_id}>
                <button
                  type="button"
                  className={index === highlighted ? "search-result highlighted" : "search-result"}
                  onMouseEnter={() => setHighlighted(index)}
                  onClick={() => void openContact(result.contact_id)}
                  role="option"
                  aria-selected={index === highlighted}
                >
                  <strong>{result.name}</strong>
                  <span>{result.role}</span>
                  <small>{result.location_name}</small>
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {selected && (
        <section className="panel contact-summary" aria-label="Contact summary">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Contact</p>
              <h3>{selected.name}</h3>
              <p>{selected.role} · {selected.location_name}</p>
            </div>
            <button type="button" className="secondary" onClick={() => startEdit(selected)}>Edit</button>
          </div>

          <div className="prepared-information">
            <p className="muted">Prepared information</p>
            <blockquote>{selected.prepared_information.claim_text}</blockquote>
            <small>GM Truth status: {selected.prepared_information.gm_veracity}</small>
          </div>

          {selected.gm_note && (
            <details className="gm-note">
              <summary>GM note</summary>
              <p>{selected.gm_note}</p>
            </details>
          )}

          {!selected.reveal_preview ? (
            <p className="muted">Reveal is unavailable until exactly one Player Character is assigned in this campaign.</p>
          ) : !showRevealPreview ? (
            <button type="button" onClick={() => { setShowRevealPreview(true); setRevealMessage(null); }}>
              Reveal…
            </button>
          ) : (
            <div className="reveal-preview">
              <p className="eyebrow">Disclosure preview</p>
              <p>Recipient: <strong>{selected.reveal_preview.recipient_name}</strong></p>
              <p>They will see exactly:</p>
              <blockquote>{selected.reveal_preview.claim_text}</blockquote>
              <div className="action-row">
                <button type="button" disabled={revealPending} onClick={() => void reveal()}>
                  {revealPending ? "Revealing…" : "Confirm Reveal"}
                </button>
                <button type="button" className="secondary" disabled={revealPending} onClick={() => setShowRevealPreview(false)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
          {revealMessage && <p className="inline-success" role="status">{revealMessage}</p>}
        </section>
      )}
    </section>
  );
}
