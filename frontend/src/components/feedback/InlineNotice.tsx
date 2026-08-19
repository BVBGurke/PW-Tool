/** Ruhige, zugängliche Rückmeldung im Field-Manual-Design. */

export type Notice = { kind: "error" | "ok" | "info"; text: string } | null;

export function InlineNotice({ notice }: { notice: Notice }) {
  if (!notice) return null;
  return <p className={`notice notice--${notice.kind}`} role={notice.kind === "error" ? "alert" : "status"}>{notice.text}</p>;
}
