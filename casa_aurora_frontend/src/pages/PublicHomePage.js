import { ApiError } from "../api/client.js";
import { publicApi } from "../api/publicApi.js";
import {
  setAppData,
  setAppError,
  setAppLoading
} from "../state/appStore.js";
import { createElement, replaceContent } from "../utils/dom.js";
import { mediaOrPlaceholder } from "../utils/media.js";
import { ProductCard } from "../components/ProductCard.js";
import { CategoryCard } from "../components/CategoryCard.js";
import { PromotionCard } from "../components/PromotionCard.js";
import { LoadingState } from "../components/LoadingState.js";
import { EmptyState } from "../components/EmptyState.js";
import { ErrorState } from "../components/ErrorState.js";

function sectionHeading(eyebrow, title, description = "") {
  return createElement(
    "div",
    { className: "section-heading" },
    createElement("p", { className: "eyebrow" }, eyebrow),
    createElement("h2", {}, title),
    description ? createElement("p", {}, description) : null
  );
}

function heroSection() {
  return createElement(
    "section",
    { className: "hero", "aria-labelledby": "home-title" },
    createElement(
      "div",
      { className: "container hero-grid" },
      createElement(
        "div",
        { className: "hero-copy" },
        createElement(
          "p",
          { className: "eyebrow" },
          "Casa Aurora · Presentes e decoração"
        ),
        createElement(
          "h1",
          {
            id: "home-title",
            "data-hero-title": ""
          },
          "Detalhes que acolhem e inspiram."
        ),
        createElement(
          "p",
          {
            className: "hero-description",
            "data-hero-description": ""
          },
          "Explore o catálogo de peças para presentear e decorar."
        ),
        createElement(
          "div",
          { className: "hero-actions" },
          createElement(
            "a",
            {
              className: "button button-primary",
              href: "/catalogo",
              "data-link": "",
              "data-hero-action": ""
            },
            "Explorar catálogo"
          ),
          createElement(
            "a",
            {
              className: "text-link",
              href: "#sobre-titulo"
            },
            "Conhecer a loja"
          )
        )
      ),
      createElement(
        "div",
        {
          className: "hero-visual",
          "data-hero-visual": ""
        },
        createElement(
          "div",
          {
            className: "hero-visual-placeholder",
            "aria-hidden": "true"
          },
          createElement("span", {}, "✦"),
          createElement("p", {}, "Um espaço para descobrir")
        )
      )
    )
  );
}

function contactSection() {
  return createElement(
    "section",
    {
      className: "section section-contact",
      "aria-labelledby": "sobre-titulo"
    },
    createElement(
      "div",
      { className: "container about-grid" },
      createElement(
        "div",
        {},
        createElement(
          "p",
          { className: "eyebrow" },
          "Sobre a loja"
        ),
        createElement(
          "h2",
          { id: "sobre-titulo" },
          "Um catálogo para descobrir."
        ),
        createElement(
          "p",
          { "data-store-description": "" },
          "Informações sobre a loja ainda não cadastradas."
        )
      ),
      createElement(
        "div",
        { className: "contact-panel" },
        createElement(
          "h3",
          {},
          "Informações da loja"
        ),
        createElement("p", {
          "data-store-address": "",
          hidden: true
        }),
        createElement("p", {
          "data-store-hours": "",
          hidden: true
        }),
        createElement(
          "p",
          { className: "contact-note" },
          "Este projeto é uma demonstração. Confirme contatos e conteúdos antes da publicação."
        )
      )
    )
  );
}

function applyStoreToPage(store, root) {
  if (!store) return;

  root.querySelector("[data-hero-title]").textContent =
    store.banner_text ||
    store.slogan ||
    store.name ||
    "Casa Aurora";

  root.querySelector("[data-hero-description]").textContent =
    store.description ||
    "Explore o catálogo de presentes e decoração.";

  root.querySelector("[data-hero-action]").textContent =
    store.primary_button_text || "Explorar catálogo";

  const visual = root.querySelector("[data-hero-visual]");

  if (store.banner_image) {
    visual.replaceChildren(
      mediaOrPlaceholder(
        store.banner_image,
        store.banner_text ||
          `Banner de ${store.name || "Casa Aurora"}`
      )
    );
  }

  root.querySelector("[data-store-description]").textContent =
    store.description ||
    "Informações sobre a loja ainda não cadastradas.";

  const address = root.querySelector("[data-store-address]");
  const hours = root.querySelector("[data-store-hours]");

  if (store.demo_address) {
    address.textContent =
      `Endereço informado: ${store.demo_address}`;
    address.hidden = false;
  }

  if (store.opening_hours) {
    hours.textContent =
      `Horário informado: ${store.opening_hours}`;
    hours.hidden = false;
  }
}

function isCurrent(signal, node) {
  return !signal.aborted && node.isConnected;
}

