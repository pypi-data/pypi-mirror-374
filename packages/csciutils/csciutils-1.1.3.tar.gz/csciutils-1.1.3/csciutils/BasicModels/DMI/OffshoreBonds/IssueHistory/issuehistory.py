import requests
from BasicModels.DMI.utils import sign_generator, timestamp_generator, load_device_id_from_cookie
from BasicModels.DMI.General.search import GeneralSearch
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

class Proxies():
    def __init__(self, cookie) -> None:
        self.cookie = cookie
        self.device_id = load_device_id_from_cookie(cookie)
        self.timestamp = timestamp_generator()
        self.sign = sign_generator(self.timestamp + self.device_id)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            'Host':'web.cscidmi.com',
            'Origin':'https://web.cscidmi.com',
            'Referer':'https://web.cscidmi.com/international-web/'
        }
        
    def bondStatusList(self):
        self.bondStatusList_proxy = {
            "未到期": 1,
            "已到期": 2,
            "违约": 3
        }

    def industryTypeList(self):
        self.industryTypeList_proxy = {
            "城投": 10,
            "地产": 20,
            "金融": 30,
            "科技": 40,
            "能源": 50,
            "其他": 60,
        }

    def bondCurrencyList(self):
        res = requests.get(url = f"https://web.cscidmi.com/international-bond-service/api/international/dollarBond/distinct/bond/currency?timestamp={self.timestamp}&sign={self.sign}",
                           headers = self.headers)
        if res.status_code == 200:
            data = res.json().get("data")
            self.bondCurrencyList_proxy = {}
            for currency in data:
                self.bondCurrencyList_proxy[currency["parameterName"]] = currency["parameterCode"]
        else:
            self.bondCurrencyList_proxy = None
        
    def generate(self):
        self.bondCurrencyList()
        self.bondStatusList()
        self.industryTypeList()
    



class IssueHistory():
    def __init__(self, cookie) -> None:
        self.cookie = cookie
        self.device_id = load_device_id_from_cookie(cookie)
        self.G = GeneralSearch(cookie = cookie)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            'Host':'web.cscidmi.com',
            'Origin':'https://web.cscidmi.com',
            'Referer':'https://web.cscidmi.com/international-web/'
        }
        self.proxies = Proxies(cookie = cookie)
        self.proxies.generate()

        

    def _filterSearch(self,
            定价日起始日: str = None,
            定价日结束日: str = None,
            # 起息日起始日: str = None,
            # 起息日结束日: str = None,
            兑付日起始日: str = None,
            兑付日结束日: str = None,
            # 票息最低: float = None,
            # 票息最高: float = None,
            货币: list = None,
            # 剩余期限: str = None,
            # 主题债券: list = None,
            全部板块: list = None,
            # 公司类型: list = None,
            # 全部发行方式: list = None,
            # 主体评级: list = None,
            # 发行规模: list = None,
            # 全部期限: list = None,
            # 发行架构: list = None,
            # 全部主体: list = None,
            # 全部债项: list = None,
            # 全部票面: list = None,
            # 全部条款: list = None,
            全部状态: list = None,
            # 全部债券: list = None,
            # 发行规则: list = None,
    ):
        timestamp = timestamp_generator()
        sign = sign_generator(timestamp + self.device_id)
        
        bondStatusList = [self.proxies.bondStatusList_proxy.get(bondStatus) for bondStatus in 全部状态] if 全部状态 is not None else None
        industryTypeList = [self.proxies.industryTypeList_proxy.get(industryType) for industryType in 全部板块] if 全部板块 is not None else None
        bondCurrencyList = [self.proxies.bondCurrencyList_proxy.get(currency) for currency in 货币] if 货币 is not None else None

        payload = {
            "remainingTenor":0, # 全部期限
            "pageSize":50, # 默认
            "industryTypeList":industryTypeList, 
            "bondStatusList":bondStatusList,
            "priceStartDate":定价日起始日,
            "priceEndDate":定价日结束日,
            "depositStatus":0, # 非存单，默认
            "sort":{"sortDirection":"ASC","propertyName":"pricingDate"}, # 默认
            "bondCurrencyList":bondCurrencyList,
            "payStartDate":兑付日起始日,
            "payEndDate":兑付日结束日,
            "bondIssueMethodList":[10,20] # 新发，增发，默认
        }

        data = {}

        for key, value in payload.items():
            if value is not None:
                data[key] = value

        res = requests.post(url = f"https://web.cscidmi.com/international-bond-primary/api/dollarBond/bond/history?timestamp={timestamp}&sign={sign}",
                           headers = self.headers,
                           data = data)
        if res.status_code == 200:
            return res.json()
        return res



    def _searchBond(self, keyword):
        bondUniCode = self.G.fetch_bondUniCode_offshore(bondcode=keyword)
        if bondUniCode:
            timestamp = timestamp_generator()
            sign = sign_generator(timestamp + self.device_id)
            url = f"https://web.cscidmi.com/international-bond-primary/api/dollarBond/bond/history?timestamp={timestamp}&sign={sign}"
            payload = {
                "remainingTenor":0,
                "pageSize":50,
                "bondUniCode":bondUniCode,
                "depositStatus":0,
                "bondIssueMethodList":[10,20],
                }
            session = requests.session()
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            res = session.post(url, headers=self.headers, json=payload, verify=False).json()
            return res
        else:
            return None
    