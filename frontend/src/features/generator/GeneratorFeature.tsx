/** Design: technische, fokussierte Konfiguration mit sichtbarem Maximalsicherheitsprofil. */

import { type FormEvent, useId, useState } from "react";

import { passwordApi } from "../../api/passwords";
import { InlineNotice, type Notice } from "../../components/feedback/InlineNotice";
import type { GenerationInput, GenerationResponse } from "../../types/api";

const initialForm: GenerationInput = { length: 64, count: 1, charset: "complete", save_history: false };

export function GeneratorFeature({ onGenerated }: { onGenerated: (result: GenerationResponse) => void }) {
  const [form, setForm] = useState<GenerationInput>(initialForm);
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);
  const lengthId = useId();
  const countId = useId();

  async function generate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const result = await passwordApi.generate(form);
      onGenerated(result);
      setNotice({ kind: "ok", text: `${result.passwords.length} Wert(e) direkt über den OS-CSPRNG erzeugt.` });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Erzeugung fehlgeschlagen." });
    } finally {
      setBusy(false);
    }
  }

  return <section id="generator" className="generator-section" aria-labelledby="generator-title">
    <div className="generator-section__intro">
      <p className="section-index">01 / GENERATE</p>
      <h1 id="generator-title">Ein klarer<br /><em>Zufallspfad.</em></h1>
      <p>Der Generator arbeitet direkt auf dem OS-CSPRNG-CPU-Pfad. Keine Cloud, keine algorithmische Lotterie und keine GPU-Entropie.</p>
      <ul className="signal-list" aria-label="Sicherheitsmerkmale"><li>OS-CSPRNG</li><li>CPU / ARM64</li><li>Konto-geschützt</li></ul>
    </div>
    <form className="generator-panel" onSubmit={generate} noValidate>
      <div className="panel-head"><span>CONFIGURATION / SESSION</span><span className="inspection-mark" aria-hidden="true" /></div>
      <button type="button" className="preset" onClick={() => setForm({ ...form, length: 64, charset: "complete" })}>
        <span>MAXIMALES SICHERHEITSPROFIL</span><b>64 Zeichen · vollständig</b>
      </button>
      <div className="field-group">
        <label htmlFor={lengthId}>Passwortlänge <output>{form.length}</output></label>
        <input id={lengthId} type="range" min="16" max="256" value={form.length} onChange={(event) => setForm({ ...form, length: Number(event.target.value) })} />
        <small>16–256 Zeichen; das Profil setzt eine konservative 64-Zeichen-Voreinstellung.</small>
      </div>
      <div className="field-group">
        <label htmlFor={countId}>Anzahl</label>
        <input id={countId} type="number" min="1" max="10000" value={form.count} onChange={(event) => setForm({ ...form, count: Number(event.target.value) })} />
      </div>
      <fieldset>
        <legend>Zeichenauswahl</legend>
        <label className="choice"><input type="radio" checked={form.charset === "complete"} onChange={() => setForm({ ...form, charset: "complete" })} /> <span>Vollständig<small>Alle Klassen, Sonderzeichen garantiert</small></span></label>
        <label className="choice"><input type="radio" checked={form.charset === "normal"} onChange={() => setForm({ ...form, charset: "normal" })} /> <span>Kompatibel<small>Buchstaben und Ziffern</small></span></label>
      </fieldset>
      <label className="choice choice--check"><input type="checkbox" checked={form.save_history} onChange={(event) => setForm({ ...form, save_history: event.target.checked })} /> <span>Diesen Batch verschlüsselt im Verlauf speichern<small>Opt-in; Werte liegen verschlüsselt in deiner lokalen Datenbank.</small></span></label>
      <InlineNotice notice={notice} />
      <div className="panel-actions"><button className="button button--primary" disabled={busy}>{busy ? "Erzeuge …" : "Passwörter erzeugen"}</button></div>
    </form>
  </section>;
}
