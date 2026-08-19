# Validierungsnotizen

## Frontend-Vorschau, Desktop-Anmeldeansicht

Die lokale Vite-Vorschau auf `127.0.0.1:4173` wurde mit dem geschichteten FastAPI-Backend auf `127.0.0.1:8000` geprüft. Die nicht authentifizierte Ansicht rendert eine klar strukturierte lokale Anmeldekarte mit sichtbaren Beschriftungen, beiden Eingabefeldern, Mindestkennworthinweis, primärer Aktion und Umschalter zur Registrierung. Die linke Statusleiste, Papier-/Tinten-Kontraste und Fokusstruktur sind ohne Überlauf sichtbar.

Die Prüfung bestätigt lediglich die gerenderte lokale Anmeldeansicht. Authentifizierte Interaktionen, mobile Breakpoints, Netzwerkfehler und vollständige API-Flows werden im abschließenden Qualitätsreview nochmals getrennt geprüft.

Der Registrierungsumschalter änderte Überschrift und primäre Aktion ohne Layoutbruch. Beide beschrifteten Eingabefelder ließen sich per Browserautomatisierung mit einem lokalen Testkonto befüllen; das Kennwortfeld blieb visuell maskiert. Der Submit- und Generatorflow wird im nächsten Schritt geprüft und die lokale Testkonfiguration danach entfernt.

Eine Vorschau auf Port `4173` wurde erwartungsgemäß mit `Failed to fetch` abgelehnt, weil dieser Port nicht als lokale Origin konfiguriert war. Die Browser- und Serverdiagnose zeigte eine CORS-Preflight-Ablehnung. Die Standardvorschau auf Port `5173` entspricht dagegen der explizit erzeugten lokalen Origin-Konfiguration und ist wieder erreichbar. Das bestätigt, dass die Origin-Grenze nicht stillschweigend aufgeweicht wird.

Über die erlaubte Standard-Origin ließ sich die Registrierung erneut aufrufen und beide Felder semantisch korrekt befüllen. Der tatsächliche Submit prüft anschließend die Cookie-Sitzung, API-Antwort und den Wechsel in die Generatoransicht.

Nach der ersten erfolgreichen Registrierung zeigte der geschützte App-Bereich bei Verlauf und Capability noch eine abgelaufene Sitzung. Ursache war die bisher fest auf `127.0.0.1` gesetzte lokale API-Basis bei einer Frontend-Origin `localhost`: Für die SameSite-Cookie-Policy sind diese Hostnamen nicht dieselbe Site. Der API-Client leitet die lokale API-Basis deshalb jetzt aus `window.location.hostname` ab; ein expliziter `VITE_API_BASE_URL` bleibt für TLS-/Reverse-Proxy-LAN vorgesehen. Der Build nach dieser Korrektur bestand; der erneute echte Sitzungsflow folgt.

Für den abschließenden SameSite-Regressionstest wurde ein neues lokales Testkonto über die erlaubte `localhost:5173`-Origin vorbereitet. Die tatsächliche Registrierung und die geschützten Folgerouten werden unmittelbar danach geprüft.

Die erneute Registrierung war erfolgreich. Danach lieferten Verlauf und Capability-Route ohne erneute Anmeldung die erwarteten Daten; der Laufzeitstatus bestätigte `os-csprng-cpu` und hielt CUDA explizit aus Passwort- und Hash-Demopfad heraus. Die echte Generatorroute erzeugte einen 64 Zeichen langen vollständigen Wert, zeigte die konservative Entropieuntergrenze sowie die sichtbaren Aktionen zum Kopieren und sofortigen Verwerfen. Damit ist die React-Oberfläche nicht nur eine Demo, sondern an die echten Backend-Daten und die serverseitige Sitzung gebunden.

Die App wurde anschließend innerhalb eines echten 375-Pixel-Browserframes gerendert. Generator und Konfigurationspanel wechseln erwartungsgemäß in eine Spalte; Felder, Preset, Radio-/Checkbox-Zeilen und primäre Aktion bleiben innerhalb der Framebreite. Die obere mobile Statusleiste zeigte jedoch eine unnötig dichte Mischung aus Kennung und Abschnittslinks. Vor Abschluss wird die Kennung auf schmalen Ansichten verborgen und der Navigationsabstand reduziert.

Nach der Responsive-Nachbesserung ist die sekundäre Kennung auf schmalen Ansichten ausgeblendet, während die drei Abschnittslinks erhalten bleiben. Der 375-Pixel-Frame bestätigt weiterhin den einspaltigen Generator und sichtbare, bedienbare Eingabefelder ohne horizontalen Überlauf. Die lokale Browserprüfung wurde anschließend beendet.
