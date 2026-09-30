import { createElement } from "../utils/dom.js";

export function SiteFooter(store) {
  return createElement(
    "footer",
    { className: "site-footer" },
    createElement(
      "div",
      { className: "container footer-grid" },
      createElement(
        "div",
        {},
        createElement(
          "p",
          {
            className: "footer-brand",
            "data-footer-name": ""
          },
          store?.name || "Casa Aurora"
        ),
        createElement(
          "p",
          { className: "footer-description" },
          "Presentes e decoração para conhecer no catálogo."
        )
      ),
      createElement(
        "nav",
        { "aria-label": "Links do rodapé" },
        createElement(
          "a",
          { href: "/", "data-link": "" },
          "Início"
        ),
        createElement(
          "a",
          { href: "/catalogo", "data-link": "" },
          "Catálogo"
        ),
        createElement(
          "a",
          { href: "/sobre", "data-link": "" },
          "Sobre"
        )
      )
    ),
    createElement(
      "div",
      { className: "container footer-bottom" },
      createElement(
        "p",
        {},
        "Projeto demonstrativo. Confirme contatos, imagens e conteúdos antes da publicação."
      )
    )
  );
}