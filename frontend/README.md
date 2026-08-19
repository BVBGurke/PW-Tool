# PW-Tool Frontend

Die React-App nutzt die lokale oder explizit konfigurierte LAN-API. Für die Entwicklung erwartet sie standardmäßig `http://127.0.0.1:8000`. Bei einem anderen Backend-Endpunkt wird `VITE_API_URL` vor `pnpm dev` gesetzt.

```bash
pnpm install
pnpm dev
```

Die Anwendung nutzt HTTP-only-Sitzungscookies. Ein LAN-Betrieb benötigt eine exakt konfigurierte Origin im Backend; Wildcard-CORS ist nicht erlaubt.
