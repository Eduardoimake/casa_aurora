const state = {
  store: null,
  categories: [],
  featuredProducts: [],
  promotions: [],
  loading: {
    store: false,
    categories: false,
    featuredProducts: false,
    promotions: false
  },
  errors: {
    store: null,
    categories: null,
    featuredProducts: null,
    promotions: null
  }
};

export function getAppState() {
  return state;
}

export function setAppData(section, value) {
  if (!(section in state) || section === "loading" || section === "errors") {
    throw new Error(`Seção de dados desconhecida: ${section}`);
  }

  state[section] = value;
}

export function setAppLoading(section, value) {
  state.loading[section] = Boolean(value);
}

export function setAppError(section, error) {
  state.errors[section] = error;
}