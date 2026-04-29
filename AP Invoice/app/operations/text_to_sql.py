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
        r"\bap\s+invoice\s*[:#-]?\s*(\d+)\b",
        r"\binvoice\s*[:#-]?\s*(\d+)\b",
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


def build_ap_invoice_fetch_sql(fetch_query: str, intent_card_code: str | None = None, intent_doc_entry: int | None = None) -> dict[str, Any]:
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
        where_clauses.append("(api.doc_entry = :doc_number OR api.doc_num = :doc_number)")
        params["doc_number"] = doc_number
        filters["docNumber"] = doc_number

    if card_code:
        where_clauses.append("api.card_code = :card_code")
        params["card_code"] = card_code
        filters["cardCode"] = card_code

    if status:
        where_clauses.append("api.status = :status")
        params["status"] = status
        filters["status"] = status

    if item_code:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM ap_invoice_lines ail_filter
                WHERE ail_filter.invoice_id = api.id
                  AND ail_filter.item_code = :item_code
            )
            """.strip()
        )
        params["item_code"] = item_code
        filters["itemCode"] = item_code

    sql = """
        SELECT
            api.id,
            api.doc_entry,
            api.doc_num,
            api.series,
            api.num_at_card,
            api.card_code,
            api.card_name,
            api.lic_trad_num,
            api.cntct_code,
            api.doc_date,
            api.doc_due_date,
            api.tax_date,
            api.create_date,
            api.update_date,
            api.doc_cur,
            api.doc_rate,
            api.doc_total,
            api.vat_sum,
            api.disc_sum,
            api.round_dif,
            api.paid_to_date,
            api.paid_sum,
            api.balance_due,
            api.pay_method,
            api.pay_block,
            api.ctl_account,
            api.status,
            api.doc_status,
            api.canceled,
            api.confirmed,
            api.wdd_status,
            api.base_entry,
            api.base_type,
            api.receipt_num,
            api.trans_id,
            api.vat_percent,
            api.vat_paid,
            api.wt_details,
            api.gst_tran_typ,
            api.tax_inv_no,
            api.ship_to_code,
            api.project,
            api.slp_code,
            api.comments,
            api.owner_code,
            api.attachment,
            api.created_at,
            api.updated_at,
            COALESCE(line_summary.line_count, 0) AS line_count,
            COALESCE(line_summary.item_codes, '') AS item_codes,
            COALESCE(line_summary.lines, '[]'::json) AS lines
        FROM ap_invoices api
        LEFT JOIN (
            SELECT
                ail.invoice_id,
                COUNT(*) AS line_count,
                STRING_AGG(ail.item_code, ', ' ORDER BY ail.line_number) AS item_codes,
                JSON_AGG(
                    JSON_BUILD_OBJECT(
                        'doc_entry', api_line.doc_entry,
                        'line_number', ail.line_number,
                        'item_code', ail.item_code,
                        'item_description', ail.item_description,
                        'base_qty', ail.base_qty,
                        'open_qty', ail.open_qty,
                        'open_inv_qty', ail.open_inv_qty,
                        'quantity', ail.quantity,
                        'price', ail.price,
                        'unit_price', ail.price,
                        'price_bef_di', ail.price_bef_di,
                        'disc_prcnt', ail.disc_prcnt,
                        'line_total', ail.line_total,
                        'currency', ail.currency,
                        'rate', ail.rate,
                        'stock_price', ail.stock_price,
                        'gross_buy_pr', ail.gross_buy_pr,
                        'g_total', ail.g_total,
                        'vat_prcnt', ail.vat_prcnt,
                        'vat_sum', ail.vat_sum,
                        'tax_code', ail.tax_code,
                        'tax_type', ail.tax_type,
                        'line_vat', ail.line_vat,
                        'base_type', ail.base_type,
                        'base_entry', ail.base_entry,
                        'base_line', ail.base_line,
                        'po_trg_entry', ail.po_trg_entry,
                        'trget_entry', ail.trget_entry,
                        'whs_code', ail.whs_code,
                        'invnt_sttus', ail.invnt_sttus,
                        'stock_value', ail.stock_value,
                        'acct_code', ail.acct_code,
                        'ocr_code', ail.ocr_code,
                        'project', ail.project,
                        'ship_to_code', ail.ship_to_code,
                        'ship_to_desc', ail.ship_to_desc,
                        'trns_code', ail.trns_code,
                        'line_status', ail.line_status,
                        'free_txt', ail.free_txt,
                        'owner_code', ail.owner_code
                    )
                    ORDER BY ail.line_number
                ) AS lines
            FROM ap_invoice_lines ail
            JOIN ap_invoices api_line
                ON api_line.id = ail.invoice_id
            GROUP BY ail.invoice_id
        ) AS line_summary
            ON line_summary.invoice_id = api.id
    """.strip()

    if where_clauses:
        sql += "\nWHERE " + "\n  AND ".join(where_clauses)

    order_by = "api.created_at DESC, api.doc_entry DESC"
    if re.search(r"\b(oldest|earliest)\b", query_text, flags=re.IGNORECASE):
        order_by = "api.created_at ASC, api.doc_entry ASC"

    sql += f"\nORDER BY {order_by}\nLIMIT :limit"

    return {
        "sql": sql,
        "params": params,
        "filters": filters,
    }
