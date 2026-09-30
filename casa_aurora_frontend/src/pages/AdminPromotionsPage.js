import { adminApi } from "../api/adminApi.js";
import { createElement, replaceContent } from "../utils/dom.js";
import {
  requiredText,
  validateNonNegativeInteger,
  validatePeriod
} from "../utils/validation.js";
import { AdminTable } from "../components/admin/AdminTable.js";
import {
  AdminForm,
  confirmDiscardActiveForm
} from "../components/admin/AdminForm.js";
import { ImageField } from "../components/admin/ImageField.js";
import { ConfirmDialog } from "../components/admin/ConfirmDialog.js";
import { LoadingState } from "../components/LoadingState.js";
import { EmptyState } from "../components/EmptyState.js";
import { ErrorState } from "../components/ErrorState.js";
import { Toast } from "../components/Toast.js";

function currentPage() {
  const raw = new URLSearchParams(window.location.search).get("page");
  const value = Number(raw);
  return raw && Number.isInteger(value) && value > 0 ? value : 1;
}

function pagePath(page) {
  return page <= 1
    ? "/painel/promocoes"
    : `/painel/promocoes?page=${page}`;
}

function pager(data, page, navigate) {
  const navigation = createElement("nav", {
    className: "pagination",
    "aria-label": "Paginação das promoções"
  });

  if (data.previous) {
    navigation.append(
      createElement(
        "button",
        {
          type: "button",
          className: "button button-outline button-small",
          onclick: () => navigate(pagePath(page - 1))
        },
        "Anterior"
      )
    );
  }

  navigation.append(
    createElement(
      "span",
      { className: "pagination-status" },
      `Página ${page} • ${data.count} promoção${data.count === 1 ? "" : "ões"}`
    )
  );

  if (data.next) {
    navigation.append(
      createElement(
        "button",
        {
          type: "button",
          className: "button button-outline button-small",
          onclick: () => navigate(pagePath(page + 1))
        },
        "Próxima"
      )
    );
  }

  return navigation;
}

function localDateTime(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const local = new Date(
    date.getTime() - date.getTimezoneOffset() * 60000
  );

  return local.toISOString().slice(0, 16);
}

function isoDateTime(value) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  return date.toISOString();
}

function fields(promotion, products) {
  return [
    {
      name: "title",
      label: "Título",
      value: promotion?.title || "",
      required: true,
      maxLength: 180
    },
    {
      name: "description",
      label: "Descrição",
      type: "textarea",
      value: promotion?.description || "",
      required: true
    },
    {
      name: "product",
      label: "Produto vinculado",
      type: "select",
      value: promotion?.product ?? "",
      options: [
        { value: "", label: "Sem produto vinculado" },
        ...products.map((product) => ({
          value: product.id,
          label: product.name
        }))
      ]
    },
    {
      name: "starts_at",
      label: "Início",
      type: "datetime-local",
      value: localDateTime(promotion?.starts_at)
    },
    {
      name: "ends_at",
      label: "Fim",
      type: "datetime-local",
      value: localDateTime(promotion?.ends_at)
    },
    {
      name: "display_order",
      label: "Ordem de exibição",
      type: "number",
      value: promotion?.display_order ?? 0
    },
    {
      name: "is_active",
      label: "Promoção ativa",
      type: "checkbox",
      value: promotion?.is_active ?? true
    }
  ];
}

