/** Design: Schulungsfunktion als begrenzter Nachweis, nicht als Angriffsoberfläche. */

import { useState } from "react";

import { securityApi } from "../../api/security";
import { InlineNotice, type Notice } from "../../components/feedback/InlineNotice";
import { FadeContent } from "../../components/react-bits/FadeContent";
import type { HashDemoResponse } from "../../types/api";

export function HashDemoFeature({ length, charset }: { length: number; charset: "normal" | "complete" }) {
  const [result, setResult] = useState<HashDemoResponse | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true); setNotice(null);
    try {
      const value = await securityApi.hashDemo({ length, charset });
      setResult(value);
      setNotice({ kind: "info", text: "Selbstbezogene Hash-Demo abgeschlossen; kein Demo-Wert wurde angezeigt." });
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Hash-Demo fehlgeschlagen." });
    } finally { setBusy(false); }
  }

  return <section id="demo" className="demo-section" aria-labelledby="demo-title"><p className="section-index">03 / HASH DEMO</p><h2 id="demo-title">Prüfen, nicht raten.</h2><p>Die Demo nutzt einen frischen, nicht angezeigten Wert und scrypt. Fremdhashes, Wortlisten und Rateversuche sind nicht vorgesehen.</p><button className="button button--secondary" type="button" disabled={busy} onClick={() => void run()}>{busy ? "Prüfe …" : "Hash-Demo starten"}</button><InlineNotice notice={notice} />
    {result && <FadeContent><div className="demo-result"><b>{result.algorithm.toUpperCase()} / SELBSTPRÜFUNG {result.verified ? "OK" : "FEHLER"}</b><span>{result.duration_ms} ms · {result.output_bytes} Byte · nur lokale Metadaten</span></div></FadeContent>}
  </section>;
}
