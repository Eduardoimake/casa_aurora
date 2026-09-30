import { authApi } from "../api/authApi.js";
import {
  createElement,
  replaceContent
} from "../utils/dom.js";
import {
  setSessionError,
  setSessionLoading
} from "../state/sessionStore.js";
import { detailFromApiError } from "../utils/errors.js";
import { validateLogin } from "../utils/validation.js";
import { ErrorState } from "../components/ErrorState.js";

function fieldError(id, message) {
  return createElement(
    "p",
    {
      id,
      className: "field-error",
      role: "alert"
    },
    message
  );
}

function createLoginForm({ onSuccess }) {
  const usernameInput = createElement("input", {
    id: "login-username",
    name: "username",
    type: "text",
    autocomplete: "username",
    required: true,
    "aria-describedby": "login-username-help"
  });

  const passwordInput = createElement("input", {
    id: "login-password",
    name: "password",
    type: "password",
    autocomplete: "current-password",
    required: true
  });

  const usernameError = createElement("div", {
    id: "login-username-error"
  });

  const passwordError = createElement("div", {
    id: "login-password-error"
  });

  const generalError = createElement("div", {
    className: "login-general-error",
    "aria-live": "polite"
  });

  const submitButton = createElement(
    "button",
    {
      className: "button button-primary login-submit",
      type: "submit"
    },
    "Entrar no painel"
  );

  const form = createElement(
    "form",
    {
      className: "login-form",
      novalidate: ""
    },
    createElement(
      "div",
      { className: "form-field" },
      createElement(
        "label",
        { for: "login-username" },
        "Usuário"
      ),
      usernameInput,
      createElement(
        "p",
        {
          id: "login-username-help",
          className: "field-hint"
        },
        "Use a conta staff criada no backend."
      ),
      usernameError
    ),
    createElement(
      "div",
      { className: "form-field" },
      createElement(
        "label",
        { for: "login-password" },
        "Senha"
      ),
      passwordInput,
      passwordError
    ),
    generalError,
    submitButton
  );

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    replaceContent(usernameError);
    replaceContent(passwordError);
    replaceContent(generalError);

    usernameInput.removeAttribute("aria-invalid");
    passwordInput.removeAttribute("aria-invalid");
    usernameInput.setAttribute(
      "aria-describedby",
      "login-username-help"
    );
    passwordInput.removeAttribute("aria-describedby");

    setSessionError(null);

    const values = {
      username: usernameInput.value,
      password: passwordInput.value
    };

    const validationErrors = validateLogin(values);

    if (validationErrors.username) {
      replaceContent(
        usernameError,
        fieldError(
          "login-username-error-message",
          validationErrors.username
        )
      );

      usernameInput.setAttribute(
        "aria-invalid",
        "true"
      );
      usernameInput.setAttribute(
        "aria-describedby",
        "login-username-error-message"
      );
    }

    if (validationErrors.password) {
      replaceContent(
        passwordError,
        fieldError(
          "login-password-error-message",
          validationErrors.password
        )
      );

      passwordInput.setAttribute(
        "aria-invalid",
        "true"
      );
      passwordInput.setAttribute(
        "aria-describedby",
        "login-password-error-message"
      );
    }

    if (Object.keys(validationErrors).length > 0) {
      const firstInvalid = validationErrors.username
        ? usernameInput
        : passwordInput;

      firstInvalid.focus();
      return;
    }

    setSessionLoading(true);
    submitButton.disabled = true;
    submitButton.textContent = "Entrando…";

    try {
      await authApi.login(
        values.username,
        values.password
      );

      usernameInput.value = "";
      passwordInput.value = "";

      onSuccess();
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error("Falha no login:", error);
      }

      const message = detailFromApiError(
        error,
        "Não foi possível iniciar a sessão. Confira os dados informados."
      );

      setSessionError(error);

      replaceContent(
        generalError,
        ErrorState(message)
      );
    } finally {
      setSessionLoading(false);
      submitButton.disabled = false;
      submitButton.textContent = "Entrar no painel";
    }
  });

  return form;
}

export function AdminLoginPage({ main, navigate }) {
  const card = createElement(
    "section",
    {
      className: "login-page container",
      "aria-labelledby": "login-title"
    },
    createElement(
      "div",
      { className: "login-card" },
      createElement(
        "div",
        { className: "login-brand-mark", "aria-hidden": "true" },
        "✦"
      ),
      createElement(
        "p",
        { className: "eyebrow" },
        "Área administrativa"
      ),
      createElement(
        "h1",
        { id: "login-title" },
        "Entrar no painel"
      ),
      createElement(
        "p",
        { className: "login-introduction" },
        "Gerencie o catálogo e a apresentação da Casa Aurora com uma conta staff criada no backend Django."
      ),
      createLoginForm({
        onSuccess: () => navigate("/painel")
      }),
      createElement(
        "p",
        { className: "login-security-note" },
        "A sessão usa cookies gerenciados pelo navegador e proteção CSRF. Nenhuma senha ou token é salvo no armazenamento do navegador."
      )
    )
  );

  main.append(card);
}