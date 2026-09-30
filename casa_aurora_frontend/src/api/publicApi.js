import { apiGet } from "./client.js";

const PUBLIC_BASE = "/api/v1/public";

function safeSlug(slug) {
  if (typeof slug !== "string" || !/^[a-zA-Z0-9_-]+$/.test(slug)) {
    throw new Error("Slug de produto inválido.");
  }

  return encodeURIComponent(slug);
}

export const publicApi = {
  getStore(options = {}) {
    return apiGet(`${PUBLIC_BASE}/store/`, options);
  },

  getCategories(options = {}) {
    return apiGet(`${PUBLIC_BASE}/categories/`, options);
  },

  getProducts({ params = {}, signal } = {}) {
    const allowedOrdering = new Set([
      "name",
      "-name",
      "price",
      "-price"
    ]);

    const query = {};

    if (typeof params.search === "string" && params.search.trim()) {
      query.search = params.search.trim();
    }

    if (typeof params.category === "string" && params.category.trim()) {
      query.category = params.category.trim();
    }

    if (params.featured === true || params.featured === "true") {
      query.featured = "true";
    }

    if (allowedOrdering.has(params.ordering)) {
      query.ordering = params.ordering;
    }

    if (Number.isInteger(params.page) && params.page > 0) {
      query.page = params.page;
    }

    if (
      Number.isInteger(params.page_size) &&
      params.page_size > 0 &&
      params.page_size <= 50
    ) {
      query.page_size = params.page_size;
    }

    return apiGet(`${PUBLIC_BASE}/products/`, {
      params: query,
      signal
    });
  },

  getFeaturedProducts({ signal } = {}) {
    return this.getProducts({
      params: {
        featured: true,
        page: 1,
        page_size: 4
      },
      signal
    });
  },

  getProductBySlug(slug, { signal } = {}) {
    return apiGet(
      `${PUBLIC_BASE}/products/${safeSlug(slug)}/`,
      { signal }
    );
  },

  getPromotions(options = {}) {
    return apiGet(`${PUBLIC_BASE}/promotions/`, options);
  }
};