export function detailFromApiError(error, fallback) {
  if (
    error &&
    typeof error.details === "object" &&
    error.details !== null &&
    typeof error.details.detail === "string"
  ) {
    return error.details.detail;
  }

  if (error && typeof error.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallback;
}

export function isAccessDeniedError(error) {
  return Boolean(error && [401, 403].includes(error.status));
}

export function isNotFoundError(error) {
  return Boolean(error && error.status === 404);
}