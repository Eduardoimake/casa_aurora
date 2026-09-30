export function requiredText(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    return `${label} é obrigatório.`;
  }

  return "";
}

export function validateLogin({ username, password }) {
  const errors = {};

  const usernameError = requiredText(username, "Usuário");
  const passwordError = requiredText(password, "Senha");

  if (usernameError) errors.username = usernameError;
  if (passwordError) errors.password = passwordError;

  return errors;
}

export function validateSlug(value, label = "Slug") {
  if (typeof value !== "string" || !/^[a-z0-9_-]+$/.test(value.trim())) {
    return `${label} deve conter somente letras minúsculas, números, hífen ou sublinhado.`;
  }

  return "";
}

export function validateNonNegativeInteger(value, label) {
  if (!/^\d+$/.test(String(value).trim())) {
    return `${label} deve ser um número inteiro não negativo.`;
  }

  return "";
}

export function validateDecimalPrice(value) {
  if (
    typeof value !== "string" ||
    !/^\d{1,8}(?:\.\d{1,2})?$/.test(value.trim())
  ) {
    return "Informe um preço não negativo, com ponto decimal e até duas casas, como 89.90.";
  }

  return "";
}

export function validateWhatsapp(value) {
  if (
    typeof value !== "string" ||
    !/^[1-9][0-9]{9,14}$/.test(value.trim())
  ) {
    return "Informe de 10 a 15 dígitos internacionais, sem +, espaços ou pontuação.";
  }

  return "";
}

export function validateImageFile(file, maxMegabytes = 5) {
  if (!file) return "";

  const extension = file.name.toLowerCase().split(".").pop();
  const allowedExtensions = new Set(["jpg", "jpeg", "png", "webp"]);
  const allowedTypes = new Set([
    "image/jpeg",
    "image/png",
    "image/webp"
  ]);

  if (!allowedExtensions.has(extension) || !allowedTypes.has(file.type)) {
    return "Selecione uma imagem JPEG, PNG ou WebP.";
  }

  if (file.size > maxMegabytes * 1024 * 1024) {
    return `A imagem deve ter no máximo ${maxMegabytes} MB.`;
  }

  return "";
}

export function validatePeriod(startsAt, endsAt) {
  if (!startsAt || !endsAt) return "";

  const start = Date.parse(startsAt);
  const end = Date.parse(endsAt);

  if (!Number.isFinite(start) || !Number.isFinite(end)) {
    return "Informe datas e horários válidos.";
  }

  if (start > end) {
    return "O fim não pode ser anterior ao início.";
  }

  return "";
}