from fastapi import FastAPI
from app.api import auth, purchase_orders
from app.db.base import init_db_pool
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SAP B1 Purchase Order Agent")

app.include_router(auth.router, tags=["Auth"])
app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup"""
    try:
        init_db_pool()
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        raise

@app.get("/")
def root():
    return {"message": "SAP B1 Purchase Order Agent is running"}
