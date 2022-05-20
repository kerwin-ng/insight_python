# coding = utf-8
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/wxlogin', methods=['POST', 'GET'])
def wxuser_login():
    data = json.loads(request.get_data().decode('utf-8'))
    appid = 'wx410bd3df4bf97389'  # 小程序 appid
    secret = '1d59463a0b6182cf5874a1319dba300d'  # 小程序 app secret
    wx_login_api = 'https://api.weixin.qq.com/sns/jscode2session'  # 微信 auth.code2Session API
    code = data['userCode']  # 获取小程序用户临时登录凭证 code
    print('log-code:', code)

    request_params = {
        'appid': appid,
        'secret': secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }

    # 向 API 请求返回的 openid 和 session_key
    response_data = requests.get(wx_login_api, params=request_params)
    res_data = response_data.json()
    print('log-res_data:', res_data)

    openid = res_data['openid']
    session_key = res_data['session_key']
    print('log-openid:', openid)
    print('log-session_key:', session_key)

    return code


if __name__ == '__main__':
    app.debug = True
    app.run()
