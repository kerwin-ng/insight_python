# coding = utf-8

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    appid = 'wx410bd3df4bf97389'
    secret = '1d59463a0b6182cf5874a1319dba300d'
    code = request.args.get('code')
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
    print(res_data)
    return 'done'


if __name__ == '__main__':
    app.debug = True
    app.run()
