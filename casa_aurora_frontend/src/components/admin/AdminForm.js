import {
  createElement,
  replaceContent
} from "../../utils/dom.js";
import { Toast } from "../Toast.js";

let activeForm = null;

export function hasUnsavedAdminChanges() {
  return Boolean(activeForm?.isDirty());
}

export function confirmDiscardActiveForm() {
  return (
    !hasUnsavedAdminChanges() ||
    window.confirm(
      "Descartar as alterações não salvas?"
    )
  );
}

export function discardActiveForm() {
  activeForm?.destroy();
}

export function AdminForm({
  title,
  fields,
  onSubmit,
  onCancel,
  submitLabel = "Salvar",
  setExternalError
}) {
  const fieldMap = new Map();

  const errorsBox = createElement("div", {
    className: "form-general-error",
    "aria-live": "polite"
  });

  const statusBox = createElement("div", {
    className: "form-status",
    "aria-live": "polite"
  });

  const submitButton = createElement(
    "button",
    {
      className: "button button-primary",
      type: "submit"
    },
    submitLabel
  );

  const cancelButton = createElement(
    "button",
    {
      className: "button button-outline",
      type: "button"
    },
    "Cancelar"
  );

  const form = createElement(
    "form",
    {
      className: "admin-form",
      novalidate: ""
    }
  );

  let dirty = false;
  let submitting = false;

  for (const field of fields) {
    const {
      name,
      label,
      type = "text",
      value = "",
      options = [],
      required = false,
      maxLength,
      hint = ""
    } = field;

    let control;

    if (type === "textarea") {
      control = createElement(
        "textarea",
        {
          id: `field-${name}`,
          name,
          rows: 4,
          maxlength: maxLength,
          required
        }
      );

      control.value = value ?? "";
    } else if (type === "select") {
      control = createElement(
        "select",
        {
          id: `field-${name}`,
          name,
          required
        },
        options.map((option) =>
          createElement(
            "option",
            {
              value: String(option.value)
            },
            option.label
          )
        )
      );

      control.value = String(value ?? "");
    } else {
      control = createElement(
        "input",
        {
          id: `field-${name}`,
          name,
          type,
          maxlength: maxLength,
          required
        }
      );

      if (type === "checkbox") {
        control.checked = Boolean(value);
      } else {
        control.value = value ?? "";
      }
    }

    const error = createElement("p", {
      id: `field-${name}-error`,
      className: "field-error",
      role: "alert"
    });

    fieldMap.set(name, {
      control,
      error
    });

    const fieldClass =
      type === "checkbox"
        ? "form-field checkbox-field"
        : "form-field";

    const labelContent =
      type === "checkbox"
        ? [
            control,
            label,
            required ? " *" : ""
          ]
        : [
            label,
            required ? " *" : ""
          ];

    form.append(
      createElement(
        "div",
        {
          className: fieldClass
        },
        createElement(
          "label",
          {
            for: `field-${name}`
          },
          ...labelContent
        ),
        type === "checkbox"
          ? null
          : control,
        hint
          ? createElement(
              "p",
              {
                className: "field-hint"
              },
              hint
            )
          : null,
        error
      )
    );

    control.addEventListener("input", () => {
      dirty = true;
      error.textContent = "";
      control.removeAttribute("aria-invalid");
      control.removeAttribute("aria-describedby");
    });

    control.addEventListener("change", () => {
      dirty = true;
      error.textContent = "";
      control.removeAttribute("aria-invalid");
      control.removeAttribute("aria-describedby");
    });
  }

  function clearFieldErrors() {
    for (const {
      control,
      error
    } of fieldMap.values()) {
      error.textContent = "";
      control.removeAttribute("aria-invalid");
      control.removeAttribute("aria-describedby");
    }
  }

  function setErrors(errors = {}) {
    replaceContent(errorsBox);
    clearFieldErrors();

    for (const [name, messages] of Object.entries(
      errors
    )) {
      const text = Array.isArray(messages)
        ? messages.map(String).join(" ")
        : String(messages);

      const target = fieldMap.get(name);

      if (target) {
        target.error.textContent = text;
        target.control.setAttribute(
          "aria-invalid",
          "true"
        );
        target.control.setAttribute(
          "aria-describedby",
          target.error.id
        );
        continue;
      }

      if (
        typeof setExternalError === "function" &&
        setExternalError(name, text)
      ) {
        continue;
      }

      errorsBox.append(
        Toast(text, "error")
      );
    }

    const firstInvalid = [
      ...fieldMap.values()
    ].find(({ error }) =>
      Boolean(error.textContent)
    );

    firstInvalid?.control.focus();
  }

  function getValues() {
    const values = {};

    for (const [
      name,
      { control }
    ] of fieldMap) {
      values[name] =
        control.type === "checkbox"
          ? control.checked
          : control.value;
    }

    return values;
  }

  function destroy() {
    if (activeForm === instance) {
      activeForm = null;
    }
  }

  const instance = {
    element: form,
    controls: fieldMap,
    setErrors,
    getValues,

    markDirty() {
      dirty = true;
    },

    isDirty() {
      return dirty;
    },

    resetDirty() {
      dirty = false;
    },

    destroy
  };

  cancelButton.addEventListener(
    "click",
    () => {
      if (
        dirty &&
        !confirmDiscardActiveForm()
      ) {
        return;
      }

      dirty = false;
      destroy();
      onCancel?.();
    }
  );

  form.addEventListener(
    "submit",
    async (event) => {
      event.preventDefault();

      if (submitting) return;

      submitting = true;
      submitButton.disabled = true;
      cancelButton.disabled = true;
      submitButton.textContent = "Salvando…";

      replaceContent(errorsBox);
      replaceContent(statusBox);
      clearFieldErrors();

      try {
        const result = await onSubmit(
          getValues(),
          {
            setErrors,

            setStatus(
              message,
              type = "success"
            ) {
              replaceContent(
                statusBox,
                Toast(message, type)
              );
            }
          }
        );

        if (result !== false) {
          dirty = false;
          destroy();
        }
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error(
            "Falha ao salvar formulário:",
            error
          );
        }

        if (
          error.details &&
          typeof error.details === "object" &&
          !Array.isArray(error.details)
        ) {
          setErrors(error.details);
        } else {
          replaceContent(
            errorsBox,
            Toast(
              error.message ||
                "Não foi possível salvar.",
              "error"
            )
          );
        }
      } finally {
        submitting = false;
        submitButton.disabled = false;
        cancelButton.disabled = false;
        submitButton.textContent = submitLabel;
      }
    }
  );

  form.prepend(
    createElement(
      "div",
      {
        className: "admin-form-heading"
      },
      createElement(
        "div",
        {},
        createElement(
          "p",
          {
            className: "admin-form-kicker"
          },
          "Edição"
        ),
        createElement(
          "h2",
          {},
          title
        )
      ),
      createElement(
        "p",
        {
          className: "admin-form-required-note"
        },
        "* Campo obrigatório"
      )
    )
  );

  form.append(
    errorsBox,
    statusBox,
    createElement(
      "div",
      {
        className: "admin-form-actions"
      },
      submitButton,
      cancelButton
    )
  );

  activeForm = instance;
  return instance;
}