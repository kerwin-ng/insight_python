# coding = utf-8
import json
import os
import sys
import click

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 数据库路径
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
print('log-database', prefix)


class User(db.Model):
    openid = db.Column(db.String(64), primary_key=True)
    session_key = db.Column(db.String(64))


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

@app.route('/db')
def db_search():
    user = User.query.first()
    print('log-db:', user)
    return None

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


if __name__ == '__main__':
    app.debug = True
    app.run()
