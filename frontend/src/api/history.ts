/** Kontogebundene Verlaufsendpunkte. */

import { request } from "./client";
import type { HistoryEntry } from "../types/api";

export const historyApi = {
  list: () => request<{ entries: HistoryEntry[] }>("/history"),
  remove: (entryId: number) => request<void>(`/history/${entryId}`, { method: "DELETE" }),
};
