import logging

from fastapi import FastAPI

from app.api import ap_invoices, auth


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SAP B1 AP Invoice Agent")

app.include_router(auth.router, tags=["Auth"])
app.include_router(ap_invoices.router, prefix="/ap-invoices", tags=["AP Invoices"])


@app.get("/")
def root():
    return {"message": "SAP B1 AP Invoice Agent is running"}
