import { createElement } from "../utils/dom.js";

export function ErrorState(
  message = "Não foi possível carregar esta seção.",
  onRetry
) {
  const state = createElement(
    "div",
    { className: "feedback-state feedback-error", role: "alert" },
    createElement("p", {}, message)
  );

  if (typeof onRetry === "function") {
    state.append(
      createElement(
        "button",
        {
          className: "button button-outline button-small",
          type: "button",
          onclick: onRetry
        },
        "Tentar novamente"
      )
    );
  }

  return state;
}