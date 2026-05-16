from typing import List, Optional

from pydantic import BaseModel, Field


class SalesDocumentLine(BaseModel):
    itemCode: str = Field(..., description="SAP item code")
    quantity: int = Field(..., gt=0)
    unitPrice: Optional[float] = None
    taxCode: Optional[str] = None


class SalesIntent(BaseModel):
    action: str = Field(..., description="create | update | cancel | close | fetch")
    documentType: str = Field(..., description="sales_order | ar_invoice | sales_return")
    cardCode: Optional[str] = None
    docEntry: Optional[int] = None
    docDate: Optional[str] = None
    docDueDate: Optional[str] = None
    comments: Optional[str] = None
    items: Optional[List[SalesDocumentLine]] = None
    fetchQuery: Optional[str] = None
