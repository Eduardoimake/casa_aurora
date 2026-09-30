import { adminApi } from "../api/adminApi.js";
import {
  createElement,
  replaceContent
} from "../utils/dom.js";
import {
  requiredText,
  validateNonNegativeInteger,
  validateSlug
} from "../utils/validation.js";
import { AdminTable } from "../components/admin/AdminTable.js";
import {
  AdminForm,
  confirmDiscardActiveForm
} from "../components/admin/AdminForm.js";
import { ConfirmDialog } from "../components/admin/ConfirmDialog.js";
import { LoadingState } from "../components/LoadingState.js";
import { EmptyState } from "../components/EmptyState.js";
import { ErrorState } from "../components/ErrorState.js";
import { Toast } from "../components/Toast.js";

function currentPage() {
  const raw =
    new URLSearchParams(window.location.search)
      .get("page");

  const value = Number(raw);

  return raw &&
    Number.isInteger(value) &&
    value > 0
    ? value
    : 1;
}

function pagePath(page) {
  return page <= 1
    ? "/painel/categorias"
    : `/painel/categorias?page=${page}`;
}

function pager(data, page, navigate) {
  const navigation = createElement(
    "nav",
    {
      className: "pagination",
      "aria-label": "Paginação das categorias"
    }
  );

  if (data.previous) {
    navigation.append(
      createElement(
        "button",
        {
          type: "button",
          className:
            "button button-outline button-small",
          onclick: () =>
            navigate(pagePath(page - 1))
        },
        "Anterior"
      )
    );
  }

  navigation.append(
    createElement(
      "span",
      {
        className: "pagination-status"
      },
      `Página ${page} • ${data.count} categoria${
        data.count === 1 ? "" : "s"
      }`
    )
  );

  if (data.next) {
    navigation.append(
      createElement(
        "button",
        {
          type: "button",
          className:
            "button button-outline button-small",
          onclick: () =>
            navigate(pagePath(page + 1))
        },
        "Próxima"
      )
    );
  }

  return navigation;
}

function categoryFields(category = {}) {
  return [
    {
      name: "name",
      label: "Nome",
      value: category.name || "",
      required: true,
      maxLength: 120
    },
    {
      name: "slug",
      label: "Slug",
      value: category.slug || "",
      required: true,
      maxLength: 140,
      hint: "Use letras minúsculas, números e hífens."
    },
    {
      name: "short_description",
      label: "Descrição curta",
      value: category.short_description || "",
      maxLength: 240
    },
    {
      name: "display_order",
      label: "Ordem de exibição",
      type: "number",
      value: category.display_order ?? 0,
      hint: "Números menores aparecem primeiro."
    },
    {
      name: "is_active",
      label: "Categoria ativa",
      type: "checkbox",
      value: category.is_active ?? true
    }
  ];
}

function categoryPayload(values) {
  const errors = {};

  const nameError = requiredText(
    values.name,
    "Nome"
  );

  const slugError = validateSlug(
    values.slug
  );

  const orderError =
    validateNonNegativeInteger(
      values.display_order,
      "Ordem"
    );

  if (nameError) errors.name = nameError;
  if (slugError) errors.slug = slugError;
  if (orderError) {
    errors.display_order = orderError;
  }

  return {
    errors,
    payload: {
      name: values.name.trim(),
      slug: values.slug.trim(),
      short_description:
        values.short_description.trim(),
      display_order: Number(
        values.display_order
      ),
      is_active: values.is_active
    }
  };
}

