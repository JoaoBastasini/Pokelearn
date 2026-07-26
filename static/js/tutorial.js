(function () {
  let images = [];
  let current = 0;

  const overlay = document.createElement("div");
  overlay.id = "tutorial-overlay";
  overlay.innerHTML = `
    <div id="tutorial-modal" role="dialog" aria-modal="true">
      <button id="tutorial-close" aria-label="Fechar tutorial">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
      </button>
      <div id="tutorial-img-wrap">
        <img id="tutorial-img" src="" alt="" />
      </div>
      <div id="tutorial-progress"></div>
      <div id="tutorial-nav">
        <button id="tutorial-prev">← Anterior</button>
        <span id="tutorial-step-label"></span>
        <button id="tutorial-next">Próximo →</button>
      </div>
    </div>
  `;

  function render() {
    overlay.querySelector("#tutorial-img").src = images[current];
    overlay.querySelector("#tutorial-img").alt = `Passo ${current + 1}`;
    overlay.querySelector("#tutorial-step-label").textContent =
      `${current + 1} / ${images.length}`;

    const progress = overlay.querySelector("#tutorial-progress");
    progress.innerHTML = images
      .map(
        (_, i) =>
          `<div class="tutorial-dot${i === current ? " active" : ""}"></div>`,
      )
      .join("");

    const prev = overlay.querySelector("#tutorial-prev");
    const next = overlay.querySelector("#tutorial-next");
    prev.disabled = current === 0;
    next.textContent =
      current === images.length - 1 ? "Concluir ✓" : "Próximo →";
  }

  function open(imgs) {
    images = imgs;
    current = 0;
    render();
    overlay.classList.add("open");
  }

  function close() {
    overlay.classList.remove("open");
  }

  overlay.querySelector("#tutorial-close").addEventListener("click", close);
  overlay.querySelector("#tutorial-prev").addEventListener("click", () => {
    if (current > 0) {
      current--;
      render();
    }
  });
  overlay.querySelector("#tutorial-next").addEventListener("click", () => {
    if (current < images.length - 1) {
      current++;
      render();
    } else close();
  });
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  document.addEventListener("keydown", (e) => {
    if (!overlay.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowRight" && current < images.length - 1) {
      current++;
      render();
    }
    if (e.key === "ArrowLeft" && current > 0) {
      current--;
      render();
    }
  });

  function mount() {
    document.body.appendChild(overlay);

    // Cada botão define suas próprias imagens via data-tutorial-images
    document.querySelectorAll("[data-tutorial-open]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const imgs = JSON.parse(btn.dataset.tutorialImages || "[]");
        if (imgs.length === 0)
          return console.warn("tutorial: nenhuma imagem definida.");
        open(imgs);
      });
    });
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
