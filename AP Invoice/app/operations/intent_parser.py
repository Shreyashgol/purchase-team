import json

import requests

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.model.ap_invoice_intent import APInvoiceIntent


PARSE_PROMPT_TEMPLATE = """
You are a SAP B1 AP invoice assistant. Parse the user request into a JSON object.
Return ONLY raw JSON - no markdown, no explanation.

Rules:
1. action must be exactly one of: create / fetch
2. "fetch" means the user wants invoice details, lookup, show, get, or fetch
3. Extract these keys and use null when unknown:
   - action
   - docEntry
   - cardCode
   - docDate
   - docDueDate
   - taxDate
   - items: list of objects with itemCode, quantity, unitPrice, taxCode
   - fetchQuery
4. For fetch, set items to null and preserve the original text in fetchQuery
5. If taxDate is missing but docDueDate exists, set taxDate equal to docDueDate

User request: {user_prompt}
"""


def _extract_json(raw: str) -> dict:
    if "```" in raw:
        for block in raw.split("```"):
            block = block.strip().lstrip("json").strip()
            if block.startswith("{"):
                raw = block
                break

    candidates = []
    for start in range(len(raw)):
        if raw[start] != "{":
            continue
        depth = 0
        for end in range(start, len(raw)):
            if raw[end] == "{":
                depth += 1
            elif raw[end] == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(raw[start : end + 1])
                    break

    for candidate in sorted(candidates, key=len, reverse=True):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise json.JSONDecodeError("No valid JSON object found in API output", raw, 0)


def parse_ap_invoice_intent(user_prompt: str) -> APInvoiceIntent:
    formatted_prompt = PARSE_PROMPT_TEMPLATE.format(user_prompt=user_prompt)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": formatted_prompt}],
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise Exception(f"Groq API request failed: {str(exc)}") from exc

    parsed = _extract_json(response.json()["choices"][0]["message"]["content"].strip())
    if isinstance(parsed.get("items"), list) and len(parsed["items"]) == 0:
        parsed["items"] = None

    if parsed.get("docEntry") is not None:
        try:
            parsed["docEntry"] = int(parsed["docEntry"])
        except (ValueError, TypeError):
            parsed["docEntry"] = None

    if not parsed.get("taxDate") and parsed.get("docDueDate"):
        parsed["taxDate"] = parsed["docDueDate"]

    if not parsed.get("action"):
        parsed["action"] = "create"

    return APInvoiceIntent(**parsed)
