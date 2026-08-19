/** Design: eine React-Bits-Spotlight-Karte für den nachprüfbaren Sicherheitspfad. */

import { useEffect, useState } from "react";

import { securityApi } from "../../api/security";
import { SpotlightCard } from "../../components/react-bits/SpotlightCard";
import type { CapabilityResponse } from "../../types/api";

export function CapabilityCard() {
  const [capability, setCapability] = useState<CapabilityResponse | null>(null);

  useEffect(() => { void securityApi.capabilities().then(setCapability).catch(() => setCapability(null)); }, []);

  return <SpotlightCard className="capability-card"><p className="section-index">RUNTIME STATUS</p><h2>Der sichere Pfad bleibt CPU-basiert.</h2>{capability ? <dl><div><dt>Pfad</dt><dd>{capability.password_generation_path}</dd></div><div><dt>Architektur</dt><dd>{capability.architecture}</dd></div><div><dt>CUDA</dt><dd>nicht im Passwort- oder Hash-Demopfad</dd></div></dl> : <p className="muted">Laufzeitstatus wird nach lokaler Anmeldung abgerufen.</p>}</SpotlightCard>;
}
