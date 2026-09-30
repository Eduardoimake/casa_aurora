import { createElement } from "../utils/dom.js";

export function LoadingState(message = "Carregando informações") {
  return createElement(
    "div",
    {
      className: "feedback-state feedback-loading",
      role: "status",
      "aria-live": "polite"
    },
    createElement("span", {
      className: "loading-indicator",
      "aria-hidden": "true"
    }),
    createElement("p", {}, message)
  );
}