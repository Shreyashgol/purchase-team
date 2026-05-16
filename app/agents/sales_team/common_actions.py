from fastapi import HTTPException

from app.operations.sales_rag import build_sales_rag_fetch_sql
from app.operations.sql_executor import execute_read_only_sql
from app.schema.response import SalesActionResponse


def execute_create(intent, repository) -> SalesActionResponse:
    if not intent.cardCode:
        raise HTTPException(status_code=400, detail="Customer CardCode is required for sales document creation.")
    if not intent.items:
        raise HTTPException(status_code=400, detail="At least one line item is required for sales document creation.")

    result = repository.create_document(intent)
    return SalesActionResponse(
        status="created",
        message=f"Created {intent.documentType.replace('_', ' ')} for customer {intent.cardCode}.",
        data={"postgresRecord": result, "team": "sales", "documentType": intent.documentType},
    )


def execute_update(intent, repository) -> SalesActionResponse:
    if not intent.docEntry:
        raise HTTPException(status_code=400, detail="DocEntry is required to update a sales document.")

    result = repository.update_document(intent)
    if not result:
        raise HTTPException(status_code=404, detail=f"{intent.documentType} {intent.docEntry} was not found.")

    return SalesActionResponse(
        status="updated",
        message=f"Updated {intent.documentType.replace('_', ' ')} {intent.docEntry}.",
        data={"postgresRecord": result, "team": "sales", "documentType": intent.documentType},
    )


def execute_cancel(intent, repository) -> SalesActionResponse:
    if not intent.docEntry:
        raise HTTPException(status_code=400, detail="DocEntry is required to cancel a sales document.")

    result = repository.set_status(intent.documentType, intent.docEntry, "cancelled")
    if not result:
        raise HTTPException(status_code=404, detail=f"{intent.documentType} {intent.docEntry} was not found.")

    return SalesActionResponse(
        status="cancelled",
        message=f"Cancelled {intent.documentType.replace('_', ' ')} {intent.docEntry}.",
        data={"postgresRecord": result, "team": "sales", "documentType": intent.documentType},
    )


def execute_close(intent, repository) -> SalesActionResponse:
    if not intent.docEntry:
        raise HTTPException(status_code=400, detail="DocEntry is required to close a sales document.")

    result = repository.set_status(intent.documentType, intent.docEntry, "closed")
    if not result:
        raise HTTPException(status_code=404, detail=f"{intent.documentType} {intent.docEntry} was not found.")

    return SalesActionResponse(
        status="closed",
        message=f"Closed {intent.documentType.replace('_', ' ')} {intent.docEntry}.",
        data={"postgresRecord": result, "team": "sales", "documentType": intent.documentType},
    )


def execute_fetch(intent, repository) -> SalesActionResponse:
    if intent.documentType == "sales_return":
        if intent.docEntry:
            record = repository.get_document(intent.documentType, intent.docEntry)
            results = [record] if record else []
        else:
            results = repository.list_documents(intent.documentType)
        return SalesActionResponse(
            status="success",
            message=f"Sales return fetch completed successfully. {len(results)} result(s) returned.",
            data={
                "results": results,
                "rowCount": len(results),
                "strategy": "postgres",
                "team": "sales",
                "documentType": intent.documentType,
            },
        )

    question = intent.fetchQuery or ""
    query_spec = build_sales_rag_fetch_sql(question)
    results = execute_read_only_sql(query_spec["sql"], query_spec["params"])
    return SalesActionResponse(
        status="success",
        message=f"Sales fetch completed successfully. {len(results)} result(s) returned.",
        data={
            "sql": query_spec["sql"],
            "filters": query_spec["filters"],
            "results": results,
            "rowCount": len(results),
            "strategy": "rag",
            "team": "sales",
            "documentType": intent.documentType,
        },
    )
