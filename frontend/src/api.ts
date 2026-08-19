export type Account = { id: number; username: string };
export type SecuritySummary = { profile: string; minimum_length: number; alphabet_size: number; conservative_entropy_bits: number; all_distinct: boolean; guaranteed_classes: number };
export type Generated = { passwords: string[]; security: SecuritySummary; saved: boolean };
export type HistoryEntry = { id: number; password: string; charset: string; created_at: string };

const base = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : "Anfrage fehlgeschlagen");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  me: () => request<{ account: Account }>("/api/auth/me"),
  register: (username: string, password: string) => request<{ account: Account }>("/api/auth/register", { method: "POST", body: JSON.stringify({ username, password }) }),
  login: (username: string, password: string) => request<{ account: Account }>("/api/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  logout: () => request<void>("/api/auth/logout", { method: "POST", body: "{}" }),
  generate: (payload: { length: number; count: number; charset: string; save_history: boolean }) => request<Generated>("/api/passwords/generate", { method: "POST", body: JSON.stringify(payload) }),
  history: () => request<{ entries: HistoryEntry[] }>("/api/history"),
  deleteHistory: (id: number) => request<void>(`/api/history/${id}`, { method: "DELETE" }),
  hashDemo: (payload: { length: number; charset: string }) => request<{ algorithm: string; n: number; r: number; p: number; salt_bytes: number; output_bytes: number; duration_ms: number; verified: boolean; notice: string }>("/api/security/hash-demo", { method: "POST", body: JSON.stringify(payload) }),
};
