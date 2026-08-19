/** Kapselt Sitzungsinitialisierung und vermeidet jede Token-Persistenz im Client. */

import { useCallback, useEffect, useState } from "react";

import { authApi } from "../api/auth";
import type { Account } from "../types/api";

type SessionState = { status: "loading" | "anonymous" | "authenticated"; account: Account | null };

export function useSession() {
  const [state, setState] = useState<SessionState>({ status: "loading", account: null });

  const refresh = useCallback(async () => {
    try {
      const response = await authApi.me();
      setState({ status: "authenticated", account: response.account });
    } catch {
      setState({ status: "anonymous", account: null });
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  return {
    ...state,
    authenticated: (account: Account) => setState({ status: "authenticated", account }),
    logout: async () => { await authApi.logout(); setState({ status: "anonymous", account: null }); },
  };
}
