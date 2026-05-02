import logging

from fastapi import FastAPI

from app.api import auth, purchase_returns
from app.db.base import init_db_pool


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SAP B1 Purchase Return Agent")

app.include_router(auth.router, tags=["Auth"])
app.include_router(purchase_returns.router, prefix="/purchase-returns", tags=["Purchase Returns"])


@app.on_event("startup")
async def startup_event():
    init_db_pool()


@app.get("/")
def root():
    return {"message": "SAP B1 Purchase Return Agent is running"}
