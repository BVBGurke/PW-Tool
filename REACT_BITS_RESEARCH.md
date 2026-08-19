# React-Bits-Recherche für PW-Tool

Die offizielle Dokumentation beschreibt React Bits als Sammlung von React-Komponenten, die entweder manuell als Quellcode übernommen oder über unterstützte CLI-Methoden eingebunden werden. Komponenten können jeweils mit projektspezifischen Abhängigkeiten integriert und anschließend wie normale React-Komponenten verwendet werden.[1]

| Vorgesehener Baustein | Dokumentierter Zweck | Geplante, begrenzte Verwendung |
|---|---|---|
| `AnimatedContent` | Inhaltsübergänge mit Richtung, Distanz, Dauer, Schwelle und optionaler Opacity-Animation; benötigt GSAP. | Einmalige, reduzierte Bereichs- oder Zustandsübergänge in App und Website; bei `prefers-reduced-motion` deaktiviert. |
| `FadeContent` | Einfache Fade-Übergänge mit optionaler Unschärfe, Dauer und Intersection-Schwelle. | Ruhige Erscheinung von Ergebnis-, Status- oder Informationsbereichen ohne permanente Bewegung. |
| `SpotlightCard` | Interaktive Karte mit konfigurierbarer Spotlight-Farbe. | Nur für eine fokussierte Status-/Sicherheitsinformation, sofern die Mausinteraktion keinen Touch- oder Tastaturflow stört. |

Die folgenden Regeln sind verbindlich: React Bits wird nicht als rein dekoratives Alibi verwendet, sondern nur in UX-relevanten Bereichen. Semantische Passwortfelder, zugängliche Formulare, Fehleranzeigen und Tabellen bleiben eigene Komponenten, wenn React Bits keine gleichwertige fachliche Primitive liefert. Alle übernommenen Komponenten erhalten eine Abhängigkeits-, Lizenz-, Performance-, Kontrast- und Reduced-Motion-Prüfung.

## Quellen

[1] [React Bits – Installation](https://reactbits.dev/get-started/installation)

[2] [React Bits – Animated Content](https://reactbits.dev/animations/animated-content)

[3] [React Bits – Fade Content](https://reactbits.dev/animations/fade-content)

[4] [React Bits – Spotlight Card](https://reactbits.dev/animations/spotlight-card)
