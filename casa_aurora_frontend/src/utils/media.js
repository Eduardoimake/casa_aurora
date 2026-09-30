const configuredBase = (import.meta.env.VITE_API_BASE_URL || "").trim();

function apiOrigin() {
  try {
    return new URL(
      configuredBase || window.location.origin,
      window.location.origin
    ).origin;
  } catch {
    return window.location.origin;
  }
}

export function safeMediaUrl(value) {
  if (typeof value !== "string" || value.trim() === "") return null;

  try {
    const url = new URL(value.trim(), apiOrigin());

    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return null;
    }

    const allowedOrigins = new Set([
      window.location.origin,
      apiOrigin()
    ]);

    if (!allowedOrigins.has(url.origin)) {
      return null;
    }

    return url.href;
  } catch {
    return null;
  }
}

export function mediaOrPlaceholder(value, altText = "") {
  const url = safeMediaUrl(value);
  const frame = document.createElement("div");
  frame.className = "media-frame";

  function showPlaceholder() {
    frame.replaceChildren();
    frame.classList.add("media-frame-empty");
    frame.setAttribute("role", "img");
    frame.setAttribute("aria-label", "Imagem não disponível");
    frame.textContent = "Imagem não disponível";
  }

  if (!url) {
    showPlaceholder();
    return frame;
  }

  const image = document.createElement("img");
  image.src = url;
  image.alt = altText || "Imagem do catálogo";
  image.loading = "lazy";
  image.decoding = "async";
  image.addEventListener("error", showPlaceholder, { once: true });

  frame.append(image);
  return frame;
}