import {
  apiDelete,
  apiGet,
  apiPatch,
  apiPost
} from "./client.js";
import { getSessionState } from "../state/sessionStore.js";

const BASE = "/api/v1/admin";

function detailId(id) {
  const number = Number(id);

  if (!Number.isSafeInteger(number) || number <= 0) {
    throw new Error("ID administrativo inválido.");
  }

  return number;
}

function listOptions(page, signal) {
  return {
    params: {
      page: Number.isInteger(page) && page > 0 ? page : 1,
      page_size: 12
    },
    signal
  };
}

function writeOptions(signal) {
  const csrfToken = getSessionState().csrfToken;

  if (!csrfToken) {
    throw new Error(
      "Token CSRF indisponível. Reabra o painel e tente novamente."
    );
  }

  return { csrfToken, signal };
}

export const adminApi = {
  getDashboard({ signal } = {}) {
    return apiGet(`${BASE}/dashboard/`, { signal });
  },

  getCategories({ page = 1, signal } = {}) {
    return apiGet(`${BASE}/categories/`, listOptions(page, signal));
  },

  getCategory(id, { signal } = {}) {
    return apiGet(`${BASE}/categories/${detailId(id)}/`, { signal });
  },

  createCategory(data, { signal } = {}) {
    return apiPost(`${BASE}/categories/`, data, writeOptions(signal));
  },

  updateCategory(id, data, { signal } = {}) {
    return apiPatch(
      `${BASE}/categories/${detailId(id)}/`,
      data,
      writeOptions(signal)
    );
  },

  deleteCategory(id, { signal } = {}) {
    return apiDelete(
      `${BASE}/categories/${detailId(id)}/`,
      writeOptions(signal)
    );
  },

  getProducts({ page = 1, signal } = {}) {
    return apiGet(`${BASE}/products/`, listOptions(page, signal));
  },

  getProduct(id, { signal } = {}) {
    return apiGet(`${BASE}/products/${detailId(id)}/`, { signal });
  },

  createProduct(data, { signal } = {}) {
    return apiPost(`${BASE}/products/`, data, writeOptions(signal));
  },

  updateProduct(id, data, { signal } = {}) {
    return apiPatch(
      `${BASE}/products/${detailId(id)}/`,
      data,
      writeOptions(signal)
    );
  },

  deleteProduct(id, { signal } = {}) {
    return apiDelete(
      `${BASE}/products/${detailId(id)}/`,
      writeOptions(signal)
    );
  },

  getStore({ signal } = {}) {
    return apiGet(`${BASE}/store/`, { signal });
  },

  updateStore(data, { signal } = {}) {
    return apiPatch(`${BASE}/store/`, data, writeOptions(signal));
  },

  getPromotions({ page = 1, signal } = {}) {
    return apiGet(`${BASE}/promotions/`, listOptions(page, signal));
  },

  getPromotion(id, { signal } = {}) {
    return apiGet(`${BASE}/promotions/${detailId(id)}/`, { signal });
  },

  createPromotion(data, { signal } = {}) {
    return apiPost(`${BASE}/promotions/`, data, writeOptions(signal));
  },

  updatePromotion(id, data, { signal } = {}) {
    return apiPatch(
      `${BASE}/promotions/${detailId(id)}/`,
      data,
      writeOptions(signal)
    );
  },

  deletePromotion(id, { signal } = {}) {
    return apiDelete(
      `${BASE}/promotions/${detailId(id)}/`,
      writeOptions(signal)
    );
  }
};