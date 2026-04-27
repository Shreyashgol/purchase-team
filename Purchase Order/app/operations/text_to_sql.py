import re
from typing import Any


DEFAULT_LIMIT = 10
MAX_LIMIT = 50


def _extract_limit(fetch_query: str) -> int:
    patterns = [
        r"\btop\s+(\d+)\b",
        r"\blatest\s+(\d+)\b",
        r"\blast\s+(\d+)\b",
        r"\bfirst\s+(\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, fetch_query, flags=re.IGNORECASE)
        if match:
            return max(1, min(int(match.group(1)), MAX_LIMIT))
    return DEFAULT_LIMIT


def _extract_doc_number(fetch_query: str) -> int | None:
    patterns = [
        r"\bdoc(?:ument)?\s*(?:entry|number|num)?\s*[:#-]?\s*(\d+)\b",
        r"\bpurchase\s+order\s*[:#-]?\s*(\d+)\b",
        r"\bpo\s*[:#-]?\s*(\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, fetch_query, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _extract_card_code(fetch_query: str) -> str | None:
    match = re.search(r"\bV\d+\b", fetch_query, flags=re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def _extract_item_code(fetch_query: str) -> str | None:
    match = re.search(r"\bITEM[\w-]*\b", fetch_query, flags=re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def _extract_status(fetch_query: str) -> str | None:
    status_map = {
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
        "closed": "Closed",
        "open": "Open",
    }
    lowered = fetch_query.lower()
    for token, status in status_map.items():
        if token in lowered:
            return status
    return None


def build_purchase_order_fetch_sql(fetch_query: str, intent_card_code: str | None = None, intent_doc_entry: int | None = None) -> dict[str, Any]:
    query_text = fetch_query.strip()
    if not query_text and intent_card_code is None and intent_doc_entry is None:
        raise ValueError("Fetch query is empty")

    doc_number = intent_doc_entry if intent_doc_entry is not None else _extract_doc_number(query_text)
    card_code = intent_card_code or _extract_card_code(query_text)
    item_code = _extract_item_code(query_text)
    status = _extract_status(query_text)
    limit = 1 if doc_number is not None else _extract_limit(query_text)

    where_clauses = []
    params: dict[str, Any] = {"limit": limit}
    filters: dict[str, Any] = {"limit": limit}

    if doc_number is not None:
        where_clauses.append("(po.doc_entry = :doc_number OR po.doc_num = :doc_number)")
        params["doc_number"] = doc_number
        filters["docNumber"] = doc_number

    if card_code:
        where_clauses.append("po.card_code = :card_code")
        params["card_code"] = card_code
        filters["cardCode"] = card_code

    if status:
        where_clauses.append("po.status = :status")
        params["status"] = status
        filters["status"] = status

    if item_code:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM purchase_order_lines pol_filter
                WHERE pol_filter.po_id = po.id
                  AND pol_filter.item_code = :item_code
            )
            """.strip()
        )
        params["item_code"] = item_code
        filters["itemCode"] = item_code

    sql = """
        SELECT
            po.id,
            po.doc_entry,
            po.doc_num,
            po.card_code,
            po.card_name,
            po.doc_date,
            po.doc_due_date,
            po.doc_total,
            po.vat_sum,
            po.disc_sum,
            po.status,
            po.created_at,
            po.updated_at,
            COALESCE(line_summary.line_count, 0) AS line_count,
            COALESCE(line_summary.item_codes, '') AS item_codes
        FROM purchase_orders po
        LEFT JOIN (
            SELECT
                pol.po_id,
                COUNT(*) AS line_count,
                STRING_AGG(pol.item_code, ', ' ORDER BY pol.line_number) AS item_codes
            FROM purchase_order_lines pol
            GROUP BY pol.po_id
        ) AS line_summary
            ON line_summary.po_id = po.id
    """.strip()

    if where_clauses:
        sql += "\nWHERE " + "\n  AND ".join(where_clauses)

    order_by = "po.created_at DESC, po.doc_entry DESC"
    if re.search(r"\b(oldest|earliest)\b", query_text, flags=re.IGNORECASE):
        order_by = "po.created_at ASC, po.doc_entry ASC"

    sql += f"\nORDER BY {order_by}\nLIMIT :limit"

    return {
        "sql": sql,
        "params": params,
        "filters": filters,
    }
