from app.operations.sap_client import SAPClient


class APInvoiceRepository:
    def __init__(self):
        self.client = SAPClient()

    def create_ap_invoice(self, payload: dict):
        return self.client.create_ap_invoice(payload)

    def fetch_ap_invoice(self, doc_entry: int):
        return self.client.get_ap_invoice(doc_entry)

    def get_vendor(self, card_code: str):
        return self.client.get_vendor(card_code)

    def get_item(self, item_code: str):
        return self.client.get_item(item_code)
