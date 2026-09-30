import {
  createElement,
  replaceContent
} from "../../utils/dom.js";
import {
  safeMediaUrl
} from "../../utils/media.js";
import {
  validateImageFile
} from "../../utils/validation.js";

export function ImageField({
  id,
  label,
  currentUrl = null,
  maxMegabytes = 5
}) {
  const preview = createElement("div", {
    className: "image-preview"
  });

  const input = createElement("input", {
    id,
    name: id,
    type: "file",
    accept:
      ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
  });

  const errorNode = createElement("p", {
    className: "field-error",
    id: `${id}-error`,
    role: "alert"
  });

  let objectUrl = null;

  function revokePreview() {
    if (!objectUrl) return;

    URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }

  function showError(message) {
    errorNode.textContent = message || "";

    if (message) {
      input.setAttribute(
        "aria-invalid",
        "true"
      );
      input.setAttribute(
        "aria-describedby",
        errorNode.id
      );
    } else {
      input.removeAttribute("aria-invalid");
      input.removeAttribute("aria-describedby");
    }
  }

  function renderCurrent() {
    revokePreview();

    const url = safeMediaUrl(currentUrl);

    if (!url) {
      replaceContent(
        preview,
        createElement(
          "div",
          {
            className: "image-preview-empty",
            role: "img",
            "aria-label": "Nenhuma imagem persistida"
          },
          createElement(
            "span",
            {
              "aria-hidden": "true"
            },
            "✦"
          ),
          createElement(
            "p",
            {},
            "Nenhuma imagem persistida."
          )
        )
      );
      return;
    }

    const image = createElement("img", {
      src: url,
      alt: "Imagem atualmente cadastrada"
    });

    image.addEventListener(
      "error",
      () => {
        replaceContent(
          preview,
          createElement(
            "p",
            {},
            "A imagem cadastrada não pôde ser carregada."
          )
        );
      },
      { once: true }
    );

    replaceContent(
      preview,
      image,
      createElement(
        "p",
        {},
        "Imagem atualmente cadastrada."
      )
    );
  }

  input.addEventListener("change", () => {
    revokePreview();
    showError("");

    const file = input.files?.[0] || null;
    const message = validateImageFile(
      file,
      maxMegabytes
    );

    if (message) {
      showError(message);
      renderCurrent();
      return;
    }

    if (!file) {
      renderCurrent();
      return;
    }

    objectUrl = URL.createObjectURL(file);

    replaceContent(
      preview,
      createElement("img", {
        src: objectUrl,
        alt:
          "Pré-visualização local da imagem selecionada"
      }),
      createElement(
        "p",
        {},
        "Pré-visualização local; a imagem ainda não foi enviada."
      )
    );
  });

  renderCurrent();

  return {
    element: createElement(
      "div",
      {
        className: "form-field image-field"
      },
      createElement(
        "label",
        { for: id },
        label
      ),
      input,
      createElement(
        "p",
        { className: "field-hint" },
        `JPEG, PNG ou WebP. Limite local informado: ${maxMegabytes} MB. O backend pode usar outro limite.`
      ),
      errorNode,
      preview
    ),

    setError(message) {
      showError(message);
    },

    getFile() {
      const file = input.files?.[0] || null;
      const message = validateImageFile(
        file,
        maxMegabytes
      );

      showError(message);

      return {
        file: message ? null : file,
        error: message
      };
    },

    reset(current = null) {
      currentUrl = current;
      input.value = "";
      showError("");
      renderCurrent();
    },

    destroy() {
      revokePreview();
    }
  };
}