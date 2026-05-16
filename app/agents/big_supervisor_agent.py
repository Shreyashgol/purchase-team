from app.agents.purchase_team.supervisor_agent import execute as purchase_team_execute
from app.agents.sales_team.supervisor_agent import routing_decision as sales_routing_decision
from app.config import BIG_SUPERVISOR_GROQ_API_KEY, BIG_SUPERVISOR_GROQ_MODEL
from app.operations.groq_client import groq_chat_completion
from app.operations.sales_intent_parser import parse_sales_intent
from app.schema.response import PurchaseTeamRoutingResponse


_BIG_SUPERVISOR_SYSTEM = """You are the top-level SAP ERP Supervisor Agent.

Choose the team that should handle the user's request.
- purchase: vendor-side buying documents such as purchase orders, purchase invoices / AP invoices, purchase returns.
- sales: customer-side selling documents such as sales orders, sales invoices / AR invoices, sales returns, customers, revenue.

Reply with exactly one lowercase word: purchase or sales.
"""


def decide_team(prompt: str) -> str:
    try:
        result = groq_chat_completion(
            [
                {"role": "system", "content": _BIG_SUPERVISOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=5,
            timeout=30,
            api_key=BIG_SUPERVISOR_GROQ_API_KEY,
            model=BIG_SUPERVISOR_GROQ_MODEL,
        )
        team = result.strip().lower().split()[0]
        if team in {"purchase", "sales"}:
            return team
    except Exception:
        pass

    lowered = prompt.lower()
    sales_keywords = (
        "sales", "sales order", "customer", "client", "ar invoice", "sales invoice",
        "revenue", "receivable", "return from customer", "sold", "selling",
    )
    return "sales" if any(keyword in lowered for keyword in sales_keywords) else "purchase"


def route(prompt: str) -> dict:
    team = decide_team(prompt)

    if team == "sales":
        intent = parse_sales_intent(prompt)
        return {
            "team": "sales",
            "team_label": "Sales Team",
            "endpoint": "/sales/parse-and-execute",
            "routing_decision": sales_routing_decision(intent),
        }

    try:
        purchase_response: PurchaseTeamRoutingResponse = purchase_team_execute(prompt)
        response_data = purchase_response.model_dump()["data"]
        routing_decision = response_data.get("fetchAgent", {})
    except Exception:
        routing_decision = {
            "action": "fetch",
            "documentType": "purchase_order",
            "documentAgent": "purchase_team.purchase_order",
            "subagent": "purchase_team.purchase_order.fetch_agent",
            "team": "purchase",
        }

    endpoints = {
        "purchase_order": "/purchase-orders/parse-and-execute",
        "ap_invoice": "/ap-invoices/parse-and-execute",
        "purchase_return": "/purchase-returns/parse-and-execute",
    }
    doc_type = routing_decision.get("documentType", "purchase_order")
    return {
        "team": "purchase",
        "team_label": "Purchase Team",
        "endpoint": endpoints.get(doc_type, "/purchase-orders/parse-and-execute"),
        "routing_decision": routing_decision,
    }
