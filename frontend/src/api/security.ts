/** Begrenzte Hash-Demo und harmlose Laufzeit-Capability-Abfragen. */

import { request } from "./client";
import type { CapabilityResponse, HashDemoResponse } from "../types/api";

export const securityApi = {
  hashDemo: (input: { length: number; charset: "normal" | "complete" }) => request<HashDemoResponse>("/security/hash-demo", { method: "POST", body: input }),
  capabilities: () => request<CapabilityResponse>("/security/capabilities"),
};
