from typing import Any, Dict, Optional

from pydantic import BaseModel


class APInvoiceActionResponse(BaseModel):
    status: str
    message: str
    docEntry: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
