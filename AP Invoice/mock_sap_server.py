"""
Mock SAP Business One Service Layer for local AP Invoice testing.

Run:
    python mock_sap_server.py

It exposes a minimal subset of the SAP B1 endpoints used by the AP Invoice app:
    POST /b1s/v1/Login
    POST /b1s/v1/PurchaseInvoices
    GET  /b1s/v1/PurchaseInvoices({DocEntry})
    GET  /b1s/v1/BusinessPartners('{CardCode}')
    GET  /b1s/v1/Items('{ItemCode}')
"""

from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Mock SAP Service Layer - AP Invoice")

MOCK_SESSION_ID = "mock-session-12345"
purchase_invoices: Dict[int, dict] = {}

mock_vendors = {
    "V001": {
        "CardCode": "V001",
        "CardName": "Mock Vendor One",
        "CardType": "S",
    }
}

mock_items = {
    "ITEM123": {
        "ItemCode": "ITEM123",
        "ItemName": "Mock Item 123",
    },
    "ITEM456": {
        "ItemCode": "ITEM456",
        "ItemName": "Mock Item 456",
    },
}


def _next_ap_invoice_doc_entry() -> int:
    return max(purchase_invoices.keys(), default=5000) + 1


@app.post("/b1s/v1/Login")
async def login(request: Request):
    payload = await request.json()
    return {
        "SessionId": MOCK_SESSION_ID,
        "Version": "1.0",
        "CompanyDB": payload.get("CompanyDB", "MOCK_COMPANY"),
    }


@app.get("/b1s/v1/BusinessPartners('{card_code}')")
def get_vendor(card_code: str):
    vendor = mock_vendors.get(card_code)
    if not vendor:
        raise HTTPException(status_code=404, detail="Business Partner not found")
    return vendor


@app.get("/b1s/v1/Items('{item_code}')")
def get_item(item_code: str):
    item = mock_items.get(item_code)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/b1s/v1/PurchaseInvoices", status_code=201)
async def create_purchase_invoice(request: Request):
    data = await request.json()

    doc_entry = _next_ap_invoice_doc_entry()
    document_lines = data.get("DocumentLines", [])
    total = 0.0

    for line in document_lines:
        quantity = float(line.get("Quantity", 0) or 0)
        unit_price = float(line.get("UnitPrice", 0) or 0)
        total += quantity * unit_price

    created = {
        "DocEntry": doc_entry,
        "DocNum": doc_entry,
        "CardCode": data.get("CardCode", "V001"),
        "CardName": mock_vendors.get(data.get("CardCode", "V001"), {}).get("CardName", ""),
        "DocDate": data.get("DocDate"),
        "DocDueDate": data.get("DocDueDate"),
        "TaxDate": data.get("TaxDate"),
        "DocumentLines": document_lines,
        "DocStatus": "O",
        "DocTotal": total,
        "VatSum": 0,
        "DiscSum": 0,
    }
    purchase_invoices[doc_entry] = created
    return created


@app.get("/b1s/v1/PurchaseInvoices({doc_entry})")
def get_purchase_invoice(doc_entry: int):
    invoice = purchase_invoices.get(doc_entry)
    if not invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return invoice


if __name__ == "__main__":
    print("Starting Mock SAP Service Layer on http://127.0.0.1:50000")
    uvicorn.run(app, host="127.0.0.1", port=50000)
