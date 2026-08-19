/** Authentisierungsendpunkte über den zentralen Cookie-Client. */

import { request } from "./client";
import type { SessionResponse } from "../types/api";

export const authApi = {
  login: (username: string, password: string) => request<SessionResponse>("/auth/login", { method: "POST", body: { username, password } }),
  register: (username: string, password: string) => request<SessionResponse>("/auth/register", { method: "POST", body: { username, password } }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  me: () => request<SessionResponse>("/auth/me"),
};
