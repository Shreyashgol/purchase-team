from fastapi import APIRouter, Depends, HTTPException

from app.crud.sales_crud import SalesRepository
from app.operations.sales_intent_parser import parse_sales_intent
from app.operations.utils import load_agent_module
from app.operations.utils import verify_jwt_token
from app.schema.purchase_order import PromptRequest
from app.schema.response import SalesActionResponse

router = APIRouter()


@router.post("/parse-and-execute", response_model=SalesActionResponse)
def sales_parse_and_execute(request: PromptRequest, user: str = Depends(verify_jwt_token)):
    del user

    try:
        intent = parse_sales_intent(request.prompt)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Sales intent parsing failed: {str(exc)}") from exc

    try:
        repository = SalesRepository()
        agent_module = load_agent_module("supervisor_agent", "sales_team")
        return agent_module.execute(intent, repository)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Sales execution failed: {str(exc)}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sales execution error: {str(exc)}") from exc
