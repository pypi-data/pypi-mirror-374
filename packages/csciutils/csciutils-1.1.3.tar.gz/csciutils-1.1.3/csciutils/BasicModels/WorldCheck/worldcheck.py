import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse, parse_qsl
import json
import random
import inspect
import os
import shutil
import uuid
import re

class WorldCheck():
    def __init__(self, username:str, password:str) -> None:
        self.username = username
        self.password = password
        self.generate_state()
        self.SUCCESS = True
        
    def generate_state_old(self):
        state = str(round(random.uniform(0, 1), 16))
        self.state = state
        return state

    def generate_state(self):
        """
        生成符合UUIDv4标准的state参数
        返回: 32字符的十六进制字符串，格式为 8-4-4-4-12
        """
        state = str(uuid.uuid4())
        self.state = state
        return state
        
    def find_AWSALB(self, string):
        match = re.search(r"AWSALB=([^;]+)", string)
        if match:
            awsalb_value = match.group(1)
            AWSALB = awsalb_value
            return AWSALB
        else:
            print("未找到AWSALB的值")
            return None

    def find_AWSALBCORS(self, string):
        match = re.search(r"AWSALBCORS=([^;]+)", string)
        if match:
            awsalb_value = match.group(1)
            AWSALBCORS = awsalb_value
            return AWSALBCORS
        else:
            print("未找到AWSALBCORS的值")
            return None
        
    def get_status_id(self, configs:json, status_label:str)->str: # status_label = POSITIVE / POSSIBLE / FALSE / UNSPECIFIED
        for status in configs.get("resolutionFields").get("statuses"):
            if status.get("label") == status_label:
                return status.get("id")
        return None

    def get_risk_id(self, configs:json, risk_label:str)->str: # risk_label = HIGH / MEDIUM / LOW / UNKNOWN
        for risk in configs.get("resolutionFields").get("risks"):
            if risk.get("label") == risk_label:
                return risk.get("id")
        return None

    def get_reason_id(self, configs:json, reason_label:str)->str: # reason_label = NO MATCH / FULL MATCH / PARTIAL MATCH / UNKNOWN
        for reason in configs.get("resolutionFields").get("reasons"):
            if reason.get("label") == reason_label:
                return reason.get("id")
        return None

    def check_dir(self, folder_name:str):
        """
        folder_name: Shareholders | Organisation
        """
        # 检查文件夹是否存在
        if os.path.exists(folder_name):
            # 如果存在，清空文件夹内容
            shutil.rmtree(folder_name)
            os.makedirs(folder_name)  # 重建文件夹
            print(f"Folder '{folder_name}' already exists, remove and recreate success.")
        else:
            # 如果文件夹不存在，创建文件夹
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' create success.")

    def download_file(self, folder_name, file_name, content):
        """
        folder_name: Shareholders | Organisation
        file_name: 没有.pdf
        """
        if folder_name is None:
            folder_name = "PDFDOWNLOAD"
        with open(f"{folder_name}/{file_name}.pdf", "wb") as f:
            f.write(content)
            print(f"{file_name}.pdf in folder {folder_name} download success.")
    
    def worldcheck_refinitiv_com(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }

        response = requests.get('https://worldcheck.refinitiv.com/', headers=headers)
    
    def risk_lseg_com(self):
        cookies = {
            # 'x-meta': '%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D',
            # 'x-vsession-last-login': '1750840358200',
            # 'at_check': 'true',
            # 's_fid': '4C011F4B69F6C10C-2CC6BE013084AD0A',
            # 'OptanonAlertBoxClosed': '2025-06-25T08:36:03.515Z',
            # 'LC_PAGE_VISIT_HISTORY': '%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D',
            # 'LC_LAST_VISITED_REFERRER': 'https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one',
            # 'x-vsession-last-active': '1750840596067',
            # 'accelus.connect.sid': 's%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE',
            # '_gcl_au': '1.1.646319424.1750853672',
            # 'mbox': 'PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533',
            # '_uetsid': '9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002',
            # 'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false',
            # '_uetvid': '9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v',
            # '_ga': 'GA1.1.1137008475.1750853674',
            # 's_plt': '%5B%5BB%5D%5D',
            # 's_pltp': '%5B%5BB%5D%5D',
            # 's_cc': 'true',
            # '_ga_1J3ZS1VERY': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_L5R01EES25': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_ZKKCDJR7BE': 'GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_DGKRWS7656': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # 'x-auth-redirect': 'true',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D; x-vsession-last-login=1750840358200; at_check=true; s_fid=4C011F4B69F6C10C-2CC6BE013084AD0A; OptanonAlertBoxClosed=2025-06-25T08:36:03.515Z; LC_PAGE_VISIT_HISTORY=%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D; LC_LAST_VISITED_REFERRER=https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one; x-vsession-last-active=1750840596067; accelus.connect.sid=s%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE; _gcl_au=1.1.646319424.1750853672; mbox=PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533; _uetsid=9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; _uetvid=9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v; _ga=GA1.1.1137008475.1750853674; s_plt=%5B%5BB%5D%5D; s_pltp=%5B%5BB%5D%5D; s_cc=true; _ga_1J3ZS1VERY=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_L5R01EES25=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_ZKKCDJR7BE=GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0; _ga_DGKRWS7656=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; x-auth-redirect=true',
        }

        response = requests.get('https://risk.lseg.com/', cookies=cookies, headers=headers)
        func_name = inspect.stack()[0][3]
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            
            accelus_connect_sid = response.cookies.get("accelus.connect.sid")

            x_meta = response.cookies.get("x-meta")
            encoded_string = response.cookies.get("x-meta")
            decoded_string = urllib.parse.unquote(encoded_string)
            client_id = json.loads(decoded_string).get("authentication.aaa.epaid")

            self.accelus_connect_sid = accelus_connect_sid
            self.x_meta = x_meta
            self.client_id = client_id

            return {
                "success": True,
                "data":{
                    "accelus.connect.sid": accelus_connect_sid,
                    "x-meta": x_meta,
                    "client-id": client_id
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }
    

    def authorization_oauth2(self):
        cookies = {
            # 'idfirstadapter.previous.subjects': 'dmluY2VudHpodUBjc2NpLmhr',
            # 'PF': '5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://risk.lseg.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            # 'cookie': 'idfirstadapter.previous.subjects=dmluY2VudHpodUBjc2NpLmhr; PF=5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
        }

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'trapi openid profile email',
            # 'state': 'd0ac323c-8aa1-45de-b286-1aa5afbe8e50',
            'state': self.state, 
            'redirect_uri': 'https://risk.lseg.com/authpinglseg',
        }

        response = requests.get(
            'https://login.ciam.refinitiv.com/as/authorization.oauth2',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        func_name = inspect.stack()[0][3]
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            
            PF = response.cookies.get("PF")

            soup = BeautifulSoup(response.text)
            action_chain = soup.find("form").get("action")

            self.PF = PF
            self.action_chain = action_chain

            return {
                "success": True,
                "data":{
                    "PF": PF,
                    "action_chain": action_chain
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

       
    def authorization_ping_pre(self):
        cookies = {
            # 'idfirstadapter.previous.subjects': 'dmluY2VudHpodUBjc2NpLmhr',
            # 'PF': '5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
            'PF': self.PF
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://login.ciam.refinitiv.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://login.ciam.refinitiv.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            # 'cookie': 'idfirstadapter.previous.subjects=dmluY2VudHpodUBjc2NpLmhr; PF=5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
        }

        data = {
            'subject': self.username,
            'clear.previous.selected.subject': '',
            'cancel.identifier.selection': 'false',
        }

        response = requests.post(
            'https://login.ciam.refinitiv.com' + self.action_chain,
            cookies=cookies,
            headers=headers,
            data=data,
        )
    
    def authorization_ping(self):
        cookies = {
            # 'idfirstadapter.previous.subjects': 'dmluY2VudHpodUBjc2NpLmhr',
            # 'PF': '5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
            'PF': self.PF
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://login.ciam.refinitiv.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://login.ciam.refinitiv.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            # 'cookie': 'idfirstadapter.previous.subjects=dmluY2VudHpodUBjc2NpLmhr; PF=5iimIC7NmBV8xPpJtLje2W3pO9AdA76IxUIuQRtd4cp8',
        }

        data = {
            'pf.ok': 'clicked',
            'pf.cancel': '',
            'pf.passwordreset': '',
            'pf.usernamerecovery': '',
            'pf.username': self.username,
            'pf.pass': self.password,
            'pf.adapterId': 'formadapter',
        }

        response = requests.post(
            'https://login.ciam.refinitiv.com' + self.action_chain,
            cookies=cookies,
            headers=headers,
            data=data,
            allow_redirects=False
        )
        func_name = inspect.stack()[0][3]
        if response.status_code == 302:
            print(f"{func_name} success with status code = {response.status_code}.")
            
            location = response.headers.get("Location")
            parsed_url = urlparse(location)
            query_params = dict(parse_qsl(parsed_url.query))
            signontoken = query_params.get("code")

            self.signontoken = signontoken

            return {
                "success": True,
                "data":{
                    "signontoken": signontoken,
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }


    def risk_lseg_com_after(self):

        cookies = {
            # 'x-meta': '%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D',
            'x-meta': self.x_meta,
            # 'x-vsession-last-login': '1750840358200',
            # 'at_check': 'true',
            # 's_fid': '4C011F4B69F6C10C-2CC6BE013084AD0A',
            # 'OptanonAlertBoxClosed': '2025-06-25T08:36:03.515Z',
            # 'LC_PAGE_VISIT_HISTORY': '%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D',
            # 'LC_LAST_VISITED_REFERRER': 'https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one',
            # 'x-vsession-last-active': '1750840596067',
            # 'accelus.connect.sid': 's%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE',
            'accelus.connect.sid': self.accelus_connect_sid,
            # '_gcl_au': '1.1.646319424.1750853672',
            # 'mbox': 'PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533',
            # '_uetsid': '9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002',
            # 'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false',
            # '_uetvid': '9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v',
            # '_ga': 'GA1.1.1137008475.1750853674',
            # 's_plt': '%5B%5BB%5D%5D',
            # 's_pltp': '%5B%5BB%5D%5D',
            # 's_cc': 'true',
            # '_ga_1J3ZS1VERY': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_L5R01EES25': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_ZKKCDJR7BE': 'GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_DGKRWS7656': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            'x-auth-redirect': 'false',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            # 'referer': 'https://risk.lseg.com/?code=3XcP0dR3vsM4O8m3-gjnp-Jr547hNs_vJ8cs40uO&state=d0ac323c-8aa1-45de-b286-1aa5afbe8e50&authProvider=PING&authRedirectTarget=LSEG',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D; x-vsession-last-login=1750840358200; at_check=true; s_fid=4C011F4B69F6C10C-2CC6BE013084AD0A; OptanonAlertBoxClosed=2025-06-25T08:36:03.515Z; LC_PAGE_VISIT_HISTORY=%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D; LC_LAST_VISITED_REFERRER=https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one; x-vsession-last-active=1750840596067; accelus.connect.sid=s%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE; _gcl_au=1.1.646319424.1750853672; mbox=PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533; _uetsid=9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; _uetvid=9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v; _ga=GA1.1.1137008475.1750853674; s_plt=%5B%5BB%5D%5D; s_pltp=%5B%5BB%5D%5D; s_cc=true; _ga_1J3ZS1VERY=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_L5R01EES25=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_ZKKCDJR7BE=GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0; _ga_DGKRWS7656=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; x-auth-redirect=false',
        }

        response = requests.get('https://risk.lseg.com/', cookies=cookies, headers=headers)

        func_name = inspect.stack()[0][3]
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            
            soup = BeautifulSoup(response.text)
            csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

            self.csrf_token = csrf_token

            return {
                "success": True,
                "data":{
                    "csrf_token": csrf_token,
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }


    def login(self):
        cookies = {
            # 'x-meta': '%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D',
            'x-meta': self.x_meta, 
            # 'x-vsession-last-login': '1750840358200',
            # 'at_check': 'true',
            # 's_fid': '4C011F4B69F6C10C-2CC6BE013084AD0A',
            # 'OptanonAlertBoxClosed': '2025-06-25T08:36:03.515Z',
            # 'LC_PAGE_VISIT_HISTORY': '%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D',
            # 'LC_LAST_VISITED_REFERRER': 'https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one',
            # 'x-vsession-last-active': '1750840596067',
            # 'accelus.connect.sid': 's%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE',
            'accelus.connect.sid': self.accelus_connect_sid,
            # '_gcl_au': '1.1.646319424.1750853672',
            # 'mbox': 'PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533',
            # '_uetsid': '9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002',
            # 'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false',
            # '_uetvid': '9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v',
            # '_ga': 'GA1.1.1137008475.1750853674',
            # 's_plt': '%5B%5BB%5D%5D',
            # 's_pltp': '%5B%5BB%5D%5D',
            # 's_cc': 'true',
            # '_ga_1J3ZS1VERY': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_L5R01EES25': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_ZKKCDJR7BE': 'GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0',
            # '_ga_DGKRWS7656': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
            'x-auth-redirect': 'true',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'csrf-token': 'olNjUEw6-Mv021gta2D-9-k9JwcCiC7azLhU',
            'csrf-token': self.csrf_token,
            'origin': 'https://risk.lseg.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://risk.lseg.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D; x-vsession-last-login=1750840358200; at_check=true; s_fid=4C011F4B69F6C10C-2CC6BE013084AD0A; OptanonAlertBoxClosed=2025-06-25T08:36:03.515Z; LC_PAGE_VISIT_HISTORY=%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D; LC_LAST_VISITED_REFERRER=https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one; x-vsession-last-active=1750840596067; accelus.connect.sid=s%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE; _gcl_au=1.1.646319424.1750853672; mbox=PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533; _uetsid=9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; _uetvid=9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v; _ga=GA1.1.1137008475.1750853674; s_plt=%5B%5BB%5D%5D; s_pltp=%5B%5BB%5D%5D; s_cc=true; _ga_1J3ZS1VERY=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_L5R01EES25=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_ZKKCDJR7BE=GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0; _ga_DGKRWS7656=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; x-auth-redirect=true',
        }

        json_data = {
            # 'signontoken': '3XcP0dR3vsM4O8m3-gjnp-Jr547hNs_vJ8cs40uO',
            'signontoken': self.signontoken,
            'authProvider': 'PING',
            'authRedirectTarget': 'LSEG',
        }

        response = requests.post('https://risk.lseg.com/v1/auth/login', cookies=cookies, headers=headers, json=json_data)

        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            transfer_token = response.json().get("apps")[0].get("transferToken")

            self.transfer_token = transfer_token

            return {
                "success": True,
                "data":{
                    "transfer_token": transfer_token
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }


    
    
    # def load_login_page(self, )->dict:
    #     func_name = inspect.stack()[0][3]
    #     headers = {
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #         'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #         'priority': 'u=0, i',
    #         'referer': 'https://www.google.com/',
    #         'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'cross-site',
    #         'sec-fetch-user': '?1',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    #     }

    #     response = requests.get('https://worldcheck.refinitiv.com/', headers=headers)

    #     if response.status_code == 200:
    #         print(f"{func_name} success with status code = {response.status_code}.")
    #         soup = BeautifulSoup(response.text)
    #         csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
    #         accelus_connect_sid = response.cookies.get("accelus.connect.sid")
    #         x_meta = response.cookies.get("x-meta")
    #         encoded_string = response.cookies.get("x-meta")
    #         decoded_string = urllib.parse.unquote(encoded_string)
    #         client_id = json.loads(decoded_string).get("authentication.aaa.epaid")

    #         self.csrf_token = csrf_token
    #         self.accelus_connect_sid = accelus_connect_sid
    #         self.x_meta = x_meta
    #         self.client_id = client_id

    #         return {
    #             "success": True,
    #             "data":{
    #                 "csrf-token": csrf_token,
    #                 "accelus.connect.sid": accelus_connect_sid,
    #                 "x-meta": x_meta,
    #                 "client-id": client_id
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }

    # def risk_lseg_com_pre(self)->dict:
        



    # def authorization_oauth(self)->dict:
    #     # headers = {
    #     #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     #     'accept-language': 'zh-CN,zh;q=0.9',
    #     #     'priority': 'u=0, i',
    #     #     'referer': 'https://worldcheck.refinitiv.com/',
    #     #     'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    #     #     'sec-ch-ua-mobile': '?0',
    #     #     'sec-ch-ua-platform': '"macOS"',
    #     #     'sec-fetch-dest': 'document',
    #     #     'sec-fetch-mode': 'navigate',
    #     #     'sec-fetch-site': 'same-site',
    #     #     'upgrade-insecure-requests': '1',
    #     #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    #     # }

    #     # params = {
    #     #     'client_id': self.client_id,
    #     #     'response_type': 'code',
    #     #     'scope': 'trapi openid profile email',
    #     #     'state': self.state,
    #     #     'redirect_uri': 'https://worldcheck.refinitiv.com/authping',
    #     # }
    #     # response = requests.get('https://login.ciam.refinitiv.com/as/authorization.oauth2', params=params, headers=headers)
    #     headers = {
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'pragma': 'no-cache',
    #         'priority': 'u=0, i',
    #         'referer': 'https://worldcheck.refinitiv.com/',
    #         'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'same-site',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    #     }

    #     params = {
    #         'client_id': self.client_id,
    #         'response_type': 'code',
    #         'scope': 'trapi openid profile email',
    #         'state': self.state,
    #         'redirect_uri': 'https://worldcheck.refinitiv.com/authping',
    #     }

    #     response = requests.get('https://login.ciam.refinitiv.com/as/authorization.oauth2', params=params, headers=headers)


    #     func_name = inspect.stack()[0][3]
    #     if response.status_code == 200:
    #         print(f"{func_name} success with status code = {response.status_code}.")
    #         soup = BeautifulSoup(response.text)
    #         action_chain = soup.find("form").get("action")
    #         PF = response.cookies.get("PF")

    #         self.action_chain = action_chain
    #         self.PF = PF

    #         print({
    #             "success": True,
    #             "data":{
    #                 "action_chain": action_chain,
    #                 "PF": PF
    #             }
    #         })

    #         return {
    #             "success": True,
    #             "data":{
    #                 "action_chain": action_chain,
    #                 "PF": PF
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }
        
    # def authorization_ping_pre(self)->dict:
    #     cookies = {
    #         'PF': self.PF,
    #     }

    #     headers = {
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'content-type': 'application/x-www-form-urlencoded',
    #         'origin': 'https://login.ciam.refinitiv.com',
    #         'pragma': 'no-cache',
    #         'priority': 'u=0, i',
    #         'referer': 'https://login.ciam.refinitiv.com/',
    #         'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'same-origin',
    #         'sec-fetch-user': '?1',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    #         # 'cookie': 'PF=ZkWxmQmxy7AGiZmHBlCRM2',
    #     }

    #     data = {
    #         'subject': self.username,
    #         'clear.previous.selected.subject': '',
    #         'cancel.identifier.selection': 'false',
    #     }

    #     response = requests.post(
    #         f'https://login.ciam.refinitiv.com{self.action_chain}',
    #         cookies=cookies,
    #         headers=headers,
    #         data=data,
    #         allow_redirects=False
    #     )

    #     # print(response.text)

    #     func_name = inspect.stack()[0][3]

    #     if response.status_code == 200:
    #         print(f"{func_name} success with status code = {response.status_code}.")

    #         return {
    #             "success": True,
    #             "data":{
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }


    # def authorization_ping(self)->dict:
    #     cookies = {
    #         'PF': self.PF,
    #         # 'pf-accept-language': 'zh',
    #     }

    #     headers = {
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'content-type': 'application/x-www-form-urlencoded',
    #         'origin': 'https://login.ciam.refinitiv.com',
    #         'pragma': 'no-cache',
    #         'priority': 'u=0, i',
    #         'referer': 'https://login.ciam.refinitiv.com/',
    #         'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'same-origin',
    #         'sec-fetch-user': '?1',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    #         # 'cookie': 'PF=ZkWxmQmxy7AGiZmHBlCRM2',
    #     }

    #     data = {
    #         'pf.ok': 'clicked',
    #         'pf.cancel': '',
    #         'pf.passwordreset': '',
    #         'pf.usernamerecovery': '',
    #         'pf.username': self.username,
    #         'pf.pass': self.password,
    #         'pf.adapterId': 'formadapter',
    #     }

    #     response = requests.post(
    #         f'https://login.ciam.refinitiv.com{self.action_chain}',
    #         cookies=cookies,
    #         headers=headers,
    #         data=data,
    #         allow_redirects=False
    #     )
    #     func_name = inspect.stack()[0][3]

    #     # print(f'https://login.ciam.refinitiv.com{self.action_chain}')

    #     # print(response.headers)

    #     if response.status_code == 302:
    #         print(f"{func_name} success with status code = {response.status_code}.")
    #         location = response.headers.get("Location")
    #         parsed_url = urlparse(location)
    #         query_params = dict(parse_qsl(parsed_url.query))
    #         signontoken = query_params.get("code")

    #         self.signontoken = signontoken

    #         return {
    #             "success": True,
    #             "data":{
    #                 "signontoken": signontoken,
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }




    # def risk_lseg_com(self)->dict:
    #     # cookies = {
    #     #     'x-meta': '%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D',
    #     #     'x-vsession-last-active': '',
    #     #     'x-vsession-last-login': '',
    #     #     'at_check': 'true',
    #     #     # 'mbox': 'session#a52763cfff894c908691153c94a0bf5c#1750836730|PC#a52763cfff894c908691153c94a0bf5c.38_0#1814079670',
    #     #     # 'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jun+25+2025+15%3A01%3A10+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a3f9c2de-8cc5-4fc7-9dab-e3f6398638b8&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fwww.lseg.com%2Fen%2Ftraining%2Flearning-centre%2Flearning-paths%2Flearning-path-for-risk-and-compliance%2Flearn-lseg-world-check-one&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1',
    #     #     # 's_cc': 'true',
    #     #     'accelus.connect.sid': 's%3A9Zwaq4UVlCTmymuuuzG03LUUgN292dFF.2GFHgJogR%2FkouzNn2cVFlp%2FJYBQZebPyH8znH2N7byM',
    #     #     'x-auth-redirect': 'false',
    #     # }
    #     cookies = {
    #         'x-meta': self.x_meta,
    #         'accelus.connect.sid': self.accelus_connect_sid,
    #         'x-auth-redirect': 'true',
    #     }

    #     headers = {
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'pragma': 'no-cache',
    #         'priority': 'u=0, i',
    #         'referer': 'https://risk.lseg.com/?code=oXVf8UruZr31T7Gf3pCsPbc_5ZNISyDgmGcZvOuU&state=4f28a848-4a1b-4ef7-8a8b-fccbb5920074&authProvider=PING&authRedirectTarget=LSEG',
    #         'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'same-origin',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    #         # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D; x-vsession-last-active=; x-vsession-last-login=; at_check=true; mbox=session#a52763cfff894c908691153c94a0bf5c#1750836730|PC#a52763cfff894c908691153c94a0bf5c.38_0#1814079670; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+25+2025+15%3A01%3A10+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a3f9c2de-8cc5-4fc7-9dab-e3f6398638b8&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fwww.lseg.com%2Fen%2Ftraining%2Flearning-centre%2Flearning-paths%2Flearning-path-for-risk-and-compliance%2Flearn-lseg-world-check-one&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; s_cc=true; accelus.connect.sid=s%3A9Zwaq4UVlCTmymuuuzG03LUUgN292dFF.2GFHgJogR%2FkouzNn2cVFlp%2FJYBQZebPyH8znH2N7byM; x-auth-redirect=false',
    #     }

    #     response = requests.get('https://risk.lseg.com/', cookies=cookies, headers=headers)
    #     func_name = inspect.stack()[0][3]

    #     if response.status_code == 200:
    #         print(f"{func_name} success with status code = {response.status_code}.")
    #         soup = BeautifulSoup(response.text)
    #         csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]


    #         self.csrf_token = csrf_token

    #         return {
    #             "success": True,
    #             "data":{
    #                 "csrf-token": csrf_token,
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }






























    # def login(self)->dict:

    #     cookies = {
    #         'x-meta': self.x_meta,
    #         # 'x-meta': '%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D',
    #         # 'x-vsession-last-login': '1750840358200',
    #         # 'at_check': 'true',
    #         # 's_fid': '4C011F4B69F6C10C-2CC6BE013084AD0A',
    #         # 'OptanonAlertBoxClosed': '2025-06-25T08:36:03.515Z',
    #         # 'LC_PAGE_VISIT_HISTORY': '%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D',
    #         # 'LC_LAST_VISITED_REFERRER': 'https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one',
    #         # 'x-vsession-last-active': '1750840596067',
    #         # 'accelus.connect.sid': 's%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE',
    #         'accelus.connect.sid': self.accelus_connect_sid,
    #         # '_gcl_au': '1.1.646319424.1750853672',
    #         # 'mbox': 'PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533',
    #         # '_uetsid': '9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002',
    #         # 'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false',
    #         # '_uetvid': '9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v',
    #         # '_ga': 'GA1.1.1137008475.1750853674',
    #         # 's_plt': '%5B%5BB%5D%5D',
    #         # 's_pltp': '%5B%5BB%5D%5D',
    #         # 's_cc': 'true',
    #         # '_ga_1J3ZS1VERY': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
    #         # '_ga_L5R01EES25': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
    #         # '_ga_ZKKCDJR7BE': 'GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0',
    #         # '_ga_DGKRWS7656': 'GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0',
    #         'x-auth-redirect': 'true',
    #     }

    #     headers = {
    #         'accept': '*/*',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'content-type': 'application/json',
    #         'csrf-token': self.csrf_token, # 来自risk_lseg_com
    #         # 'csrf-token': 'olNjUEw6-Mv021gta2D-9-k9JwcCiC7azLhU',
    #         'origin': 'https://risk.lseg.com',
    #         'pragma': 'no-cache',
    #         'priority': 'u=1, i',
    #         'referer': 'https://risk.lseg.com/',
    #         'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"macOS"',
    #         'sec-fetch-dest': 'empty',
    #         'sec-fetch-mode': 'cors',
    #         'sec-fetch-site': 'same-origin',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    #         'x-requested-with': 'XMLHttpRequest',
    #         # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22aaa.accelus.lseg.host%22%3A%22risk.lseg.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22redirect.lseg.uri.ping%22%3A%22https%3A%2F%2Frisk.lseg.com%2Fauthpinglseg%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%2C%22vue.userPreferencesPage.redesign.enabled%22%3A%22true%22%7D; x-vsession-last-login=1750840358200; at_check=true; s_fid=4C011F4B69F6C10C-2CC6BE013084AD0A; OptanonAlertBoxClosed=2025-06-25T08:36:03.515Z; LC_PAGE_VISIT_HISTORY=%5B%22https%3A//www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one%22%5D; LC_LAST_VISITED_REFERRER=https://www.lseg.com/en/training/learning-centre/learning-paths/learning-path-for-risk-and-compliance/learn-lseg-world-check-one; x-vsession-last-active=1750840596067; accelus.connect.sid=s%3A4g6c89IN9C36fq1Y5yC3vv1YBg1QvdYY.CKGHfw2OYW3q1qhUrUipj8cel6Wrg%2FDwTLlm8LNpClE; _gcl_au=1.1.646319424.1750853672; mbox=PC#9a4f232372c74534bc012b0493a914b8.38_0#1814098473|session#c39af5196a4446bd904e3fb0fbf38bdd#1750855533; _uetsid=9da5af60519e11f0a5773326913e9dae|1q6hcpv|2|fx2|0|2002; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+25+2025+20%3A14%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=040caf7f-faac-4984-811e-d0c337bb40ac&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; _uetvid=9da5d200519e11f0a191bd0c1cc7650e|1xzx2xp|1750853673956|1|1|bat.bing-int.com/p/conversions/c/v; _ga=GA1.1.1137008475.1750853674; s_plt=%5B%5BB%5D%5D; s_pltp=%5B%5BB%5D%5D; s_cc=true; _ga_1J3ZS1VERY=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_L5R01EES25=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; _ga_ZKKCDJR7BE=GS2.1.s1750853674$o1$g0$t1750853772$j60$l0$h0; _ga_DGKRWS7656=GS2.1.s1750853772$o1$g0$t1750853772$j60$l0$h0; x-auth-redirect=true',
    #     }

    #     json_data = {
    #         # 'signontoken': '3XcP0dR3vsM4O8m3-gjnp-Jr547hNs_vJ8cs40uO',
    #         'signontoken': self.signontoken,
    #         'authProvider': 'PING',
    #         'authRedirectTarget': 'LSEG',
    #     }

    #     response = requests.post('https://risk.lseg.com/v1/auth/login', cookies=cookies, headers=headers, json=json_data, verify = False)

    #     # # Note: json_data will not be serialized by requests
    #     # # exactly as it was in the original request.
    #     # #data = '{"signontoken":"3XcP0dR3vsM4O8m3-gjnp-Jr547hNs_vJ8cs40uO","authProvider":"PING","authRedirectTarget":"LSEG"}'
    #     # #response = requests.post('https://risk.lseg.com/v1/auth/login', cookies=cookies, headers=headers, data=data)
    #     # cookies = {
    #     #     'x-meta': self.x_meta,
    #     #     'accelus.connect.sid': self.accelus_connect_sid,
    #     #     'x-auth-redirect': 'true',
    #     # }

    #     # headers = {
    #     #     'accept': '*/*',
    #     #     'accept-language': 'zh-CN,zh;q=0.9',
    #     #     'content-type': 'application/json',
    #     #     # 'cookie': 'x-meta=%7B%22aaa.login.sts.new.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22aaa.login.sts.old.referer%22%3A%22identity.ciam.refinitiv.net%22%2C%22authentication.loginRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%3FTargetResource%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.sts_new_rehoming%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2Flogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22authentication.logoutRedirectPath.ping%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fidp%2FstartSLO.ping%22%2C%22authentication.logoutRedirectPath.alternative%22%3A%22https%3A%2F%2Fwww.refinitiv.com%2Fen%2Flearning-centre%2Flearning-paths%2Flearning-paths-for-risk-and-compliance%2Flearn-refinitiv-world-check-one%22%2C%22authentication.logoutRedirectPath.sts_old%22%3A%22https%3A%2F%2Fidentity.ciam.refinitiv.net%2Fauth%2FUI%2FLogout%3Fnocache%3D%7BnoCache%7D%26locale%3Den-US%26product%3Dcustom%26epaid%3D%7BauthenticationAaaEpaid%7D%26producthome%3Dhttps%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22redirect.uri%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%22%2C%22session.maxage%22%3A%221800000%22%2C%22authentication.onepass.url%22%3A%22https%3A%2F%2Fsignon.thomsonreuters.com%22%2C%22onepass.product.code%22%3A%22MKTACC%22%2C%22session.expiry.warning%22%3A%22300000%22%2C%22authentication.aaa.url%22%3A%22https%3A%2F%2Fsts.identity.ciam.refinitiv.net%2Foauth2%2Fv1%2Fauthorize%22%2C%22authentication.aaa.epaid%22%3A%2255199a53d1804dcbb43f65c03b5085f1cf3b1c0b%22%2C%22authentication.aaa.scope%22%3A%22trapi%22%2C%22aaa.accelus.host%22%3A%22worldcheck.refinitiv.com%22%2C%22app.prompt.timeout%22%3A%22810000%22%2C%22tr.redirect.enabled%22%3A%22true%22%2C%22tr.redirect.productcodes%22%3A%22ri%2Codis%22%2C%22tr.redirect.url%22%3A%22https%3A%2F%2Fregintel.thomsonreuters.com%22%2C%22redirect.uri.ping%22%3A%22https%3A%2F%2Fworldcheck.refinitiv.com%2Fauthping%22%2C%22authentication.aaa.ping.url%22%3A%22https%3A%2F%2Flogin.ciam.refinitiv.com%2Fas%2Fauthorization.oauth2%22%2C%22authentication.stsping.pingByDefault%22%3A%22true%22%2C%22authentication.aaa.ping.scope%22%3A%22trapi%20openid%20profile%20email%22%2C%22vue.login.regkeyselection.redesign.enabled%22%3A%22true%22%2C%22accelus.login.showUserInfoFromFsp.enable%22%3A%22true%22%7D; accelus.connect.sid=s%3ABP_FkqNrZ_OHzMbXAwrQZl5Sa3fHejfO.wuyChvuWpJv2bU1wnQcynZJ3WoiHHjO2TAiiK%2B1hd8E; x-auth-redirect=true',
    #     #     'csrf-token': self.csrf_token,
    #     #     'origin': 'https://worldcheck.refinitiv.com',
    #     #     'priority': 'u=1, i',
    #     #     'referer': 'https://worldcheck.refinitiv.com/',
    #     #     'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    #     #     'sec-ch-ua-mobile': '?0',
    #     #     'sec-ch-ua-platform': '"macOS"',
    #     #     'sec-fetch-dest': 'empty',
    #     #     'sec-fetch-mode': 'cors',
    #     #     'sec-fetch-site': 'same-origin',
    #     #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    #     #     'x-requested-with': 'XMLHttpRequest',
    #     # }

    #     # json_data = {
    #     #     'signontoken': self.signontoken,
    #     #     'authRedirectTarget' : "LSEG",
    #     #     'authProvider': 'PING',
    #     # }

    #     # response = requests.post('https://worldcheck.refinitiv.com/v1/auth/login', cookies=cookies, headers=headers, json=json_data, verify=False)



    #     func_name = inspect.stack()[0][3]    
    #     if response.status_code == 200:
    #         print(f"{func_name} success with status code = {response.status_code}.")
    #         transfer_token = response.json().get("apps")[0].get("transferToken")

    #         self.transfer_token = transfer_token

    #         return {
    #             "success": True,
    #             "data":{
    #                 "transfer_token": transfer_token
    #             }
    #         }
    #     else:
    #         print(f"{func_name} fail with status code = {response.status_code}.")
    #         self.SUCCESS = False
    #         return {
    #             "success": False,
    #             "data":{}
    #         }

    def session(self)->dict:
        cookies = {
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'AWSALB=U8gGs2W2g/ADOpOLl1H59NJGWVt7W9+0LDL7It4vHotlEB2zcsJVPJBmehYNTXhMz5tEW2/S6zc6hHUXrDTA3JYT7gatZ1wBB6zHafpOJ0aQzJRNgFuIpSE2DPeI; AWSALBCORS=U8gGs2W2g/ADOpOLl1H59NJGWVt7W9+0LDL7It4vHotlEB2zcsJVPJBmehYNTXhMz5tEW2/S6zc6hHUXrDTA3JYT7gatZ1wBB6zHafpOJ0aQzJRNgFuIpSE2DPeI',
            'csrf-token': '{csrfToken}',
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/api.html?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'transferToken': self.transfer_token,
        }

        response = requests.post(
            'https://wc1-worldcheck.refinitiv.com/fsp/auth/v1/session',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            connect_sid = response.cookies.get("connect.sid")

            self.connect_sid = connect_sid

            return {
                "success": True,
                "data":{
                    "connect_sid": connect_sid
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def current_locale_en_GB(self)->dict:
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'CksL66DiZvHFj26LykwEk89KWTdbrXDBz3zTwp2VB76bJxoapRuKQ0YxQoDRQMjbHyxBuJzAxpicEdaTJ3N1ML6D7Dfo+FYaYBAMIfOVtJXauCxJlWmly2DpsKMn',
            # 'AWSALBCORS': 'CksL66DiZvHFj26LykwEk89KWTdbrXDBz3zTwp2VB76bJxoapRuKQ0YxQoDRQMjbHyxBuJzAxpicEdaTJ3N1ML6D7Dfo+FYaYBAMIfOVtJXauCxJlWmly2DpsKMn',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': 'connect.sid=s%3AiTKWmu6lc_czFkUQoqol0KF-4BzIdXqM.BiPkcqKNzSgZv8Dbwe028ms4A39t7kWPTAq7h1HhV%2B8; AWSALB=CksL66DiZvHFj26LykwEk89KWTdbrXDBz3zTwp2VB76bJxoapRuKQ0YxQoDRQMjbHyxBuJzAxpicEdaTJ3N1ML6D7Dfo+FYaYBAMIfOVtJXauCxJlWmly2DpsKMn; AWSALBCORS=CksL66DiZvHFj26LykwEk89KWTdbrXDBz3zTwp2VB76bJxoapRuKQ0YxQoDRQMjbHyxBuJzAxpicEdaTJ3N1ML6D7Dfo+FYaYBAMIfOVtJXauCxJlWmly2DpsKMn',
            'priority': 'u=0, i',
            'referer': 'https://worldcheck.refinitiv.com/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        params = {
            'locale': 'en-GB',
        }

        response = requests.get('https://wc1-worldcheck.refinitiv.com/current/', params=params, cookies=cookies, headers=headers)
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            soup = BeautifulSoup(response.text)
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"}).get("content")

            self.csrf_token = csrf_token

            return {
                "success": True,
                "data":{
                    "csrf_token": csrf_token
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def features(self):
        cookies = {
        # 'AWSALB': 'RILVrEvnhwMwkVNa2wEN4YMWwwNOMBxWD94twQ4Z2Ik8OPi6xn5qtnib0EefEIUTnKSQ2hImnrJZ3Evq+JTJrtbVS/0qqCLk9nssuwJit1ClKPuHBAB1TjKMNmwW',
        # 'AWSALBCORS': 'RILVrEvnhwMwkVNa2wEN4YMWwwNOMBxWD94twQ4Z2Ik8OPi6xn5qtnib0EefEIUTnKSQ2hImnrJZ3Evq+JTJrtbVS/0qqCLk9nssuwJit1ClKPuHBAB1TjKMNmwW',
            'connect.sid': self.connect_sid,
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'AWSALB=RILVrEvnhwMwkVNa2wEN4YMWwwNOMBxWD94twQ4Z2Ik8OPi6xn5qtnib0EefEIUTnKSQ2hImnrJZ3Evq+JTJrtbVS/0qqCLk9nssuwJit1ClKPuHBAB1TjKMNmwW; AWSALBCORS=RILVrEvnhwMwkVNa2wEN4YMWwwNOMBxWD94twQ4Z2Ik8OPi6xn5qtnib0EefEIUTnKSQ2hImnrJZ3Evq+JTJrtbVS/0qqCLk9nssuwJit1ClKPuHBAB1TjKMNmwW; connect.sid=s%3A3DnqijezOuzdIHn-EFTUkmovEycICzhh.VQzhzbTe7WqZWDdzRkNiw1fkST5FmEwB3FvTbaAcaXU',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/api.html?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = requests.get('https://wc1-worldcheck.refinitiv.com/fsp/ums/v1/features', cookies=cookies, headers=headers)

        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            groupId = response.json().get("clientId")

            self.groupId = groupId

            return {
                "success": True,
                "data":{
                    "groupId": groupId
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }
        
    def config(self)->dict:
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'PMe2Y+pgqcpNgW8aZc/Z8eVm7Yqs4zuPKYbJDx6tXJA8zmVGxf4ZfTlZSmsv5L38epqLYjh3t23HmI2FjIZ6vfUGKFylASrMfVmvtBJD90Yy92q0GA32q7JrS9Gv',
            # 'AWSALBCORS': 'PMe2Y+pgqcpNgW8aZc/Z8eVm7Yqs4zuPKYbJDx6tXJA8zmVGxf4ZfTlZSmsv5L38epqLYjh3t23HmI2FjIZ6vfUGKFylASrMfVmvtBJD90Yy92q0GA32q7JrS9Gv',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'connect.sid=s%3AXB9YPHVywDr_OjiWKCm8LNVM_ViYXeor.tDWUSIQ9ZSzU6Bgc0yxRZCdiV1Aq8Ax22fYZ13jvYWY; AWSALB=PMe2Y+pgqcpNgW8aZc/Z8eVm7Yqs4zuPKYbJDx6tXJA8zmVGxf4ZfTlZSmsv5L38epqLYjh3t23HmI2FjIZ6vfUGKFylASrMfVmvtBJD90Yy92q0GA32q7JrS9Gv; AWSALBCORS=PMe2Y+pgqcpNgW8aZc/Z8eVm7Yqs4zuPKYbJDx6tXJA8zmVGxf4ZfTlZSmsv5L38epqLYjh3t23HmI2FjIZ6vfUGKFylASrMfVmvtBJD90Yy92q0GA32q7JrS9Gv',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = requests.get(
            f'https://wc1-worldcheck.refinitiv.com/fsp/ums/v1/group/{self.groupId}/config',
            cookies=cookies,
            headers=headers,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            configs = response.json()
            self.configs = configs
            return {
                "success": True,
                "data":{
                    "configs": configs
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }
    
    def save(self, keyword:str, entityType = "ORGANISATION"):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': AWSALB,
            # 'AWSALBCORS': AWSALBCORS,
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3AiTKWmu6lc_czFkUQoqol0KF-4BzIdXqM.BiPkcqKNzSgZv8Dbwe028ms4A39t7kWPTAq7h1HhV%2B8; AWSALB=DESNgZLQYzLhxWUrG+ltmRp+NI3r/KCdvHnQ1jVZPYFe5poDt8r3bPzhXz1Sw5Po4AnF5atpJijFxrnERPc4yBDKrv91AspEuPf5ShTXjQ1IFlZKSvb7O21ta0CL; AWSALBCORS=DESNgZLQYzLhxWUrG+ltmRp+NI3r/KCdvHnQ1jVZPYFe5poDt8r3bPzhXz1Sw5Po4AnF5atpJijFxrnERPc4yBDKrv91AspEuPf5ShTXjQ1IFlZKSvb7O21ta0CL',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'groupId': self.groupId,
            'entityTypes': [
                entityType, 
            ],
            'providerTypes': [
                'WATCHLIST',
                'MEDIA_CHECK',
            ],
            'clientCaseId': '',
            'nameTransposition': False,
            'caseScreeningState': 'INITIAL',
            'names': [
                {
                    'typeId': 'PRIMARY',
                    'value': keyword,
                },
            ],
        }

        response = requests.post(
            'https://wc1-worldcheck.refinitiv.com/fsp/case/v1/case/save',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            caseId = response.json().get('caseId')

            self.caseId = caseId

            return {
                "success": True,
                "data":{
                    "caseId": caseId
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def screen(self):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'JKH/JlTkw6cUDWOG+z0XjSvNqINrAEi8qKXgVgtyPajO61kDav2Ctdy2wdU46NyJ5LOoulyT15WWKkf2I0s3RchC/5EzX6QIpeU3jah37lZpm2ztvoWnf4KK/pyI',
            # 'AWSALBCORS': 'JKH/JlTkw6cUDWOG+z0XjSvNqINrAEi8qKXgVgtyPajO61kDav2Ctdy2wdU46NyJ5LOoulyT15WWKkf2I0s3RchC/5EzX6QIpeU3jah37lZpm2ztvoWnf4KK/pyI',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3Ay7o06YwqYDxUM960cW1dEcwe_DXRqEem.CoQe8A9nELoDZwrs6Vplra%2F6aZ4Om7qtbfiFabivpPI; AWSALB=JKH/JlTkw6cUDWOG+z0XjSvNqINrAEi8qKXgVgtyPajO61kDav2Ctdy2wdU46NyJ5LOoulyT15WWKkf2I0s3RchC/5EzX6QIpeU3jah37lZpm2ztvoWnf4KK/pyI; AWSALBCORS=JKH/JlTkw6cUDWOG+z0XjSvNqINrAEi8qKXgVgtyPajO61kDav2Ctdy2wdU46NyJ5LOoulyT15WWKkf2I0s3RchC/5EzX6QIpeU3jah37lZpm2ztvoWnf4KK/pyI',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {}

        response = requests.put(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v1/case/{self.caseId}/screen',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            return {
                "success": True,
                "data":{
                    "screen_result_json": response.json()
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def summary(self):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': AWSALB,
            # 'AWSALBCORS': AWSALBCORS,
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'connect.sid=s%3AiTKWmu6lc_czFkUQoqol0KF-4BzIdXqM.BiPkcqKNzSgZv8Dbwe028ms4A39t7kWPTAq7h1HhV%2B8; AWSALB=3DFzPkjPfty77vDpYuyboKuS9k7ZWeSjvZWiCkbkYNP7waTfLtksnCKJSGENXiBSHq5N5nCzNZLqsg8NjCbrdB5P+/u8UC+g13x9xs6YRkfk2ZON62Uh2WxwZMwc; AWSALBCORS=3DFzPkjPfty77vDpYuyboKuS9k7ZWeSjvZWiCkbkYNP7waTfLtksnCKJSGENXiBSHq5N5nCzNZLqsg8NjCbrdB5P+/u8UC+g13x9xs6YRkfk2ZON62Uh2WxwZMwc',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = requests.get(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v1/case/{self.caseId}/summary',
            cookies=cookies,
            headers=headers,
        )
        string = response.headers.get("Set-Cookie")
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            summary_result_json = response.json()

            self.summary_result_json = summary_result_json

            return {
                "success": True,
                "data":{
                    "summary_result_json": summary_result_json,
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def watchlist(self):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'llFwyk7SkkMA4vBzvieFkO4O2uk6zlWqyeJSlSGAXebEh6ajPHvKfsOROc4FU9iajj7/YVCbQWqAPfPMa0GvR+ugFf785pSrViVn3r0TJ9KdtzEC5knf2sOAla6t',
            # 'AWSALBCORS': 'llFwyk7SkkMA4vBzvieFkO4O2uk6zlWqyeJSlSGAXebEh6ajPHvKfsOROc4FU9iajj7/YVCbQWqAPfPMa0GvR+ugFf785pSrViVn3r0TJ9KdtzEC5knf2sOAla6t',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'connect.sid=s%3Ay7o06YwqYDxUM960cW1dEcwe_DXRqEem.CoQe8A9nELoDZwrs6Vplra%2F6aZ4Om7qtbfiFabivpPI; AWSALB=llFwyk7SkkMA4vBzvieFkO4O2uk6zlWqyeJSlSGAXebEh6ajPHvKfsOROc4FU9iajj7/YVCbQWqAPfPMa0GvR+ugFf785pSrViVn3r0TJ9KdtzEC5knf2sOAla6t; AWSALBCORS=llFwyk7SkkMA4vBzvieFkO4O2uk6zlWqyeJSlSGAXebEh6ajPHvKfsOROc4FU9iajj7/YVCbQWqAPfPMa0GvR+ugFf785pSrViVn3r0TJ9KdtzEC5knf2sOAla6t',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = requests.get(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v2/case/{self.caseId}/watchlist',
            cookies=cookies,
            headers=headers,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            watchlist_result_json = response.json()

            self.watchlist_result_json = watchlist_result_json

            return {
                "success": True,
                "data":{
                    "watchlist_result_json": watchlist_result_json
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def resolve(self, resultIds:list, statusId, riskId, reasonId, remark):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'zc4gs+MA20+tRBzEWUGL1EeG8C6f23hP5AcheEaqI394Cl1tRBuG6/3L0CH/aiF7A3HVLwQhRISuqIlQgZxcVJfOIAx4KL6hf7nKFjeRv9jengG/i0zw+iri5/E+',
            # 'AWSALBCORS': 'zc4gs+MA20+tRBzEWUGL1EeG8C6f23hP5AcheEaqI394Cl1tRBuG6/3L0CH/aiF7A3HVLwQhRISuqIlQgZxcVJfOIAx4KL6hf7nKFjeRv9jengG/i0zw+iri5/E+',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3AXB9YPHVywDr_OjiWKCm8LNVM_ViYXeor.tDWUSIQ9ZSzU6Bgc0yxRZCdiV1Aq8Ax22fYZ13jvYWY; AWSALB=zc4gs+MA20+tRBzEWUGL1EeG8C6f23hP5AcheEaqI394Cl1tRBuG6/3L0CH/aiF7A3HVLwQhRISuqIlQgZxcVJfOIAx4KL6hf7nKFjeRv9jengG/i0zw+iri5/E+; AWSALBCORS=zc4gs+MA20+tRBzEWUGL1EeG8C6f23hP5AcheEaqI394Cl1tRBuG6/3L0CH/aiF7A3HVLwQhRISuqIlQgZxcVJfOIAx4KL6hf7nKFjeRv9jengG/i0zw+iri5/E+',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'caseId': self.caseId,
            'resultIds': resultIds,
            'statusId': statusId,
            'riskId': riskId,
            'reasonId': reasonId,
            'remark': remark,
        }

        response = requests.post(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v1/case/{self.caseId}/resolve',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            return {
                "success": True,
                "data":{
                    "resolve_result_json": response.json()
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def media_check(self, entityName, entityType:str = "ORGANISATION"):

        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': '1AcYGxczttxxb+wOWHx7DRXhSXhWAS8GRxVGNGCcpAWJnWv7uWORqreUwZCIdsBW31+g0pu4dIciD14YKYVXaIJVAyS/mUNoyLfY8acUSEBfoLy5y2189pDE6vs+',
            # 'AWSALBCORS': '1AcYGxczttxxb+wOWHx7DRXhSXhWAS8GRxVGNGCcpAWJnWv7uWORqreUwZCIdsBW31+g0pu4dIciD14YKYVXaIJVAyS/mUNoyLfY8acUSEBfoLy5y2189pDE6vs+',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3A32t3fIvNgKkvmAleMEZWWGYzNunHCeh9.6WjA%2BaiXc76y%2FUlEvEltrywbGyt%2FTQM9ikbhnEU57Vw; AWSALB=1AcYGxczttxxb+wOWHx7DRXhSXhWAS8GRxVGNGCcpAWJnWv7uWORqreUwZCIdsBW31+g0pu4dIciD14YKYVXaIJVAyS/mUNoyLfY8acUSEBfoLy5y2189pDE6vs+; AWSALBCORS=1AcYGxczttxxb+wOWHx7DRXhSXhWAS8GRxVGNGCcpAWJnWv7uWORqreUwZCIdsBW31+g0pu4dIciD14YKYVXaIJVAyS/mUNoyLfY8acUSEBfoLy5y2189pDE6vs+',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'requests': {
                'NEW_ARTICLES': {
                    'caseId': self.caseId,
                    'searchNameAsTerm': False,
                    'deduplication': 'compositeNew',
                    'entityName': entityName,
                    'entityType': entityType,
                    'includeSnippets': True,
                    'facetRequest': {
                        'drillDownKeys': [],
                        'facetCategoryFilters': [
                            {
                                'facetCategoryType': 'phases',
                            },
                            {
                                'facetCategoryType': 'risk-topics',
                            },
                            {
                                'maximumCount': 50,
                                'facetCategoryType': 'rcs-geography',
                            },
                            {
                                'facetCategoryType': 'pub-types',
                            },
                            {
                                'facetCategoryType': 'pub-date',
                                'order': 'ASC',
                                'interval': None,
                            },
                        ],
                    },
                    'pagination': {
                        'itemsPerPage': 25,
                        'sort': 'newToOld',
                    },
                    'query': None,
                    'time': None,
                    'timeConstraints': None,
                    'searchRequestType': 'REVIEW_REQUIRED',
                    'groupId': self.groupId,
                },
            },
        }

        response = requests.post(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v3/case/{self.caseId}/mediacheck',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            media_check_result_json = response.json()
            self.media_check_result_json = media_check_result_json
            return {
                "success": True,
                "data":{
                    "media_check_result_json": media_check_result_json
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def media_check_review(self):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'AsQrfcx2LOSdbpE7dQ8WcLHlNjOD4Mmb7NBcKGrtNUpfhywAL5sCLW5WjhkqRzJqrUw8ERa3++29rJMFPgQlYudJAJ8nZ4k/qMJFO2FuR6Tk4sLCtFWmZ4jfD3mw',
            # 'AWSALBCORS': 'AsQrfcx2LOSdbpE7dQ8WcLHlNjOD4Mmb7NBcKGrtNUpfhywAL5sCLW5WjhkqRzJqrUw8ERa3++29rJMFPgQlYudJAJ8nZ4k/qMJFO2FuR6Tk4sLCtFWmZ4jfD3mw',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'content-length': '0',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3A32t3fIvNgKkvmAleMEZWWGYzNunHCeh9.6WjA%2BaiXc76y%2FUlEvEltrywbGyt%2FTQM9ikbhnEU57Vw; AWSALB=AsQrfcx2LOSdbpE7dQ8WcLHlNjOD4Mmb7NBcKGrtNUpfhywAL5sCLW5WjhkqRzJqrUw8ERa3++29rJMFPgQlYudJAJ8nZ4k/qMJFO2FuR6Tk4sLCtFWmZ4jfD3mw; AWSALBCORS=AsQrfcx2LOSdbpE7dQ8WcLHlNjOD4Mmb7NBcKGrtNUpfhywAL5sCLW5WjhkqRzJqrUw8ERa3++29rJMFPgQlYudJAJ8nZ4k/qMJFO2FuR6Tk4sLCtFWmZ4jfD3mw',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = requests.put(
            f'https://wc1-worldcheck.refinitiv.com/fsp/case/v1/case/{self.caseId}/mediaCheckReview',
            cookies=cookies,
            headers=headers,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            return {
                "success": True,
                "data":{
                    "media_check_review_result_json": response.json()
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }
        
    def export_case_report(self): 
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'QCEuY5/TcF9g3VhNxq9whWR+Rc6BgAOgR/Q2pCiQxcgSUIQQmZgRWtHQlcbJEr+XfCoVTmBWcvTgOAL8bQazg7nIKaKp/rcEnvlV8ADc+VRfMpNPJafxLJJRNvPH',
            # 'AWSALBCORS': 'QCEuY5/TcF9g3VhNxq9whWR+Rc6BgAOgR/Q2pCiQxcgSUIQQmZgRWtHQlcbJEr+XfCoVTmBWcvTgOAL8bQazg7nIKaKp/rcEnvlV8ADc+VRfMpNPJafxLJJRNvPH',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3A32t3fIvNgKkvmAleMEZWWGYzNunHCeh9.6WjA%2BaiXc76y%2FUlEvEltrywbGyt%2FTQM9ikbhnEU57Vw; AWSALB=QCEuY5/TcF9g3VhNxq9whWR+Rc6BgAOgR/Q2pCiQxcgSUIQQmZgRWtHQlcbJEr+XfCoVTmBWcvTgOAL8bQazg7nIKaKp/rcEnvlV8ADc+VRfMpNPJafxLJJRNvPH; AWSALBCORS=QCEuY5/TcF9g3VhNxq9whWR+Rc6BgAOgR/Q2pCiQxcgSUIQQmZgRWtHQlcbJEr+XfCoVTmBWcvTgOAL8bQazg7nIKaKp/rcEnvlV8ADc+VRfMpNPJafxLJJRNvPH',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        params = {
            'format': 'pdf',
            'mediaCheck': 'NONE',
        }

        json_data = {
            'note': '',
        }

        response = requests.post(
            f'https://wc1-worldcheck.refinitiv.com/fsp/reporting/v1/case/{self.caseId}/dossier/export',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            case_report_content = response.content

            self.case_report_content = case_report_content

            return {
                "success": True,
                "data":{
                    "case_report_content": case_report_content
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }
        
    def export_record(self, resultId):
        cookies = {
            'connect.sid': self.connect_sid,
            # 'AWSALB': 'qB+/jTOEYqmXkzNfIi9rlWPtJqc165u0L75E0LDvjAZsPgHIvRZnnDkcA9vZhAEt7wQldzSWVKnG5E/5V0BJ2fh9++60DViq7NVz6cw1VmfZk+c4Fw5lJPJ2mYmD',
            # 'AWSALBCORS': 'qB+/jTOEYqmXkzNfIi9rlWPtJqc165u0L75E0LDvjAZsPgHIvRZnnDkcA9vZhAEt7wQldzSWVKnG5E/5V0BJ2fh9++60DViq7NVz6cw1VmfZk+c4Fw5lJPJ2mYmD',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'connect.sid=s%3A32t3fIvNgKkvmAleMEZWWGYzNunHCeh9.6WjA%2BaiXc76y%2FUlEvEltrywbGyt%2FTQM9ikbhnEU57Vw; AWSALB=qB+/jTOEYqmXkzNfIi9rlWPtJqc165u0L75E0LDvjAZsPgHIvRZnnDkcA9vZhAEt7wQldzSWVKnG5E/5V0BJ2fh9++60DViq7NVz6cw1VmfZk+c4Fw5lJPJ2mYmD; AWSALBCORS=qB+/jTOEYqmXkzNfIi9rlWPtJqc165u0L75E0LDvjAZsPgHIvRZnnDkcA9vZhAEt7wQldzSWVKnG5E/5V0BJ2fh9++60DViq7NVz6cw1VmfZk+c4Fw5lJPJ2mYmD',
            'csrf-token': self.csrf_token,
            'origin': 'https://wc1-worldcheck.refinitiv.com',
            'priority': 'u=1, i',
            'referer': 'https://wc1-worldcheck.refinitiv.com/current/?locale=en-GB',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        params = {
            'format': 'pdf',
        }

        json_data = {
            'note': '',
        }

        response = requests.post(
            f'https://wc1-worldcheck.refinitiv.com/fsp/reporting/v1/case/{self.caseId}/match/{resultId}/export',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        func_name = inspect.stack()[0][3]    
        if response.status_code == 200:
            print(f"{func_name} success with status code = {response.status_code}.")
            record_content = response.content
            self.record_content = record_content
            return {
                "success": True,
                "data":{
                    "record_content": record_content
                }
            }
        else:
            print(f"{func_name} fail with status code = {response.status_code}.")
            self.SUCCESS = False
            return {
                "success": False,
                "data":{}
            }

    def Load_Login_Page(self):
        self.worldcheck_refinitiv_com()
        self.risk_lseg_com()
        self.authorization_oauth2()
        self.authorization_ping_pre()
        print("[Done] Load login page success.")

    def Login(self):
        self.authorization_ping()
        self.risk_lseg_com_after()
        self.login()
        self.session()
        self.current_locale_en_GB()
        print("[Done] Login success.")

    def Features(self):
        self.features()
        self.config()
        print("[Done] Features and configs load success.")
    
    def Screen(self, entityName, entityType):
        print(f"[Working] Screening {entityName} as {entityType} ...")
        self.save(keyword=entityName, entityType = entityType)
        self.screen()
        self.summary()
        self.watchlist()
        self.total_num = None
        self.match_num = None
        print(f"[Done] Screen {entityName} as {entityType} success.")

    def Resolve(self):
        print(f"[Working] Resolving ...")
        total_num = len(self.watchlist_result_json.get("results"))
        match_num = 0
        match_items = []
        none_match_items = []
        for item in self.watchlist_result_json.get("results"):
            if item.get("score") == 1 and item.get("strength") == "EXACT":
                match_items.append(item)
                match_num += 1
            else:
                none_match_items.append(item)
        self.total_num = total_num
        self.match_num = match_num
        print(f"[Working] {match_num}/{total_num} match found.")
        if total_num == 0:
            self.CaseReportExport = True
            self.RecordExport = False
            res = None
        elif total_num != 0:
            if match_num == 0:
                resultIds = []
                self.CaseReportExport = True
                self.RecordExport = False
                # resolve none_match loop
                for item in none_match_items:
                    resultIds.append(item.get("resultId"))
                statusId = self.get_status_id(configs = self.configs, status_label = "FALSE")
                riskId = self.get_risk_id(configs = self.configs, risk_label = "UNKNOWN")
                reasonId = self.get_reason_id(configs = self.configs, reason_label = "NO MATCH")
                remark = 'wrong name'
                self.resolve(
                    resultIds=resultIds,
                    statusId=statusId,
                    riskId=riskId,
                    reasonId=reasonId,
                    remark=remark
                )
                self.watchlist()
                self.summary()
                res = None
            elif match_num == 1:
                self.CaseReportExport = True
                self.RecordExport = True
                # resolve match case
                resultIds = []
                for item in match_items:
                    resultIds.append(item.get("resultId"))
                statusId = self.get_status_id(configs = self.configs, status_label = "POSITIVE")
                riskId = self.get_risk_id(configs = self.configs, risk_label = "LOW")
                reasonId = self.get_reason_id(configs = self.configs, reason_label = "FULL MATCH")
                remark = ''
                self.resolve(
                    resultIds=resultIds,
                    statusId=statusId,
                    riskId=riskId,
                    reasonId=reasonId,
                    remark=remark
                )
                # resolve none_match cases loop
                resultIds = []
                for item in none_match_items:
                    resultIds.append(item.get("resultId"))
                statusId = self.get_status_id(configs = self.configs, status_label = "FALSE")
                riskId = self.get_risk_id(configs = self.configs, risk_label = "UNKNOWN")
                reasonId = self.get_reason_id(configs = self.configs, reason_label = "NO MATCH")
                remark = 'wrong name'
                self.resolve(
                    resultIds=resultIds,
                    statusId=statusId,
                    riskId=riskId,
                    reasonId=reasonId,
                    remark=remark
                )
                res = match_items[0].get("resultId")
            elif match_num > 1:
                self.CaseReportExport = False
                self.RecordExport = False
                # human
                res = False
        print(f"[Done] Resolve success.")
        return res
        
    def Main(self, entities:dict):
        self.Load_Login_Page()
        self.Login()
        self.Features()
        entityClasses = []
        for entityName, value_dict in entities.items():
            entityClass = value_dict.get("entityClass")
            if entityClass not in entityClasses:
                entityClasses.append(entityClass)
                self.check_dir(folder_name=entityClass)
            else:
                continue
        for entityName, value_dict in entities.items():
            entityType = value_dict.get("entityType")
            entityClass = value_dict.get("entityClass")
            self.Screen(entityName=entityName, entityType=entityType)
            res = self.Resolve()
            if res is None:
                pass
            elif res == False:
                print(f"[Warning] {entityName} as {entityType} has multiple matcheds, please check manually.")
            else:
                resultId = res
            
            if self.CaseReportExport:
                self.export_case_report()
                self.download_file(folder_name = entityClass, file_name = entityName, content = self.case_report_content)
            if self.RecordExport:
                self.export_record(resultId=resultId)
                self.download_file(folder_name = entityClass, file_name = f"{entityName}_profile", content = self.record_content)
            
            entities[entityName].update({
                "Screening Result": self.match_num,
                "Note": f"{self.total_num} screening results found and {self.match_num} matched" if self.match_num<=1 else f"{entityName} as {entityType} has multiple matcheds, please check manually."
                })
        self.output = entities