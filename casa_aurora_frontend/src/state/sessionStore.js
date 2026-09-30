const state = {
  user: null,
  csrfToken: null,
  initialized: false,
  loading: false,
  error: null
};

const listeners = new Set();

function emit() {
  for (const listener of listeners) {
    listener(state);
  }
}

export function getSessionState() {
  return state;
}

export function subscribeToSession(listener) {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}

export function setSessionLoading(value) {
  state.loading = Boolean(value);
  emit();
}

export function setSessionError(error) {
  state.error = error || null;
  emit();
}

export function setCsrfToken(token) {
  state.csrfToken =
    typeof token === "string" && token.trim() ? token : null;
  emit();
}

export function setSessionUser(user) {
  state.user = user || null;
  emit();
}

export function markSessionInitialized(value = true) {
  state.initialized = Boolean(value);
  emit();
}

export function clearSessionState() {
  state.user = null;
  state.csrfToken = null;
  state.error = null;
  state.loading = false;
  state.initialized = true;
  emit();
}

export function isStaffAuthenticated() {
  return Boolean(state.user?.is_staff);
}