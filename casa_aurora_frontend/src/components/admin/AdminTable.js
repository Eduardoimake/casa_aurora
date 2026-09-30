import { createElement } from "../../utils/dom.js";

function normalizedValue(raw) {
  return raw === undefined ||
    raw === null ||
    raw === ""
    ? "—"
    : String(raw);
}

export function AdminTable({
  caption,
  columns,
  rows
}) {
  const header = createElement(
    "tr",
    {},
    columns.map((column) =>
      createElement(
        "th",
        {
          scope: "col"
        },
        column.label
      )
    )
  );

  const body = createElement("tbody");

  for (const row of rows) {
    const cells = columns.map((column) => {
      const value = normalizedValue(
        column.value(row)
      );

      return createElement(
        "td",
        {
          "data-label": column.label
        },
        value
      );
    });

    body.append(
      createElement(
        "tr",
        {},
        cells
      )
    );
  }

  return createElement(
    "div",
    {
      className: "admin-table-scroll",
      role: "region",
      tabindex: "0",
      "aria-label": caption
    },
    createElement(
      "table",
      {
        className: "admin-table"
      },
      createElement(
        "caption",
        {},
        caption
      ),
      createElement(
        "thead",
        {},
        header
      ),
      body
    )
  );
}