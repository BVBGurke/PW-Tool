# Migrationsstatus

Die vorherige flache FastAPI-Implementierung unter `backend/pwtool/` wurde vollständig durch die strukturierte Anwendung unter `backend/app/` ersetzt. Die alte Textual-CLI bleibt bewusst nicht als parallele Produktoberfläche erhalten; ihre sicherheitsrelevanten Funktionsgrenzen wurden in der Feature-Matrix geprüft und in API, Services und React-App übernommen.

| Früherer Bereich | Neue Position | Migrationsstatus |
|---|---|---|
| CSPRNG-Passwortkern | `backend/app/core/password_policy.py` | Erhalten und isoliert testbar. |
| Konten, KDF und Sessions | `security/`, `services/auth.py`, `repositories/` | Erhalten, geschichtet und durch API-Tests abgesichert. |
| Datenbank und Verlauf | `repositories/`, `services/history.py`, `security/history_crypto.py` | Erhalten; IDOR-sichere Auswahl und Löschung getestet. |
| Routen und Pydantic-Modelle | `api/routes/`, `schemas/` | Entkoppelt und auf `/api/v1` versioniert. |
| Rate Limit, Origin und Header | `middleware/` | Zentralisiert. |
| React-Monolith | `frontend/src/features/`, `api/`, `hooks/`, `types/` | In Fachbereiche aufgeteilt. |
| Vorherige UI-Effekte | `components/react-bits/` | React-Bits-Integration mit Reduced-Motion-Fallback. |
| Direkte LAN-Bindung | TLS-Reverse-Proxy-Modell | Bewusst entfernt, um unsichere HTTP-Sitzungen im LAN zu vermeiden. |

Die vollständige Bestandsaufnahme und Funktionsparität ist in [`MODERNIZATION_BASELINE.md`](MODERNIZATION_BASELINE.md) festgehalten. Das verbindliche Zielmodell dokumentiert [`TARGET_ARCHITECTURE.md`](TARGET_ARCHITECTURE.md).
