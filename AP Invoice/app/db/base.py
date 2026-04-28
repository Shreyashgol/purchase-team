import logging
from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.config import DATABASE_CONNECTION_STRING
from app.db.models import APInvoiceLineRecord, APInvoiceRecord, Base
from shared.db.runtime import DatabaseRuntime

logger = logging.getLogger(__name__)

db_runtime = DatabaseRuntime(
    database_url=DATABASE_CONNECTION_STRING,
    metadata=Base.metadata,
    logger_name=__name__,
)


def init_db_pool():
    return db_runtime.init()


def get_db_session():
    return db_runtime.session_scope()


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _serialize_ap_invoice(record: APInvoiceRecord) -> dict:
    return {
        "id": record.id,
        "doc_entry": record.doc_entry,
        "doc_num": record.doc_num,
        "card_code": record.card_code,
        "card_name": record.card_name,
        "doc_date": record.doc_date.isoformat() if record.doc_date else None,
        "doc_due_date": record.doc_due_date.isoformat() if record.doc_due_date else None,
        "tax_date": record.tax_date.isoformat() if record.tax_date else None,
        "doc_total": float(record.doc_total or 0),
        "vat_sum": float(record.vat_sum or 0),
        "disc_sum": float(record.disc_sum or 0),
        "status": record.status,
        "sap_payload": record.sap_payload,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "line_items": [
            {
                "line_number": line.line_number,
                "item_code": line.item_code,
                "item_description": line.item_description,
                "quantity": float(line.quantity or 0),
                "unit_price": float(line.unit_price or 0),
                "tax_code": line.tax_code,
                "line_total": float(line.line_total or 0),
            }
            for line in sorted(record.line_items, key=lambda item: item.line_number)
        ],
    }


def _serialize_ap_invoices(records: Sequence[APInvoiceRecord]) -> list[dict]:
    return [_serialize_ap_invoice(record) for record in records]


def save_ap_invoice(invoice_data: dict, line_items: list | None = None) -> int:
    with get_db_session() as session:
        invoice_stmt = (
            insert(APInvoiceRecord)
            .values(
                doc_entry=invoice_data.get("DocEntry"),
                doc_num=invoice_data.get("DocNum"),
                card_code=invoice_data.get("CardCode"),
                card_name=invoice_data.get("CardName", ""),
                doc_date=invoice_data.get("DocDate"),
                doc_due_date=invoice_data.get("DocDueDate"),
                tax_date=invoice_data.get("TaxDate"),
                doc_total=_to_decimal(invoice_data.get("DocTotal", 0)),
                vat_sum=_to_decimal(invoice_data.get("VatSum", 0)),
                disc_sum=_to_decimal(invoice_data.get("DiscSum", 0)),
                status=invoice_data.get("Status", "Open"),
                sap_payload=invoice_data,
            )
            .on_conflict_do_update(
                index_elements=[APInvoiceRecord.doc_entry],
                set_={
                    "doc_num": invoice_data.get("DocNum"),
                    "card_code": invoice_data.get("CardCode"),
                    "card_name": invoice_data.get("CardName", ""),
                    "doc_date": invoice_data.get("DocDate"),
                    "doc_due_date": invoice_data.get("DocDueDate"),
                    "tax_date": invoice_data.get("TaxDate"),
                    "doc_total": _to_decimal(invoice_data.get("DocTotal", 0)),
                    "vat_sum": _to_decimal(invoice_data.get("VatSum", 0)),
                    "disc_sum": _to_decimal(invoice_data.get("DiscSum", 0)),
                    "status": invoice_data.get("Status", "Open"),
                    "sap_payload": invoice_data,
                },
            )
            .returning(APInvoiceRecord.id)
        )

        invoice_id = session.execute(invoice_stmt).scalar_one()
        session.execute(delete(APInvoiceLineRecord).where(APInvoiceLineRecord.invoice_id == invoice_id))

        for idx, item in enumerate(line_items or []):
            quantity = _to_decimal(item.get("Quantity", 0) or 0)
            unit_price = _to_decimal(item.get("UnitPrice", item.get("Price", 0)) or 0)
            line_total = item.get("LineTotal")
            if line_total is None:
                line_total = quantity * unit_price
            else:
                line_total = _to_decimal(line_total)

            session.add(
                APInvoiceLineRecord(
                    invoice_id=invoice_id,
                    line_number=idx,
                    item_code=item.get("ItemCode"),
                    item_description=item.get("ItemDescription", ""),
                    quantity=quantity,
                    unit_price=unit_price,
                    tax_code=item.get("TaxCode", ""),
                    line_total=line_total,
                )
            )

        session.flush()
        return invoice_id


def fetch_ap_invoice_by_doc_num(doc_num: int) -> dict | None:
    with get_db_session() as session:
        statement = select(APInvoiceRecord).where(APInvoiceRecord.doc_num == doc_num)
        record = session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return _serialize_ap_invoice(record)


def fetch_ap_invoice_by_doc_entry(doc_entry: int) -> dict | None:
    with get_db_session() as session:
        statement = select(APInvoiceRecord).where(APInvoiceRecord.doc_entry == doc_entry)
        record = session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return _serialize_ap_invoice(record)


def fetch_ap_invoices_by_card_code(card_code: str, limit: int = 20) -> list[dict]:
    with get_db_session() as session:
        statement = (
            select(APInvoiceRecord)
            .where(APInvoiceRecord.card_code == card_code)
            .order_by(APInvoiceRecord.created_at.desc())
            .limit(limit)
        )
        records = session.execute(statement).scalars().all()
        return _serialize_ap_invoices(records)
