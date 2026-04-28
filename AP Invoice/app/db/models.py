from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class APInvoiceRecord(Base):
    __tablename__ = "ap_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_entry: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    doc_num: Mapped[Optional[int]] = mapped_column(index=True)
    card_code: Mapped[str] = mapped_column(String, nullable=False)
    card_name: Mapped[str] = mapped_column(String, default="")
    doc_date: Mapped[Optional[date]] = mapped_column(Date)
    doc_due_date: Mapped[Optional[date]] = mapped_column(Date)
    tax_date: Mapped[Optional[date]] = mapped_column(Date)
    doc_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    vat_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    disc_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String, default="Open", nullable=False)
    sap_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    line_items: Mapped[List["APInvoiceLineRecord"]] = relationship(
        back_populates="ap_invoice",
        cascade="all, delete-orphan",
    )


class APInvoiceLineRecord(Base):
    __tablename__ = "ap_invoice_lines"
    __table_args__ = (UniqueConstraint("invoice_id", "line_number", name="uq_ap_invoice_lines_invoice_id_line_number"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("ap_invoices.id", ondelete="CASCADE"), nullable=False)
    line_number: Mapped[int] = mapped_column(nullable=False)
    item_code: Mapped[str] = mapped_column(String, nullable=False)
    item_description: Mapped[str] = mapped_column(String, default="")
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    tax_code: Mapped[str] = mapped_column(String, default="")
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ap_invoice: Mapped[APInvoiceRecord] = relationship(back_populates="line_items")
