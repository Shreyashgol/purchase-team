from fastapi import HTTPException

from app.operations.error_handler import translate_sap_error
from app.schema.response import APInvoiceActionResponse


def execute(intent, repository) -> APInvoiceActionResponse:
    if not intent.cardCode:
        raise HTTPException(status_code=400, detail="Vendor code (CardCode) is required to create an AP invoice")

    if not intent.items:
        raise HTTPException(status_code=400, detail="At least one invoice line item is required")

    invoice_payload = {
        "CardCode": intent.cardCode,
        "DocDate": intent.docDate,
        "DocDueDate": intent.docDueDate,
        "TaxDate": intent.taxDate or intent.docDueDate,
        "DocumentLines": [
            {
                "ItemCode": item.itemCode,
                "Quantity": item.quantity,
                "UnitPrice": item.unitPrice,
                "TaxCode": item.taxCode,
            }
            for item in intent.items
        ],
    }

    try:
        result = repository.create_ap_invoice(invoice_payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=translate_sap_error(str(exc))) from exc

    return APInvoiceActionResponse(
        status="created",
        message="AP Invoice created successfully.",
        docEntry=result.get("DocEntry"),
        data=result,
    )
