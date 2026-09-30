import { createElement } from "../utils/dom.js";
import { formatPrice } from "../utils/formatters.js";
import { mediaOrPlaceholder } from "../utils/media.js";

export function ProductCard(product) {
  const name = product.name || "Produto";
  const href = `/produto/${encodeURIComponent(product.slug)}`;

  return createElement(
    "article",
    { className: "product-card" },
    createElement(
      "a",
      {
        className: "product-card-image",
        href,
        "data-link": "",
        "aria-label": `Ver detalhes de ${name}`
      },
      mediaOrPlaceholder(
        product.main_image,
        product.alt_text || name
      )
    ),
    createElement(
      "div",
      { className: "product-card-content" },
      product.category?.name
        ? createElement(
            "p",
            { className: "product-card-category" },
            product.category.name
          )
        : null,
      createElement("h3", {}, name),
      product.short_description
        ? createElement(
            "p",
            { className: "product-card-description" },
            product.short_description
          )
        : null,
      createElement(
        "p",
        { className: "product-card-price" },
        formatPrice(product.price)
      ),
      createElement(
        "a",
        {
          className: "text-link",
          href,
          "data-link": ""
        },
        "Ver detalhes"
      )
    )
  );
}