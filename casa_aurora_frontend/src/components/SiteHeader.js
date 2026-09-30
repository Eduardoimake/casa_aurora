import { authApi } from "../api/authApi.js";
import { getSessionState } from "../state/sessionStore.js";
import { createElement } from "../utils/dom.js";

function pageAttributes(href) {
  const attributes = {
    href,
    "data-link": ""
  };

  if (window.location.pathname === href) {
    attributes["aria-current"] = "page";
  }

  return attributes;
}

function createPanelLink(user) {
  const href = user?.is_staff ? "/painel" : "/painel/login";

  return createElement(
    "a",
    pageAttributes(href),
    user?.is_staff ? "Painel" : "Área administrativa"
  );
}

function createLogoutButton({ beforeLogout, onLogout }) {
  const button = createElement(
    "button",
    {
      className: "site-nav-button",
      type: "button"
    },
    "Sair"
  );

  const feedback = createElement("span", {
    role: "alert",
    "aria-live": "assertive",
    className: "logout-feedback"
  });

  button.addEventListener("click", async () => {
    if (typeof beforeLogout === "function" && !beforeLogout()) {
      return;
    }

    button.disabled = true;
    button.textContent = "Saindo…";
    feedback.textContent = "";

    try {
      await authApi.logout();
      onLogout?.();
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error("Falha ao encerrar a sessão:", error);
      }

      feedback.textContent =
        "A saída não foi confirmada. Confira a conexão e tente novamente.";

      button.disabled = false;
      button.textContent = "Tentar sair novamente";
    }
  });

  return createElement(
    "div",
    { className: "logout-control" },
    button,
    feedback
  );
}

export function SiteHeader(
  store,
  { beforeLogout, onLogout } = {}
) {
  const session = getSessionState();
  const navigationId = "navegacao-principal";

  const menuButton = createElement(
    "button",
    {
      className: "menu-toggle",
      type: "button",
      "aria-expanded": "false",
      "aria-controls": navigationId,
      "aria-label": "Abrir menu de navegação"
    },
    "Menu"
  );

  const navigation = createElement(
    "nav",
    {
      id: navigationId,
      className: "site-nav",
      "aria-label": "Navegação principal"
    },
    createElement("a", pageAttributes("/"), "Início"),
    createElement("a", pageAttributes("/catalogo"), "Catálogo"),
    createElement("a", pageAttributes("/sobre"), "Sobre"),
    createPanelLink(session.user)
  );

  if (session.user?.is_staff) {
    navigation.append(
      createLogoutButton({ beforeLogout, onLogout })
    );
  }

  function closeMenu() {
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute(
      "aria-label",
      "Abrir menu de navegação"
    );
    navigation.classList.remove("is-open");
  }

  menuButton.addEventListener("click", () => {
    const open =
      menuButton.getAttribute("aria-expanded") === "true";

    menuButton.setAttribute(
      "aria-expanded",
      String(!open)
    );
    menuButton.setAttribute(
      "aria-label",
      open
        ? "Abrir menu de navegação"
        : "Fechar menu de navegação"
    );

    navigation.classList.toggle("is-open", !open);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      closeMenu();
    }
  });

  const brand = createElement(
    "a",
    {
      className: "site-brand",
      href: "/",
      "data-link": ""
    },
    createElement(
      "span",
      {
        className: "site-brand-symbol",
        "aria-hidden": "true"
      },
      "✦"
    ),
    createElement(
      "span",
      { className: "site-brand-copy" },
      createElement(
        "span",
        {
          className: "site-brand-name",
          "data-store-name": ""
        },
        store?.name || "Casa Aurora"
      ),
      createElement(
        "span",
        {
          className: "site-brand-slogan",
          "data-store-slogan": ""
        },
        store?.slogan || "Presentes e decoração"
      )
    )
  );

  return createElement(
    "header",
    { className: "site-header" },
    createElement(
      "div",
      { className: "container site-header-inner" },
      brand,
      menuButton,
      navigation
    )
  );
}