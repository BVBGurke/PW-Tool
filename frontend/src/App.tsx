import { FormEvent, useEffect, useState } from "react";
import { api, Account, Generated, HistoryEntry } from "./api";

type Notice = { kind: "error" | "ok" | "info"; text: string } | null;

const initialForm = { length: 64, count: 1, charset: "complete", save_history: false };

function InspectionMark() { return <span className="inspection-mark" aria-hidden="true" />; }

function Auth({ onAuthenticated }: { onAuthenticated: (account: Account) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true); setNotice(null);
    try {
      const response = mode === "login" ? await api.login(username, password) : await api.register(username, password);
      onAuthenticated(response.account);
    } catch (error) { setNotice({ kind: "error", text: error instanceof Error ? error.message : "Anmeldung fehlgeschlagen" }); }
    finally { setBusy(false); }
  }

  return <main className="auth-shell">
    <aside className="auth-rail"><InspectionMark /><span>PW—LAN / 01</span><i /><small>LOCAL ACCOUNT GATE</small></aside>
    <section className="auth-card">
      <div className="eyebrow">PW-TOOL / GESCHÜTZTER ZUGANG</div>
      <h1>{mode === "login" ? "Willkommen zurück." : "Lokales Konto anlegen."}</h1>
      <p>Die Anwendung bleibt auf deinem Server oder im bewusst konfigurierten LAN. Kontokennwörter werden nicht im Klartext gespeichert.</p>
      <form onSubmit={submit}>
        <label>Benutzername<input value={username} minLength={3} maxLength={64} onChange={e => setUsername(e.target.value)} required autoComplete="username" /></label>
        <label>Kontokennwort<input value={password} minLength={12} onChange={e => setPassword(e.target.value)} required type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
        {notice && <div className={`notice ${notice.kind}`}>{notice.text}</div>}
        <button disabled={busy} className="button primary">{busy ? "Bitte warten …" : mode === "login" ? "Anmelden" : "Konto erstellen"}</button>
      </form>
      <button className="text-button" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Noch kein Konto? Registrieren" : "Bereits registriert? Anmelden"}</button>
    </section>
  </main>;
}

function copy(values: string[], setNotice: (n: Notice) => void) {
  navigator.clipboard.writeText(values.join("\n"))
    .then(() => setNotice({ kind: "ok", text: "Ergebnisse wurden in die Zwischenablage kopiert." }))
    .catch(() => setNotice({ kind: "error", text: "Die Zwischenablage ist in dieser Umgebung nicht verfügbar." }));
}

