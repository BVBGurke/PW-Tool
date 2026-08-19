/** Design: ruhige lokale Zugangskontrolle, semantische Felder und sofortige Fehlerrückmeldung. */

import { type FormEvent, useId, useState } from "react";

import { authApi } from "../../api/auth";
import { InlineNotice, type Notice } from "../../components/feedback/InlineNotice";
import { AnimatedContent } from "../../components/react-bits/AnimatedContent";
import type { Account } from "../../types/api";

export function AuthFeature({ onAuthenticated }: { onAuthenticated: (account: Account) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);
  const usernameId = useId();
  const passwordId = useId();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const response = mode === "login" ? await authApi.login(username, password) : await authApi.register(username, password);
      onAuthenticated(response.account);
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Anmeldung fehlgeschlagen." });
    } finally {
      setBusy(false);
    }
  }

  return <main className="auth-layout" aria-labelledby="auth-title">
    <aside className="auth-layout__rail" aria-label="PW-Tool Status">
      <span className="inspection-mark" aria-hidden="true" />
      <span>PW—LAN / 01</span><i aria-hidden="true" /><small>LOCAL ACCOUNT GATE</small>
    </aside>
    <AnimatedContent className="auth-card">
      <p className="eyebrow">PW-TOOL / GESCHÜTZTER ZUGANG</p>
      <h1 id="auth-title">{mode === "login" ? "Lokale Sitzung öffnen." : "Lokales Konto anlegen."}</h1>
      <p>Die Anwendung bleibt auf deinem Server oder im bewusst konfigurierten LAN. Kontokennwörter werden nicht im Klartext gespeichert.</p>
      <form onSubmit={submit} noValidate>
        <div className="field-group">
          <label htmlFor={usernameId}>Benutzername</label>
          <input id={usernameId} value={username} minLength={3} maxLength={64} onChange={(event) => setUsername(event.target.value)} required autoComplete="username" aria-describedby={notice?.kind === "error" ? "auth-notice" : undefined} />
        </div>
        <div className="field-group">
          <label htmlFor={passwordId}>Kontokennwort</label>
          <input id={passwordId} value={password} minLength={12} onChange={(event) => setPassword(event.target.value)} required type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} aria-describedby={notice?.kind === "error" ? "auth-notice" : undefined} />
          <small>Mindestens 12 Zeichen; nur lokal als langsamer scrypt-Wert gespeichert.</small>
        </div>
        <div id="auth-notice"><InlineNotice notice={notice} /></div>
        <button disabled={busy} className="button button--primary">{busy ? "Bitte warten …" : mode === "login" ? "Anmelden" : "Konto erstellen"}</button>
      </form>
      <button className="text-button" type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setNotice(null); }}>
        {mode === "login" ? "Noch kein Konto? Registrierung öffnen" : "Bereits registriert? Zur Anmeldung"}
      </button>
    </AnimatedContent>
  </main>;
}
