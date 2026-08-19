# Zielarchitektur für PW-Tool

## Leitprinzip

PW-Tool bleibt ein **lokaler beziehungsweise bewusst TLS-abgesicherter LAN-Dienst**. Das System erzeugt Passwörter über den OS-CSPRNG-CPU-Pfad, verwaltet lokale Konten und verschlüsselt nur ausdrücklich gespeicherte Verlaufswerte. Es entwickelt sich weder zu einem öffentlichen Dienst noch zu einem Analyse-, Angriffs- oder Crackwerkzeug.

Der Weg einer fachlichen Anfrage ist ausnahmslos:

```text
React-Feature → API-Client → FastAPI-Route → Service → Core-/Security-Funktion → Repository → SQLite
```

Routen enthalten keine Krypto-, Geschäfts- oder SQL-Logik. Repositories kennen keine HTTP-Objekte. Services geben fachliche Ergebnisse oder wohldefinierte Domainfehler zurück. Der API-Layer übersetzt diese Fehler zentral in stabile, nicht sensitive HTTP-Antworten.

## Backend-Zielbaum

```text
backend/
  app/
    api/
      dependencies.py        aktuelle Sitzung, Request-Kontext
      router.py              API-V1-Aggregation
      routes/
        auth.py              Registrierung, Login, Logout, aktuelle Sitzung
        passwords.py         Erzeugung und Sicherheitszusammenfassung
        history.py           eigene Verlaufseinträge lesen/löschen
        security.py          selbstbezogene Hash-Demo und Capability-Status
        health.py            Health- und Readiness-Status
    core/
      config.py              validierte Laufzeitkonfiguration
      exceptions.py          Domainfehler und zentrale HTTP-Übersetzung
      password_policy.py     reine CSPRNG-Policy und Sicherheitszusammenfassung
      logging.py             redigierte, strukturierte Laufzeitprotokolle
    middleware/
      request_id.py          sichere Korrelations-ID
      security_headers.py    No-Store, nosniff, Framing- und Referrer-Schutz
      origin_check.py        Origin-Prüfung für zustandsändernde Anfragen
      rate_limit.py          prozesslokale Schutzgrenzen
    models/
      records.py             interne Datenbankdatenträger/Typen
    repositories/
      accounts.py            Accounts, eindeutige Benutzerbehandlung
      sessions.py            opaque Session-Digests und Ablauf
      history.py             kontogebundener Verlauf
    schemas/
      auth.py                Pydantic Request-/Response-Verträge
      passwords.py
      history.py
      security.py
      common.py
    security/
      passwords.py           scrypt-KDF und konstanter Vergleich
      sessions.py            Token, HMAC-Digest, Cookie-Policy
      history_crypto.py      AES-GCM mit kontogebundener AAD
    services/
      auth.py
      passwords.py
      history.py
      hash_demo.py
      capability.py
    main.py
  tests/
  .env.example
  pyproject.toml
```

`backend/main.py` bleibt als kompatibler Startpunkt erhalten und importiert ausschließlich `app.main`. Die bisherige Struktur `backend/pwtool/` wird nach einer vollständigen Regression entfernt oder – falls für bestehende Nutzer sinnvoll – durch eine dokumentierte, dünne Kompatibilitätsschicht ersetzt. Es darf keine zwei aktiven Implementierungen derselben Sicherheitslogik geben.

## Datenmodell und Autorisierungsgrenzen

| Entität | Zweck | Integritäts- und Zugriffsregel |
|---|---|---|
| `accounts` | Benutzername, Passwort-KDF-Resultat, Erstellung | Benutzernamen sind eindeutig; nur eine nicht sensitive Kontosicht verlässt den Service. |
| `sessions` | HMAC-Digest eines zufälligen opaque Session-Tokens, Account-ID, Ablauf | Rohes Token wird nie gespeichert; abgelaufene Einträge werden bereinigt; Logout widerruft serverseitig. |
| `history_entries` | AES-GCM-Nonce, Ciphertext, Zeichensatz, Erstellung | Jede Auswahl und Löschung enthält zwingend `account_id`; eine ID allein autorisiert niemals Zugriff. |

