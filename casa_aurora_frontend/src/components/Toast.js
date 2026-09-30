import { createElement } from "../utils/dom.js";

export function Toast(message, type = "success") {
  const safeType = type === "error" ? "error" : "success";

  return createElement(
    "div",
    {
      className: `toast toast-${safeType}`,
      role: safeType === "error" ? "alert" : "status",
      "aria-live": safeType === "error" ? "assertive" : "polite"
    },
    message
  );
}