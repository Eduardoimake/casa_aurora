import { createElement } from "../utils/dom.js";

export function CategoryCard(category) {
  return createElement(
    "article",
    { className: "category-card" },
    createElement(
      "span",
      {
        className: "category-mark",
        "aria-hidden": "true"
      },
      "✦"
    ),
    createElement(
      "h3",
      {},
      category.name || "Categoria"
    ),
    category.short_description
      ? createElement(
          "p",
          {},
          category.short_description
        )
      : null,
    category.slug
      ? createElement(
          "a",
          {
            className: "text-link",
            href: `/catalogo?category=${encodeURIComponent(category.slug)}`,
            "data-link": ""
          },
          "Explorar categoria"
        )
      : null
  );
}