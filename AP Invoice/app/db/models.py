from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class APInvoiceRecord(Base):
    __tablename__ = "ap_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_entry: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    doc_num: Mapped[Optional[int]] = mapped_column(index=True)
    series: Mapped[Optional[int]] = mapped_column(Integer)
    num_at_card: Mapped[Optional[str]] = mapped_column(String)
    card_code: Mapped[str] = mapped_column(String, nullable=False)
    card_name: Mapped[str] = mapped_column(String, default="")
    lic_trad_num: Mapped[Optional[str]] = mapped_column(String)
    cntct_code: Mapped[Optional[int]] = mapped_column(Integer)
    doc_date: Mapped[Optional[date]] = mapped_column(Date)
    doc_due_date: Mapped[Optional[date]] = mapped_column(Date)
    tax_date: Mapped[Optional[date]] = mapped_column(Date)
    create_date: Mapped[Optional[date]] = mapped_column(Date)
    update_date: Mapped[Optional[date]] = mapped_column(Date)
    doc_cur: Mapped[Optional[str]] = mapped_column(String)
    doc_rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    doc_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    vat_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    disc_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    round_dif: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    paid_to_date: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    paid_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    balance_due: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    pay_method: Mapped[Optional[str]] = mapped_column(String)
    pay_block: Mapped[Optional[str]] = mapped_column(String)
    ctl_account: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="Open", nullable=False)
    doc_status: Mapped[Optional[str]] = mapped_column(String)
    canceled: Mapped[Optional[str]] = mapped_column(String)
    confirmed: Mapped[Optional[str]] = mapped_column(String)
    wdd_status: Mapped[Optional[str]] = mapped_column(String)
    base_entry: Mapped[Optional[int]] = mapped_column(Integer)
    base_type: Mapped[Optional[int]] = mapped_column(Integer)
    receipt_num: Mapped[Optional[int]] = mapped_column(Integer)
    trans_id: Mapped[Optional[int]] = mapped_column(Integer)
    vat_percent: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    vat_paid: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    wt_details: Mapped[Optional[Any]] = mapped_column(JSONB)
    gst_tran_typ: Mapped[Optional[str]] = mapped_column(String)
    tax_inv_no: Mapped[Optional[str]] = mapped_column(String)
    ship_to_code: Mapped[Optional[str]] = mapped_column(String)
    project: Mapped[Optional[str]] = mapped_column(String)
    slp_code: Mapped[Optional[int]] = mapped_column(Integer)
    comments: Mapped[Optional[str]] = mapped_column(String)
    owner_code: Mapped[Optional[int]] = mapped_column(Integer)
    attachment: Mapped[Optional[str]] = mapped_column(String)
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
    base_qty: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    open_qty: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    open_inv_qty: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    price_bef_di: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    disc_prcnt: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    currency: Mapped[Optional[str]] = mapped_column(String)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    stock_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    gross_buy_pr: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    g_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    vat_prcnt: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    vat_sum: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    tax_code: Mapped[str] = mapped_column(String, default="")
    tax_type: Mapped[Optional[str]] = mapped_column(String)
    line_vat: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    base_type: Mapped[Optional[int]] = mapped_column(Integer)
    base_entry: Mapped[Optional[int]] = mapped_column(Integer)
    base_line: Mapped[Optional[int]] = mapped_column(Integer)
    po_trg_entry: Mapped[Optional[int]] = mapped_column(Integer)
    trget_entry: Mapped[Optional[int]] = mapped_column(Integer)
    whs_code: Mapped[Optional[str]] = mapped_column(String)
    invnt_sttus: Mapped[Optional[str]] = mapped_column(String)
    stock_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    acct_code: Mapped[Optional[str]] = mapped_column(String)
    ocr_code: Mapped[Optional[str]] = mapped_column(String)
    project: Mapped[Optional[str]] = mapped_column(String)
    ship_to_code: Mapped[Optional[str]] = mapped_column(String)
    ship_to_desc: Mapped[Optional[str]] = mapped_column(String)
    trns_code: Mapped[Optional[str]] = mapped_column(String)
    line_status: Mapped[Optional[str]] = mapped_column(String)
    free_txt: Mapped[Optional[str]] = mapped_column(String)
    owner_code: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ap_invoice: Mapped[APInvoiceRecord] = relationship(back_populates="line_items")
