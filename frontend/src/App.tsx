/** Design: ruhiges Technical Field Manual; klare Hierarchie statt dekorativer Oberflächen. */

import { useState } from "react";

import { AuthFeature } from "./features/auth/AuthFeature";
import { CapabilityCard } from "./features/capability/CapabilityCard";
import { GeneratedResults } from "./features/generator/GeneratedResults";
import { GeneratorFeature } from "./features/generator/GeneratorFeature";
import { HistoryFeature } from "./features/history/HistoryFeature";
import { HashDemoFeature } from "./features/security-demo/HashDemoFeature";
import { useSession } from "./hooks/useSession";
import type { GenerationResponse } from "./types/api";

function InspectionMark() { return <span className="inspection-mark" aria-hidden="true" />; }

export default function App() {
  const session = useSession();
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [historyRefresh, setHistoryRefresh] = useState(0);

  if (session.status === "loading") return <main className="app-loading" aria-live="polite">PW—TOOL / INITIIERE LOKALE SITZUNG …</main>;
  if (session.status === "anonymous") return <AuthFeature onAuthenticated={session.authenticated} />;

  async function logout() {
    await session.logout();
    setResult(null);
    setHistoryRefresh(0);
  }

  return <div className="app-shell">
    <aside className="app-rail" aria-label="Abschnittsnavigation"><InspectionMark /><b>PW—02</b><span className="rail-rule" /><nav><a href="#generator">01 <small>GEN</small></a><a href="#history">02 <small>VAULT</small></a><a href="#demo">03 <small>DEMO</small></a></nav><span className="rail-vertical">LOCAL / TLS-LAN CONTROLLED</span></aside>
    <header className="app-header"><a className="brand" href="#generator" aria-label="PW-Tool Generator"><InspectionMark />PW<span>/</span>TOOL</a><div className="app-header__right"><span className="account-chip">ANGEMELDET: <b>{session.account?.username}</b></span><button className="text-button" type="button" onClick={() => void logout()}>Abmelden</button></div></header>
    <main className="app-main">
      <GeneratorFeature onGenerated={(generated) => { setResult(generated); if (generated.saved) setHistoryRefresh((value) => value + 1); }} />
      <GeneratedResults result={result} onDiscard={() => setResult(null)} />
      <div className="lower-grid"><HistoryFeature refreshKey={historyRefresh} /><HashDemoFeature length={64} charset="complete" /></div>
      <CapabilityCard />
    </main>
  </div>;
}
