import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore
from BasicModels.DMI.utils import sign_generator, timestamp_generator, load_device_id_from_cookie
import json

class GeneralSearch():
    def __init__(self, cookie:str):
        self.cookie = cookie
        self.device_id = load_device_id_from_cookie(cookie)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Referer": "https://web.cscidmi.com/international-web/",
            "Host": "web.cscidmi.com",
            "Cookie": cookie,
            "Content-Type": "text/plain"
        }

    def search(self, keyword)-> dict:
        timestamp = timestamp_generator()
        sign = sign_generator(timestamp + self.device_id)
        url = f"https://web.cscidmi.com/international-bond-basic/api/search/gathering?timestamp={timestamp}&sign={sign}"
        payload = {
            "keyword": keyword,
            "pageSize": 5
        }
        data = json.dumps(payload)
        session = requests.session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        res = session.post(url, headers=self.headers, data=data, verify=False).json()
        return res

    def fetch_comUniCode(self, companyName:str):
        res = self.search(keyword=companyName)
        if res["data"]["comInfoSearchResults"]:
            return res["data"]["comInfoSearchResults"][0]["comUniCode"]
        else:
            return None

    def fetch_bondUniCode_onshore(self, bondcode:str):
        res = self.search(keyword=bondcode)
        if res["data"]["onshoreBondInfoSearchResults"]:
            return res["data"]["onshoreBondInfoSearchResults"][0]["bondUniCode"]
        else:
            return None

    def fetch_bondUniCode_offshore(self, bondcode:str):
        res = self.search(keyword=bondcode)
        if res["data"]["internationalBondInfoSearchResults"]:
            return res["data"]["internationalBondInfoSearchResults"][0]["bondUniCode"]
        else:
            return None