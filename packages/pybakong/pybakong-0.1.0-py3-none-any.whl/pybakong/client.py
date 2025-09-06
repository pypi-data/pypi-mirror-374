
import requests
from .exceptions import BakongAPIError

class BakongClient:
    def __init__(self, base_url: str = "https://api-bakong.nbc.gov.kh/v1"):
        self.base_url = base_url.rstrip('/')
        self.token = None

    def request_token(self, email: str, organization: str, project: str):
        response = requests.post(
            f"{self.base_url}/request_token",
            json={"email": email, "organization": organization, "project": project},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        return data

    def verify_token(self, code: str):
        response = requests.post(
            f"{self.base_url}/verify",
            json={"code": code},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        self.token = data["data"]["token"]
        return self.token

    def renew_token(self, email: str):
        response = requests.post(
            f"{self.base_url}/renew_token",
            json={"email": email},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        self.token = data["data"]["token"]
        return self.token

    def generate_deeplink(self, qr: str, app_icon_url: str, app_name: str, app_deep_link_callback: str):
        response = requests.post(
            f"{self.base_url}/generate_deeplink_by_qr",
            json={
                "qr": qr,
                "sourceInfo": {
                    "appIconUrl": app_icon_url,
                    "appName": app_name,
                    "appDeepLinkCallback": app_deep_link_callback
                }
            },
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        return data["data"]["shortLink"]

    def check_transaction_md5(self, md5: str):
        return self._check_transaction("md5", md5)

    def check_transaction_hash(self, full_hash: str):
        return self._check_transaction("hash", full_hash)

    def check_transaction_short(self, short_hash: str, amount: str, currency: str):
        return self._check_transaction("short_hash", {"short_hash": short_hash, "amount": amount, "currency": currency})

    def check_bakong_account(self, account_id: str):
        response = requests.post(
            f"{self.base_url}/check_bakong_account",
            json={"accountId": account_id},
            headers=self._auth_header()
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        return data["data"]

    def _check_transaction(self, endpoint: str, data: dict):
        response = requests.post(
            f"{self.base_url}/check_transaction_by_{endpoint}",
            json=data,
            headers=self._auth_header()
        )
        data = response.json()
        if data.get("responseCode") != 0:
            raise BakongAPIError(data.get("responseMessage"))
        return data["data"]

    def _auth_header(self):
        if not self.token:
            raise BakongAPIError("Token is not set. Please verify first.")
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
