import { ApiError } from "../api/client.js";
import { publicApi } from "../api/publicApi.js";
import {
  createElement,
  replaceContent
} from "../utils/dom.js";
import { mediaOrPlaceholder } from "../utils/media.js";
import { formatPrice } from "../utils/formatters.js";
import { LoadingState } from "../components/LoadingState.js";
import { ErrorState } from "../components/ErrorState.js";

function detailContent(product) {
  const information = createElement(
    "div",
    { className: "product-detail-info" },
    createElement(
      "p",
      { className: "eyebrow" },
      product.category?.name || "Produto"
    ),
    createElement(
      "h1",
      {},
      product.name || "Produto"
    ),
    createElement(
      "p",
      { className: "product-detail-price" },
      formatPrice(product.price)
    )
  );

  if (product.short_description) {
    information.append(
      createElement(
        "p",
        { className: "product-detail-intro" },
        product.short_description
      )
    );
  }

  if (product.description) {
    information.append(
      createElement(
        "div",
        {
          className: "product-detail-description"
        },
        createElement(
          "h2",
          {},
          "Sobre este produto"
        ),
        createElement(
          "p",
          {},
          product.description
        )
      )
    );
  }

  information.append(
    createElement(
      "div",
      { className: "product-detail-actions" },
      createElement(
        "a",
        {
          className: "button button-primary",
          href: "/catalogo",
          "data-link": ""
        },
        "Explorar catálogo"
      )
    ),
    createElement(
      "p",
      { className: "product-detail-note" },
      "Catálogo demonstrativo: esta página apresenta o produto e não conclui uma compra."
    )
  );

  return createElement(
    "div",
    { className: "product-detail-grid" },
    mediaOrPlaceholder(
      product.main_image,
      product.alt_text ||
        product.name ||
        ""
    ),
    information
  );
}

export async function ProductDetailPage({
  main,
  signal,
  slug
}) {
  const section = createElement(
    "section",
    {
      className:
        "container product-detail-page",
      "aria-label": "Detalhes do produto"
    }
  );

  main.append(section);

  async function loadProduct() {
    replaceContent(
      section,
      LoadingState("Carregando produto")
    );

    try {
      const product =
        await publicApi.getProductBySlug(slug, {
          signal
        });

      if (
        signal.aborted ||
        !section.isConnected
      ) {
        return;
      }

      if (
        !product ||
        typeof product.name !== "string" ||
        typeof product.slug !== "string"
      ) {
        throw new Error(
          "A API retornou um produto em formato inesperado."
        );
      }

      replaceContent(
        section,
        detailContent(product)
      );

      document.title =
        `${product.name} — Casa Aurora`;
    } catch (error) {
      if (
        error.name === "AbortError" ||
        signal.aborted ||
        !section.isConnected
      ) {
        return;
      }

      if (
        error instanceof ApiError &&
        error.status === 404
      ) {
        replaceContent(
          section,
          createElement(
            "div",
            {
              className: "detail-not-found"
            },
            createElement(
              "p",
              { className: "eyebrow" },
              "Catálogo"
            ),
            createElement(
              "h1",
              {},
              "Produto não encontrado"
            ),
            createElement(
              "p",
              {},
              "Este produto não está disponível no catálogo público."
            ),
            createElement(
              "a",
              {
                className:
                  "button button-primary",
                href: "/catalogo",
                "data-link": ""
              },
              "Ver catálogo"
            )
          )
        );

        document.title =
          "Produto não encontrado — Casa Aurora";
        return;
      }

      if (import.meta.env.DEV) {
        console.error(error);
      }

      replaceContent(
        section,
        ErrorState(
          "Não foi possível carregar o produto.",
          loadProduct
        )
      );
    }
  }

  await loadProduct();
}