function prepare(values, file, original) {
  const errors = {};

  const titleError = requiredText(values.title, "Título");
  const descriptionError = requiredText(
    values.description,
    "Descrição"
  );
  const periodError = validatePeriod(
    values.starts_at,
    values.ends_at
  );
  const orderError = validateNonNegativeInteger(
    values.display_order,
    "Ordem"
  );

  if (titleError) errors.title = titleError;
  if (descriptionError) errors.description = descriptionError;
  if (periodError) errors.ends_at = periodError;
  if (orderError) errors.display_order = orderError;

  if (
    values.product &&
    (!/^\d+$/.test(values.product) || Number(values.product) <= 0)
  ) {
    errors.product = "Selecione um produto válido.";
  }

  if (Object.keys(errors).length) {
    return { errors, payload: null, clearDates: null };
  }

  const payload = {
    title: values.title.trim(),
    description: values.description.trim(),
    product: values.product ? Number(values.product) : null,
    starts_at: isoDateTime(values.starts_at),
    ends_at: isoDateTime(values.ends_at),
    display_order: Number(values.display_order),
    is_active: values.is_active
  };

  if (!file) {
    return { errors, payload, clearDates: null };
  }

  const clearDates = {};

  for (const key of ["starts_at", "ends_at"]) {
    if (original?.[key] && payload[key] === null) {
      clearDates[key] = null;
    }
  }

  const multipart = new FormData();

  for (const [key, value] of Object.entries(payload)) {
    if (value !== null) {
      multipart.append(key, String(value));
    }
  }

  multipart.append("image", file);

  return {
    errors,
    payload: multipart,
    clearDates:
      Object.keys(clearDates).length > 0 ? clearDates : null
  };
}

async function allProducts(signal) {
  const products = [];
  let page = 1;

  while (true) {
    const data = await adminApi.getProducts({ page, signal });

    if (!data || !Array.isArray(data.results)) {
      throw new Error("Formato inesperado na lista de produtos.");
    }

    products.push(...data.results);
    if (!data.next) return products;

    page += 1;
    if (page > 1000) {
      throw new Error("A paginação de produtos excedeu o limite esperado.");
    }
  }
}

