from fastapi import HTTPException

from app.operations.sql_executor import execute_read_only_sql
from app.operations.text_to_sql import build_purchase_order_fetch_sql
from app.schema.response import PurchaseOrderActionResponse


def execute(intent, repository):
    del repository

    fetch_query = intent.fetchQuery or ""

    try:
        query_spec = build_purchase_order_fetch_sql(
            fetch_query=fetch_query,
            intent_card_code=intent.cardCode,
            intent_doc_entry=intent.docEntry,
        )
        rows = execute_read_only_sql(query_spec["sql"], query_spec["params"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fetch execution failed: {str(exc)}") from exc

    if not rows:
        raise HTTPException(status_code=404, detail="No purchase orders matched the fetch query")

    doc_entry = rows[0].get("doc_entry")
    count = len(rows)
    filters = query_spec["filters"]

    if count == 1:
        message = "Purchase Order fetched successfully."
    else:
        message = f"Fetched {count} purchase orders successfully."

    return PurchaseOrderActionResponse(
        status="fetched",
        message=message,
        docEntry=doc_entry,
        data={
            "filters": filters,
            "rowCount": count,
            "sql": query_spec["sql"],
            "rows": rows,
        },
    )
