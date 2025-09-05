from BasicModels.DMI.utils import load_device_id_from_cookie, timestamp_generator, sign_generator
import requests

class OffshoreBondFirstMarket_NewIssueBond():
    def __init__(self, cookie:str = ""):
        self.cookie = cookie
        self.device_id = load_device_id_from_cookie(cookie)
        self.general_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://web.cscidmi.com/international-web/",
            "Host": "web.cscidmi.com",
            "Cookie": cookie,
        }
    
    def fetchPage(self, pageNum = 1, event = 4, pageSize = 50)->dict:
        """获取制定页码的所有记录及具体内容"""
        timestamp = timestamp_generator()
        sign = sign_generator(str(event) + str(pageNum) + str(pageSize) + str(timestamp) + str(self.device_id))
        url = f"""https://web.cscidmi.com/international-bond-service/api/international/dollarBond/bondNews?pageNum={pageNum}&pageSize={pageSize}&event={event}&timestamp={timestamp}&sign={sign}"""
        res = requests.get(url, headers=self.general_headers, verify=False).json()
        return res