/**
 * React Bits source integration, adapted to one short in-place fade for application states.
 * Design: no blur, no scroll-trigger, no animation for reduced-motion users.
 */

import { useEffect, useRef, type HTMLAttributes, type ReactNode } from "react";
import { gsap } from "gsap";

import { useReducedMotion } from "../../hooks/useReducedMotion";

type Props = HTMLAttributes<HTMLDivElement> & { children: ReactNode; delay?: number };

export function FadeContent({ children, delay = 0, className, style, ...props }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const element = ref.current;
    if (!element || reducedMotion) return;
    const context = gsap.context(() => {
      gsap.fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, delay, duration: 0.18, ease: "power2.out" });
    }, element);
    return () => context.revert();
  }, [delay, reducedMotion]);

  return <div ref={ref} className={className} style={{ visibility: reducedMotion ? "visible" : "hidden", ...style }} {...props}>{children}</div>;
}