export async function AdminPromotionsPage({
  main,
  signal,
  onUnauthorized,
  navigate
}) {
  const page = currentPage();

  const notice = createElement("div", { "aria-live": "polite" });
  const formSlot = createElement("div");
  const content = createElement("div", {
    className: "admin-page-content",
    "aria-live": "polite"
  });

  main.append(
    createElement(
      "section",
      { "aria-labelledby": "admin-title" },
      createElement(
        "div",
        { className: "admin-page-heading" },
        createElement(
          "div",
          {},
          createElement("p", { className: "eyebrow" }, "Destaques"),
          createElement("h1", { id: "admin-title" }, "Promoções"),
          createElement(
            "p",
            { className: "admin-page-description" },
            "Gerencie o conteúdo promocional apresentado no catálogo."
          )
        ),
        createElement(
          "button",
          {
            type: "button",
            className: "button button-primary",
            onclick: () => openForm()
          },
          "Nova promoção"
        )
      ),
      notice,
      formSlot,
      content
    )
  );

  let currentForm = null;
  let currentImage = null;
  let requestNumber = 0;

  function showNotice(message, type = "success") {
    replaceContent(notice, Toast(message, type));
  }

  function closeForm() {
    currentForm?.destroy();
    currentImage?.destroy();
    currentForm = null;
    currentImage = null;
    replaceContent(formSlot);
  }

  async function openForm(promotion = null) {
    if (!confirmDiscardActiveForm()) return;

    closeForm();
    const requestId = ++requestNumber;

    replaceContent(
      formSlot,
      LoadingState("Carregando produtos para o formulário")
    );

    let products;

    try {
      products = await allProducts(signal);
    } catch (error) {
      if (signal.aborted || !formSlot.isConnected) return;

      if (error.status === 401 || error.status === 403) {
        await onUnauthorized();
        return;
      }

      replaceContent(
        formSlot,
        ErrorState(
          "Não foi possível carregar os produtos.",
          () => openForm(promotion)
        )
      );
      return;
    }

    if (
      signal.aborted ||
      !formSlot.isConnected ||
      requestId !== requestNumber
    ) {
      return;
    }

    const editing = Boolean(promotion);

    const image = ImageField({
      id: "image",
      label: "Imagem da promoção",
      currentUrl: promotion?.image || null
    });

    const form = AdminForm({
      title: editing
        ? `Editar promoção: ${promotion.title}`
        : "Criar promoção",
      fields: fields(promotion, products),
      submitLabel: editing
        ? "Salvar alterações"
        : "Criar promoção",
      setExternalError(name, message) {
        if (name !== "image") return false;
        image.setError(message);
        return true;
      },
      onCancel: closeForm,
      onSubmit: async (values, helpers) => {
        const selected = image.getFile();
        if (selected.error) return false;

        const prepared = prepare(
          values,
          selected.file,
          promotion
        );

        if (Object.keys(prepared.errors).length) {
          helpers.setErrors(prepared.errors);
          return false;
        }

        try {
          if (editing) {
            if (prepared.clearDates) {
              await adminApi.updatePromotion(
                promotion.id,
                prepared.clearDates
              );
            }

            await adminApi.updatePromotion(
              promotion.id,
              prepared.payload
            );
          } else {
            await adminApi.createPromotion(prepared.payload);
          }

          currentForm?.resetDirty();
          closeForm();

          showNotice(
            editing
              ? "Promoção atualizada."
              : "Promoção criada."
          );

          await load();
          return true;
        } catch (error) {
          if (error.status === 401 || error.status === 403) {
            await onUnauthorized();
            return false;
          }

          if (prepared.clearDates) {
            showNotice(
              "A atualização usou duas requisições. Confira a promoção antes de tentar novamente: a primeira alteração pode ter sido salva.",
              "error"
            );
          }

          throw error;
        }
      }
    });

    form.element
      .querySelector(".admin-form-actions")
      .before(image.element);

    image.element.addEventListener(
      "change",
      () => form.markDirty()
    );

    currentForm = form;
    currentImage = image;

    replaceContent(formSlot, form.element);
    form.element.querySelector("input")?.focus();
  }

  async function removePromotion(promotion) {
    if (!confirmDiscardActiveForm()) return;

    if (
      !ConfirmDialog(
        `Excluir a promoção "${promotion.title}"? Esta operação não pode ser desfeita.`
      )
    ) {
      return;
    }

    try {
      await adminApi.deletePromotion(promotion.id);
      closeForm();
      showNotice("Promoção excluída.");

      if (page > 1) {
        const current = await adminApi.getPromotions({
          page,
          signal
        });

        if (!current.results.length) {
          navigate(pagePath(page - 1), { replace: true });
          return;
        }
      }

      await load();
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        await onUnauthorized();
        return;
      }

      if (error.status === 404 && page > 1) {
        navigate(pagePath(page - 1), { replace: true });
        return;
      }

      showNotice(
        error.message || "Não foi possível excluir a promoção.",
        "error"
      );
    }
  }

  async function load() {
    replaceContent(content, LoadingState("Carregando promoções"));

    try {
      const data = await adminApi.getPromotions({ page, signal });

      if (signal.aborted || !content.isConnected) return;

      if (!data || !Array.isArray(data.results)) {
        throw new Error("Formato inesperado na lista de promoções.");
      }

      if (!data.results.length) {
        replaceContent(
          content,
          EmptyState("Nenhuma promoção nesta página."),
          pager(data, page, navigate)
        );
        return;
      }

      replaceContent(
        content,
        AdminTable({
          caption: "Promoções cadastradas",
          columns: [
            { label: "Título", value: (item) => item.title },
            { label: "Produto (ID)", value: (item) => item.product },
            {
              label: "Situação",
              value: (item) => item.is_active ? "Ativa" : "Inativa"
            }
          ],
          rows: data.results
        }),
        createElement(
          "div",
          { className: "admin-record-actions" },
          data.results.map((promotion) =>
            createElement(
              "div",
              { className: "admin-record-action" },
              createElement("span", {}, promotion.title),
              createElement(
                "button",
                {
                  type: "button",
                  className: "button button-outline button-small",
                  onclick: () => openForm(promotion)
                },
                "Editar"
              ),
              createElement(
                "button",
                {
                  type: "button",
                  className: "button button-outline button-small",
                  onclick: () => removePromotion(promotion)
                },
                "Excluir"
              )
            )
          )
        ),
        pager(data, page, navigate)
      );
    } catch (error) {
      if (signal.aborted || !content.isConnected) return;

      if (error.status === 401 || error.status === 403) {
        await onUnauthorized();
        return;
      }

      if (error.status === 404 && page > 1) {
        replaceContent(
          content,
          ErrorState(
            "Essa página não existe mais.",
            () => navigate(pagePath(page - 1), { replace: true })
          )
        );
        return;
      }

      if (import.meta.env.DEV) console.error(error);

      replaceContent(
        content,
        ErrorState("Não foi possível carregar as promoções.", load)
      );
    }
  }

  await load();
}