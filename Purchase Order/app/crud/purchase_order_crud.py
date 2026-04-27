import logging

from app.db.base import (
    fetch_po_by_doc_entry,
    fetch_po_by_doc_num,
    fetch_pos_by_card_code,
    save_purchase_order,
    update_po_status_by_doc_entry,
)
from app.operations.sap_client import SAPClient

logger = logging.getLogger(__name__)


class PurchaseOrderRepository:
    def __init__(self):
        self.client = SAPClient()

    def create_purchase_order(self, payload: dict):
        """Create PO in SAP and save to database"""
        response = self.client.create_purchase_order(payload)

        if response and "DocEntry" in response:
            po_data = {
                "DocEntry": response.get("DocEntry"),
                "DocNum": response.get("DocNum"),
                "CardCode": payload.get("CardCode"),
                "DocDate": payload.get("DocDate"),
                "DueDate": payload.get("DocDueDate"),
                "DocTotal": response.get("DocTotal"),
                "VatSum": response.get("VatSum"),
                "DiscSum": response.get("DiscSum"),
                "Status": "Open",
            }

            line_items = payload.get("DocumentLines", [])
            save_purchase_order(po_data, line_items)
            logger.info(f"PO saved to database: {response.get('DocNum')}")

        return response

    def cancel_purchase_order(self, doc_entry: int):
        """Cancel PO in SAP and update database"""
        response = self.client.cancel_purchase_order(doc_entry)
        update_po_status_by_doc_entry(doc_entry, "Cancelled")
        logger.info("PO status updated to Cancelled in database")
        return response

    def close_purchase_order(self, doc_entry: int):
        """Close PO in SAP and update database"""
        response = self.client.close_purchase_order(doc_entry)
        update_po_status_by_doc_entry(doc_entry, "Closed")
        logger.info("PO status updated to Closed in database")
        return response

    def update_purchase_order(self, doc_entry: int, payload: dict):
        return self.client.update_purchase_order(doc_entry, payload)

    def get_vendor(self, card_code: str):
        return self.client.get_vendor(card_code)

    def get_item(self, item_code: str):
        return self.client.get_item(item_code)
    
    def get_po_from_db(self, doc_num: int):
        """Fetch PO from database"""
        return fetch_po_by_doc_num(doc_num)

    def get_po_by_doc_entry(self, doc_entry: int):
        """Fetch PO from database using DocEntry"""
        return fetch_po_by_doc_entry(doc_entry)

    def get_pos_by_card_code(self, card_code: str, limit: int = 20):
        """Fetch purchase orders for a vendor from database"""
        return fetch_pos_by_card_code(card_code, limit=limit)
