(function () {
  const overlay = document.createElement("div");
  overlay.id = "lightbox-overlay";
  overlay.innerHTML = `
    <div id="lightbox-modal">
      <button id="lightbox-close" aria-label="Fechar">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
      </button>
      <img id="lightbox-img" src="" alt="" />
    </div>
  `;

  function open(src, alt) {
    overlay.querySelector("#lightbox-img").src = src;
    overlay.querySelector("#lightbox-img").alt = alt || "";
    overlay.classList.add("open");
  }

  function close() {
    overlay.classList.remove("open");
  }

  overlay.querySelector("#lightbox-close").addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("open")) close();
  });

  function mount() {
    document.body.appendChild(overlay);

    // Ativa qualquer botão com data-lightbox-src na página
    // Exemplo: <button data-lightbox-src="/static/img/tabela.png" data-lightbox-alt="Tabela de tipos">
    document.querySelectorAll("[data-lightbox-src]").forEach((btn) => {
      btn.addEventListener("click", () => {
        open(btn.dataset.lightboxSrc, btn.dataset.lightboxAlt || "");
      });
    });
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
