import { adminApi } from "../api/adminApi.js";
import { createElement, replaceContent } from "../utils/dom.js";
import {
  requiredText,
  validateWhatsapp
} from "../utils/validation.js";
import {
  AdminForm,
  confirmDiscardActiveForm
} from "../components/admin/AdminForm.js";
import { ImageField } from "../components/admin/ImageField.js";
import { LoadingState } from "../components/LoadingState.js";
import { ErrorState } from "../components/ErrorState.js";
import { Toast } from "../components/Toast.js";

function fields(store = {}) {
  return [
    {
      name: "name",
      label: "Nome da loja",
      value: store.name || "",
      required: true,
      maxLength: 180
    },
    {
      name: "slogan",
      label: "Slogan",
      value: store.slogan || "",
      maxLength: 240
    },
    {
      name: "description",
      label: "Apresentação",
      type: "textarea",
      value: store.description || ""
    },
    {
      name: "whatsapp_number",
      label: "WhatsApp internacional",
      value: store.whatsapp_number || "",
      required: true,
      maxLength: 15,
      hint: "Cadastrar um número não habilita um link público."
    },
    {
      name: "demo_address",
      label: "Endereço informado",
      value: store.demo_address || "",
      maxLength: 240
    },
    {
      name: "opening_hours",
      label: "Horário informado",
      value: store.opening_hours || "",
      maxLength: 240
    },
    {
      name: "banner_text",
      label: "Texto do banner",
      value: store.banner_text || "",
      maxLength: 280
    },
    {
      name: "primary_button_text",
      label: "Texto do botão principal",
      value: store.primary_button_text || "",
      maxLength: 80
    }
  ];
}

function payloadFor(values, file) {
  const errors = {};

  const nameError = requiredText(values.name, "Nome da loja");
  const whatsappError = validateWhatsapp(values.whatsapp_number);

  if (nameError) errors.name = nameError;
  if (whatsappError) errors.whatsapp_number = whatsappError;

  if (Object.keys(errors).length) {
    return { errors, payload: null };
  }

  const plain = {
    name: values.name.trim(),
    slogan: values.slogan.trim(),
    description: values.description.trim(),
    whatsapp_number: values.whatsapp_number.trim(),
    demo_address: values.demo_address.trim(),
    opening_hours: values.opening_hours.trim(),
    banner_text: values.banner_text.trim(),
    primary_button_text: values.primary_button_text.trim()
  };

  if (!file) {
    return { errors, payload: plain };
  }

  const multipart = new FormData();

  for (const [key, value] of Object.entries(plain)) {
    multipart.append(key, value);
  }

  multipart.append("banner_image", file);
  return { errors, payload: multipart };
}

export async function AdminStorePage({
  main,
  signal,
  onUnauthorized
}) {
  const notice = createElement("div", { "aria-live": "polite" });

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
        { className: "admin-page-intro" },
        createElement("p", { className: "eyebrow" }, "Identidade"),
        createElement("h1", { id: "admin-title" }, "Loja"),
        createElement(
          "p",
          { className: "admin-lead" },
          "Configure a apresentação exibida no site. Confirme a autorização de contatos e imagens antes da publicação."
        )
      ),
      notice,
      content
    )
  );

  let currentForm = null;
  let currentImage = null;

  function cleanup() {
    currentForm?.destroy();
    currentImage?.destroy();
    currentForm = null;
    currentImage = null;
  }

  async function load() {
    if (!confirmDiscardActiveForm()) return;

    cleanup();
    replaceContent(content, LoadingState("Carregando loja"));

    try {
      const store = await adminApi.getStore({ signal });

      if (signal.aborted || !content.isConnected) return;
      showForm(store);
    } catch (error) {
      if (signal.aborted || !content.isConnected) return;

      if (error.status === 401 || error.status === 403) {
        await onUnauthorized();
        return;
      }

      if (error.status === 404) {
        showForm(null);
        return;
      }

      if (import.meta.env.DEV) console.error(error);

      replaceContent(
        content,
        ErrorState(
          "Não foi possível carregar a configuração da loja.",
          load
        )
      );
    }
  }

  function showForm(store) {
    const image = ImageField({
      id: "banner_image",
      label: "Imagem do banner",
      currentUrl: store?.banner_image || null
    });

    const form = AdminForm({
      title: store ? "Editar loja" : "Criar configuração da loja",
      fields: fields(store || {}),
      submitLabel: "Salvar loja",
      setExternalError(name, message) {
        if (name !== "banner_image") return false;
        image.setError(message);
        return true;
      },
      onCancel: load,
      onSubmit: async (values, helpers) => {
        const selected = image.getFile();
        if (selected.error) return false;

        const prepared = payloadFor(values, selected.file);

        if (Object.keys(prepared.errors).length) {
          helpers.setErrors(prepared.errors);
          return false;
        }

        try {
          await adminApi.updateStore(prepared.payload);

          form.resetDirty();
          cleanup();

          replaceContent(
            notice,
            Toast(
              store ? "Loja atualizada." : "Loja configurada."
            )
          );

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

    image.element.addEventListener(
      "change",
      () => form.markDirty()
    );

    currentForm = form;
    currentImage = image;

    replaceContent(content, form.element);
  }

  await load();
}