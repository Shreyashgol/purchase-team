from typing import Any, Dict

from pydantic import BaseModel


class PurchaseTeamRoutingResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]
