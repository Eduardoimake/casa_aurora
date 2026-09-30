import { createElement } from "../utils/dom.js";

export function NotFoundPage(message = "A página solicitada não foi encontrada.") {
  return createElement(
    "section",
    { className: "container route-message", "aria-labelledby": "not-found-title" },
    createElement("p", { className: "eyebrow" }, "Casa Aurora"),
    createElement("h1", { id: "not-found-title" }, "Página não encontrada"),
    createElement("p", {}, message),
    createElement(
      "a",
      {
        className: "button button-primary",
        href: "/",
        "data-link": ""
      },
      "Voltar ao início"
    )
  );
}