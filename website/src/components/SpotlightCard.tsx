/** React-Bits-inspirierte quellbasierte SpotlightCard für den klar abgegrenzten TLS-LAN-Hinweis. */

import { useRef, type PropsWithChildren } from "react";

export function SpotlightCard({ children }: PropsWithChildren) {
  const ref = useRef<HTMLElement>(null);
  return <article ref={ref} className="spotlight-card" onMouseMove={(event) => {
    const element = ref.current;
    if (!element) return;
    const rect = element.getBoundingClientRect();
    element.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`);
    element.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`);
  }}>{children}</article>;
}
