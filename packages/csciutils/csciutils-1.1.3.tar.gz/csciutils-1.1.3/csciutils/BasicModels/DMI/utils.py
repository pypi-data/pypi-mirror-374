import time as timer
import hashlib
import requests
import re

def sign_generator(param:str):
    hl = hashlib.md5()
    hl.update(param.encode("utf-8"))
    return hl.hexdigest()

def timestamp_generator() -> str:
    return str(int(round(timer.time()*1000)))

def load_device_id_from_cookie(cookie:str):
    pattern = r'device_id=(\w+);?'
    matches = re.search(pattern, cookie)
    if matches:
        device_id = matches.group(1)
        return device_id
    else:
        return None

class fakeLogin():
    def __init__(self)->None:
        self.device_id = "e9f11848297513a743509508dcd45e4d"
    
    def login(self, username, password)->None:
        session = requests.session()
        url = "https://web.cscidmi.com/international-auth-service/login/web?redirect_to="
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer":"https://web.cscidmi.com/international-auth-service/login/web",
        }
        data = {
            "username": username,
            "password": password
        }
        respond = session.post(url, headers = headers, data = data)
        cookies_dict = session.cookies.get_dict()
        self.city = cookies_dict.get("city")
        self.name = cookies_dict.get("name")
        self.sid = cookies_dict.get("sid")
        self.uid = cookies_dict.get("uid")
        self.userInst = cookies_dict.get("userInst")
        self.userName = cookies_dict.get("userName")
        self.userid = cookies_dict.get("userid")
        self.cookie = f"city={self.city}; userInst={self.userInst}; device_id={self.device_id}; uid={self.uid}; userid={self.userid}; name={self.name}; userName={self.userName}; sid={self.sid}"
        self.success = True if respond.status_code == 200 and self.sid is not None else False