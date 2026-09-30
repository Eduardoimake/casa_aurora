import { authApi } from "./api/authApi.js";
import {
  clearSessionState,
  getSessionState,
  isStaffAuthenticated
} from "./state/sessionStore.js";
import { createElement, replaceContent } from "./utils/dom.js";
import { SiteHeader } from "./components/SiteHeader.js";
import { SiteFooter } from "./components/SiteFooter.js";
import { LoadingState } from "./components/LoadingState.js";
import { ErrorState } from "./components/ErrorState.js";
import { AdminSidebar } from "./components/admin/AdminSidebar.js";
import {
  confirmDiscardActiveForm,
  discardActiveForm,
  hasUnsavedAdminChanges
} from "./components/admin/AdminForm.js";
import { PublicHomePage } from "./pages/PublicHomePage.js";
import { ProductsPage } from "./pages/ProductsPage.js";
import { ProductDetailPage } from "./pages/ProductDetailPage.js";
import { AdminLoginPage } from "./pages/AdminLoginPage.js";
import { AdminDashboardPage } from "./pages/AdminDashboardPage.js";
import { AdminCategoriesPage } from "./pages/AdminCategoriesPage.js";
import { AdminProductsPage } from "./pages/AdminProductsPage.js";
import { AdminStorePage } from "./pages/AdminStorePage.js";
import { AdminPromotionsPage } from "./pages/AdminPromotionsPage.js";
import { NotFoundPage } from "./pages/NotFoundPage.js";

const HISTORY_INDEX_KEY = "casaAuroraHistoryIndex";

let activeController = null;
let currentStore = null;
let currentLocation = null;
let renderVersion = 0;
let currentHistoryIndex = 0;
let revertingPopstate = false;

function pathName() {
  return window.location.pathname.replace(/\/+$/, "") || "/";
}

function locationKey() {
  return (
    window.location.pathname +
    window.location.search +
    window.location.hash
  );
}

function historyIndex(state) {
  const value = state?.[HISTORY_INDEX_KEY];

  return Number.isSafeInteger(value) ? value : null;
}

function withHistoryIndex(index) {
  const previous =
    window.history.state &&
    typeof window.history.state === "object"
      ? window.history.state
      : {};

  return {
    ...previous,
    [HISTORY_INDEX_KEY]: index
  };
}

function replaceHistoryIndex(index) {
  window.history.replaceState(
    withHistoryIndex(index),
    "",
    locationKey()
  );

  currentHistoryIndex = index;
}

function infoPage(title, message) {
  return createElement(
    "section",
    {
      className: "container route-message",
      "aria-labelledby": "route-title"
    },
    createElement("p", { className: "eyebrow" }, "Casa Aurora"),
    createElement("h1", { id: "route-title" }, title),
    createElement("p", {}, message),
    createElement(
      "a",
      {
        className: "button button-primary",
        href: "/",
        "data-link": ""
      },
      "Voltar para a página inicial"
    )
  );
}

function createShell() {
  const shell = createElement("div", {
    className: "site-shell"
  });

  const header = SiteHeader(currentStore, {
    beforeLogout: confirmDiscardActiveForm,
    onLogout: () => navigate("/", {
      force: true,
      replace: true
    })
  });

  const main = createElement("main", {
    id: "conteudo",
    tabindex: "-1"
  });

  const footer = SiteFooter(currentStore);

  shell.append(header, main, footer);

  return { shell, main };
}

function updateShellStore(store) {
  currentStore = store;

  const brandName = document.querySelector("[data-store-name]");
  const brandSlogan = document.querySelector("[data-store-slogan]");
  const footerName = document.querySelector("[data-footer-name]");

  if (brandName) {
    brandName.textContent = store?.name || "Casa Aurora";
  }

  if (brandSlogan) {
    brandSlogan.textContent =
      store?.slogan || "Presentes e decoração";
  }

  if (footerName) {
    footerName.textContent = store?.name || "Casa Aurora";
  }
}

