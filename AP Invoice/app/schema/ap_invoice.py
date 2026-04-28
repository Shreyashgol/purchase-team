from typing import List, Optional

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str


class APInvoiceDocumentLine(BaseModel):
    ItemCode: str = Field(..., description="SAP item code")
    Quantity: int = Field(..., gt=0, description="Invoice quantity")
    TaxCode: Optional[str] = Field(None, description="Tax code")
    UnitPrice: Optional[float] = Field(None, description="Unit price")


class APInvoiceCreatePayload(BaseModel):
    CardCode: str = Field(..., description="Vendor card code")
    DocumentLines: List[APInvoiceDocumentLine] = Field(..., min_length=1, description="AP invoice line items")
