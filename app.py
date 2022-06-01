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


# User表
class User(db.Model):
    openid = db.Column(db.String, primary_key=True)  # OpenID
    session_key = db.Column(db.String)  # session key
    openid_uuid = db.Column(db.String)  # 由 OpenID 生成的 uuid


# Report表 记录报告上来的数据
class Report(db.Model):
    report_uuid = db.Column(db.String, primary_key=True)  # 每一项报告生成的 uuid
    openid_uuid = db.Column(db.String)  # 用户 uuid
    time = db.Column(db.String)  # 报告生成时间
    name = db.Column(db.String)  # 名字
    the_class = db.Column(db.String)  # 班级
    no = db.Column(db.String)  # 学号
    phone = db.Column(db.String)  # 手机号
    temperature = db.Column(db.String)  # 体温
    risk_location = db.Column(db.String)  # 中高风险城市
    address = db.Column(db.String)  # 当前位置
    health_code = db.Column(db.String)  # 健康码截图路径
    itinerary_code = db.Column(db.String)  # 行程卡截图路径


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
    openid_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, openid))  # 将 openid 转化为 uuid
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
        print(type(user_uuid_count))
        if user_uuid_count == 1:
            # 文件名生成 年月日时分 + UUID
            filename = 'hc_' + time.strftime("%Y_%m_%d_%H%M_%S_", time.localtime()) + user_uuid + '.png'
            file.save('./data/img/health_code/{}'.format(filename))  # 保存到 /data/img/health_code/
            status = 1

        else:
            filename = 'none'
            status = 0
            print('无效请求，uuid未注册')

    return_data = {
        'filename': filename,
        'status': status
    }

    return filename


# 上传行程卡
@app.route('/user/upload/itinerary_code', methods=['POST'])
def itinerary_code_upload():
    try:
        user_uuid = request.form['uuid']

    except:
        filename = 'none'
        status = 0
        print('无效请求，uuid不存在')

    else:
        print('user uuid', user_uuid)
        file = request.files['ItineraryCode']

        # 查询数据库是否存在这条 uuid
        user_uuid_count = db.session.query(User).filter_by(openid_uuid=user_uuid).count()
        if user_uuid_count == 1:
            # 文件名生成
            filename = 'ic_' + time.strftime("%Y_%m_%d_%H%M_%S_", time.localtime()) + user_uuid + '.png'
            file.save('./data/img/itinerary_code/{}'.format(filename))
            status = 1

        else:
            filename = 'none'
            status = 0
            print('无效请求，uuid未注册')

        return_data = {
            'filename': filename,
            'status': status
        }

        return filename


# 报告模块
@app.route('/user/report', methods=['POST'])
def report_submit():
    data = json.loads(request.get_data().decode('utf-8'))
    print('接收到的数据：', data)
    name = data['name']
    the_class = data['the_class']
    no = data['no']
    phone = data['phone']
    risk_location = data['risk_location']
    temperature = data['temperature']
    address = data['address']
    health_code = data['health_code']
    itinerary_code = data['itinerary_code']
    user_uuid = data['uuid']
    report_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    print(name, the_class, no, phone, risk_location, temperature, address, health_code, itinerary_code)
    print('用户uuid：', user_uuid)
    report_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, report_time + user_uuid))
    print('报告uuid：', report_uuid)

    user_search = db.session.query(User).filter_by(openid_uuid=user_uuid).count()
    if user_search == 1:

        # 写入数据库
        new_report = Report(report_uuid=report_uuid, openid_uuid=user_uuid, time=report_time, name=name,
                            the_class=the_class, no=no, phone=phone, temperature=temperature,
                            risk_location=risk_location,
                            address=address, health_code=health_code, itinerary_code=itinerary_code)
        db.session.add(new_report)
        db.session.commit()
        print('写入数据库成功,report uuid: ', report_uuid)

    else:
        print('User表没有找到这个uuid，不执行写入数据库')
        return 'uuid err'

    return report_uuid


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
