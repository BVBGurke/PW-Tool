/** Fehlerbewusste Zwischenablagehilfe für bewusst ausgewählte Passwortwerte. */

import { useState } from "react";

export function useClipboard() {
  const [copied, setCopied] = useState(false);

  async function copy(value: string): Promise<void> {
    if (!navigator.clipboard) throw new Error("Die Zwischenablage ist in dieser Umgebung nicht verfügbar.");
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return { copied, copy };
}
