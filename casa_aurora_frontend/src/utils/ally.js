export function runAccessibilityAudit(root = document) {
  const issues = [];

  for (const image of root.querySelectorAll("img")) {
    if (!image.hasAttribute("alt")) {
      issues.push("Imagem sem atributo alt.");
    }
  }

  for (const control of root.querySelectorAll(
    "button, input, select, textarea"
  )) {
    const hasAccessibleName =
      control.getAttribute("aria-label") ||
      control.getAttribute("aria-labelledby") ||
      control.id &&
        root.querySelector(`label[for="${CSS.escape(control.id)}"]`)?.textContent?.trim() ||
      control.closest("label")?.textContent?.trim();

    if (!hasAccessibleName) {
      issues.push(
        `Controle sem nome acessível: ${control.outerHTML.slice(0, 120)}`
      );
    }
  }

  for (const label of root.querySelectorAll("label")) {
    const targetId = label.getAttribute("for");

    if (targetId && !root.querySelector(`#${CSS.escape(targetId)}`)) {
      issues.push(`Label aponta para controle inexistente: ${targetId}`);
    }
  }

  return {
    passed: issues.length === 0,
    issues
  };
}