export function navigate(
  path,
  {
    replace = false,
    force = false
  } = {}
) {
  if (
    typeof path !== "string" ||
    !path.startsWith("/") ||
    path.startsWith("//")
  ) {
    return false;
  }

  const destination = new URL(path, window.location.origin);

  if (destination.origin !== window.location.origin) {
    return false;
  }

  const nextLocation =
    destination.pathname +
    destination.search +
    destination.hash;

  if (nextLocation === locationKey()) {
    return true;
  }

  if (!force && !confirmDiscardActiveForm()) {
    return false;
  }

  discardActiveForm();

  if (replace) {
    window.history.replaceState(
      withHistoryIndex(currentHistoryIndex),
      "",
      nextLocation
    );
  } else {
    currentHistoryIndex += 1;

    window.history.pushState(
      withHistoryIndex(currentHistoryIndex),
      "",
      nextLocation
    );
  }

  renderRoute();

  window.scrollTo({
    top: 0,
    behavior: "instant"
  });

  return true;
}

function adminPageForPath(path) {
  const pages = {
    "/painel": AdminDashboardPage,
    "/painel/categorias": AdminCategoriesPage,
    "/painel/produtos": AdminProductsPage,
    "/painel/loja": AdminStorePage,
    "/painel/promocoes": AdminPromotionsPage
  };

  return pages[path] || null;
}

async function renderAdminRoute({
  path,
  main,
  signal,
  version
}) {
  const page = adminPageForPath(path);

  if (!page) {
    main.append(
      NotFoundPage("A página administrativa não existe.")
    );

    document.title = "Página não encontrada — Casa Aurora";
    return;
  }

  replaceContent(
    main,
    LoadingState("Confirmando sessão administrativa")
  );

  try {
    if (!isStaffAuthenticated()) {
      const restored = await authApi.restoreSession({ signal });

      if (!restored) {
        if (version === renderVersion) {
          navigate("/painel/login", {
            replace: true,
            force: true
          });
        }

        return;
      }
    } else {
      await authApi.getCurrentUser({ signal });

      if (!getSessionState().csrfToken) {
        await authApi.obtainCsrf({ signal });
      }
    }

    if (signal.aborted || version !== renderVersion) {
      return;
    }

    const content = createElement("div", {
      className: "admin-main"
    });

    replaceContent(
      main,
      createElement(
        "div",
        { className: "container admin-layout" },
        AdminSidebar(path),
        content
      )
    );

    await page({
      main: content,
      signal,
      navigate,

      onUnauthorized: async () => {
        if (signal.aborted || version !== renderVersion) {
          return;
        }

        clearSessionState();

        navigate("/painel/login", {
          replace: true,
          force: true
        });
      }
    });

    if (version === renderVersion) {
      document.title = "Painel — Casa Aurora";
    }
  } catch (error) {
    if (error.name === "AbortError" || signal.aborted) {
      return;
    }

    if (version !== renderVersion) {
      return;
    }

    if (error.status === 401 || error.status === 403) {
      clearSessionState();

      navigate("/painel/login", {
        replace: true,
        force: true
      });

      return;
    }

    if (import.meta.env.DEV) {
      console.error("Falha ao abrir o painel:", error);
    }

    replaceContent(
      main,
      ErrorState(
        "Não foi possível confirmar a sessão com a API. Tente novamente.",
        () => renderRoute()
      )
    );
  }
}

