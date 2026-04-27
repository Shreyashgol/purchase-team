from typing import Any, Dict, Optional

from pydantic import BaseModel


class PurchaseOrderActionResponse(BaseModel):
    status: str
    message: str
    docEntry: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
