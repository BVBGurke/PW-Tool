/** Zentraler, cookie-basierter Client; Designprinzip: keine Tokens im Browser-Speicher. */

const localApiBaseUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? localApiBaseUrl;

export class ApiProblem extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId?: string;

  constructor(status: number, code: string, message: string, requestId?: string) {
    super(message);
    this.name = "ApiProblem";
    this.status = status;
    this.code = code;
    this.requestId = requestId;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown };

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.body === undefined ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    const fallback = "Die lokale API konnte die Anfrage nicht ausführen.";
    const body = await response.json().catch(() => null) as { detail?: string; type?: string; request_id?: string } | null;
    const code = body?.type?.split("/").at(-1) ?? "request_failed";
    throw new ApiProblem(response.status, code, body?.detail ?? fallback, body?.request_id);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
