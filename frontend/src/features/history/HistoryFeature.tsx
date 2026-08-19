/** Design: opt-in Verlauf mit explizitem Lade-, Leer-, Fehler- und Löschzustand. */

import { useEffect, useState } from "react";

import { historyApi } from "../../api/history";
import { InlineNotice, type Notice } from "../../components/feedback/InlineNotice";
import { FadeContent } from "../../components/react-bits/FadeContent";
import type { HistoryEntry } from "../../types/api";

export function HistoryFeature({ refreshKey }: { refreshKey: number }) {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [notice, setNotice] = useState<Notice>(null);

  async function load() {
    setState("loading");
    try {
      const response = await historyApi.list();
      setEntries(response.entries);
      setState("ready");
    } catch (error) {
      setState("error");
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Verlauf konnte nicht geladen werden." });
    }
  }

  useEffect(() => { void load(); }, [refreshKey]);

  async function remove(entryId: number) {
    setNotice(null);
    try {
      await historyApi.remove(entryId);
      setEntries((current) => current.filter((entry) => entry.id !== entryId));
      setNotice({ kind: "ok", text: "Verlaufseintrag gelöscht." });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Eintrag konnte nicht gelöscht werden." });
    }
  }

  return <section id="history" className="history-section" aria-labelledby="history-title"><p className="section-index">02 / ENCRYPTED HISTORY</p><h2 id="history-title">Bewusst speichern.</h2><p>Opt-in-Verlauf: Werte liegen nur verschlüsselt in der lokalen Datenbank.</p><InlineNotice notice={notice} />
    {state === "loading" && <div className="empty-state compact" role="status">Verschlüsselten Verlauf laden …</div>}
    {state === "error" && <button className="button button--secondary" type="button" onClick={() => void load()}>Erneut laden</button>}
    {state === "ready" && entries.length === 0 && <div className="empty-state compact">Keine gespeicherten Einträge.</div>}
    {state === "ready" && entries.length > 0 && <FadeContent><ul className="history-list">{entries.map((entry) => <li key={entry.id}><code>{entry.password}</code><button className="text-button text-button--danger" type="button" onClick={() => void remove(entry.id)}>Löschen</button></li>)}</ul></FadeContent>}
  </section>;
}
