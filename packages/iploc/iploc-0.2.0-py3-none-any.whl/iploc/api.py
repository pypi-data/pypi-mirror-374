import requests

class IPLoc:
    def __init__(self, api_key: str, base_url: str = "https://www.iploc.site"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def check_ip(self, ip: str) -> dict:
        url = f"{self.base_url}/full_check"
        resp = requests.get(url, params={"ip": ip}, headers={"API-Key": self.api_key})
        resp.raise_for_status()
        return resp.json()

