import { adminApi } from "../api/adminApi.js";
import { createElement, replaceContent } from "../utils/dom.js";
import { formatPrice } from "../utils/formatters.js";
import {
  requiredText,
  validateDecimalPrice,
  validateNonNegativeInteger,
  validateSlug
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
    ? "/painel/produtos"
    : `/painel/produtos?page=${page}`;
}

function pager(data, page, navigate) {
  const navigation = createElement("nav", {
    className: "pagination",
    "aria-label": "Paginação dos produtos"
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
      `Página ${page} • ${data.count} produto${data.count === 1 ? "" : "s"}`
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

function fields(product, categories) {
  return [
    {
      name: "category",
      label: "Categoria",
      type: "select",
      value: product?.category ?? "",
      required: true,
      options: [
        { value: "", label: "Selecione uma categoria" },
        ...categories.map((category) => ({
          value: category.id,
          label: category.is_active
            ? category.name
            : `${category.name} (inativa)`
        }))
      ]
    },
    {
      name: "name",
      label: "Nome",
      value: product?.name || "",
      required: true,
      maxLength: 180
    },
    {
      name: "slug",
      label: "Slug",
      value: product?.slug || "",
      required: true,
      maxLength: 200
    },
    {
      name: "short_description",
      label: "Descrição curta",
      value: product?.short_description || "",
      required: true,
      maxLength: 280
    },
    {
      name: "description",
      label: "Descrição completa",
      type: "textarea",
      value: product?.description || "",
      required: true
    },
    {
      name: "price",
      label: "Preço",
      value: product?.price || "",
      required: true,
      hint: "Use ponto decimal, por exemplo 89.90."
    },
    {
      name: "status",
      label: "Situação",
      type: "select",
      value: product?.status || "hidden",
      options: [
        { value: "hidden", label: "Oculto" },
        { value: "published", label: "Publicado" }
      ]
    },
    {
      name: "display_order",
      label: "Ordem de exibição",
      type: "number",
      value: product?.display_order ?? 0
    },
    {
      name: "is_featured",
      label: "Destaque na página inicial",
      type: "checkbox",
      value: product?.is_featured ?? false
    },
    {
      name: "alt_text",
      label: "Texto alternativo da imagem",
      value: product?.alt_text || "",
      maxLength: 180
    }
  ];
}

function payloadFor(values, file) {
  const errors = {};

  if (!/^\d+$/.test(values.category) || Number(values.category) <= 0) {
    errors.category = "Selecione uma categoria.";
  }

  for (const [name, label] of [
    ["name", "Nome"],
    ["short_description", "Descrição curta"],
    ["description", "Descrição completa"]
  ]) {
    const message = requiredText(values[name], label);
    if (message) errors[name] = message;
  }

  const slugError = validateSlug(values.slug);
  const priceError = validateDecimalPrice(values.price);
  const orderError = validateNonNegativeInteger(
    values.display_order,
    "Ordem"
  );

  if (slugError) errors.slug = slugError;
  if (priceError) errors.price = priceError;
  if (orderError) errors.display_order = orderError;

  if (Object.keys(errors).length) {
    return { errors, payload: null };
  }

  const plain = {
    category: Number(values.category),
    name: values.name.trim(),
    slug: values.slug.trim(),
    short_description: values.short_description.trim(),
    description: values.description.trim(),
    price: values.price.trim(),
    status: values.status,
    display_order: Number(values.display_order),
    is_featured: values.is_featured,
    alt_text: values.alt_text.trim()
  };

  if (!file) return { errors, payload: plain };

  const multipart = new FormData();

  for (const [key, value] of Object.entries(plain)) {
    multipart.append(key, String(value));
  }

  multipart.append("main_image", file);
  return { errors, payload: multipart };
}

async function allCategories(signal) {
  const items = [];
  let page = 1;

  while (true) {
    const result = await adminApi.getCategories({ page, signal });

    if (!result || !Array.isArray(result.results)) {
      throw new Error("Formato inesperado na lista de categorias.");
    }

    items.push(...result.results);
    if (!result.next) return items;

    page += 1;
    if (page > 1000) {
      throw new Error("A paginação de categorias excedeu o limite esperado.");
    }
  }
}

export async function AdminProductsPage({
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
          createElement("p", { className: "eyebrow" }, "Catálogo"),
          createElement("h1", { id: "admin-title" }, "Produtos"),
          createElement(
            "p",
            { className: "admin-page-description" },
            "Cadastre, publique e organize os itens apresentados ao público."
          )
        ),
        createElement(
          "button",
          {
            type: "button",
            className: "button button-primary",
            onclick: () => openForm()
          },
          "Novo produto"
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

  async function openForm(product = null) {
    if (!confirmDiscardActiveForm()) return;

    closeForm();
    const requestId = ++requestNumber;
    replaceContent(
      formSlot,
      LoadingState("Carregando categorias para o formulário")
    );

    let categories;

    try {
      categories = await allCategories(signal);
    } catch (error) {
      if (signal.aborted || !formSlot.isConnected) return;

      if (error.status === 401 || error.status === 403) {
        await onUnauthorized();
        return;
      }

      replaceContent(
        formSlot,
        ErrorState(
          "Não foi possível carregar as categorias.",
          () => openForm(product)
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

    const editing = Boolean(product);
    const image = ImageField({
      id: "main_image",
      label: "Imagem principal",
      currentUrl: product?.main_image || null
    });

    const form = AdminForm({
      title: editing
        ? `Editar produto: ${product.name}`
        : "Criar produto",
      fields: fields(product, categories),
      submitLabel: editing ? "Salvar alterações" : "Criar produto",
      setExternalError(name, message) {
        if (name !== "main_image") return false;
        image.setError(message);
        return true;
      },
      onCancel: closeForm,
      onSubmit: async (values, helpers) => {
        const selected = image.getFile();
        if (selected.error) return false;

        const prepared = payloadFor(values, selected.file);

        if (Object.keys(prepared.errors).length) {
          helpers.setErrors(prepared.errors);
          return false;
        }

        try {
          if (editing) {
            await adminApi.updateProduct(product.id, prepared.payload);
          } else {
            await adminApi.createProduct(prepared.payload);
          }

          currentForm?.resetDirty();
          closeForm();
          showNotice(editing ? "Produto atualizado." : "Produto criado.");
          await load();
          return true;
        } catch (error) {
          if (error.status === 401 || error.status === 403) {
            await onUnauthorized();
            return false;
          }
          throw error;
        }
      }
    });

    form.element
      .querySelector(".admin-form-actions")
      .before(image.element);

    image.element.addEventListener("change", () => form.markDirty());

    currentForm = form;
    currentImage = image;

    replaceContent(formSlot, form.element);
    form.element.querySelector("select")?.focus();
  }

  async function removeProduct(product) {
    if (!confirmDiscardActiveForm()) return;

    if (
      !ConfirmDialog(
        `Excluir o produto "${product.name}"? Esta operação não pode ser desfeita.`
      )
    ) {
      return;
    }

    try {
      await adminApi.deleteProduct(product.id);
      closeForm();
      showNotice("Produto excluído.");

      if (page > 1) {
        const current = await adminApi.getProducts({ page, signal });

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
        error.message || "Não foi possível excluir o produto.",
        "error"
      );
    }
  }

  async function load() {
    replaceContent(content, LoadingState("Carregando produtos"));

    try {
      const data = await adminApi.getProducts({ page, signal });

      if (signal.aborted || !content.isConnected) return;

      if (!data || !Array.isArray(data.results)) {
        throw new Error("Formato inesperado na lista de produtos.");
      }

      if (!data.results.length) {
        replaceContent(
          content,
          EmptyState("Nenhum produto nesta página."),
          pager(data, page, navigate)
        );
        return;
      }

      replaceContent(
        content,
        AdminTable({
          caption: "Produtos cadastrados",
          columns: [
            { label: "Nome", value: (item) => item.name },
            { label: "Categoria (ID)", value: (item) => item.category },
            { label: "Preço", value: (item) => formatPrice(item.price) },
            {
              label: "Situação",
              value: (item) =>
                item.status === "published" ? "Publicado" : "Oculto"
            }
          ],
          rows: data.results
        }),
        createElement(
          "div",
          { className: "admin-record-actions" },
          data.results.map((product) =>
            createElement(
              "div",
              { className: "admin-record-action" },
              createElement("span", {}, product.name),
              createElement(
                "button",
                {
                  type: "button",
                  className: "button button-outline button-small",
                  onclick: () => openForm(product)
                },
                "Editar"
              ),
              createElement(
                "button",
                {
                  type: "button",
                  className: "button button-outline button-small",
                  onclick: () => removeProduct(product)
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
        ErrorState("Não foi possível carregar os produtos.", load)
      );
    }
  }

  await load();
}