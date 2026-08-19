/**
 * React Bits SpotlightCard source integration with a touch-safe static fallback.
 * Design: security status gets a restrained pointer spotlight, never glass/neon treatment.
 */

import { useRef, type PropsWithChildren } from "react";

type Props = PropsWithChildren<{ className?: string; spotlightColor?: string }>;

export function SpotlightCard({ children, className = "", spotlightColor = "rgba(48, 107, 84, 0.15)" }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const handleMouseMove: React.MouseEventHandler<HTMLDivElement> = (event) => {
    const element = ref.current;
    if (!element) return;
    const rect = element.getBoundingClientRect();
    element.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`);
    element.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`);
    element.style.setProperty("--spotlight-color", spotlightColor);
  };

  return <div ref={ref} onMouseMove={handleMouseMove} className={`spotlight-card ${className}`}>{children}</div>;
}