Verlaufstexte erhalten pro Account eine zusätzliche authentifizierte Datenbindung. Dadurch kann ein Ciphertext eines Kontos nicht gültig im Kontext eines anderen Kontos entschlüsselt werden. Logeinträge dürfen niemals Rohpasswörter, Roh-Sessiontokens, Authorization-/Cookie-Header, KDF-Resultate, Schlüsselmaterial oder verschlüsselte Verlaufsciphertexte enthalten.

## API-Vertrag und Fehlersemantik

| Bereich | Endpunkte | Autorisierung | Besondere Regeln |
|---|---|---|---|
| System | `GET /api/v1/health`, `GET /api/v1/readiness` | keine | Liefert keine Secrets, Dateipfade oder vollständige CORS-Konfiguration. |
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` | Login/Registrierung offen; Rest sitzungsgebunden | Antwortfehler sind nicht enumerationstauglich; Login und Registrierung sind gedrosselt. |
| Generator | `POST /passwords/generate` | Sitzung | Längen-, Batch- und Zeichensatzgrenzen; CSPRNG nur serverseitig; Verlauf ist opt-in. |
| Verlauf | `GET /history`, `DELETE /history/{entry_id}` | Sitzung | Höchstens eigene Einträge; Löschung ist idempotenzarm und liefert bei fremder/nicht vorhandener ID denselben nicht sensitiven Fehler. |
| Sicherheitsdemo | `POST /security/hash-demo` | Sitzung | Nur frischer selbst erzeugter Wert, keine Eingabe für Fremdhashes, Kandidaten oder Wortlisten. |
| Capability | `GET /security/capabilities` | Sitzung | Informative CPU-/ARM64-/optionale CUDA-Erkennung; keine GPU-Erzeugungs- oder Crackroute. |

Fehlerantworten werden als `application/problem+json` mit `request_id`, stabilem Fehlercode und nutzerverständlicher deutscher Nachricht ausgegeben. Validierungsdetails bleiben bei sicheren Eingabefehlern präzise, aber enthalten keine internen Modulnamen, SQL-Nachrichten oder Stacktraces.

## Laufzeit-, Cookie- und LAN-Sicherheitsmodell

| Betriebsart | Bindung / Origin | Sitzungscookie | Zulässigkeit |
|---|---|---|---|
| Lokale Entwicklung | `127.0.0.1` oder `localhost`, explizite HTTP-Origin | `HttpOnly`, `SameSite=Lax`, kein `Secure` nur für diesen isolierten Entwicklungsmodus | Zulässig für lokale Entwicklung. |
| Lokale Produktnutzung | `127.0.0.1` hinter lokalem TLS oder über einen lokalen sicheren Launcher | `HttpOnly`, `Secure`, `SameSite=Strict` soweit UX-kompatibel | Bevorzugte Nutzungsform. |
| LAN | explizite **HTTPS**-Origins, TLS-Reverse-Proxy und bewusst aktivierte LAN-Bindung | `HttpOnly`, `Secure`, `SameSite=Strict`, Pfad `/`, kurze Laufzeit | Zulässig nur bei vollständiger TLS-Konfiguration. |
| Internet | öffentliche Bindung, öffentliche Origins oder Portfreigaben | nicht zutreffend | Ausgeschlossen. |

Eine LAN-Konfiguration mit HTTP-Origin, Wildcard-CORS, fehlender Cookie-Absicherung oder nicht lokalem Bindungsmodus ohne ausdrückliche TLS-Angaben wird beim Start abgelehnt. Für alle zustandsändernden Methoden (`POST`, `PUT`, `PATCH`, `DELETE`) ist eine strikte Origin-Prüfung erforderlich. CORS ist nur ein Browser-Mechanismus und ersetzt diese Prüfung nicht. API-Antworten mit sensiblen Konten-, Generator- oder Verlaufsdaten bekommen `Cache-Control: no-store`.

## React- und TypeScript-Zielbaum

```text
frontend/src/
  api/
    client.ts               Fetch, Problem-Details, credentials, Request-ID
    auth.ts
    passwords.ts
    history.ts
    security.ts
  components/
    feedback/               Loading, Empty, Error, Success, InlineNotice
    primitives/             Button, Field, Dialog, CodeValue, AccessibleCard
    react-bits/             geprüfte, lokal übernommene React-Bits-Komponenten
  features/
    auth/
    generator/
    history/
    security-demo/
    capability/
  hooks/
    useReducedMotion.ts
    useClipboard.ts
    useSession.ts
  layouts/
    AuthLayout.tsx
    AppLayout.tsx
  styles/
    tokens.css
    base.css
    components.css
  types/
    api.ts
    domain.ts
  App.tsx
