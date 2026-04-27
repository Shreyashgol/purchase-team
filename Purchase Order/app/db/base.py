import logging
from collections.abc import Sequence
from contextlib import contextmanager
from decimal import Decimal

from sqlalchemy import create_engine, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_CONNECTION_STRING
from app.db.models import Base, PurchaseOrderLineRecord, PurchaseOrderRecord

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None


def get_database_connection_string() -> str:
    return DATABASE_CONNECTION_STRING


def init_db_pool():
    global engine, SessionLocal

    if engine is not None and SessionLocal is not None:
        return engine

    if not DATABASE_CONNECTION_STRING:
        logger.warning("DATABASE_CONNECTION_STRING is empty; database persistence is disabled")
        return None

    engine = create_engine(
        DATABASE_CONNECTION_STRING,
        pool_pre_ping=True,
        future=True,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    logger.info("SQLAlchemy engine initialized")
    return engine


@contextmanager
def get_db_session():
    init_db_pool()
    if SessionLocal is None:
        raise RuntimeError("DATABASE_CONNECTION_STRING is not configured")

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _serialize_purchase_order(record: PurchaseOrderRecord) -> dict:
    return {
        "id": record.id,
        "doc_entry": record.doc_entry,
        "doc_num": record.doc_num,
        "card_code": record.card_code,
        "card_name": record.card_name,
        "doc_date": record.doc_date.isoformat() if record.doc_date else None,
        "doc_due_date": record.doc_due_date.isoformat() if record.doc_due_date else None,
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


def _serialize_purchase_orders(records: Sequence[PurchaseOrderRecord]) -> list[dict]:
    return [_serialize_purchase_order(record) for record in records]


def save_purchase_order(po_data: dict, line_items: list | None = None) -> int:
    with get_db_session() as session:
        purchase_order_stmt = (
            insert(PurchaseOrderRecord)
            .values(
                doc_entry=po_data.get("DocEntry"),
                doc_num=po_data.get("DocNum"),
                card_code=po_data.get("CardCode"),
                card_name=po_data.get("CardName", ""),
                doc_date=po_data.get("DocDate"),
                doc_due_date=po_data.get("DueDate"),
                doc_total=_to_decimal(po_data.get("DocTotal", 0)),
                vat_sum=_to_decimal(po_data.get("VatSum", 0)),
                disc_sum=_to_decimal(po_data.get("DiscSum", 0)),
                status=po_data.get("Status", "Open"),
                sap_payload=po_data,
            )
            .on_conflict_do_update(
                index_elements=[PurchaseOrderRecord.doc_entry],
                set_={
                    "doc_num": po_data.get("DocNum"),
                    "card_code": po_data.get("CardCode"),
                    "card_name": po_data.get("CardName", ""),
                    "doc_date": po_data.get("DocDate"),
                    "doc_due_date": po_data.get("DueDate"),
                    "doc_total": _to_decimal(po_data.get("DocTotal", 0)),
                    "vat_sum": _to_decimal(po_data.get("VatSum", 0)),
                    "disc_sum": _to_decimal(po_data.get("DiscSum", 0)),
                    "status": po_data.get("Status", "Open"),
                    "sap_payload": po_data,
                },
            )
            .returning(PurchaseOrderRecord.id)
        )

        po_id = session.execute(purchase_order_stmt).scalar_one()
        session.execute(delete(PurchaseOrderLineRecord).where(PurchaseOrderLineRecord.po_id == po_id))

        for idx, item in enumerate(line_items or []):
            quantity = _to_decimal(item.get("Quantity", 0) or 0)
            unit_price = _to_decimal(item.get("UnitPrice", item.get("Price", 0)) or 0)
            line_total = item.get("LineTotal")
            if line_total is None:
                line_total = quantity * unit_price
            else:
                line_total = _to_decimal(line_total)

            session.add(
                PurchaseOrderLineRecord(
                    po_id=po_id,
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
        return po_id


def fetch_po_by_doc_num(doc_num: int) -> dict | None:
    with get_db_session() as session:
        statement = select(PurchaseOrderRecord).where(PurchaseOrderRecord.doc_num == doc_num)
        record = session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return _serialize_purchase_order(record)


def fetch_po_by_doc_entry(doc_entry: int) -> dict | None:
    with get_db_session() as session:
        statement = select(PurchaseOrderRecord).where(PurchaseOrderRecord.doc_entry == doc_entry)
        record = session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return _serialize_purchase_order(record)


def fetch_pos_by_card_code(card_code: str, limit: int = 20) -> list[dict]:
    with get_db_session() as session:
        statement = (
            select(PurchaseOrderRecord)
            .where(PurchaseOrderRecord.card_code == card_code)
            .order_by(PurchaseOrderRecord.created_at.desc())
            .limit(limit)
        )
        records = session.execute(statement).scalars().all()
        return _serialize_purchase_orders(records)


def update_po_status_by_doc_entry(doc_entry: int, status: str):
    with get_db_session() as session:
        statement = select(PurchaseOrderRecord).where(PurchaseOrderRecord.doc_entry == doc_entry)
        record = session.execute(statement).scalar_one_or_none()
        if record is None:
            return
        record.status = status
        session.add(record)
