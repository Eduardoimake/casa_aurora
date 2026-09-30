import { apiGet, apiPost } from "./client.js";
import {
  clearSessionState,
  getSessionState,
  markSessionInitialized,
  setCsrfToken,
  setSessionUser
} from "../state/sessionStore.js";

const AUTH_BASE = "/api/v1/auth";

export const authApi = {
  async obtainCsrf({ signal } = {}) {
    const data = await apiGet(`${AUTH_BASE}/csrf/`, { signal });

    if (!data || typeof data.csrfToken !== "string" || !data.csrfToken) {
      throw new Error("A API não retornou um token CSRF válido.");
    }

    setCsrfToken(data.csrfToken);
    return data;
  },

  async login(username, password, { signal } = {}) {
    if (!getSessionState().csrfToken) {
      await this.obtainCsrf({ signal });
    }

    const data = await apiPost(
      `${AUTH_BASE}/login/`,
      { username, password },
      {
        signal,
        csrfToken: getSessionState().csrfToken
      }
    );

    if (
      !data ||
      !data.user ||
      data.user.is_staff !== true ||
      typeof data.csrfToken !== "string" ||
      !data.csrfToken
    ) {
      clearSessionState();
      throw new Error("A API retornou uma resposta de login inválida.");
    }

    setCsrfToken(data.csrfToken);
    setSessionUser(data.user);
    markSessionInitialized(true);

    return data;
  },

  async getCurrentUser({ signal } = {}) {
    const user = await apiGet(`${AUTH_BASE}/me/`, { signal });

    if (!user || user.is_staff !== true) {
      clearSessionState();
      throw new Error("A sessão atual não pertence a um usuário staff.");
    }

    setSessionUser(user);
    markSessionInitialized(true);
    return user;
  },

  async restoreSession({ signal } = {}) {
    if (!getSessionState().csrfToken) {
      await this.obtainCsrf({ signal });
    }

    try {
      return await this.getCurrentUser({ signal });
    } catch (error) {
      if (error.name === "AbortError") throw error;

      if (error.status === 401 || error.status === 403) {
        clearSessionState();
        return null;
      }

      throw error;
    }
  },

  async logout({ signal } = {}) {
    if (!getSessionState().csrfToken) {
      await this.obtainCsrf({ signal });
    }

    try {
      await apiPost(`${AUTH_BASE}/logout/`, null, {
        signal,
        csrfToken: getSessionState().csrfToken
      });

      clearSessionState();
      return true;
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        try {
          await this.getCurrentUser({ signal });
        } catch (sessionError) {
          if (
            sessionError.status === 401 ||
            sessionError.status === 403
          ) {
            clearSessionState();
            return true;
          }

          throw sessionError;
        }

        throw new Error(
          "A saída não foi confirmada. Sua sessão ainda está ativa; tente novamente."
        );
      }

      throw error;
    }
  }
};