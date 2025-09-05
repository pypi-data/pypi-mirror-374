from BasicModels.DMI.General.search import GeneralSearch
from BasicModels.DMI.utils import load_device_id_from_cookie, timestamp_generator, sign_generator
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

def fetchRemainBondsList(cookie:str, companyName:str)->list:
    headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://web.cscidmi.com/international-web/",
                "Host": "web.cscidmi.com",
                "Cookie": cookie,
                "Content-Type": "application/json"
            }


    G = GeneralSearch(cookie)

    comUniCode = G.fetch_comUniCode(companyName)
    if comUniCode is None:
        return None

    page = 1
    device_id = load_device_id_from_cookie(cookie)
    bondUniCodes = []

    while True:
        timestamp = timestamp_generator()
        sign = sign_generator(str(comUniCode) + "false" + str(page) + "30" + "issueDate:desc" + str(timestamp) + str(device_id))


        url = f"""https://web.cscidmi.com/international-bond-service/api/international/com/circulate?pageNum={page}&pageSize=30&sort=issueDate%3Adesc&comUniCodeList={comUniCode}&containExpiry=false&timestamp={timestamp}&sign={sign}"""
        session = requests.session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        res = session.get(url, headers = headers, verify=False).json()

        for bond in res.get("data").get("interCirculatingBonds"):
            bondUniCodes.append(bond.get("bondUniCode"))
    
        total_page_num = int(res.get("data").get("pages"))
        if total_page_num <= page:
            break
        else:
            page += 1

    return bondUniCodes