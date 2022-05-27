# coding = utf-8
import json
import os
import sys
import uuid
import time
import appkey  # 导入密钥

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
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')  # 连接数据库
print('log-database:', prefix)


# User 表
class User(db.Model):
    openid = db.Column(db.String(64), primary_key=True)
    session_key = db.Column(db.String(64))
    openid_uuid = db.Column(db.String(256))


# 注册登录模块
@app.route('/wxlogin', methods=['POST', 'GET'])
def wxuser_login():
    data = json.loads(request.get_data().decode('utf-8'))
    appid = appkey.appid  # 小程序 appid
    secret = appkey.secret  # 小程序 app secret
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
    openid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, openid))  # 将 openid 转化为 uuid
    print('log:生成uuid ', openid_uuid)

    user_count = db.session.query(User).filter_by(openid=openid).count()  # 查询数据库openid是否已经存在
    if user_count == 0:

        print('数据展示:')
        print('openid:', openid)
        print('session_key:', session_key)
        print('uuid', openid_uuid)
        print(type(openid_uuid))

        new_user = User(openid=openid, session_key=session_key, openid_uuid=openid_uuid)
        db.session.add(new_user)
        db.session.commit()
        status = '1'
        registered = '0'
        print('用户未存在，注册成功')

    else:
        status = '1'
        registered = '1'
        print('用户已存在，登录成功')

    return_data = {
        'uuid': openid_uuid,
        # 'session_key': session_key,
        'status': status,
        'registered': registered
    }

    return return_data


# 上传健康码
@app.route('/user/upload/health_code', methods=['POST'])
def health_code_upload():
    try:
        user_uuid = request.form['uuid']

    except:
        filename = 'none'
        status = 0
        print('无效请求，uuid不存在')

    else:
        print('user uuid:', user_uuid)
        file = request.files['HealthCode']

        # 查询数据库是否存在这条 uuid
        user_uuid_count = db.session.query(User).filter_by(openid_uuid=user_uuid).count()
        if user_uuid_count == 1:
            # 文件名生成 年月日时分 + UUID
            filename = time.strftime("%Y_%m_%d_%H_%M_", time.localtime()) + user_uuid + '.png'
            file.save('./data/img/health_code/{}'.format(filename))  # 保存到 /data/img/health_code/
            status = 1

        else:
            filename = 'none'
            status = 0
            print('无效请求，uuid不存在')

    # if request.form['uuid']:
    #     user_uuid = request.form['uuid']
    #     print('user uuid:', user_uuid)
    #     file = request.files['HealthCode']
    #
    #     user_uuid_count = db.session.query(User).filter_by(openid_uuid=user_uuid).count()
    #     if user_uuid_count == 1:
    #         # 文件名生成 年月日时分 + UUID
    #         filename = time.strftime("%Y_%m_%d_%H_%M_", time.localtime()) + user_uuid + '.png'
    #         file.save('./data/img/health_code/{}'.format(filename))  # 保存到 /data/img/health_code/
    #         status = 1
    #
    #     else:
    #         filename = 'none'
    #         status = 0
    #         print('无效请求，uuid不存在')
    #
    # else:
    #     filename = 'uuid err'
    #     status = 0

    return_data = {
        'filename': filename,
        'status': status
    }

    return return_data


# 报告模块
@app.route('/user/report', methods=['POST'])
def report_submit():
    data = json.loads(request.get_data().decode('utf-8'))
    print(data)
    return '200'


@app.route('/db')
def db_search():
    user = User.query.first()
    print('log-db:', user)
    return None


@app.route('/time', methods=['POST', 'GET'])
def get_time():
    return_time = time.strftime("%Y-%m-%d", time.localtime())
    return return_time


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
    app.run(port=19999)
