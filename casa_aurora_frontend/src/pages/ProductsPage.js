import { ApiError } from "../api/client.js";
import { publicApi } from "../api/publicApi.js";
import {
  createElement,
  replaceContent
} from "../utils/dom.js";
import { ProductCard } from "../components/ProductCard.js";
import { Pagination } from "../components/Pagination.js";
import { LoadingState } from "../components/LoadingState.js";
import { EmptyState } from "../components/EmptyState.js";
import { ErrorState } from "../components/ErrorState.js";

const PAGE_SIZE = 12;

const ORDERING_VALUES = new Set([
  "name",
  "-name",
  "price",
  "-price"
]);

function filtersFromLocation() {
  const searchParams = new URLSearchParams(
    window.location.search
  );

  const pageRaw = searchParams.get("page");
  const pageNumber = Number(pageRaw);

  return {
    search: (searchParams.get("search") || "").trim(),
    category: (searchParams.get("category") || "").trim(),
    featured: searchParams.get("featured") === "true",
    ordering: ORDERING_VALUES.has(
      searchParams.get("ordering")
    )
      ? searchParams.get("ordering")
      : "",
    page:
      pageRaw &&
      Number.isInteger(pageNumber) &&
      pageNumber > 0
        ? pageNumber
        : 1
  };
}

function catalogUrl(filters) {
  const params = new URLSearchParams();

  if (filters.search) {
    params.set("search", filters.search);
  }

  if (filters.category) {
    params.set("category", filters.category);
  }

  if (filters.featured) {
    params.set("featured", "true");
  }

  if (filters.ordering) {
    params.set("ordering", filters.ordering);
  }

  if (filters.page > 1) {
    params.set("page", String(filters.page));
  }

  const query = params.toString();

  return query
    ? `/catalogo?${query}`
    : "/catalogo";
}

function createOption(value, label, selectedValue) {
  return createElement(
    "option",
    {
      value,
      selected: value === selectedValue
    },
    label
  );
}

function createFilters(filters) {
  const searchInput = createElement("input", {
    id: "catalog-search",
    name: "search",
    type: "search",
    value: filters.search,
    placeholder: "Nome ou descrição curta"
  });

  const categorySelect = createElement(
    "select",
    {
      id: "catalog-category",
      name: "category"
    },
    createOption(
      "",
      "Todas as categorias",
      filters.category
    )
  );

  const featuredInput = createElement("input", {
    id: "catalog-featured",
    name: "featured",
    type: "checkbox",
    value: "true"
  });

  featuredInput.checked = filters.featured;

  const orderingSelect = createElement(
    "select",
    {
      id: "catalog-ordering",
      name: "ordering"
    },
    createOption(
      "",
      "Ordem padrão",
      filters.ordering
    ),
    createOption(
      "name",
      "Nome: A a Z",
      filters.ordering
    ),
    createOption(
      "-name",
      "Nome: Z a A",
      filters.ordering
    ),
    createOption(
      "price",
      "Menor preço",
      filters.ordering
    ),
    createOption(
      "-price",
      "Maior preço",
      filters.ordering
    )
  );

  const form = createElement(
    "form",
    {
      className: "catalog-filters",
      role: "search"
    },
    createElement(
      "div",
      { className: "form-field" },
      createElement(
        "label",
        { for: "catalog-search" },
        "Buscar produtos"
      ),
      searchInput
    ),
    createElement(
      "div",
      { className: "form-field" },
      createElement(
        "label",
        { for: "catalog-category" },
        "Categoria"
      ),
      categorySelect
    ),
    createElement(
      "div",
      { className: "form-field" },
      createElement(
        "label",
        { for: "catalog-ordering" },
        "Ordenar por"
      ),
      orderingSelect
    ),
    createElement(
      "div",
      { className: "form-field checkbox-field" },
      createElement(
        "label",
        { for: "catalog-featured" },
        featuredInput,
        "Somente destaques"
      )
    ),
    createElement(
      "div",
      { className: "filter-actions" },
      createElement(
        "button",
        {
          className: "button button-primary",
          type: "submit"
        },
        "Aplicar filtros"
      ),
      createElement(
        "a",
        {
          className: "button button-outline",
          href: "/catalogo",
          "data-link": ""
        },
        "Limpar filtros"
      )
    )
  );

  return {
    form,
    categorySelect,
    getValues() {
      return {
        search: searchInput.value.trim(),
        category: categorySelect.value,
        featured: featuredInput.checked,
        ordering: orderingSelect.value,
        page: 1
      };
    }
  };
}

function isCurrent(signal, node) {
  return !signal.aborted && node.isConnected;
}

