/** PW-Tool Website — Field Manual: lokale Sicherheit, nachvollziehbare Schichten, keine Marketing-Übertreibungen. */

import { SpotlightCard } from "./components/SpotlightCard";

const repository = "https://github.com/BVBGurke/PW-Tool";
function Mark() { return <span className="mark" aria-hidden="true" />; }

export default function App() {
  return <div className="manual">
    <aside className="rail"><Mark /><span>PW—SITE</span><i /><nav><a href="#policy">01</a><a href="#lan">02</a><a href="#start">03</a></nav><small>LOCAL / CONTROLLED</small></aside>
    <header><a className="brand" href="#top"><Mark />PW<span>/</span>TOOL</a><nav><a href="#policy">Architektur</a><a href="#lan">LAN</a><a href="#start">Start</a></nav><a href={repository}>Repository ↗</a></header>
    <main id="top">
      <section className="hero shell"><div><p className="index">01 / LOCAL RANDOMNESS</p><p className="eyebrow">PYTHON / FASTAPI / REACT + TYPESCRIPT</p><h1>Erzeuge lokal.<br /><em>Kontrolliere</em><br />bewusst.</h1><p className="lead">PW-Tool verbindet eine auditierbare OS-CSPRNG-Policy mit einer lokalen React-Anwendung, kontogebundenem Verlauf und klaren Betriebsgrenzen. Kein Cloudkonto, kein unsichtbarer Zufallspfad.</p><div className="actions"><a className="button" href={repository}>Zum Repository ↗</a><a className="plain" href="#start">Installation →</a></div></div><div className="diagram" aria-label="Schematische Sicherheitspolicy"><div className="diagram-grid" /><Mark /><div className="shape" /><div className="meter">DEFAULT<strong>64</strong>CHARACTER PROFILE</div></div></section>
      <section className="claims shell"><span><b>01</b> OS-CSPRNG / CPU</span><span><b>02</b> API → Service → Repository</span><span><b>03</b> React Bits + Reduced Motion</span></section>
      <section id="policy" className="policy shell"><div><p className="index">02 / CONSTRUCTION</p><p className="eyebrow">EIN NACHVOLLZIEHBARER PFAD</p><h2>Keine<br /><em>algorithmische</em><br />Lotterie.</h2></div><div className="cards"><article className="ink"><Mark /><h3>Direkte Policy</h3><p>Der Generator nutzt OS-CSPRNG, garantierte Zeichenklassen, Rejection Sampling und einen CSPRNG-Shuffle.</p></article><article><Mark /><h3>Klare Schichten</h3><p>Routen übersetzen HTTP. Services halten Fachlogik. Repositories kapseln den lokalen SQLite-Zugriff.</p></article><article className="copper"><Mark /><h3>Grenzen sichtbar</h3><p>GPU bleibt harmlose Statusmetadaten. Die scrypt-Demo ist eine Selbstprüfung, kein Crack-Tool.</p></article></div></section>
      <section id="lan" className="lan shell"><div className="lan-title"><p className="index">03 / LAN RUNTIME</p><h2>Standard: lokal.<br />LAN: TLS-bewusst.</h2></div><div className="lan-table"><div><b>127.0.0.1</b><span>Standardbindung ohne Netzfreigabe</span><em>STANDARD</em></div><SpotlightCard><b>Vertrauenswürdiges LAN</b><span>Explizite HTTPS-Origin(s), sichere Cookies, Konten und TLS-Reverse-Proxy</span><em>OPT-IN</em></SpotlightCard><div><b>Öffentliches Internet</b><span>Nicht Teil des Produkts</span><em>AUSGESCHLOSSEN</em></div></div></section>
      <section className="hash shell"><div><p className="index">04 / HASH DEMO</p><h2>Prüfen,<br /><em>nicht</em> raten.</h2><p>Die scrypt-Demo nutzt einen frischen selbst erzeugten Wert und gibt nur Metadaten zurück. Sie nimmt keine Fremdhashes, Wortlisten oder Kandidatenlisten an.</p></div><ol><li><b>1</b>Frischer lokaler Demo-Wert</li><li><b>2</b>Neuer Salt, nicht angezeigt</li><li><b>3</b>scrypt auf dem CPU-Pfad</li><li><b>4</b>Einmalige Selbstprüfung</li></ol></section>
      <section id="start" className="start shell"><div><p className="index">05 / GET STARTED</p><h2>Dein Server.<br />Deine Kontrolle.</h2></div><div className="terminal"><span>TERMINAL / SHELL</span><code><b>$</b> git clone {repository}.git && cd PW-Tool<br /><b>$</b> ./setup.sh && ./start.sh stack</code><p>Setup installiert bewusst Abhängigkeiten und erzeugt eine lokale, ignorierte Konfiguration. Starter ändern nichts und binden standardmäßig nur an localhost.</p></div></section>
    </main>
    <footer className="shell"><a className="brand" href="#top"><Mark />PW<span>/</span>TOOL</a><span>Lokale Passworterzeugung mit sichtbaren Grenzen.</span><a href={repository}>GitHub ↗</a></footer>
  </div>;
}
