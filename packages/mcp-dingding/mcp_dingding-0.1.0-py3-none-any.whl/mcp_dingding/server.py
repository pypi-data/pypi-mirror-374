from mcp.server.fastmcp import FastMCP

import requests
import json
import base64
import time
import hmac
import hashlib
import base64
import urllib.parse
# https://oapi.dingtalk.com/robot/send?access_token=110c78e30c2efaa94c783f8dd652417d06f1f3f0800e40eee628205e67a443e4
mcp = FastMCP("dingservice")

secret = ""
access_token = ""

@mcp.tool()
async def auth(new_secret: str, new_access_token: str):
    """
    这是进行钉钉推送之前所必须的验证部分，
    在运行本mcp服务其他功能之前必须调用该函数，
    在运行其他所有功能之前，必须先验证
    secret和access_token的内容必须通过询问用户获得
    
    Args:
        secret (str): 验证所需要的secret
        access_token (str): 验证所需要的access_token

    Returns:
        dict: 返回一个字典，包含secret和access_token
    """
    global secret 
    global access_token
    secret = new_secret
    access_token = new_access_token
    return {"secret": secret, "access_token": access_token}

@mcp.tool()
async def push(content: str):
    """
    使用钉钉推送消息，
    要求符合钉钉推送格式
    
    Args:
        content (str): 需要推送的内容

    Returns:
        dict: 返回一个字典，包含推送是否成功
    """

    timestamp, sign = get_sign()

    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'

    print(url)

    body = {
        # "at": {
        #     "isAtAll": str(is_at_all).lower(),
        #     "atUserIds": at_user_ids or [],
        #     "atMobiles": at_mobiles or []
        # },
        "text": {
            "content": content
        },
        "msgtype": "text"
    }
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=body, headers=headers)
    # print("钉钉自定义机器人群消息响应：%s", resp.json())
    return resp.json()

def get_sign():
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign

if __name__ == "__main__":
    mcp.run(transport="stdio")
