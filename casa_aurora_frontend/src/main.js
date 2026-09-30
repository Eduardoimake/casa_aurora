import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/pages.css";

import { startRouter } from "./router.js";

const app = document.querySelector("#app");

if (!app) {
  throw new Error("O elemento #app não foi encontrado.");
}

startRouter(app);