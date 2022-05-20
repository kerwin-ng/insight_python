# coding = utf-8
import json

import requests
from flask import Flask, request

from WXBizDataCrypt import WXBizDataCrypt

app = Flask(__name__)


@app.route('/wxlogin', methods=['GET', 'POST'])
def wxuser_login():
    data = json.loads(request.get_data().decode('utf-8'))
    appid = 'wx410bd3df4bf97389'  # 小程序 appid
    secret = '1d59463a0b6182cf5874a1319dba300d'  # 小程序 app secret
    code = data['platCode']
    encrypted_data = data['platUserInfoMap']['encryptedData']
    iv = data['platUserInfoMap']['iv']

    print('code:', code)

    request_params = {
        'appid': appid,
        'secret': secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }

    wx_login_api = 'https://api.weixin.qq.com/sns/jscode2session'
    response_data = requests.get(wx_login_api, params=request_params)
    res_data = response_data.json()

    openid = res_data['openid']
    session_key = res_data['session_key']
    print('openid:', openid)
    print('session_key:', session_key)
    print('response_data:', response_data)
    print('res_data:', res_data)
    pc = WXBizDataCrypt()
    userinfo = pc.decrypt(encrypted_data, iv)
    print(userinfo)

    return 'done'


if __name__ == '__main__':
    app.debug = True
    app.run()
