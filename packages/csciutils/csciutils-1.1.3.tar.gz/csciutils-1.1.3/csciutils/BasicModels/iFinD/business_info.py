"""
工商信息
"""

from datetime import datetime
import requests
import inspect

class iFinD_Basic_Info():
    def __init__(self, access_token:str, credit_base_date:str = None) -> None:
        """
        - credit_base_date: str | yyyymmdd | 授信日期，一般默认当天
        """
        self.proxy = {
            'ths_unified_social_credit_code_company': '统一社会信用代码',
            'ths_operating_scope_company': '经营范围',
            'ths_established_date_company': '成立日期',
            'ths_reg_address_company': '注册地址',
            'ths_corp_tel_company': '联系方式',
            'ths_legal_representative_company': '法定代表人',
            'ths_reg_capital_company': '注册资本',
            'ths_registered_capital_currency_company': '注册资本单位',
            'ths_province_company': '省份',
            'ths_n_latest_credit_line_company': '授信金额（亿）',
            'ths_n_latest_unused_credit_line_company': '未使用授信金额（亿）',
            'ths_n_latest_used_credit_line_company': '已使用授信金额（亿）',
            'ths_n_latest_credit_extension_date_company': '最新授信日期' #yyyymmdd
        }
        self.credit_base_date = datetime.today().strftime("%Y%m%d") if credit_base_date is None else credit_base_date
        self.requestHeaders = {
            "Content-Type":"application/json",
            "access_token":access_token
        }
        self.url = 'https://quantapi.51ifind.com/api/v1/basic_data_service'
        
    def search(self, companyName:str):
        formData = {
            "codes": companyName,
            "indipara":[
                {"indicator":"ths_unified_social_credit_code_company"},
                {"indicator":"ths_operating_scope_company"},
                {"indicator":"ths_established_date_company"},
                {"indicator":"ths_reg_address_company"},
                {"indicator":"ths_corp_tel_company"},
                {"indicator":"ths_legal_representative_company"},
                {"indicator":"ths_reg_capital_company"},
                {"indicator":"ths_registered_capital_currency_company"},
                {"indicator":"ths_province_company"},
                {"indicator":"ths_n_latest_credit_line_company","indiparams":[self.credit_base_date]},
                {"indicator":"ths_n_latest_unused_credit_line_company","indiparams":[self.credit_base_date]},
                {"indicator":"ths_n_latest_used_credit_line_company","indiparams":[self.credit_base_date]},
                {"indicator":"ths_n_latest_credit_extension_date_company","indiparams":[self.credit_base_date]}
            ]
        }
        res = requests.post(url = self.url, headers = self.requestHeaders, json = formData)
        dic = {
            'success': False,
            'data': {}
        }
        if res.status_code == 200:
            if res.json().get("errorcode") == 0:
                tables = res.json().get('tables')[0]
                table = tables.get("table")
                for k,v in self.proxy.items():
                    dic['data'].update({
                        v: table.get(k)[0]
                    })
                dic['success'] = True
                print(f'{self.__class__.__name__}/{inspect.stack()[0][3]} for companyName = {companyName} success.')
            else:
                print(f'{self.__class__.__name__}/{inspect.stack()[0][3]} for companyName = {companyName} failed with errorcode = {res.json().get("errorcode")}.')
        else:
            print(f'{self.__class__.__name__}/{inspect.stack()[0][3]} for companyName = {companyName} failed with status_code = {res.status_code}.')
        return dic
        