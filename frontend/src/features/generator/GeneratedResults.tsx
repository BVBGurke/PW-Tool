/** Design: sensible Resultate sind sichtbar, kopierbar und sofort aktiv verwerfbar. */

import { FadeContent } from "../../components/react-bits/FadeContent";
import { useClipboard } from "../../hooks/useClipboard";
import type { GenerationResponse } from "../../types/api";

export function GeneratedResults({ result, onDiscard }: { result: GenerationResponse | null; onDiscard: () => void }) {
  const { copied, copy } = useClipboard();

  if (!result) return <section className="result-section" aria-labelledby="result-title"><p className="section-index">OUTPUT / CURRENT BATCH</p><h2 id="result-title">Sichtbare Ausgabe, kein Standardverlauf.</h2><div className="empty-state">Noch kein Batch erzeugt. Die Ausgabe erscheint nur in dieser Sitzung, sofern du sie nicht bewusst in den verschlüsselten Verlauf speicherst.</div></section>;

  return <FadeContent><section className="result-section" aria-labelledby="result-title">
    <div className="result-head"><div><p className="section-index">OUTPUT / CURRENT BATCH</p><h2 id="result-title">Prüfen, kopieren, verwerfen.</h2></div><div className="result-actions"><button type="button" className="text-button" onClick={() => void copy(result.passwords.join("\n"))}>{copied ? "Kopiert" : "Alle kopieren"}</button><button type="button" className="text-button text-button--danger" onClick={onDiscard}>Anzeige verwerfen</button></div></div>
    <p className="sensitive-note">Kopieren übergibt Werte an die Betriebssystem-Zwischenablage. Verwirf die Anzeige, sobald du die Werte abgelegt hast.</p>
    <ol className="password-list">{result.passwords.map((password, index) => <li key={`${index}-${password}`}><span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span><code>{password}</code></li>)}</ol>
    <div className="security-strip" aria-label="Sicherheitszusammenfassung"><span>MIN. {result.security.minimum_length} ZEICHEN</span><span>≈ {result.security.conservative_entropy_bits} BIT UNTERGRENZE</span><span>{result.security.all_distinct ? "EINDEUTIGER BATCH" : "DUPLIKATE ERKANNT"}</span></div>
  </section></FadeContent>;
}
