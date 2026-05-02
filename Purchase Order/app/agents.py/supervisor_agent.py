from fastapi import HTTPException

from app.operations.utils import load_agent_module


ACTION_AGENT_MAP = {
    "cancel": "cancel_agent",
    "close": "close_agent",
    "update": "update_agent",
    "fetch": "fetch_agent",
    "create": "create_po_agent",
}


def _resolve_agent_name(action: str) -> str:
    return ACTION_AGENT_MAP.get((action or "create").lower(), "create_po_agent")


def execute(intent, repository):
    action = (intent.action or "create").lower()
    agent_name = _resolve_agent_name(action)

    if action in {"cancel", "close", "update"} and not intent.docEntry and not getattr(intent, "mobileNumber", None):
        raise HTTPException(
            status_code=400,
            detail=f"Supervisor blocked {action}: DocEntry is required before calling {agent_name}.",
        )

    if action == "create" and (not intent.cardCode or not intent.items):
        raise HTTPException(
            status_code=400,
            detail="Supervisor blocked create: vendor CardCode and at least one item are required.",
        )

    agent_module = load_agent_module(agent_name)
    response = agent_module.execute(intent, repository)

    data = response.data or {}
    data["supervisor"] = {
        "decision": f"Routing to {agent_name}",
        "action": action,
        "agent": agent_name,
    }
    response.data = data
    return response
