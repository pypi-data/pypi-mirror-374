import inspect
import requests

class FetchInfo():
    def __init__(self,
                 token:str,
                 user:str,
                 proxy_ip:str = None,
                 proxy_port:int = None) -> None:
        self.token = token
        self.user = user
        self.dataid_proxy = {
            "shareholders_all": "1261" # 所有股东信息（包含间接）
        }
        if proxy_ip is not None and proxy_port is not None:
            self.proxies = {
                "http": f"http://{proxy_ip}:{proxy_port}",
                "https": f"http://{proxy_ip}:{proxy_port}"
            }
        else:
            self.proxies = None

    def search(self, keyword)->dict:
        func_name = inspect.stack()[0][3]
        cookies = {}
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'client': 'pc-web;pro',
            'pcuss': self.token,
            'priority': 'u=1, i',
            'referer': 'https://www.qyyjt.cn/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'system': 'new',
            'system1': 'Macintosh; Intel Mac OS X 10_15_7;Chrome;128.0.0.0',
            'terminal': 'pc-web;pro',
            'user': self.user,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }
        params = {
            'pagesize': '15',
            'skip': '0',
            'text': keyword,
            'type': '1',
            'template': 'listNoLabel',
            # '_t': 'o2JzQV',
        }

        response = requests.get(
            'https://www.qyyjt.cn/finchinaAPP/v1/finchina-search/v1/multipleSearch',
            params=params,
            cookies=cookies,
            headers=headers,
            proxies=self.proxies
        )

        # 目标参数
        code = None

        res = {
            'success': False,
            'data': {}
        }
        if response.status_code == 200:
            resp = response.json()
            lst = resp.get("data").get("list")
            for lst_item in lst:
                name = lst_item.get("name")
                if name == keyword:
                    code = lst_item.get("code")
                    print(f"{self.__class__.__name__}/{func_name} success: found {keyword} with code = {code}")
                    break
            res.update({'success':True})
            res.update({'data': {
                        'code': code
                    }})
        else:
            print(f"{self.__class__.__name__}/{func_name} fail: keyword = {keyword}")
        
        return res
    
    def fetch_shareholders_all(self, code:str)->dict:
        func_name = inspect.stack()[0][3]
        dataid = "1261"
        cookies = {}
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'client': 'pc-web;pro',
            'dataid': dataid,
            'origin': 'https://www.qyyjt.cn',
            'pcuss': self.token, 
            'priority': 'u=1, i',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'system': 'new',
            'system1': 'Macintosh; Intel Mac OS X 10_15_7;Chrome;128.0.0.0',
            'terminal': 'pc-web;pro',
            'user': self.user, 
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        params = {
            'code': code,
            'type': 'company',
            'typePercent': 'weight',
            'page': '1',
            'pagesize': '50',
            'selected': '',
            'overview': '1',
            # '_t': '3PYfjp',
        }
        # 目标参数
        res = {
            'success': False,
            'data': {}
        }
        target_cols = {
            'percent': '持股比例',
        }
        response = requests.post('https://www.qyyjt.cn/getData.action', params=params, cookies=cookies, headers=headers, proxies=self.proxies)

        if response.status_code == 200:
            shareholders_all = {}
            try:
                for item in response.json().get("data").get("data"):
                    name = item.get('name')
                    current_dic = {name: {}}
                    for key, cn_name in target_cols.items():
                        current_dic[name].update({
                            cn_name: item.get(key)
                        })
                    shareholders_all.update(current_dic)
                res.update({'success':True})
                res.update({'data': {
                            'shareholders_all': shareholders_all
                        }})
                print(f"{self.__class__.__name__}/{func_name} success")
            except:
                res.update({'success':True})
                print(f"{self.__class__.__name__}/{func_name} success but with no shareholders_all info found")
        else:
            print(f"{self.__class__.__name__}/{func_name} fail")

        return res