export async function AdminCategoriesPage({
  main,
  signal,
  onUnauthorized,
  navigate
}) {
  const page = currentPage();

  const notice = createElement("div", {
    "aria-live": "polite"
  });

  const formSlot = createElement("div");
  const content = createElement("div", {
    className: "admin-page-content",
    "aria-live": "polite"
  });

  main.append(
    createElement(
      "section",
      {
        "aria-labelledby": "admin-title"
      },
      createElement(
        "div",
        {
          className: "admin-page-heading"
        },
        createElement(
          "div",
          {},
          createElement(
            "p",
            {
              className: "eyebrow"
            },
            "Organização"
          ),
          createElement(
            "h1",
            {
              id: "admin-title"
            },
            "Categorias"
          ),
          createElement(
            "p",
            {
              className: "admin-page-description"
            },
            "Organize a descoberta dos produtos publicados."
          )
        ),
        createElement(
          "button",
          {
            type: "button",
            className: "button button-primary",
            onclick: () => openForm()
          },
          "Nova categoria"
        )
      ),
      notice,
      formSlot,
      content
    )
  );

  let currentForm = null;

  function showNotice(
    message,
    type = "success"
  ) {
    replaceContent(
      notice,
      Toast(message, type)
    );
  }

  function closeForm() {
    currentForm?.destroy();
    currentForm = null;
    replaceContent(formSlot);
  }

  function openForm(category = null) {
    if (!confirmDiscardActiveForm()) {
      return;
    }

    closeForm();

    const editing = Boolean(category);

    currentForm = AdminForm({
      title: editing
        ? `Editar categoria: ${category.name}`
        : "Criar categoria",
      fields: categoryFields(category || {}),
      submitLabel: editing
        ? "Salvar alterações"
        : "Criar categoria",
      onCancel: closeForm,
      onSubmit: async (values, helpers) => {
        const {
          errors,
          payload
        } = categoryPayload(values);

        if (Object.keys(errors).length > 0) {
          helpers.setErrors(errors);
          return false;
        }

        try {
          if (editing) {
            await adminApi.updateCategory(
              category.id,
              payload
            );
          } else {
            await adminApi.createCategory(
              payload
            );
          }

          currentForm?.resetDirty();
          closeForm();

          showNotice(
            editing
              ? "Categoria atualizada."
              : "Categoria criada."
          );

          await load();
          return true;
        } catch (error) {
          if (
            error.status === 401 ||
            error.status === 403
          ) {
            await onUnauthorized();
            return false;
          }

          throw error;
        }
      }
    });

    replaceContent(
      formSlot,
      currentForm.element
    );

    currentForm.element
      .querySelector("input")
      ?.focus();
  }

  async function removeCategory(category) {
    if (!confirmDiscardActiveForm()) {
      return;
    }

    if (
      !ConfirmDialog(
        `Excluir a categoria "${category.name}"? Esta operação não pode ser desfeita.`
      )
    ) {
      return;
    }

    try {
      await adminApi.deleteCategory(
        category.id
      );

      closeForm();
      showNotice("Categoria excluída.");

      if (page > 1) {
        const current =
          await adminApi.getCategories({
            page,
            signal
          });

        if (!current.results.length) {
          navigate(
            pagePath(page - 1),
            { replace: true }
          );
          return;
        }
      }

      await load();
    } catch (error) {
      if (
        error.status === 401 ||
        error.status === 403
      ) {
        await onUnauthorized();
        return;
      }

      if (
        error.status === 404 &&
        page > 1
      ) {
        navigate(
          pagePath(page - 1),
          { replace: true }
        );
        return;
      }

      showNotice(
        error.status === 409
          ? "Esta categoria possui produtos vinculados e não pode ser excluída."
          : error.message ||
              "Não foi possível excluir a categoria.",
        "error"
      );
    }
  }

  async function load() {
    replaceContent(
      content,
      LoadingState("Carregando categorias")
    );

    try {
      const data =
        await adminApi.getCategories({
          page,
          signal
        });

      if (
        signal.aborted ||
        !content.isConnected
      ) {
        return;
      }

      if (
        !data ||
        !Array.isArray(data.results)
      ) {
        throw new Error(
          "Formato inesperado na lista de categorias."
        );
      }

      if (!data.results.length) {
        replaceContent(
          content,
          EmptyState(
            "Nenhuma categoria nesta página."
          ),
          pager(data, page, navigate)
        );
        return;
      }

      replaceContent(
        content,
        AdminTable({
          caption: "Categorias cadastradas",
          columns: [
            {
              label: "Nome",
              value: (item) => item.name
            },
            {
              label: "Slug",
              value: (item) => item.slug
            },
            {
              label: "Situação",
              value: (item) =>
                item.is_active
                  ? "Ativa"
                  : "Inativa"
            }
          ],
          rows: data.results
        }),
        createElement(
          "div",
          {
            className: "admin-record-actions"
          },
          data.results.map((category) =>
            createElement(
              "div",
              {
                className:
                  "admin-record-action"
              },
              createElement(
                "span",
                {},
                category.name
              ),
              createElement(
                "button",
                {
                  type: "button",
                  className:
                    "button button-outline button-small",
                  onclick: () =>
                    openForm(category)
                },
                "Editar"
              ),
              createElement(
                "button",
                {
                  type: "button",
                  className:
                    "button button-outline button-small",
                  onclick: () =>
                    removeCategory(category)
                },
                "Excluir"
              )
            )
          )
        ),
        pager(data, page, navigate)
      );
    } catch (error) {
      if (
        signal.aborted ||
        !content.isConnected
      ) {
        return;
      }

      if (
        error.status === 401 ||
        error.status === 403
      ) {
        await onUnauthorized();
        return;
      }

      if (
        error.status === 404 &&
        page > 1
      ) {
        replaceContent(
          content,
          ErrorState(
            "Essa página não existe mais.",
            () =>
              navigate(
                pagePath(page - 1),
                { replace: true }
              )
          )
        );
        return;
      }

      if (import.meta.env.DEV) {
        console.error(error);
      }

      replaceContent(
        content,
        ErrorState(
          "Não foi possível carregar as categorias.",
          load
        )
      );
    }
  }

  await load();
}