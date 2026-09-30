import { createElement } from "../../utils/dom.js";
import { getSessionState } from "../../state/sessionStore.js";

const links = [
  ["/painel", "Visão geral"],
  ["/painel/categorias", "Categorias"],
  ["/painel/produtos", "Produtos"],
  ["/painel/loja", "Loja"],
  ["/painel/promocoes", "Promoções"]
];

function linkAttributes(href, currentPath) {
  const attributes = {
    href,
    "data-link": ""
  };

  if (href === currentPath) {
    attributes["aria-current"] = "page";
  }

  return attributes;
}

export function AdminSidebar(currentPath) {
  const navigation = createElement(
    "nav",
    {
      className: "admin-navigation",
      "aria-label": "Navegação administrativa"
    },
    ...links.map(([href, label]) =>
      createElement(
        "a",
        linkAttributes(href, currentPath),
        createElement(
          "span",
          {
            className: "admin-navigation-dot",
            "aria-hidden": "true"
          },
          "•"
        ),
        createElement(
          "span",
          {},
          label
        )
      )
    )
  );

  const username =
    getSessionState().user?.username;

  return createElement(
    "aside",
    { className: "admin-sidebar" },
    createElement(
      "div",
      { className: "admin-sidebar-heading" },
      createElement(
        "p",
        { className: "eyebrow" },
        "Gestão do catálogo"
      ),
      createElement(
        "h2",
        {},
        "Painel Casa Aurora"
      ),
      username
        ? createElement(
            "p",
            { className: "admin-sidebar-account" },
            "Conta: ",
            createElement(
              "strong",
              {},
              username
            )
          )
        : null
    ),
    navigation,
    createElement(
      "div",
      { className: "admin-sidebar-note" },
      createElement(
        "span",
        {
          className: "admin-sidebar-note-mark",
          "aria-hidden": "true"
        },
        "✓"
      ),
      createElement(
        "p",
        {},
        "A API verifica as permissões de cada requisição."
      )
    )
  );
}