async function renderRoute() {
  const version = ++renderVersion;

  activeController?.abort();
  activeController = new AbortController();

  const path = pathName();
  const nextLocation = locationKey();
  const changedLocation =
    nextLocation !== currentLocation;

  currentLocation = nextLocation;

  const { shell, main } = createShell();
  document.querySelector("#app").replaceChildren(shell);

  document.title =
    path === "/"
      ? "Casa Aurora — Presentes e Decoração"
      : "Casa Aurora";

  if (path === "/") {
    await PublicHomePage({
      main,
      signal: activeController.signal,
      onStore: (store) => {
        if (version === renderVersion) {
          updateShellStore(store);
        }
      }
    });
  } else if (path === "/catalogo") {
    await ProductsPage({
      main,
      signal: activeController.signal,
      navigate
    });
  } else if (path.startsWith("/produto/")) {
    const rawSlug = path.slice("/produto/".length);
    let slug = "";

    try {
      slug = decodeURIComponent(rawSlug);
    } catch {
      slug = "";
    }

    if (slug && !slug.includes("/")) {
      await ProductDetailPage({
        main,
        signal: activeController.signal,
        slug
      });
    } else {
      main.append(
        NotFoundPage("O endereço do produto é inválido.")
      );

      document.title = "Página não encontrada — Casa Aurora";
    }
  } else if (path === "/sobre") {
    main.append(
      infoPage(
        "Sobre e contato",
        "A apresentação da loja e as informações cadastradas aparecem na página inicial. Uma página dedicada poderá ser incorporada quando seu conteúdo estiver definido."
      )
    );
  } else if (path === "/painel/login") {
    if (isStaffAuthenticated()) {
      navigate("/painel", {
        replace: true,
        force: true
      });

      return;
    }

    try {
      await authApi.obtainCsrf({
        signal: activeController.signal
      });
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }

      if (import.meta.env.DEV) {
        console.error(error);
      }
    }

    if (version !== renderVersion) {
      return;
    }

    AdminLoginPage({
      main,
      navigate
    });

    document.title = "Login administrativo — Casa Aurora";
  } else if (path === "/painel" || path.startsWith("/painel/")) {
    await renderAdminRoute({
      path,
      main,
      signal: activeController.signal,
      version
    });
  } else {
    main.append(NotFoundPage());
    document.title = "Página não encontrada — Casa Aurora";
  }

  if (version !== renderVersion) return;

  if (changedLocation) {
    main.focus({ preventScroll: true });
  }
}

function onDocumentClick(event) {
  const link = event.target.closest("a[data-link]");

  if (
    !link ||
    event.defaultPrevented ||
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey ||
    link.target ||
    link.hasAttribute("download")
  ) {
    return;
  }

  const url = new URL(link.href, window.location.href);

  if (url.origin !== window.location.origin) {
    return;
  }

  event.preventDefault();

  navigate(
    `${url.pathname}${url.search}${url.hash}`
  );
}

function onPopstate(event) {
  const destinationIndex = historyIndex(event.state);

  if (revertingPopstate) {
    revertingPopstate = false;
    return;
  }

  if (!confirmDiscardActiveForm()) {
    if (destinationIndex !== null) {
      const delta = currentHistoryIndex - destinationIndex;

      if (delta !== 0) {
        revertingPopstate = true;
        window.history.go(delta);
      }
    } else {
      window.history.replaceState(
        withHistoryIndex(currentHistoryIndex),
        "",
        currentLocation || "/"
      );
    }

    return;
  }

  discardActiveForm();

  if (destinationIndex !== null) {
    currentHistoryIndex = destinationIndex;
  } else {
    replaceHistoryIndex(currentHistoryIndex);
  }

  renderRoute();
}

function onBeforeUnload(event) {
  if (!hasUnsavedAdminChanges()) return;

  event.preventDefault();
  event.returnValue = "";
}

export function startRouter() {
  const existingIndex = historyIndex(window.history.state);

  if (existingIndex === null) {
    replaceHistoryIndex(0);
  } else {
    currentHistoryIndex = existingIndex;
  }

  document.addEventListener("click", onDocumentClick);
  window.addEventListener("popstate", onPopstate);
  window.addEventListener("beforeunload", onBeforeUnload);

  renderRoute();
}