export default function App() {
  const [account, setAccount] = useState<Account | null>(null);
  const [ready, setReady] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState<Generated | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [demo, setDemo] = useState<{ algorithm: string; duration_ms: number; verified: boolean } | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);

  const loadHistory = async () => { try { setHistory((await api.history()).entries); } catch { setHistory([]); } };
  useEffect(() => { api.me().then(r => { setAccount(r.account); loadHistory(); }).catch(() => setAccount(null)).finally(() => setReady(true)); }, []);
  if (!ready) return <div className="loading">PW—TOOL / INITIALISIERE LOKALE SITZUNG …</div>;
  if (!account) return <Auth onAuthenticated={a => { setAccount(a); setReady(true); }} />;

  async function generate(event: FormEvent) {
    event.preventDefault(); setBusy(true); setNotice(null);
    try { const generated = await api.generate(form); setResult(generated); if (form.save_history) await loadHistory(); setNotice({ kind: "ok", text: `${generated.passwords.length} Wert(e) lokal erzeugt.` }); }
    catch (error) { setNotice({ kind: "error", text: error instanceof Error ? error.message : "Erzeugung fehlgeschlagen" }); }
    finally { setBusy(false); }
  }
  async function runDemo() {
    setBusy(true); setNotice(null);
    try { const value = await api.hashDemo({ length: form.length, charset: form.charset }); setDemo(value); setNotice({ kind: "info", text: "Lokale Hash-Demo abgeschlossen; keine Demo-Werte wurden angezeigt." }); }
    catch (error) { setNotice({ kind: "error", text: error instanceof Error ? error.message : "Hash-Demo fehlgeschlagen" }); }
    finally { setBusy(false); }
  }
  async function logout() { await api.logout(); setAccount(null); setResult(null); setHistory([]); }

  return <div className="app-shell">
    <aside className="app-rail"><InspectionMark /><b>PW—02</b><span className="rail-rule" /><nav><a href="#generator">01<br /><small>GEN</small></a><a href="#history">02<br /><small>VAULT</small></a><a href="#demo">03<br /><small>DEMO</small></a></nav><span className="rail-vertical">LOCAL / LAN CONTROLLED</span></aside>
    <header className="app-header"><div className="brand"><InspectionMark />PW<span>/</span>TOOL</div><div className="account-chip">ANGEMELDET: <b>{account.username}</b></div><button className="logout" onClick={logout}>Abmelden ↗</button></header>
    <main className="app-main">
      <section id="generator" className="generator-grid">
        <div className="intro"><div className="section-index">01 / GENERATE</div><h1>Ein klarer<br /><em>Zufallspfad.</em></h1><p>Der Generator läuft direkt auf dem OS-CSPRNG-CPU-Pfad. Keine Cloud, keine algorithmische Lotterie.</p><div className="signal-list"><span>✓ OS-CSPRNG</span><span>✓ CPU / ARM64</span><span>✓ Konto-geschützt</span></div></div>
        <form className="generator-panel" onSubmit={generate}>
          <div className="panel-head"><span>CONFIGURATION / SESSION</span><InspectionMark /></div>
          <label>Passwortlänge <output>{form.length}</output><input type="range" min="16" max="128" value={form.length} onChange={e => setForm({ ...form, length: Number(e.target.value) })} /><small>16–256 Zeichen sind erlaubt.</small></label>
          <label>Anzahl <input type="number" min="1" max="10000" value={form.count} onChange={e => setForm({ ...form, count: Number(e.target.value) })} /></label>
          <fieldset><legend>Zeichenauswahl</legend><label className="choice"><input type="radio" checked={form.charset === "complete"} onChange={() => setForm({ ...form, charset: "complete" })} /> Vollständig <small>Alle Klassen, Sonderzeichen garantiert</small></label><label className="choice"><input type="radio" checked={form.charset === "normal"} onChange={() => setForm({ ...form, charset: "normal" })} /> Kompatibel <small>Buchstaben und Ziffern</small></label></fieldset>
          <label className="history-choice"><input type="checkbox" checked={form.save_history} onChange={e => setForm({ ...form, save_history: e.target.checked })} /> Diesen Batch verschlüsselt im Verlauf speichern</label>
          <div className="panel-actions"><button className="button primary" disabled={busy}>Passwörter erzeugen</button><button type="button" className="button secondary" disabled={busy} onClick={runDemo}>Hash-Demo</button></div>
        </form>
      </section>
      {notice && <div className={`notice app-notice ${notice.kind}`}>{notice.text}</div>}
      <section className="result-section">
        <div className="result-head"><div className="section-index">OUTPUT / CURRENT BATCH</div>{result && <button className="text-button" onClick={() => copy(result.passwords, setNotice)}>Alle kopieren</button>}</div>
        {result ? <><div className="password-list">{result.passwords.map((password, i) => <code key={`${password}-${i}`}>{String(i + 1).padStart(2, "0")} <b>{password}</b></code>)}</div><div className="security-strip"><span>MIN. {result.security.minimum_length} ZEICHEN</span><span>≈ {result.security.conservative_entropy_bits} BIT UNTERGRENZE</span><span>{result.security.all_distinct ? "EINDEUTIGER BATCH" : "DUPLIKATE ERKANNT"}</span></div></> : <div className="empty">Noch kein Batch erzeugt. Die Ausgabe erscheint nur in dieser Sitzung, sofern du sie nicht bewusst in den verschlüsselten Verlauf speicherst.</div>}
      </section>
      <section className="lower-grid"><section id="history" className="history-section"><div className="section-index">02 / ENCRYPTED HISTORY</div><h2>Bewusst speichern.</h2><p>Opt-in-Verlauf: Werte liegen nur verschlüsselt in der lokalen Datenbank.</p>{history.length ? <div className="history-list">{history.map(entry => <div key={entry.id}><code>{entry.password}</code><button onClick={async () => { await api.deleteHistory(entry.id); await loadHistory(); }}>Löschen</button></div>)}</div> : <div className="empty compact">Keine gespeicherten Einträge.</div>}</section><section id="demo" className="demo-section"><div className="section-index">03 / HASH DEMO</div><h2>Prüfen, nicht raten.</h2><p>Die Demo nutzt einen frischen, nicht angezeigten Wert und scrypt. Fremdhashes, Wortlisten und Rateversuche sind nicht vorgesehen.</p>{demo ? <div className="demo-result"><b>{demo.algorithm.toUpperCase()} / SELBSTPRÜFUNG {demo.verified ? "OK" : "FEHLER"}</b><span>{demo.duration_ms} ms · nur lokale Metadaten</span></div> : <div className="empty compact">Noch keine Hash-Demo ausgeführt.</div>}</section></section>
    </main>
  </div>;
}
