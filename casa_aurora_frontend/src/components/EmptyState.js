import { createElement } from "../utils/dom.js";

export function EmptyState(message = "Nenhum item disponível no momento.") {
  return createElement(
    "div",
    { className: "feedback-state" },
    createElement("p", {}, message)
  );
}