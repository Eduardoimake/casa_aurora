import { adminApi } from "../api/adminApi.js";
import {
  createElement,
  replaceContent
} from "../utils/dom.js";
import { LoadingState } from "../components/LoadingState.js";
import { ErrorState } from "../components/ErrorState.js";

const metrics = [
  [
    "products_count",
    "Produtos cadastrados",
    "Itens disponíveis na gestão"
  ],
  [
    "categories_count",
    "Categorias cadastradas",
    "Grupos organizadores do catálogo"
  ],
  [
    "active_promotions_count",
    "Promoções marcadas ativas",
    "Registros com is_active=true"
  ]
];

function dashboardContent(data) {
  for (const [field] of metrics) {
    if (
      !Number.isInteger(data?.[field]) ||
      data[field] < 0
    ) {
      throw new Error(
        `O dashboard retornou ${field} inválido.`
      );
    }
  }

  const cards = metrics.map(
    ([field, label, description]) =>
      createElement(
        "article",
        {
          className: "admin-metric"
        },
        createElement(
          "span",
          {
            className: "admin-metric-mark",
            "aria-hidden": "true"
          },
          "✦"
        ),
        createElement(
          "p",
          {},
          label
        ),
        createElement(
          "strong",
          {},
          String(data[field])
        ),
        createElement(
          "small",
          {},
          description
        )
      )
  );

  return createElement(
    "div",
    {},
    createElement(
      "div",
      {
        className: "admin-metrics"
      },
      cards
    ),
    createElement(
      "p",
      {
        className: "admin-explanation"
      },
      "“Promoções marcadas ativas” inclui registros com is_active=true; não representa necessariamente promoções vigentes e visíveis no site."
    ),
    createElement(
      "div",
      {
        className: "admin-shortcuts"
      },
      createElement(
        "a",
        {
          className: "button button-primary",
          href: "/painel/produtos",
          "data-link": ""
        },
        "Gerenciar produtos"
      ),
      createElement(
        "a",
        {
          className: "button button-outline",
          href: "/painel/loja",
          "data-link": ""
        },
        "Editar apresentação"
      )
    )
  );
}

export async function AdminDashboardPage({
  main,
  signal,
  onUnauthorized
}) {
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
          className: "admin-page-intro"
        },
        createElement(
          "p",
          {
            className: "eyebrow"
          },
          "Visão geral"
        ),
        createElement(
          "h1",
          {
            id: "admin-title"
          },
          "O catálogo em um só lugar"
        ),
        createElement(
          "p",
          {
            className: "admin-lead"
          },
          "Contagens atuais retornadas pela API administrativa."
        )
      ),
      content
    )
  );

  async function load() {
    replaceContent(
      content,
      LoadingState("Carregando painel")
    );

    try {
      const data =
        await adminApi.getDashboard({ signal });

      if (
        signal.aborted ||
        !content.isConnected
      ) {
        return;
      }

      replaceContent(
        content,
        dashboardContent(data)
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

      if (import.meta.env.DEV) {
        console.error(error);
      }

      replaceContent(
        content,
        ErrorState(
          "Não foi possível carregar o painel.",
          load
        )
      );
    }
  }

  await load();
}