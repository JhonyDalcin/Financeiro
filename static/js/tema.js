// Alterna entre Flatly (claro) e Darkly (escuro) e guarda a escolha no localStorage.
(function () {
  const link = document.getElementById("tema-css");
  const chave = "tema";

  function aplicar(tema) {
    link.href = tema === "escuro" ? link.dataset.escuro : link.dataset.claro;
    document.documentElement.setAttribute(
      "data-bs-theme",
      tema === "escuro" ? "dark" : "light",
    );
    localStorage.setItem(chave, tema);
  }

  const salvo = localStorage.getItem(chave);
  const preferido = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "escuro"
    : "claro";
  aplicar(salvo || preferido);

  document.addEventListener("DOMContentLoaded", function () {
    const botao = document.getElementById("alternar-tema");
    if (!botao) return;
    botao.addEventListener("click", function () {
      aplicar(localStorage.getItem(chave) === "escuro" ? "claro" : "escuro");
    });
  });
})();