export async function ProductsPage({
  main,
  signal,
  navigate
}) {
  const filters = filtersFromLocation();
  const controls = createFilters(filters);

  const categoryMessage = createElement("div", {
    className: "filter-message",
    "aria-live": "polite"
  });

  const results = createElement("div", {
    className: "catalog-results",
    "aria-live": "polite"
  });

  const page = createElement(
    "section",
    {
      className: "container catalog-page",
      "aria-labelledby": "catalog-title"
    },
    createElement(
      "p",
      { className: "eyebrow" },
      "Explore"
    ),
    createElement(
      "h1",
      { id: "catalog-title" },
      "Catálogo"
    ),
    createElement(
      "p",
      { className: "page-introduction" },
      "Encontre produtos publicados, filtre por categoria e organize os resultados."
    ),
    controls.form,
    categoryMessage,
    results
  );

  main.append(page);

  controls.form.addEventListener("submit", (event) => {
    event.preventDefault();
    navigate(catalogUrl(controls.getValues()));
  });

  async function loadCategories() {
    replaceContent(
      categoryMessage,
      LoadingState("Carregando categorias")
    );

    try {
      const categories = await publicApi.getCategories({
        signal
      });

      if (!isCurrent(signal, categoryMessage)) {
        return;
      }

      if (!Array.isArray(categories)) {
        throw new Error(
          "Formato inválido na lista de categorias."
        );
      }

      for (const category of categories) {
        if (
          typeof category.slug === "string" &&
          category.slug
        ) {
          controls.categorySelect.append(
            createOption(
              category.slug,
              category.name || category.slug,
              filters.category
            )
          );
        }
      }

      replaceContent(categoryMessage);

      if (
        filters.category &&
        !categories.some(
          (category) =>
            category.slug === filters.category
        )
      ) {
        categoryMessage.append(
          createElement(
            "p",
            {},
            "A categoria indicada não está disponível. Você pode escolher outra."
          )
        );
      }
    } catch (error) {
      if (
        error.name === "AbortError" ||
        !isCurrent(signal, categoryMessage)
      ) {
        return;
      }

      if (import.meta.env.DEV) {
        console.error(error);
      }

      replaceContent(
        categoryMessage,
        ErrorState(
          "As categorias não puderam ser carregadas. A busca geral ainda pode ser usada.",
          loadCategories
        )
      );
    }
  }

  async function loadProducts() {
    replaceContent(
      results,
      LoadingState("Carregando produtos")
    );

    try {
      const data = await publicApi.getProducts({
        signal,
        params: {
          search: filters.search,
          category: filters.category,
          featured: filters.featured,
          ordering: filters.ordering,
          page: filters.page,
          page_size: PAGE_SIZE
        }
      });

      if (!isCurrent(signal, results)) {
        return;
      }

      if (
        !data ||
        !Array.isArray(data.results) ||
        !Number.isInteger(data.count)
      ) {
        throw new Error(
          "Formato inesperado na paginação de produtos."
        );
      }

      if (data.results.length === 0) {
        replaceContent(
          results,
          EmptyState(
            "Nenhum produto corresponde aos filtros selecionados."
          )
        );
        return;
      }

      const grid = createElement(
        "div",
        { className: "product-grid" },
        data.results.map(ProductCard)
      );

      const count = createElement(
        "p",
        { className: "results-count" },
        `${data.count} produto${
          data.count === 1 ? "" : "s"
        } encontrado${
          data.count === 1 ? "" : "s"
        }.`
      );

      replaceContent(
        results,
        createElement(
          "div",
          { className: "catalog-results-heading" },
          count
        ),
        grid,
        Pagination({
          count: data.count,
          page: filters.page,
          pageSize: PAGE_SIZE,
          next: data.next,
          previous: data.previous
        })
      );
    } catch (error) {
      if (
        error.name === "AbortError" ||
        !isCurrent(signal, results)
      ) {
        return;
      }

      if (import.meta.env.DEV) {
        console.error(error);
      }

      if (
        error instanceof ApiError &&
        error.status === 404 &&
        filters.page > 1
      ) {
        replaceContent(
          results,
          ErrorState(
            "Essa página do catálogo não existe para os filtros selecionados.",
            () =>
              navigate(
                catalogUrl({
                  ...filters,
                  page: 1
                })
              )
          )
        );
        return;
      }

      replaceContent(
        results,
        ErrorState(
          "Não foi possível carregar os produtos. Confira a conexão e tente novamente.",
          loadProducts
        )
      );
    }
  }

  await Promise.all([
    loadCategories(),
    loadProducts()
  ]);
}