export function createElement(tagName, attributes = {}, ...children) {
  const element = document.createElement(tagName);

  for (const [name, value] of Object.entries(attributes)) {
    if (value === undefined || value === null || value === false) continue;

    if (name === "className") {
      element.className = value;
    } else if (name === "textContent") {
      element.textContent = String(value);
    } else if (name.startsWith("on") && typeof value === "function") {
      element.addEventListener(name.slice(2).toLowerCase(), value);
    } else if (value === true) {
      element.setAttribute(name, "");
    } else {
      element.setAttribute(name, String(value));
    }
  }

  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;

    element.append(
      child instanceof Node
        ? child
        : document.createTextNode(String(child))
    );
  }

  return element;
}

export function replaceContent(container, ...children) {
  container.replaceChildren(
    ...children
      .flat(Infinity)
      .filter((child) => child !== null && child !== undefined)
  );
}