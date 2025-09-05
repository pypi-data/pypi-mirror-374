from BasicModels.DMI.utils import timestamp_generator, load_device_id_from_cookie, sign_generator
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

def fetchBondBasicInfo(bondUniCode: str, cookie: str):
    timestamp = timestamp_generator()
    device_id = load_device_id_from_cookie(cookie)
    sign = sign_generator(str(bondUniCode) + str(timestamp) + str(device_id))
    url = f"https://web.cscidmi.com/international-bond-service/api/international/bond/basicInfo/v1?bondUniCode={bondUniCode}&timestamp={timestamp}&sign={sign}"
    headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Referer": "https://web.cscidmi.com/international-web/",
                "Host": "web.cscidmi.com",
                "Cookie": cookie,
            }
    session = requests.session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    res = session.get(url, headers=headers, verify=False)
    return res.json()