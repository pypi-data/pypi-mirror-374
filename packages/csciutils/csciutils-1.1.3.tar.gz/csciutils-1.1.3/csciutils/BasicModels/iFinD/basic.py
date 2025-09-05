import requests

def get_access_token(refresh_token:str)->str:
    url = 'https://ft.10jqka.com.cn/api/v1/get_access_token'
    headers = {
        'Content-Type': 'application/json',
        'refresh_token': refresh_token
    }
    res = requests.get(url = url, headers = headers)
    if res.status_code == 200:
        errmsg = res.json().get('errmsg')
        if errmsg == 'success':
            access_token = res.json().get("data").get("access_token")
            expired_time = res.json().get("data").get("expired_time")
            print(f"Get access_token = {access_token} success with status_code = {res.status_code} and errmsg = {errmsg}, this token would expire at {expired_time}")
            return {
                "success": True,
                "data": {
                    "access_token": access_token
                }
            }
    return {
        "success": False,
        "data": {}
    }