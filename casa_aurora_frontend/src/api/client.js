const configuredBase = (import.meta.env.VITE_API_BASE_URL || "").trim();
const baseUrl = configuredBase.replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(message, status = 0, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function buildUrl(path, params = {}) {
  if (!path.startsWith("/api/v1/")) {
    throw new Error("A chamada da API deve começar com /api/v1/.");
  }

  const url = new URL(`${baseUrl}${path}`, window.location.origin);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  return url;
}

async function parseResponse(response) {
  const contentType = response.headers.get("Content-Type") || "";

  if (response.status === 204) {
    return null;
  }

  if (!contentType.includes("application/json")) {
    const text = await response.text();

    return text
      ? { detail: text }
      : null;
  }

  try {
    return await response.json();
  } catch {
    throw new ApiError(
      "A API enviou uma resposta JSON inválida.",
      response.status
    );
  }
}

function errorMessageForStatus(status, body) {
  if (body && typeof body.detail === "string") {
    return body.detail;
  }

  if (status === 400) {
    return "Os dados enviados são inválidos.";
  }

  if (status === 403) {
    return "Acesso recusado ou sessão inválida.";
  }

  if (status === 404) {
    return "O recurso solicitado não foi encontrado.";
  }

  if (status === 409) {
    return "A operação não pode ser concluída devido a um conflito.";
  }

  if (status >= 500) {
    return "O servidor encontrou um problema. Tente novamente.";
  }

  return `A API respondeu com HTTP ${status}.`;
}

export async function apiRequest(
  path,
  {
    method = "GET",
    params = {},
    body,
    csrfToken,
    signal
  } = {}
) {
  const headers = {
    Accept: "application/json"
  };

  let requestBody = body;

  if (body instanceof FormData) {
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }
  } else if (body !== undefined && body !== null) {
    headers["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);

    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }
  } else if (csrfToken && method !== "GET" && method !== "HEAD") {
    headers["X-CSRFToken"] = csrfToken;
  }

  let response;

  try {
    response = await fetch(buildUrl(path, params), {
      method,
      credentials: "include",
      headers,
      body: requestBody,
      signal
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }

    throw new ApiError(
      "Não foi possível conectar à API. Verifique se o servidor está disponível."
    );
  }

  const parsedBody = await parseResponse(response);

  if (!response.ok) {
    throw new ApiError(
      errorMessageForStatus(response.status, parsedBody),
      response.status,
      parsedBody
    );
  }

  return parsedBody;
}

export function apiGet(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "GET"
  });
}

export function apiPost(path, body, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "POST",
    body
  });
}

export function apiPatch(path, body, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "PATCH",
    body
  });
}

export function apiDelete(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "DELETE"
  });
}