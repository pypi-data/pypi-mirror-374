from datetime import datetime
import inspect

class Proxy_Checklist():
    def __init__(self, inputs:dict, iFinDdic:dict) -> None:
        self.proxy_checklist = { # 最终用于填入checklist的数据，第1层数据穿透
                "项目名": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "发行人": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "关联方": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "项目负责人": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "报告日期yyyymm": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "目标时间表": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "介绍人信息": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "主动接触信息": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "报告日期yyyy": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "交易摘要": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "角色": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "资金用途": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "客户英文全称": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "客户中文全称": {
                    "success": False,
                    "resource": "inputs",
                    "data": None
                },
                "注册国家": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "成立日期": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "注册登记证号码": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "商业登记证号码": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "注册地址": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "经营范围": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "注册资本": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "注册资本单位": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "联系人姓名": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "联系人电话": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
                "报告日期yyyy_mm_dd": {
                    "success": False,
                    "resource": "function",
                    "data": None
                },
            }
        self.today = datetime.today()
        self.inputs = inputs
        self.iFinDdic = iFinDdic

    def fetchInputs(self)->None:
        for key,value in self.inputs.items():
            proxy_data = self.proxy_checklist.get(key)
            if proxy_data is not None:
                if value is not None and proxy_data.get("resource") == "inputs":
                    self.proxy_checklist[key]["data"] = value
                    self.proxy_checklist[key]["success"] = True

    def fetchFunction(self)->None:
        def 关联方():
            related = []
            for role in ["担保人", "备证行", "维好协议提供人"]:
                if self.inputs.get(role) is not None:
                    related.append(f"{role}：{self.inputs.get(role)}")
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = "\n".join(related)
        def 报告日期yyyymm():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.today.strftime("%Y%m")
        def 报告日期yyyy():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.today.strftime("%Y")
        def 介绍人信息():
            sale = self.inputs.get("介绍人")
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = f"本项目由境内债承{sale}推荐" if sale is not None else ""
        def 主动接触信息():
            sale = self.inputs.get("介绍人")
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = "本项目由DCM自主获客" if sale is None else ""
        def 客户经营范围():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("经营范围")
        def 客户英文全称():
            pass # TODO
        def 注册国家():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = "中国" # 默认中国
        def 成立日期():
            set_dt = self.iFinDdic.get("成立日期")
            set_dt = datetime(year = int(set_dt[:4]), month = int(set_dt[4:6]), day = int(set_dt[6:8])).strftime("%Y年%-m月%-d日")
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = set_dt
        def 注册登记证号码():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("统一社会信用代码")
        def 商业登记证号码():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = "NA" # 默认NA
        def 注册地址():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("注册地址")
        def 经营范围():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("经营范围")
        def 注册资本():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("注册资本")
        def 注册资本单位():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("注册资本单位")
        def 联系人姓名():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("法定代表人")
        def 联系人电话():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.iFinDdic.get("联系方式")
        def 报告日期yyyy_mm_dd():
            self.proxy_checklist[inspect.stack()[0][3]]["data"] = self.today.strftime("%Y-%m-%d")
        for key,value in self.proxy_checklist.items():
            if value.get("resource") == "function":
                eval(f"""{key}()""")
                self.proxy_checklist[key]["success"] = True