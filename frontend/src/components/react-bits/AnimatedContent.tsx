/**
 * React Bits source integration, adapted for PW-Tool reduced-motion policy.
 * Design: short, calm section transitions; never hide content when motion is reduced.
 */

import { useEffect, useRef, type HTMLAttributes, type ReactNode } from "react";
import { gsap } from "gsap";

import { useReducedMotion } from "../../hooks/useReducedMotion";

type Props = HTMLAttributes<HTMLDivElement> & { children: ReactNode; delay?: number; distance?: number };

export function AnimatedContent({ children, delay = 0, distance = 16, className, style, ...props }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const element = ref.current;
    if (!element || reducedMotion) return;
    const context = gsap.context(() => {
      gsap.fromTo(element, { autoAlpha: 0, y: distance }, { autoAlpha: 1, y: 0, delay, duration: 0.22, ease: "power2.out", clearProps: "transform" });
    }, element);
    return () => context.revert();
  }, [delay, distance, reducedMotion]);

  return <div ref={ref} className={className} style={{ visibility: reducedMotion ? "visible" : "hidden", ...style }} {...props}>{children}</div>;
}
