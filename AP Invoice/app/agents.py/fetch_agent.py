from fastapi import HTTPException

from app.operations.error_handler import translate_sap_error
from app.schema.response import APInvoiceActionResponse


def execute(intent, repository) -> APInvoiceActionResponse:
    if not intent.docEntry:
        raise HTTPException(status_code=400, detail="DocEntry is required to fetch AP invoice details")

    try:
        invoice = repository.fetch_ap_invoice(intent.docEntry)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=translate_sap_error(str(exc))) from exc

    return APInvoiceActionResponse(
        status="fetched",
        message="AP Invoice fetched successfully.",
        docEntry=invoice.get("DocEntry"),
        data=invoice,
    )
