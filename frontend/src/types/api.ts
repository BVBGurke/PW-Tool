/** API- und Domänentypen für die versionierte lokale PW-Tool-Schnittstelle. */

export type Account = { id: number; username: string };
export type SessionResponse = { account: Account };

export type GenerationInput = {
  length: number;
  count: number;
  charset: "normal" | "complete";
  save_history: boolean;
};

export type GenerationResponse = {
  passwords: string[];
  security: {
    profile: "normal" | "complete";
    minimum_length: number;
    alphabet_size: number;
    conservative_entropy_bits: number;
    all_distinct: boolean;
    guaranteed_classes: number;
  };
  saved: boolean;
};

export type HistoryEntry = {
  id: number;
  password: string;
  charset: "normal" | "complete";
  created_at: string;
};

export type HashDemoResponse = {
  algorithm: "scrypt";
  n: number;
  r: number;
  p: number;
  salt_bytes: number;
  output_bytes: number;
  duration_ms: number;
  verified: boolean;
  notice: string;
};

export type CapabilityResponse = {
  system: string;
  architecture: string;
  password_generation_path: "os-csprng-cpu";
  cuda: { used_for_passwords: boolean; used_for_hash_demo: boolean; status: string };
};
