(function () {
  const scriptEl = document.currentScript;
  const calcSrc =
    (scriptEl && scriptEl.dataset.calculatorSrc) || "/static/calculadora.html";

  const ICON_OPEN =
    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="3" fill="currentColor" opacity="0.15"/><rect x="4" y="2" width="16" height="20" rx="3" stroke="currentColor" stroke-width="1.6"/><rect x="7" y="5" width="10" height="4" rx="1" fill="currentColor"/><circle cx="8" cy="13" r="1.3" fill="currentColor"/><circle cx="12" cy="13" r="1.3" fill="currentColor"/><circle cx="16" cy="13" r="1.3" fill="currentColor"/><circle cx="8" cy="17" r="1.3" fill="currentColor"/><circle cx="12" cy="17" r="1.3" fill="currentColor"/><circle cx="16" cy="17" r="1.3" fill="currentColor"/></svg>';
  const ICON_CLOSE =
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';

  const style = document.createElement("style");
  style.textContent = `
    #calc-widget-btn {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: none;
      background: #36e0c2;
      color: #06231d;
      cursor: pointer;
      box-shadow: 0 10px 30px -8px rgba(0,0,0,0.45);
      z-index: 9998;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.15s ease, background 0.15s ease;
    }
    #calc-widget-btn:hover { background: #5cebcf; transform: scale(1.06); }
    #calc-widget-btn:active { transform: scale(0.94); }
    #calc-widget-btn:focus-visible { outline: 2px solid #36e0c2; outline-offset: 3px; }

    #calc-widget-panel {
      position: fixed;
      bottom: 92px;
      right: 24px;
      width: 320px;
      max-width: calc(100vw - 32px);
      border-radius: 22px;
      overflow: hidden;
      box-shadow: 0 30px 60px -20px rgba(0,0,0,0.55);
      z-index: 9999;
      opacity: 0;
      transform: translateY(12px) scale(0.96);
      pointer-events: none;
      transition: opacity 0.18s ease, transform 0.18s ease;
    }
    #calc-widget-panel.open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }
    #calc-widget-panel iframe {
      display: block;
      width: 100%;
      height: 500px;
      border: none;
    }

    @media (max-width: 420px) {
      #calc-widget-panel { right: 16px; left: 16px; width: auto; bottom: 88px; }
      #calc-widget-btn { right: 16px; bottom: 16px; }
    }
    @media (prefers-reduced-motion: reduce) {
      #calc-widget-btn, #calc-widget-panel { transition: none; }
    }
  `;
  document.head.appendChild(style);

  const btn = document.createElement("button");
  btn.id = "calc-widget-btn";
  btn.type = "button";
  btn.setAttribute("aria-label", "Abrir calculadora");
  btn.setAttribute("aria-expanded", "false");
  btn.title = "Calculadora";
  btn.innerHTML = ICON_OPEN;

  const panel = document.createElement("div");
  panel.id = "calc-widget-panel";

  const iframe = document.createElement("iframe");
  iframe.title = "Calculadora";
  panel.appendChild(iframe);

  let loaded = false;
  let isOpen = false;

  function setOpen(next) {
    isOpen = next;
    if (isOpen && !loaded) {
      iframe.src = calcSrc;
      loaded = true;
    }
    panel.classList.toggle("open", isOpen);
    btn.setAttribute("aria-expanded", String(isOpen));
    btn.setAttribute(
      "aria-label",
      isOpen ? "Fechar calculadora" : "Abrir calculadora",
    );
    btn.innerHTML = isOpen ? ICON_CLOSE : ICON_OPEN;
  }

  btn.addEventListener("click", () => setOpen(!isOpen));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isOpen) setOpen(false);
  });

  function mount() {
    document.body.appendChild(panel);
    document.body.appendChild(btn);
  }

  if (document.body) {
    mount();
  } else {
    document.addEventListener("DOMContentLoaded", mount);
  }
})();
