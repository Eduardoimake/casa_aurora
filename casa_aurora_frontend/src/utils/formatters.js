export function formatPrice(decimalString) {
  if (typeof decimalString !== "string") return "Preço indisponível";

  const normalized = decimalString.trim();

  if (!/^\d+(?:\.\d{1,2})?$/.test(normalized)) {
    return "Preço indisponível";
  }

  const [integerPart, fractionalPart = ""] = normalized.split(".");
  const groupedInteger = integerPart
    .replace(/^0+(?=\d)/, "")
    .replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  return `R$ ${groupedInteger},${fractionalPart.padEnd(2, "0")}`;
}