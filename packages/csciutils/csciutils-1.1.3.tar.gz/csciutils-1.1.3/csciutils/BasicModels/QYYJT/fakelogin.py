from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.proxy import Proxy, ProxyType # type: ignore
import inspect
import time
import json

class FakeLogin():
    def __init__(self,
                 proxy_ip:str = None,
                 proxy_port:int = None,
                 driver_path:str = None) -> None:
        self.chrome_options = webdriver.ChromeOptions()
        # 设置proxy
        if proxy_ip is not None and proxy_port is not None:
            # self.proxy = Proxy()
            # self.proxy.proxy_type = ProxyType.MANUAL
            # self.proxy.http_proxy = f"{proxy_ip}:{proxy_port}"
            # self.proxy.ssl_proxy = f"{proxy_ip}:{proxy_port}"
            self.chrome_options.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
        # 设置无头
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')  # 禁用沙盒
        self.chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用共享内存
        # 设置driver路径
        self.service = Service(driver_path)

    def lauch_driver(self)->None:
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")

    def load_login_page(self)->None:
        self.driver.get('http://qyyjt.cn')
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")

    def login(self, 
              account:str,
              password:str)->None:
        self.driver.find_element(By.XPATH, "//*[text()='账户密码登录']").click()
        self.driver.find_element(By.XPATH, "//*[@placeholder='请输入手机号']").clear()
        self.driver.find_element(By.XPATH, "//*[@placeholder='请输入手机号']").send_keys(account)
        self.driver.find_element(By.XPATH, "//*[@placeholder='请输入密码']").send_keys("raw")
        self.driver.find_element(By.XPATH, "//span[@class='ant-input-clear-icon ant-input-clear-icon-has-suffix']").click()
        self.driver.find_element(By.XPATH, "//*[@placeholder='请输入密码']").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")

    def fetch_user(self,max_retry = 200)->str:
        retry_times = 0
        while retry_times < max_retry:
            try:
                user = json.loads(self.driver.execute_script("return window.localStorage.getItem('u_info');")).get("user")
                break
            except:
                time.sleep(0.1)
                retry_times += 1
        self.user = user
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")
        return user

    def fetch_token(self,max_retry = 200)->str:
        retry_times = 0
        while retry_times < max_retry:
            try:
                token = self.driver.execute_script("return window.localStorage.getItem('s_tk');")
                token = token.strip('"')
                break
            except:
                time.sleep(0.1)
                retry_times += 1
        self.token = token
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")
        return token
    
    def quit_driver(self)->None:
        self.driver.quit()
        func_name = inspect.stack()[0][3]
        print(f"{self.__class__.__name__}/{func_name} success")