```

Der API-Client sendet Cookies nur über `credentials: "include"`, liest aber keine Sessiontokens aus. Alle Komponenten haben klar unterscheidbare Loading-, Error-, Empty- und Success-Zustände. Passwortwerte sind standardmäßig weder persistent noch in einem globalen Client-Store; die Nutzerin oder der Nutzer kann sie nach einer Erzeugung sofort sichtbar verwerfen.

## React-Bits-Integrationsmatrix

React Bits wird nach der offiziellen Quellcode-Integrationsmethode übernommen; die Dokumentation erlaubt die manuelle Übernahme komponentenspezifischen Codes und nennt externe Abhängigkeiten pro Komponente.[1]

| React-Bits-Komponente | UI-Bereich | Zielnutzen | Abhängigkeit | Accessibility- und Performance-Grenze |
|---|---|---|---|---|
| `AnimatedContent` | Eintreten des Generatorbereichs und einmalige Auth-/App-Abschnittswechsel | Verdeutlicht Kontextwechsel ohne die Arbeitsoberfläche zu überladen. | GSAP; die offizielle API bietet Dauer, Distanz, Schwelle und Opacity-Steuerung.[2] | Nur bei `prefers-reduced-motion: no-preference`; sonst sofort sichtbar. Keine Animation für Tastatur- oder Fehlermeldungsaktionen. |
| `FadeContent` | Ergebnis-, Verlauf- und Statusbereiche beim ersten Erscheinen | Macht asynchrones Laden nachvollziehbar und ruhig. | GSAP; die Komponente unterstützt unter anderem Dauer, Schwelle und optionalen Blur.[3] | Blur bleibt deaktiviert; Animationen unter 220 ms, keine Wiederholung beim Scrollen und kein Einfluss auf Screenreader-Live-Regionen. |
| `SpotlightCard` | Einzelne Sicherheits-/Capability-Karte | Sorgt für einen klaren visuellen Fokus auf den CSPRNG-/TLS-Status. | Keine in der offiziellen Komponentenseite ausgewiesene Fremdbibliothek; Farbe ist konfigurierbar.[4] | Fokus bleibt durch semantische Karte und sichtbare Tastaturkontur zugänglich; auf Touch-Geräten rein statische, kontraststarke Fallback-Darstellung. |

React Bits ist damit in inhaltlichen Oberflächenbereichen und nicht lediglich im Hintergrund integriert. Für Passwortinputs, Felder, Dialoge, Tabellen, Fehlermeldungen und Live-Regions wird keine beliebige Effektsammlung eingesetzt: Diese müssen als semantische, tastaturbedienbare Komponenten stabil bleiben, falls die React-Bits-Bibliothek hierfür keine fachlich gleichwertige Primitive bereitstellt.

## UI- und Accessibility-Standard

Die Oberfläche folgt einem ruhigen, technischen Field-Manual-Stil mit dunkler Tinte, warmen Papierflächen, einem zurückhaltenden Sicherheitsakzent, klarer Rasterung, hoher Informationshierarchie und keinen Glasflächen oder Neonverläufen. Alle fokussierbaren Elemente besitzen sichtbare Fokusindikatoren; Fehlermeldungen sind über `aria-describedby` mit Feldern verknüpft; Statusmeldungen nutzen passende Live-Regions; Kontrast und Touch-Ziele werden auf Mobilgeräten geprüft. Navigation, Dialoge, Ergebnislöschung und Kopieren sind vollständig per Tastatur erreichbar.

## Quellen

[1] [React Bits – Installation](https://reactbits.dev/get-started/installation)

[2] [React Bits – Animated Content](https://reactbits.dev/animations/animated-content)

[3] [React Bits – Fade Content](https://reactbits.dev/animations/fade-content)

[4] [React Bits – Spotlight Card](https://reactbits.dev/animations/spotlight-card)
