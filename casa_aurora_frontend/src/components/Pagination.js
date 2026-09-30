import { createElement } from "../utils/dom.js";

function pageHref(page) {
  const url = new URL(window.location.href);
  url.searchParams.set("page", String(page));
  return `${url.pathname}${url.search}`;
}

export function Pagination({ count, page, pageSize, next, previous }) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  if (totalPages <= 1) {
    return document.createDocumentFragment();
  }

  const navigation = createElement("nav", {
    className: "pagination",
    "aria-label": "Paginação do catálogo"
  });

  if (previous) {
    navigation.append(
      createElement(
        "a",
        {
          className: "button button-outline button-small",
          href: pageHref(page - 1),
          "data-link": "",
          rel: "prev"
        },
        "Anterior"
      )
    );
  }

  navigation.append(
    createElement(
      "span",
      { className: "pagination-status", "aria-live": "polite" },
      `Página ${page} de ${totalPages}`
    )
  );

  if (next) {
    navigation.append(
      createElement(
        "a",
        {
          className: "button button-outline button-small",
          href: pageHref(page + 1),
          "data-link": "",
          rel: "next"
        },
        "Próxima"
      )
    );
  }

  return navigation;
}