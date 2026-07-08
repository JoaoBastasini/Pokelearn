(function () {
  const scriptEl = document.currentScript;
  const calcSrc =
    (scriptEl && scriptEl.dataset.calculatorSrc) || "/static/calculadora.html";

  const ICON_OPEN =
    '<svg width="30" height="30" viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="3" fill="currentColor" opacity="0.15"/><rect x="4" y="2" width="16" height="20" rx="3" stroke="currentColor" stroke-width="1.6"/><rect x="7" y="5" width="10" height="4" rx="1" fill="currentColor"/><circle cx="8" cy="13" r="1.3" fill="currentColor"/><circle cx="12" cy="13" r="1.3" fill="currentColor"/><circle cx="16" cy="13" r="1.3" fill="currentColor"/><circle cx="8" cy="17" r="1.3" fill="currentColor"/><circle cx="12" cy="17" r="1.3" fill="currentColor"/><circle cx="16" cy="17" r="1.3" fill="currentColor"/></svg>';
  const ICON_CLOSE =
    '<svg width="30" height="30" viewBox="0 0 24 24" fill="none"><path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href =
    (scriptEl && scriptEl.dataset.calculatorCss) ||
    "/static/css/calculadora_widget_style.css";
  document.head.appendChild(link);

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
