import requests
import warnings

from app.config import SAP_BASE_URL, SAP_COMPANYDB, SAP_PASSWORD, SAP_USERNAME


warnings.filterwarnings("ignore", message="Unverified HTTPS request")


class SAPClient:
    def __init__(self):
        self.session_id = None

    def login(self):
        payload = {"UserName": SAP_USERNAME, "Password": SAP_PASSWORD, "CompanyDB": SAP_COMPANYDB}
        response = requests.post(f"{SAP_BASE_URL}/Login", json=payload, verify=False)
        if response.status_code == 200:
            self.session_id = response.json().get("SessionId")
            return
        raise Exception(f"SAP Login failed: {response.text}")

    def _headers(self):
        if not self.session_id:
            self.login()
        return {"Cookie": f"B1SESSION={self.session_id}"}

    def create_purchase_return(self, data: dict):
        response = requests.post(f"{SAP_BASE_URL}/PurchaseReturns", json=data, headers=self._headers(), verify=False)
        if response.status_code == 201:
            return response.json()
        raise Exception(f"Purchase Return creation failed: {response.text}")

    def cancel_purchase_return(self, doc_entry: int):
        response = requests.post(f"{SAP_BASE_URL}/PurchaseReturns({doc_entry})/Cancel", headers=self._headers(), verify=False)
        if response.status_code in (200, 204):
            return {"DocEntry": doc_entry, "status": "cancelled"}
        raise Exception(f"Purchase Return cancel failed (HTTP {response.status_code}): {response.text}")

    def close_purchase_return(self, doc_entry: int):
        response = requests.post(f"{SAP_BASE_URL}/PurchaseReturns({doc_entry})/Close", headers=self._headers(), verify=False)
        if response.status_code in (200, 204):
            return {"DocEntry": doc_entry, "status": "closed"}
        raise Exception(f"Purchase Return close failed (HTTP {response.status_code}): {response.text}")

    def reopen_purchase_return(self, doc_entry: int):
        response = requests.post(f"{SAP_BASE_URL}/PurchaseReturns({doc_entry})/Reopen", headers=self._headers(), verify=False)
        if response.status_code in (200, 204):
            return {"DocEntry": doc_entry, "status": "reopened"}
        raise Exception(f"Purchase Return reopen failed (HTTP {response.status_code}): {response.text}")

    def update_purchase_return(self, doc_entry: int, data: dict):
        response = requests.patch(f"{SAP_BASE_URL}/PurchaseReturns({doc_entry})", json=data, headers=self._headers(), verify=False)
        if response.status_code in (200, 204):
            return {"DocEntry": doc_entry}
        raise Exception(f"Purchase Return update failed (HTTP {response.status_code}): {response.text}")

    def get_vendor(self, card_code: str):
        response = requests.get(f"{SAP_BASE_URL}/BusinessPartners('{card_code}')", headers=self._headers(), verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("CardType") == "S":
                return data
        return None