async function loadSection({
  key,
  signal,
  container,
  request,
  convert,
  render,
  emptyText,
  errorText,
  allowStore404 = false,
  onSuccess
}) {
  setAppLoading(key, true);
  setAppError(key, null);
  replaceContent(container, LoadingState());

  try {
    const data = convert(await request({ signal }));

    if (!isCurrent(signal, container)) return;

    setAppData(key, data);
    onSuccess?.(data);

    replaceContent(
      container,
      Array.isArray(data) && data.length === 0
        ? EmptyState(emptyText)
        : render(data)
    );
  } catch (error) {
    if (
      error.name === "AbortError" ||
      !isCurrent(signal, container)
    ) {
      return;
    }

    if (
      allowStore404 &&
      error instanceof ApiError &&
      error.status === 404
    ) {
      setAppData(key, null);
      onSuccess?.(null);
      replaceContent(
        container,
        EmptyState(
          "A loja ainda não possui informações cadastradas."
        )
      );
      return;
    }

    setAppError(key, error);

    if (import.meta.env.DEV) {
      console.error(error);
    }

    replaceContent(
      container,
      ErrorState(
        errorText,
        () =>
          loadSection({
            key,
            signal,
            container,
            request,
            convert,
            render,
            emptyText,
            errorText,
            allowStore404,
            onSuccess
          })
      )
    );
  } finally {
    if (isCurrent(signal, container)) {
      setAppLoading(key, false);
    }
  }
}

export async function PublicHomePage({
  main,
  signal,
  onStore
}) {
  const categoriesContent = createElement("div", {
    className: "section-content"
  });

  const productsContent = createElement("div", {
    className: "section-content"
  });

  const promotionsContent = createElement("div", {
    className: "section-content"
  });

  const storeFeedback = createElement("div", {
    className: "store-feedback container",
    "aria-live": "polite"
  });

  const root = createElement(
    "div",
    { className: "public-home" },
    heroSection(),
    storeFeedback,
    createElement(
      "section",
      {
        className: "section",
        "aria-label": "Categorias"
      },
      createElement(
        "div",
        { className: "container" },
        sectionHeading(
          "Explore",
          "Categorias",
          "Encontre um caminho para descobrir o catálogo."
        ),
        categoriesContent
      )
    ),
    createElement(
      "section",
      {
        className: "section section-alt",
        "aria-label": "Produtos em destaque"
      },
      createElement(
        "div",
        { className: "container" },
        sectionHeading(
          "Para conhecer",
          "Produtos em destaque",
          "Itens selecionados entre os produtos publicados."
        ),
        productsContent,
        createElement(
          "div",
          { className: "section-action" },
          createElement(
            "a",
            {
              className: "button button-outline",
              href: "/catalogo",
              "data-link": ""
            },
            "Ver catálogo completo"
          )
        )
      )
    ),
    createElement(
      "section",
      {
        className: "section",
        "aria-label": "Promoções"
      },
      createElement(
        "div",
        { className: "container" },
        sectionHeading(
          "No catálogo",
          "Promoções",
          "Conteúdo promocional disponível no momento."
        ),
        promotionsContent
      )
    ),
    contactSection()
  );

  main.append(root);

  await Promise.all([
    loadSection({
      key: "store",
      signal,
      container: storeFeedback,
      request: publicApi.getStore,
      convert: (data) => data,
      render: () => document.createDocumentFragment(),
      emptyText: "",
      errorText:
        "Não foi possível carregar as informações da loja.",
      allowStore404: true,
      onSuccess: (store) => {
        onStore(store);
        applyStoreToPage(store, root);
      }
    }),
    loadSection({
      key: "categories",
      signal,
      container: categoriesContent,
      request: publicApi.getCategories,
      convert: (data) => {
        if (!Array.isArray(data)) {
          throw new Error(
            "A API retornou categorias em formato inesperado."
          );
        }

        return data;
      },
      render: (items) =>
        createElement(
          "div",
          { className: "category-grid" },
          items.map(CategoryCard)
        ),
      emptyText:
        "Nenhuma categoria disponível no momento.",
      errorText:
        "Não foi possível carregar as categorias."
    }),
    loadSection({
      key: "featuredProducts",
      signal,
      container: productsContent,
      request: ({ signal }) => publicApi.getFeaturedProducts({ signal }),
      convert: (data) => {
        if (!data || !Array.isArray(data.results)) {
          throw new Error(
            "A API retornou produtos em formato inesperado."
          );
        }

        return data.results;
      },
      render: (items) =>
        createElement(
          "div",
          { className: "product-grid" },
          items.map(ProductCard)
        ),
      emptyText:
        "Ainda não há produtos em destaque.",
      errorText:
        "Não foi possível carregar os produtos em destaque."
    }),
    loadSection({
      key: "promotions",
      signal,
      container: promotionsContent,
      request: publicApi.getPromotions,
      convert: (data) => {
        if (!Array.isArray(data)) {
          throw new Error(
            "A API retornou promoções em formato inesperado."
          );
        }

        return data;
      },
      render: (items) =>
        createElement(
          "div",
          { className: "promotion-grid" },
          items.map(PromotionCard)
        ),
      emptyText:
        "Não há promoções disponíveis no momento.",
      errorText:
        "Não foi possível carregar as promoções."
    })
  ]);
}