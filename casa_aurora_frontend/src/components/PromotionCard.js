import { createElement } from "../utils/dom.js";
import { mediaOrPlaceholder } from "../utils/media.js";

export function PromotionCard(promotion) {
  const content = createElement(
    "div",
    { className: "promotion-content" },
    createElement(
      "h3",
      {},
      promotion.title || "Promoção"
    ),
    promotion.description
      ? createElement(
          "p",
          {},
          promotion.description
        )
      : null
  );

  if (promotion.product?.slug) {
    content.append(
      createElement(
        "a",
        {
          className: "text-link",
          href: `/produto/${encodeURIComponent(promotion.product.slug)}`,
          "data-link": ""
        },
        "Conhecer produto"
      )
    );
  }

  return createElement(
    "article",
    { className: "promotion-card" },
    mediaOrPlaceholder(
      promotion.image,
      promotion.title || ""
    ),
    content
  );
}